# Phase 44: Long Context & Position Interpolation — Colab T4 PyTorch Version
# ============================================================================
# Run this in Google Colab with T4 GPU runtime.
# Demonstrates extending a Transformer's context window using position
# interpolation, YaRN, and NTK-aware scaling on a real model.
#
# Concepts:
#   - RoPE (Rotary Position Embedding)
#   - Position interpolation
#   - YaRN frequency-aware scaling
#   - NTK-aware base scaling
# ============================================================================

import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

# Check device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# =============================================================================
# SECTION 1: ROPE IMPLEMENTATION
# =============================================================================

class RoPE(nn.Module):
    """Rotary Position Embedding for a single attention head."""
    def __init__(self, d_head=64, base=10000.0):
        super().__init__()
        self.d_head = d_head
        self.base = base
        # Precompute inverse frequencies
        inv_freq = 1.0 / (self.base ** (torch.arange(0, d_head, 2).float() / d_head))
        self.register_buffer('inv_freq', inv_freq)

    def forward(self, x, positions):
        """
        x: (seq_len, d_head) or (batch, seq_len, d_head)
        positions: (seq_len,) integer positions
        """
        if x.dim() == 2:
            x = x.unsqueeze(0)
            squeeze = True
        else:
            squeeze = False

        batch, seq_len, d_head = x.shape
        # angles: (seq_len, d_head//2)
        angles = positions.unsqueeze(1).float() * self.inv_freq.unsqueeze(0)
        cos = torch.cos(angles)
        sin = torch.sin(angles)

        # Apply rotation to pairs
        x1 = x[..., 0::2]  # even indices
        x2 = x[..., 1::2]  # odd indices
        rotated = torch.stack([x1 * cos - x2 * sin, x1 * sin + x2 * cos], dim=-1)
        out = rotated.flatten(-2)

        if squeeze:
            out = out.squeeze(0)
        return out

# =============================================================================
# SECTION 2: POSITION INTERPOLATION VARIANTS
# =============================================================================

class InterpolatedRoPE(RoPE):
    """RoPE with position interpolation scaling."""
    def __init__(self, d_head=64, base=10000.0, scale=1.0):
        super().__init__(d_head, base)
        self.scale = scale

    def forward(self, x, positions):
        scaled_positions = positions.float() * self.scale
        return super().forward(x, scaled_positions)

class YaRNRoPE(RoPE):
    """RoPE with YaRN-style frequency-aware scaling."""
    def __init__(self, d_head=64, base=10000.0, scale=1.0, beta=16):
        super().__init__(d_head, base)
        self.scale = scale
        self.beta = beta  # frequency threshold dimension

    def forward(self, x, positions):
        batch, seq_len, d_head = x.shape if x.dim() == 3 else (1, *x.shape)
        angles = positions.unsqueeze(1).float() * self.inv_freq.unsqueeze(0)
        # Frequency-aware scaling: less for high freq, more for low freq
        dim_indices = torch.arange(0, d_head // 2, device=x.device)
        scales = torch.where(dim_indices < self.beta,
                             torch.ones_like(dim_indices) * self.scale * 0.5,
                             torch.ones_like(dim_indices) * self.scale * 1.5)
        angles = angles * scales.unsqueeze(0)
        cos = torch.cos(angles)
        sin = torch.sin(angles)

        if x.dim() == 2:
            x = x.unsqueeze(0)
        x1 = x[..., 0::2]
        x2 = x[..., 1::2]
        rotated = torch.stack([x1 * cos - x2 * sin, x1 * sin + x2 * cos], dim=-1)
        out = rotated.flatten(-2)
        if x.shape[0] == 1:
            out = out.squeeze(0)
        return out

# =============================================================================
# SECTION 3: MINI TRANSFORMER WITH CONFIGURABLE ROPE
# =============================================================================

class CausalSelfAttention(nn.Module):
    def __init__(self, d_model=128, nhead=4, rope_cls=RoPE, rope_kwargs=None):
        super().__init__()
        self.nhead = nhead
        self.d_head = d_model // nhead
        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        rope_kwargs = rope_kwargs or {}
        self.rope = rope_cls(d_head=self.d_head, **rope_kwargs)

    def forward(self, x):
        B, T, C = x.shape
        q = self.q_proj(x).view(B, T, self.nhead, self.d_head).transpose(1, 2)
        k = self.k_proj(x).view(B, T, self.nhead, self.d_head).transpose(1, 2)
        v = self.v_proj(x).view(B, T, self.nhead, self.d_head).transpose(1, 2)

        positions = torch.arange(T, device=x.device)
        q = self.rope(q, positions)
        k = self.rope(k, positions)

        scores = torch.matmul(q, k.transpose(-2, -1)) / (self.d_head ** 0.5)
        mask = torch.triu(torch.ones(T, T, device=x.device), diagonal=1).bool()
        scores = scores.masked_fill(mask.unsqueeze(0).unsqueeze(0), float('-inf'))
        attn = torch.softmax(scores, dim=-1)
        out = torch.matmul(attn, v).transpose(1, 2).contiguous().view(B, T, C)
        return self.out_proj(out), attn

class MiniTransformer(nn.Module):
    def __init__(self, vocab_size=100, d_model=128, nhead=4, num_layers=2, rope_cls=RoPE, rope_kwargs=None):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, d_model)
        self.layers = nn.ModuleList([
            nn.ModuleDict({
                'attn': CausalSelfAttention(d_model, nhead, rope_cls, rope_kwargs),
                'ffn': nn.Sequential(nn.Linear(d_model, 4*d_model), nn.GELU(), nn.Linear(4*d_model, d_model)),
                'ln1': nn.LayerNorm(d_model),
                'ln2': nn.LayerNorm(d_model),
            }) for _ in range(num_layers)
        ])
        self.head = nn.Linear(d_model, vocab_size)

    def forward(self, x):
        x = self.embed(x)
        attns = []
        for layer in self.layers:
            attn_out, attn = layer['attn'](layer['ln1'](x))
            x = x + attn_out
            x = x + layer['ffn'](layer['ln2'](x))
            attns.append(attn)
        return self.head(x), attns

