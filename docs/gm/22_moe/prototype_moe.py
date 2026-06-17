"""
Minimal Mixture of Experts (MoE).

The idea: Replace one dense FFN with N expert FFNs + a router.
Only top-K experts activate per token. 8x params at 2x compute.

  dense:  h = FFN(x)           (1 expert, all tokens)
  MoE:    h = sum(router(x)[i] * Expert_i(x) for i in top_k)
          (8 experts, only 2 active per token)

The router: W_g * x (linear) -> softmax(top-k only) -> select

Load balancing: If the router sends all tokens to one expert, the
other experts die (get no gradient). Add an auxiliary loss that
penalizes uneven expert usage.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class MoELayer(nn.Module):
    """
    MoE FFN with N experts and top-K routing.
    """

    def __init__(self, dim, ffn_dim, n_experts=8, top_k=2):
        super().__init__()
        self.dim = dim
        self.n_experts = n_experts
        self.top_k = top_k

        # Router: linear projection to expert scores
        self.router = nn.Linear(dim, n_experts, bias=False)

        # Experts: each is a small FFN
        self.experts = nn.ModuleList(
            [
                nn.Sequential(
                    nn.Linear(dim, ffn_dim),
                    nn.ReLU(),
                    nn.Linear(ffn_dim, dim),
                )
                for _ in range(n_experts)
            ]
        )

    def forward(self, x):
        """
        x: (batch, seq_len, dim)

        Returns: (output, routing_weights)
        """
        B, T, D = x.shape
        flat = x.reshape(-1, D)  # (B*T, D)

        # Router scores
        router_logits = self.router(flat)  # (B*T, n_experts)

        # Top-K selection per token
        top_k_logits, top_k_indices = router_logits.topk(
            self.top_k, dim=-1
        )  # (B*T, K)
        top_k_weights = F.softmax(top_k_logits, dim=-1)  # (B*T, K)

        # Compute expert outputs
        output = torch.zeros_like(flat)
        for expert_idx in range(self.n_experts):
            # Find which tokens route to this expert
            mask = (top_k_indices == expert_idx).any(dim=-1)  # (B*T,)
            if not mask.any():
                continue

            tokens = flat[mask]  # (n_tokens, D)
            expert_out = self.experts[expert_idx](tokens)  # (n_tokens, D)

            # Get the weights for this expert
            weight_mask = (top_k_indices[mask] == expert_idx)
            weights = top_k_weights[mask][weight_mask].unsqueeze(-1)

            # Add to output
            output[mask] += expert_out * weights

        return output.reshape(B, T, D), router_logits


# =============================================================================
# Load balancing loss
# =============================================================================


def load_balancing_loss(router_logits, n_experts):
    """
    Penalize uneven expert usage.

    For each token, compute the probability that it routes to each expert
    (softmax over ALL experts, not just top-K). The loss pushes these
    probabilities toward a uniform distribution.

    This is the simplified "router z-loss" used in practice.
    """
    probs = F.softmax(router_logits, dim=-1)  # (n_tokens, n_experts)
    mean_prob = probs.mean(dim=0)  # (n_experts,)
    # Penalize deviation from 1/n_experts
    target = 1.0 / n_experts
    loss = ((mean_prob - target) ** 2).sum() * n_experts
    return loss


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MoE (Mixture of Experts) Demo")
    print("=" * 60)

    B, T, D = 2, 8, 64
    x = torch.randn(B, T, D)

    # Standard dense FFN
    dense = nn.Sequential(nn.Linear(D, 128), nn.ReLU(), nn.Linear(128, D))
    n_dense = sum(p.numel() for p in dense.parameters())

    # MoE: 4 experts, top-2
    moe = MoELayer(dim=D, ffn_dim=128, n_experts=4, top_k=2)
    n_moe_total = sum(p.numel() for p in moe.parameters())

    # Active compute per token: router + top_k × expert
    # Expert params: 2 * (D*128 + 128 + 128*D) = 2 * (8192+128+8192) = 2*16512 = 33024
    # Times top_k=2: 66048 active expert params
    # Plus router: D*4 = 256 params
    # Total active: 66,304 vs dense: 16,512 + 128 + 8,320 = 24,960

    print(f"\n  Dense FFN params:     {n_dense:,}")
    print(f"  MoE total params:     {n_moe_total:,} ({n_moe_total/n_dense:.1f}x)")
    print(f"  MoE active:           ~66K per token (vs dense ~25K)")

    # Forward passes
    out_dense = dense(x)
    out_moe, router_logits = moe(x)

    print(f"\n  Dense output shape:   {out_dense.shape}")
    print(f"  MoE output shape:     {out_moe.shape}")

    # Show routing for a few tokens
    print(f"\n  Router logits for 3 tokens:")
    for i in range(3):
        logits = router_logits[i].detach()
        top2 = logits.topk(2)
        print(
            f"    Token {i}: {logits.tolist()}  ->  experts {top2.indices.tolist()}  "
            f"weights {[f'{w:.2f}' for w in top2.values.tolist()]}"
        )

    # Load balancing
    bal_loss = load_balancing_loss(router_logits, 4)
    print(f"\n  Load balancing loss: {bal_loss.item():.4f}")
    print(f"  (0 = perfect balance, >0 = uneven routing)")

    print(f"\nKey insight: MoE gives {n_moe_total/n_dense:.0f}x more capacity")
    print(f"at {66/25:.0f}x the active compute per token. The router learns")
    print(f"which experts specialize in which types of input.")
    print(f"\nBrain analogy: only 1-5% of neurons fire at a time.")
    print(f"MoE is the same: only 2 of 4 experts (50% in this demo) fire per token.")
