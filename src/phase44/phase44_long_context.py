#!/usr/bin/env python3
"""
Phase 44: Long Context & Position Interpolation — NumPy Concept Demo
=====================================================================
This script demonstrates how a model trained on short sequences can
be extended to handle much longer sequences without retraining.

Key insight: RoPE encodes position through rotation angles. By scaling
position indices down, we map long sequences into the angle range the
model already knows.

Concepts demonstrated:
  - RoPE (Rotary Position Embedding)
  - Position interpolation (uniform scaling)
  - YaRN-style frequency-aware scaling
  - NTK-aware base scaling

Why this matters:
  GPT-4, Claude 3, and Gemini support 100K+ to 1M+ token contexts.
  Position interpolation is the key technique enabling this without
  retraining from scratch.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(44)

# =============================================================================
# SECTION 1: ROPE ROTATION
# =============================================================================

def apply_rope(q, position, base=10000.0):
    """
    Apply Rotary Position Embedding to a query/key vector.
    q: (d,) vector
    position: integer position
    base: RoPE base frequency
    Returns rotated vector.
    """
    d = len(q)
    result = q.copy()
    for i in range(0, d, 2):
        # Rotation angle for this dimension pair
        theta = position * (base ** (-2 * i / d))
        cos_t = np.cos(theta)
        sin_t = np.sin(theta)
        # 2D rotation
        x, y = q[i], q[i+1]
        result[i] = x * cos_t - y * sin_t
        result[i+1] = x * sin_t + y * cos_t
    return result

def attention_score(q_pos, k_pos, q_vec, k_vec, base=10000.0):
    """Compute RoPE attention score between query at q_pos and key at k_pos."""
    q_rot = apply_rope(q_vec, q_pos, base)
    k_rot = apply_rope(k_vec, k_pos, base)
    return np.dot(q_rot, k_rot)

# =============================================================================
# SECTION 2: DEMONSTRATE ROPE PROPERTIES
# =============================================================================

print("="*60)
print("Phase 44: Long Context & Position Interpolation")
print("="*60)

d = 8
q_vec = np.random.randn(d)
k_vec = np.random.randn(d)

print("\n--- RoPE Relative Position Property ---")
print("Attention score depends on relative distance, not absolute position:")
for m in [10, 20, 30]:
    n = m + 5
    score = attention_score(m, n, q_vec, k_vec)
    print(f"  Q@{m} · K@{n} (distance=5): score={score:.3f}")

# Verify same distance gives similar score
print("\nSame distance (5) from different starting points:")
for m in [5, 15, 25]:
    score = attention_score(m, m+5, q_vec, k_vec)
    print(f"  Q@{m} · K@{m+5}: score={score:.3f}")

# =============================================================================
# SECTION 3: POSITION INTERPOLATION
# =============================================================================

def interpolate_position(position, train_len, target_len):
    """Scale position so target_len maps to train_len."""
    return position * (train_len / target_len)

print("\n--- Position Interpolation ---")
train_len = 16
target_len = 64
scale = train_len / target_len

print(f"Trained on positions 0-{train_len-1}, want to use 0-{target_len-1}")
print(f"Scale factor: {scale:.3f}")

for pos in [0, 16, 32, 48, 63]:
    scaled = interpolate_position(pos, train_len, target_len)
    print(f"  Original position {pos:2d} -> scaled position {scaled:.2f} (in training range)")

# =============================================================================
# SECTION 4: VISUALIZE ROTATION ANGLES
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

d_vis = 32
positions = np.arange(0, 64)
base = 10000.0

# Plot 1: Original angles for dimensions 0, 8, 16, 24
ax = axes[0, 0]
for dim in [0, 8, 16, 24]:
    angles = positions * (base ** (-2 * dim / d_vis))
    ax.plot(positions, angles, label=f'dim {dim}')
ax.axvline(x=16, color='red', linestyle='--', label='Training cutoff')
ax.set_xlabel('Position')
ax.set_ylabel('Rotation Angle (radians)')
ax.set_title('Original RoPE Angles (No Interpolation)')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Interpolated angles
ax = axes[0, 1]
scale = 16 / 64
for dim in [0, 8, 16, 24]:
    angles = positions * scale * (base ** (-2 * dim / d_vis))
    ax.plot(positions, angles, label=f'dim {dim}')
ax.axvline(x=16, color='red', linestyle='--', label='Training cutoff')
ax.set_xlabel('Position')
ax.set_ylabel('Rotation Angle (radians)')
ax.set_title('Position Interpolation (scale=0.25)')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: YaRN-style (frequency-aware scaling)
ax = axes[1, 0]
for dim in [0, 8, 16, 24]:
    # High-frequency dims (small dim index) get less scaling
    if dim < d_vis // 2:
        yarn_scale = scale * 0.5  # Less compression for high freq
    else:
        yarn_scale = scale * 1.5  # More compression for low freq
    angles = positions * yarn_scale * (base ** (-2 * dim / d_vis))
    ax.plot(positions, angles, label=f'dim {dim}')
ax.axvline(x=16, color='red', linestyle='--', label='Training cutoff')
ax.set_xlabel('Position')
ax.set_ylabel('Rotation Angle (radians)')
ax.set_title('YaRN-Style Frequency-Aware Scaling')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Attention pattern coherence
ax = axes[1, 1]
q_pos = 32
positions_k = np.arange(0, 64)
scores_original = []
scores_interpolated = []

for k_pos in positions_k:
    # Without interpolation: model sees angles way beyond training
    score_orig = attention_score(q_pos, k_pos, q_vec, k_vec, base)
    scores_original.append(score_orig)

    # With interpolation: map to training range
    q_scaled = interpolate_position(q_pos, 16, 64)
    k_scaled = interpolate_position(k_pos, 16, 64)
    # We apply RoPE with scaled positions
    score_interp = attention_score(q_scaled, k_scaled, q_vec, k_vec, base)
    scores_interpolated.append(score_interp)

ax.plot(positions_k, scores_original, 'b-', alpha=0.5, label='No interpolation (unstable)')
ax.plot(positions_k, scores_interpolated, 'r-', label='With interpolation (coherent)')
ax.axvline(x=16, color='gray', linestyle='--', alpha=0.5, label='Training cutoff')
ax.set_xlabel('Key Position')
ax.set_ylabel('Attention Score')
ax.set_title('Attention Pattern: Query at Position 32')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
os.makedirs('src/phase44', exist_ok=True)
plt.savefig('src/phase44/long_context.png', dpi=150)
print("\nSaved plot to src/phase44/long_context.png")

# =============================================================================
# SECTION 5: NTK-AWARE BASE SCALING
# =============================================================================

print("\n--- NTK-Aware Base Scaling ---")
train_len = 16
target_len = 64
scale = target_len / train_len
d_head = 32

new_base = base * (scale ** (d_head / (d_head - 2)))
print(f"Original base: {base:.0f}")
print(f"Scale factor: {scale:.1f}")
print(f"NTK-aware new base: {new_base:.0f}")

# Compare angles for a mid-frequency dimension
i = 16
pos = 32
angle_original = pos * (base ** (-2 * i / d_head))
angle_ntk = pos * (new_base ** (-2 * i / d_head))
angle_interp = interpolate_position(pos, train_len, target_len) * (base ** (-2 * i / d_head))

print(f"\nDimension {i}, position {pos}:")
print(f"  Original (no scaling):  {angle_original:.4f} radians")
print(f"  Basic interpolation:    {angle_interp:.4f} radians")
print(f"  NTK-aware base scaling: {angle_ntk:.4f} radians")

# =============================================================================
# SECTION 6: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("Position interpolation extends context windows by scaling")
print("position indices to fit the training range:")
print(f"  - Basic interpolation: uniform scale by {train_len/target_len:.3f}")
print(f"  - YaRN: frequency-aware scaling (high freq less, low freq more)")
print(f"  - NTK-aware: increase RoPE base to {new_base:.0f}")
print("\nKey insight: The model never sees unfamiliar rotation angles.")
print("All positions map to angles it learned during training.")
print("This enables 4×, 8×, even 16× context extension without")
print("retraining from scratch.")
