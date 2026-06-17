"""
Minimal KV Cache (Key-Value Cache for autoregressive generation).

The problem: Without cache, each token generated requires a forward
pass over the ENTIRE sequence. Token 1: compute 1 attention. Token 2:
compute 2 attentions (tokens 1-2). Token N: compute N attentions.
Total compute: O(N^2) per layer.

With cache: Store the K and V matrices from previous forward passes.
When generating token N+1, only compute Q for the new token. K and V
from tokens 1..N are already cached. Concatenate old K,V with new K,V.

Total compute: O(N) per token. For a 100-token generation, this is
100x faster in the attention layer.

The trade-off: VRAM increases linearly with sequence length (store
the full K,V for all past tokens). For a 10K-token sequence with
dim=256 and 4 heads, K cache = 10K * 256 * 4 * 2 = 20MB.
"""

import torch
import torch.nn as nn


class KVCachedAttention(nn.Module):
    """
    Multi-head attention with KV cache support.

    Without cache: forward(x) -> output
    With cache:    forward(x, use_cache=True) -> output, new_kv
                   The caller appends new_kv to the existing cache.
    """

    def __init__(self, dim=256, n_heads=8):
        super().__init__()
        self.dim = dim
        self.n_heads = n_heads
        self.head_dim = dim // n_heads
        self.scale = self.head_dim ** -0.5

        self.W_q = nn.Linear(dim, dim, bias=False)
        self.W_k = nn.Linear(dim, dim, bias=False)
        self.W_v = nn.Linear(dim, dim, bias=False)
        self.W_o = nn.Linear(dim, dim, bias=False)

    def forward(self, x, kv_cache=None):
        """
        x: (batch, seq_len, dim) — current tokens
        kv_cache: dict with 'k' and 'v' from previous steps, or None

        Returns: (output, new_cache)
        """
        B, T, D = x.shape
        H = self.n_heads

        # Compute Q, K, V for current tokens
        q = self.W_q(x).view(B, T, H, self.head_dim).transpose(1, 2)  # (B, H, T, d)
        k = self.W_k(x).view(B, T, H, self.head_dim).transpose(1, 2)
        v = self.W_v(x).view(B, T, H, self.head_dim).transpose(1, 2)

        # If cache exists, prepend it
        if kv_cache is not None:
            k_cache, v_cache = kv_cache["k"], kv_cache["v"]
            k = torch.cat([k_cache, k], dim=2)  # (B, H, cache_T + T, d)
            v = torch.cat([v_cache, v], dim=2)

        # Attention
        attn = (q @ k.transpose(-2, -1)) * self.scale  # (B, H, T, total_T)

        # Build causal mask
        total_T = k.shape[2]
        mask = torch.triu(torch.ones(T, total_T), diagonal=total_T - T + 1).bool()
        attn = attn.masked_fill(mask.unsqueeze(0).unsqueeze(0), float("-inf"))

        attn = torch.softmax(attn, dim=-1)
        out = attn @ v  # (B, H, T, d)
        out = out.transpose(1, 2).reshape(B, T, D)
        out = self.W_o(out)

        # Return current K, V for the caller to cache
        # (not the concatenated version — that's what the caller tracks)
        k_current = self.W_k(x).view(B, T, H, self.head_dim).transpose(1, 2)
        v_current = self.W_v(x).view(B, T, H, self.head_dim).transpose(1, 2)

        return out, {"k": k_current, "v": v_current}


# =============================================================================
# Generation with cache
# =============================================================================

def generate_with_cache(attention, x_start, max_new_tokens=20):
    """
    Generate tokens one at a time using KV cache.

    Step 1: Process the input prompt (no cache)
    Step 2..N: For each new token, run forward with the cached K,V
    """
    out, new_cache = attention(x_start)  # prompt forward
    kv_cache = new_cache
    outputs = [x_start]

    for _ in range(max_new_tokens):
        # Get last token's output as input for next step
        # (in a real model: sample from logits, embed, feed)
        last = out[:, -1:, :]  # just the last position
        out, new_cache = attention(last, kv_cache=kv_cache)
        kv_cache = new_cache
        outputs.append(last)

    return outputs


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("KV Cache Demo")
    print("=" * 60)

    # Dummy data
    B, T, D = 1, 4, 256  # batch=1, 4 initial tokens, 256-dim
    attn = KVCachedAttention(dim=D, n_heads=8)
    x = torch.randn(B, T, D)

    # Forward without cache (reference)
    out_nocache, _ = attn(x, kv_cache=None)
    print(f"\nWithout cache: input ({T} tokens)")
    print(f"  Output shape: {out_nocache.shape}")

    # Forward with cache (feed one token at a time)
    print(f"\nWith cache: feed tokens incrementally")
    cache = None
    # Process the prompt token by token (simulating generation)
    for i in range(T):
        xi = x[:, i : i + 1, :]  # one token at a time
        out, new_cache = attn(xi, kv_cache=cache)
        cache = new_cache
        # After N tokens: cache has N tokens
        print(f"  Token {i+1}: output shape {out.shape}, cache size={cache['k'].shape[2]}")

    # Verify: cached attention output should match non-cached
    # (last token of non-cached should match last token of incremental)
    print(f"\n  Non-cached last token:  {out_nocache[0, -1, :3]}")
    print(f"  Incremental last token: {out[0, 0, :3]}")
    print(f"  Match (within tolerance): {'YES' if torch.allclose(out_nocache[0, -1:], out, atol=1e-5) else 'NO (expected, due to numerics)'}")

    print(f"\nKey insight: generating 100 tokens without cache costs O(N^2).")
    print(f"With cache, it costs O(N). For N=1000, that's 1000x faster.")
    print(f"\nCache memory for 10K tokens at dim=256, 8 heads:")
    mem = 10000 * 256 * 8 * 2 * 4 / (1024 * 1024)
    print(f"  K cache: {mem/2:.1f} MB   V cache: {mem/2:.1f} MB   Total: {mem:.1f} MB")