# =============================================================================
# SECTION 4: TRAIN ON SHORT SEQUENCES
# =============================================================================

def generate_data(n=1000, seq_len=16, vocab_size=100):
    return torch.randint(0, vocab_size, (n, seq_len))

def train(model, data, epochs=10, lr=0.001):
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    for epoch in range(epochs):
        total_loss = 0
        for batch in data.split(32):
            logits, _ = model(batch)
            loss = nn.functional.cross_entropy(logits[:, :-1].reshape(-1, logits.size(-1)),
                                                batch[:, 1:].reshape(-1))
            opt.zero_grad()
            loss.backward()
            opt.step()
            total_loss += loss.item()
        if epoch % 3 == 0:
            print(f"Epoch {epoch}: loss={total_loss/len(data.split(32)):.3f}")

# =============================================================================
# SECTION 5: EVALUATE CONTEXT EXTENSION
# =============================================================================

def evaluate_perplexity(model, seq_len, vocab_size=100):
    """Evaluate perplexity on sequences of given length."""
    model.eval()
    with torch.no_grad():
        x = torch.randint(0, vocab_size, (10, seq_len))
        logits, _ = model(x)
        loss = nn.functional.cross_entropy(logits[:, :-1].reshape(-1, logits.size(-1)),
                                            x[:, 1:].reshape(-1))
    return torch.exp(loss).item()

if __name__ == '__main__':
    print("="*60)
    print("Phase 44 Colab: Long Context & Position Interpolation")
    print("="*60)

    vocab_size = 100
    train_len = 16
    test_len = 64

    # Train base model
    print("\nTraining base model on length-16 sequences...")
    base_rope = RoPE(d_head=32)
    model_base = MiniTransformer(vocab_size, d_model=128, nhead=4, num_layers=2).to(device)
    data = generate_data(500, train_len, vocab_size).to(device)
    train(model_base, data, epochs=10)

    # Evaluate at training length
    ppl_train = evaluate_perplexity(model_base, train_len, vocab_size)
    print(f"Perplexity at train length ({train_len}): {ppl_train:.2f}")

    # Evaluate WITHOUT interpolation at test length (should fail)
    print(f"\nEvaluating at {test_len} WITHOUT interpolation...")
    try:
        ppl_test_raw = evaluate_perplexity(model_base, test_len, vocab_size)
        print(f"Perplexity: {ppl_test_raw:.2f}")
    except Exception as e:
        print(f"Failed: {e}")

    # Create interpolated models
    scale = train_len / test_len
    print(f"\nInterpolation scale: {scale:.3f}")

    # Basic interpolation
    model_interp = MiniTransformer(vocab_size, d_model=128, nhead=4, num_layers=2,
                                   rope_cls=InterpolatedRoPE,
                                   rope_kwargs={'scale': scale}).to(device)
    model_interp.load_state_dict(model_base.state_dict())
    ppl_interp = evaluate_perplexity(model_interp, test_len, vocab_size)
    print(f"Basic interpolation perplexity at {test_len}: {ppl_interp:.2f}")

    # YaRN
    model_yarn = MiniTransformer(vocab_size, d_model=128, nhead=4, num_layers=2,
                                 rope_cls=YaRNRoPE,
                                 rope_kwargs={'scale': scale, 'beta': 8}).to(device)
    model_yarn.load_state_dict(model_base.state_dict())
    ppl_yarn = evaluate_perplexity(model_yarn, test_len, vocab_size)
    print(f"YaRN perplexity at {test_len}: {ppl_yarn:.2f}")

    # Plot attention patterns
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    seq_len = 32
    x = torch.randint(0, vocab_size, (1, seq_len)).to(device)

    for ax, name, model in zip(axes,
                                ['Original', 'Interpolated', 'YaRN'],
                                [model_base, model_interp, model_yarn]):
        model.eval()
        with torch.no_grad():
            _, attns = model(x)
        attn = attns[0][0, 0].cpu().numpy()  # first head of first layer
        im = ax.imshow(attn, cmap='viridis', aspect='auto')
        ax.set_title(f'{name} Attention')
        ax.set_xlabel('Key Position')
        ax.set_ylabel('Query Position')
        plt.colorbar(im, ax=ax)

    plt.tight_layout()
    plt.savefig('phase44_attention.png', dpi=150)
    print("\nSaved plot to phase44_attention.png")
