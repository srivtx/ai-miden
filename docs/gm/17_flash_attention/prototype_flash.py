"""
Minimal Flash Attention concept: tiled softmax.

The problem: Standard attention computes Q @ K^T -> (n, n) matrix,
stores it in VRAM, then applies softmax, then multiplies by V.
For n=4096 tokens and 32 heads at fp16, the n^2 matrix is:
  32 * 4096 * 4096 * 2 bytes = 1 GB per layer. Impractical.

The solution: Process attention in TILES. For each tile of Q, compute
attention against all K, but KEEP ONLY the running softmax statistics,
never the full (n, n) matrix. This is "online softmax" — the algorithm
that Flash Attention uses at its core.

Flash Attention 1 (Dao 2022): tiled + online softmax
Flash Attention 2 (Dao 2023): better tiling + causal mask optimization
Flash Attention 3 (Shah 2024): async + Hopper-specific

This demo shows the core idea: compute softmax WITHOUT materializing
the full attention matrix.
"""

import torch
import math


def standard_attention(Q, K, V):
    """
    Standard attention: materialize (n, n) matrix.
    Memory: O(n^2). Simple but expensive.
    """
    n, d = Q.shape
    scale = d ** -0.5

    S = Q @ K.T * scale  # (n, n) — THIS is what we want to avoid
    P = torch.softmax(S, dim=-1)
    O = P @ V
    return O


def online_softmax_attention(Q, K, V):
    """
    Tiled attention with online softmax.

    Process rows of Q incrementally. For each row, compute attention
    against all K. Use the online softmax algorithm to accumulate
    results without storing the full (1, n) attention vector.

    Memory: O(n) per row (we never store the full (n, n) matrix).
    Same result as standard attention, to within floating-point error.
    """
    n, d = Q.shape
    scale = d ** -0.5

    O = torch.zeros_like(Q)
    m_prev = torch.full((n, 1), float("-inf"))  # running max per row
    l_prev = torch.zeros(n, 1)  # running sum per row

    for i in range(n):  # for each query row
        q_i = Q[i : i + 1]  # (1, d)

        # Compute scores for this row against ALL keys
        s_i = q_i @ K.T * scale  # (1, n)

        # Online softmax update:
        # m_new = max(m_prev, max(s_i))
        # l_new = exp(m_prev - m_new) * l_prev + sum(exp(s_i - m_new))
        # P = exp(s_i - m_new) / l_new
        m_curr = s_i.max(dim=-1, keepdim=True).values  # (1, 1)
        m_new = torch.maximum(m_prev[i : i + 1], m_curr)

        # Update running statistics
        l_prev_i = l_prev[i : i + 1]
        m_prev_i = m_prev[i : i + 1]

        # Rescale old sum
        l_new_i = torch.exp(m_prev_i - m_new) * l_prev_i + torch.exp(
            s_i - m_new
        ).sum(dim=-1, keepdim=True)

        # Compute attention weights
        P_i = torch.exp(s_i - m_new) / l_new_i  # (1, n)

        # Weighted sum
        o_i = P_i @ V  # (1, d)

        # Rescale previous output
        O[i : i + 1] = torch.exp(m_prev_i - m_new) * l_prev_i / l_new_i * O[i : i + 1] + o_i

        # Update running state
        m_prev[i : i + 1] = m_new
        l_prev[i : i + 1] = l_new_i

    return O


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Flash Attention concept: online softmax")
    print("=" * 60)

    n, d = 128, 64  # small for demo
    Q = torch.randn(n, d)
    K = torch.randn(n, d)
    V = torch.randn(n, d)

    # Standard attention
    O_std = standard_attention(Q, K, V)

    # Online softmax (tiled, no materialization)
    O_online = online_softmax_attention(Q, K, V)

    diff = (O_std - O_online).abs().max().item()
    print(f"\n  Sequence length: {n}, head dim: {d}")
    print(f"  Standard output shape: {O_std.shape}")
    print(f"  Online output shape:   {O_online.shape}")
    print(f"  Max difference:        {diff:.8f}")
    print(f"  Match: {'YES' if diff < 1e-4 else 'NO'}")

    # Memory comparison
    full_matrix_bytes = n * n * 4  # float32
    online_per_row_bytes = n * 4  # one row at a time
    print(f"\n  Standard memory (S matrix): {full_matrix_bytes / 1024:.1f} KB")
    print(f"  Online max memory:           {online_per_row_bytes / 1024:.4f} KB")
    print(f"  Memory reduction:            {full_matrix_bytes / online_per_row_bytes:.0f}x")

    # Causal mask optimization
    print(f"\n  Causal mask (autoregressive) optimization:")
    print(f"  Standard: compute full (n,n), then mask upper triangle")
    print(f"  Online:   only compute LOWER triangle per row")
    print(f"            (each row i only needs K[:i+1])")
    print(f"  Additional reduction: ~2x (skip upper triangle compute)")

    print(f"\nKey insight: We never store the (n,n) attention matrix.")
    print(f"The online softmax algorithm is numerically equivalent to")
    print(f"the full matrix approach. Real Flash Attention adds tiling")
    print(f"in BOTH dimensions (rows AND columns) and SRAM management,")
    print(f"but the core math is exactly this.")
