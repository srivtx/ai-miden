"""
Minimal RoPE (Rotary Position Embedding).

The idea: instead of a lookup table pos_emb[position], ROTATE the query
and key vectors by an angle proportional to their position.

  learned: attention(position_i, position_j) depends on pos_emb[i], pos_emb[j]
  RoPE:    attention(position_i, position_j) depends on (i-j), the distance

Why this matters:
  - Train on 128-token sequences, generate 10,000 tokens
  - No extra parameters (unlike learned pos_emb: max_seq_len × dim)
  - Used by Llama, Mistral, Gemma, Qwen
"""

import math
import torch


def precompute_freqs_cis(head_dim, max_seq_len, theta=10000.0):
    """
    Precompute the complex exponentials for RoPE.

    For each position i and dimension pair (2m, 2m+1):
        angle = i * theta^{-2m/head_dim}
        freqs_cis[i, m] = cos(angle) + j*sin(angle)  (as complex)

    Returns: (max_seq_len, head_dim // 2) complex tensor
    """
    # Dimension frequencies: theta^{-2m/head_dim} for m = 0..head_dim//2-1
    dim_indices = torch.arange(0, head_dim, 2).float()
    freqs = 1.0 / (theta ** (dim_indices / head_dim))

    # Position angles: pos * freq for each position
    positions = torch.arange(max_seq_len).float()
    angles = torch.outer(positions, freqs)  # (max_seq_len, head_dim//2)

    # Complex numbers: e^{i*angle} = cos(angle) + i*sin(angle)
    freqs_cis = torch.polar(torch.ones_like(angles), angles)
    return freqs_cis


def apply_rotary_emb(x, freqs_cis):
    """
    Apply rotary embedding to query or key tensor.

    x: (batch, n_heads, seq_len, head_dim) or (batch, seq_len, n_heads, head_dim)
    freqs_cis: precomputed complex exponentials

    Steps:
      1. Reshape x into complex pairs: (real, imag) for each feature pair
      2. Multiply by freqs_cis (rotation in complex plane)
      3. Reshape back to real tensor

    Why complex? A rotation by angle θ in 2D is exactly:
        [cos θ  -sin θ] [x]
        [sin θ   cos θ] [y]
    which is multiplication by e^{iθ} = cos θ + i sin θ in the complex plane.
    """
    # Reshape: treat adjacent dimension pairs as complex numbers
    x_shape = x.shape
    # Convert to complex: (B, H, S, d) -> (B, H, S, d/2, 2) -> complex
    x = x.float().reshape(*x.shape[:-1], -1, 2)
    x_complex = torch.view_as_complex(x)  # (B, H, S, d/2) complex

    # Broadcast freqs_cis: (S, d/2) -> (1, 1, S, d/2)
    freqs_cis = freqs_cis.reshape(1, 1, -1, freqs_cis.shape[-1])
    freqs_cis = freqs_cis.to(x.device)

    # Rotate by multiplying complex numbers
    x_rotated = x_complex * freqs_cis[:, :, : x.shape[2], :]

    # Convert back to real: (B, H, S, d/2) -> (B, H, S, d/2, 2) -> (B, H, S, d)
    x_out = torch.view_as_real(x_rotated).flatten(3)

    return x_out.type_as(x)


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("RoPE Demo")
    print("=" * 60)

    head_dim = 8
    max_seq_len = 32

    # Precompute sines/cosines
    freqs_cis = precompute_freqs_cis(head_dim, max_seq_len, theta=10000.0)
    print(f"\nFrequency table: ({freqs_cis.shape[0]}, {freqs_cis.shape[1]})")
    print(f"  Row 0 (pos=0):  freqs = {freqs_cis[0, :]}")
    print(f"  Row 5 (pos=5):  freqs = {freqs_cis[5, :]}")

    # Show that the rotation preserves magnitude
    print(f"\n{'=' * 60}")
    print("Rotation test: does RoPE preserve vector magnitude?")

    q = torch.randn(2, 1, 4, head_dim)  # (batch, heads, seq, dim)
    q_rot = apply_rotary_emb(q, freqs_cis)

    # Check: |q_rot[i]| == |q[i]| for each position
    q_norm = torch.norm(q.float(), dim=-1)
    q_rot_norm = torch.norm(q_rot.float(), dim=-1)
    diff = (q_norm - q_rot_norm).abs().max().item()

    print(f"  Original norm:  {q_norm}")
    print(f"  Rotated norm:   {q_rot_norm}")
    print(f"  Max difference: {diff:.8f}  (should be ~0)")
    print(f"  Magnitude preserved: {'YES' if diff < 1e-5 else 'NO'}")

    # Show relative position property
    print(f"\n{'=' * 60}")
    print("Relative position test:")
    print("  Dot product between query at position i and key at position j")
    print("  should depend only on (i-j), not on absolute i or j.\n")

    # Two queries at positions 0 and 3
    q_i0 = torch.randn(1, 1, 1, head_dim)
    q_i3 = torch.randn(1, 1, 1, head_dim)

    # Two keys at positions 1 and 4 (both +1 from their query)
    # The dot product: q_i0^T * R_{1-0} * k_j1 should equal q_i3^T * R_{4-3} * k_j4
    # because both have relative distance = +1
    # (in expectation, since the random vectors differ)

    k_j1 = torch.randn(1, 1, 1, head_dim)
    k_j4 = k_j1.clone()  # same key vector, different position

    # Manual rotation for each position
    def rotate_single(x, pos):
        cis = freqs_cis[pos : pos + 1, :].reshape(1, 1, 1, -1)
        x_c = torch.view_as_complex(x.float().reshape(1, 1, 1, -1, 2))
        return torch.view_as_real(x_c * cis).flatten(3)

    q0_rot = rotate_single(q_i0, 0)
    q3_rot = rotate_single(q_i3, 3)
    k1_rot = rotate_single(k_j1, 1)
    k4_rot = rotate_single(k_j4, 4)

    # Dot products
    dot_01 = (q0_rot * k1_rot).sum()
    dot_34 = (q3_rot * k4_rot).sum()

    # Relative encoding check: R_i^T * R_j = R_{j-i}
    # For (i=0,j=1): diff=1. For (i=3,j=4): diff=1. Same relative distance.
    # But the RANDOM vectors are different, so dot products differ.
    # The point is: we CAN show that R_i * q and R_j * k have the same
    # dot product if we use the same q,k at different positions.

    # Better demo: use the same q,k shifted
    q_same = torch.randn(1, 1, 1, head_dim)
    k_same = torch.randn(1, 1, 1, head_dim)

    # Case A: q at pos 2, k at pos 5 (diff = 3)
    q2 = rotate_single(q_same, 2)
    k5 = rotate_single(k_same, 5)
    dot_25 = (q2 * k5).sum()

    # Case B: q at pos 10, k at pos 13 (diff = 3, same relative!)
    q10 = rotate_single(q_same, 10)
    k13 = rotate_single(k_same, 13)
    dot_10_13 = (q10 * k13).sum()

    print(f"  Same q,k at (2,5):  dot = {dot_25.item():.6f}")
    print(f"  Same q,k at (10,13): dot = {dot_10_13.item():.6f}")
    print(f"  Difference: {abs(dot_25 - dot_10_13).item():.12f}")
    print(f"  Relative position encoding: {'YES' if abs(dot_25 - dot_10_13) < 1e-6 else 'NO'}")
    print()
    print("  Dot product depends on (j-i) = relative distance, not absolute")
    print("  positions. This is why RoPE extrapolates: the model has never")
    print("  seen position 10,000, but it knows what 'distance = 3' means.")
