"""
Minimal Mamba / State Space Model (SSM).

The problem: Attention is O(n^2) — for n=10,000 tokens, the attention
matrix is 100M entries per head per layer. Impractical for long sequences.

SSMs are O(n). A state space model maps input u(t) to output y(t) through
a latent state x(t):
  x'(t) = A x(t) + B u(t)           (state update)
  y(t)  = C x(t) + D u(t)           (output)

For discrete sequences, this becomes a convolution:
  y = u * K    where K is the SSM kernel (function of A, B, C)

Mamba (Gu & Dao, 2023) makes this SELECTIVE: B, C, and the delta
(step size) depend on the INPUT. This gives the model input-dependent
dynamics, similar to how attention is content-dependent.

  Selective SSM:
    delta = softplus(W_delta * u)       (step size depends on input)
    B = W_B * u                         (input projection depends on input)
    C = W_C * u                         (output projection depends on input)
    Then apply the standard SSM with these dynamic parameters.

Mamba is used in production (Codestral, Hybrid models). It handles
sequences that attention can't (100K+ tokens).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


def selective_scan(u, delta, A, B, C, D=None):
    """
    Selective scan (Mamba's core operation).

    u:    (B, L, D) input sequence
    delta: (B, L, D) step size, computed from input
    A:    (D, N)     state matrix (learned, shared across batch/time)
    B:    (B, L, N)  input projection, computed from input
    C:    (B, L, N)  output projection, computed from input

    Returns: y (B, L, D)

    O(n) complexity: one linear scan over the sequence.
    """
    B, L, D = u.shape
    N = A.shape[1]  # state dimension

    # Discretize A and B using the step size delta
    # delta_A = exp(delta * A)  (zero-order hold discretization)
    # delta_B = (delta_A - I) / A * B  (approximate in practice)
    A_discrete = torch.exp(delta.unsqueeze(-1) * A)  # (B, L, D, N)
    B_discrete = delta.unsqueeze(-1) * B.unsqueeze(-2)  # (B, L, D, N)

    # Scan: update state x and output y at each step
    y = torch.zeros(B, L, D, device=u.device)
    x = torch.zeros(B, D, N, device=u.device)  # (B, D, N) state

    for t in range(L):
        # State update: x_t = A_t * x_{t-1} + B_t * u_t
        x = A_discrete[:, t] * x + B_discrete[:, t] * u[:, t : t + 1, :]  # (B, D, N)

        # Output: y_t = C_t * x_t
        y[:, t] = (C[:, t : t + 1, :].unsqueeze(2) * x).sum(-1)  # (B, D)

    return y


class MambaBlock(nn.Module):
    """
    A minimal Mamba block: selective SSM replacing self-attention.
    """

    def __init__(self, dim, state_dim=16, expand=2):
        super().__init__()
        self.dim = dim
        self.state_dim = state_dim
        inner_dim = dim * expand

        # Input projection (expand)
        self.in_proj = nn.Linear(dim, inner_dim * 2)

        # SSM parameters
        self.A = nn.Parameter(torch.randn(dim, state_dim) * 0.1)  # state matrix
        self.D = nn.Parameter(torch.ones(dim))  # skip connection

        # Delta, B, C projections (all input-dependent = selective)
        # Delta: inner_dim -> dim  (one delta per channel)
        self.delta_proj = nn.Linear(inner_dim, dim)

        # Output projection (contract back)
        self.out_proj = nn.Linear(inner_dim, dim)

    def forward(self, x):
        """
        x: (B, L, dim)
        Returns: (B, L, dim)
        """
        B, L, D = x.shape

        # Project input
        u = self.in_proj(x)  # (B, L, inner_dim * 2)
        u, gate = u.chunk(2, dim=-1)  # each (B, L, inner_dim)

        # Compute delta, B, C from input (selective = input-dependent)
        delta = F.softplus(self.delta_proj(u))  # (B, L, D)
        # B and C: use first `state_dim` channels of the inner projection
        B_proj = u[:, :, : self.state_dim]  # (B, L, N)
        C_proj = u[:, :, : self.state_dim]  # (B, L, N)

        # Selective scan
        y_ssm = selective_scan(u, delta, self.A, B_proj, C_proj)

        # Add skip connection (like residual)
        y = y_ssm + u * self.D.unsqueeze(0).unsqueeze(0)

        # Gate (like GLU)
        y = y * F.silu(gate)

        # Output projection
        return self.out_proj(y)


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Mamba / SSM Demo")
    print("=" * 60)

    B, L, D = 2, 32, 64
    x = torch.randn(B, L, D)

    # Mamba block
    block = MambaBlock(dim=D, state_dim=16)
    out = block(x)

    n_params = sum(p.numel() for p in block.parameters())
    print(f"\n  Input:  {x.shape}")
    print(f"  Output: {out.shape}")
    print(f"  Params: {n_params:,}")

    # Compare complexity
    print(f"\n{'=' * 60}")
    print("Complexity comparison (sequence length n):")
    print(f"  Self-attention: O(n^2)  (n={L}, operations ~{L*L})")
    print(f"  Mamba/SSM:      O(n)    (n={L}, operations ~{L})")
    print(f"  At n=1000: attention 1M ops vs Mamba 1000 ops (1000x)")
    print(f"  At n=10000: attention 100M ops vs Mamba 10000 ops (10000x)")

    # Demonstrate on a longer sequence
    print(f"\n{'=' * 60}")
    print("Long sequence test:")
    x_long = torch.randn(2, 512, D)
    out_long = block(x_long)
    print(f"  Input:  {x_long.shape}")
    print(f"  Output: {out_long.shape}")
    print(f"  Memory: O(n) per layer (not O(n^2))")

    print(f"\nKey insight: Mamba processes sequences in O(n) time and O(n)")
    print(f"memory, unlike attention which is O(n^2). For very long sequences")
    print(f"(100K+ tokens), this is the only practical option.")
    print(f"\nWhere Mamba is used:")
    print(f"  - Codestral Mamba (code generation)")
    print(f"  - Hybrid Llama + Mamba models")
    print(f"  - DNA/RNA modeling (1M+ token sequences)")
    print(f"  - Any domain with long-range dependencies")
