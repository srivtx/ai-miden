#!/usr/bin/env python3
"""
Phase 125: Long Context Training — NumPy Concept Demo
=======================================================
This script demonstrates RoPE scaling methods and their effect on
position encodings and attention stability across long sequences.

We simulate:
  1. Standard RoPE position encodings
  2. Position Interpolation (PI) scaling
  3. NTK-aware scaling
  4. YaRN with attention temperature scaling
  5. Attention entropy vs. sequence length for each method
  6. Position encoding similarity matrices

Key insight: scaling RoPE frequencies extends the valid position range,
but different methods preserve local precision to different degrees.
YaRN's temperature scaling is critical for maintaining stable attention
at extreme extensions.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(125)

# =============================================================================
# SECTION 1: ROPE PARAMETERS
# =============================================================================
# RoPE uses sinusoidal position encodings with frequencies that decay
# across dimensions. The base determines how quickly frequencies drop.
# Llama uses base=10000; Llama-3 uses base=500000.

d = 64              # head dimension (simplified from 128 for speed)
base = 10000        # RoPE base frequency
orig_len = 4096     # original training context length
target_len = 8192   # target extended context length (2x)
scale_factor = target_len / orig_len  # s = 2.0

print("="*70)
print("Phase 125: Long Context Training — RoPE Scaling Concepts")
print("="*70)
print(f"Head dimension: {d}")
print(f"RoPE base: {base}")
print(f"Original context: {orig_len}")
print(f"Target context: {target_len}")
print(f"Scale factor s: {scale_factor:.1f}")

# =============================================================================
# SECTION 2: ROPE FREQUENCY COMPUTATION
# =============================================================================
# RoPE assigns each dimension pair (i, i+d/2) a frequency theta_i.
# The frequencies decay geometrically from base down to near zero.

def compute_thetas(dim, base):
    """
    Compute RoPE theta values for each dimension pair.
    theta_i = base^(-2i / dim) for i in 0..dim/2-1
    WHY negative exponent? Lower dimensions get higher frequencies,
    enabling fine-grained local position discrimination.
    """
    i = np.arange(dim // 2)
    thetas = base ** (-2 * i / dim)
    return thetas

thetas = compute_thetas(d, base)
print(f"\nTheta range: [{thetas[-1]:.6f}, {thetas[0]:.2f}]")
print(f"Highest frequency dim: {thetas[0]:.4f} (local detail)")
print(f"Lowest frequency dim:  {thetas[-1]:.8f} (global position)")

# =============================================================================
# SECTION 3: POSITION ENCODING SIMULATION
# =============================================================================
# For each position m and each dimension pair, RoPE computes:
#   [cos(m * theta_i), sin(m * theta_i)]
# We simulate the full encoding matrix for visualization.

def rope_encodings(seq_len, thetas):
    """
    Compute RoPE position encodings for all positions up to seq_len.
    Returns matrix of shape (seq_len, dim//2) with the angle values.
    WHY angles? The actual encoding is a rotation matrix; the angle
    determines how far to rotate the query/key vectors.
    """
    m = np.arange(seq_len).reshape(-1, 1)  # positions
    angles = m * thetas.reshape(1, -1)      # (seq_len, dim//2)
    return angles

angles_orig = rope_encodings(orig_len, thetas)
print(f"\nOriginal angle matrix shape: {angles_orig.shape}")
print(f"Max angle (orig): {angles_orig.max():.2f} radians")

# =============================================================================
# SECTION 4: SCALING METHODS
# =============================================================================
# We implement three scaling approaches and compare them.

def scale_pi(thetas, s):
    """
    Position Interpolation: divide all thetas by s.
    WHY? Makes long positions use the same angles as short positions.
    Position m in scaled = same angles as position m/s in original.
    """
    return thetas / s

def scale_ntk(thetas, s, dim):
    """
    NTK-aware scaling: non-uniform scaling based on dimension index.
    WHY? High frequencies (local detail) should be scaled less than
    low frequencies (global position) to preserve nearby distinctions.
    Formula: theta'_i = theta_i * s^(-dim/(dim-2*i))
    """
    i = np.arange(len(thetas))
    # Smooth interpolation from no scaling at low freqs to full scaling at high
    # We use a simplified NTK formula for demonstration
    exponents = -dim / (dim - 2 * i + 1e-8)
    scale_per_dim = s ** exponents
    return thetas * scale_per_dim

def scale_yarn(thetas, s, dim, alpha=1.0):
    """
    YaRN scaling: piecewise linear interpolation between PI and NTK.
    Plus attention temperature scaling (applied later in attention).
    WHY? YaRN finds the optimal balance between range extension and
    local precision by blending scaling strategies.
    """
    i = np.arange(len(thetas))
    # YaRN uses a ramp from 0 (no scaling) to 1 (full PI scaling)
    # based on a frequency threshold
    ramp = np.clip(i / (dim * 0.25), 0, 1)  # blend over first 25% of dims
    pi_scaled = thetas / s
    ntk_scaled = thetas * (s ** (-dim / (dim - 2 * i + 1e-8)))
    blended = (1 - ramp) * ntk_scaled + ramp * pi_scaled
    return blended

def yarn_temperature(s):
    """
    YaRN attention temperature scaling factor.
    WHY? Interpolated positions produce attention scores with different
    variance. This temperature restores the variance the softmax expects.
    """
    return 0.1 * np.log(s) + 1.0

theta_pi = scale_pi(thetas, scale_factor)
theta_ntk = scale_ntk(thetas, scale_factor, d)
theta_yarn = scale_yarn(thetas, scale_factor, d)
temp_yarn = yarn_temperature(scale_factor)

print(f"\n--- Scaling Comparison (first 4 dimensions) ---")
for i in range(4):
    print(f"Dim {i}: orig={thetas[i]:.4f}, PI={theta_pi[i]:.4f}, "
          f"NTK={theta_ntk[i]:.4f}, YaRN={theta_yarn[i]:.4f}")
print(f"YaRN attention temperature: {temp_yarn:.4f}")

# =============================================================================
# SECTION 5: POSITION SIMILARITY MATRICES
# =============================================================================
# We compute cosine similarity between position encodings at different
# positions. A good scaling method should:
#   - Keep nearby positions distinct (high differentiation)
#   - Allow distant positions to be recognized (not random)

def encoding_similarity(angles):
    """
    Compute cosine similarity matrix between all position pairs.
    WHY cosine? RoPE encodings are used in dot products; cosine
    similarity approximates the normalized attention pattern.
    """
    # Use actual cos/sin vectors for similarity
    enc = np.concatenate([np.cos(angles), np.sin(angles)], axis=1)
    norm = np.linalg.norm(enc, axis=1, keepdims=True)
    enc_norm = enc / (norm + 1e-8)
    sim = enc_norm @ enc_norm.T
    return sim

# Compute for target length with each scaling method
angles_target_pi = rope_encodings(target_len, theta_pi)
angles_target_ntk = rope_encodings(target_len, theta_ntk)
angles_target_yarn = rope_encodings(target_len, theta_yarn)

sim_pi = encoding_similarity(angles_target_pi)
sim_ntk = encoding_similarity(angles_target_ntk)
sim_yarn = encoding_similarity(angles_target_yarn)

print(f"\nComputed similarity matrices: {sim_pi.shape}")

# =============================================================================
# SECTION 6: ATTENTION ENTROPY VS. SEQUENCE LENGTH
# =============================================================================
# We simulate attention distributions for a query at different positions
# and measure entropy. Stable attention should have moderate entropy —
# not too sharp (overconfident) and not too flat (unfocused).
# We model attention as softmax(Q@K^T / sqrt(d)) where Q,K include RoPE.

def simulate_attention_entropy(angles, temp=1.0, query_pos=None):
    """
    Simulate attention entropy for a query at various positions.
    WHY entropy? High entropy = flat attention (model cannot focus).
    Low entropy = sharp peaks (model ignores relevant context).
    We want stable moderate entropy across all positions.
    """
    seq_len = angles.shape[0]
    if query_pos is None:
        query_pos = seq_len // 2

    # Build Q and K from position encodings (simplified: Q=K=encoding)
    enc = np.concatenate([np.cos(angles), np.sin(angles)], axis=1)
    q = enc[query_pos:query_pos+1]  # (1, dim)
    k = enc  # (seq_len, dim)

    # Attention scores with temperature scaling
    scores = (q @ k.T) / (np.sqrt(d) * temp)
    scores = scores[0]  # (seq_len,)

    # Causal mask: can only attend to previous positions
    causal_scores = np.where(np.arange(seq_len) <= query_pos, scores, -1e9)

    # Softmax
    exp_scores = np.exp(causal_scores - np.max(causal_scores))
    probs = exp_scores / (np.sum(exp_scores) + 1e-8)

    # Entropy: -sum(p * log(p))
    entropy = -np.sum(probs * np.log(probs + 1e-10))
    return entropy, probs

def entropy_vs_length(max_len, thetas_scaled, temp=1.0, method_name=""):
    """
    Measure attention entropy at the last position for increasing lengths.
    WHY? The last position is the hardest because it attends to the
    most distant tokens. If entropy collapses or explodes here,
    the model fails at long context.
    """
    lengths = []
    entropies = []
    for L in range(512, max_len + 1, 512):
        angles = rope_encodings(L, thetas_scaled)
        ent, _ = simulate_attention_entropy(angles, temp=temp, query_pos=L-1)
        lengths.append(L)
        entropies.append(ent)
    return np.array(lengths), np.array(entropies)

len_pi, ent_pi = entropy_vs_length(target_len, theta_pi, temp=1.0, method_name="PI")
len_ntk, ent_ntk = entropy_vs_length(target_len, theta_ntk, temp=1.0, method_name="NTK")
len_yarn, ent_yarn = entropy_vs_length(target_len, theta_yarn, temp=temp_yarn, method_name="YaRN")

# Also compute for unscaled (original thetas) as a broken baseline
# At target_len, original thetas have never seen these positions
len_unscaled, ent_unscaled = entropy_vs_length(target_len, thetas, temp=1.0, method_name="Unscaled")

print(f"\n--- Attention Entropy at Target Length ({target_len}) ---")
print(f"Unscaled:  {ent_unscaled[-1]:.3f} (broken: angles exceed training range)")
print(f"PI:        {ent_pi[-1]:.3f}")
print(f"NTK:       {ent_ntk[-1]:.3f}")
print(f"YaRN:      {ent_yarn[-1]:.3f} (temperature={temp_yarn:.3f})")

# =============================================================================
# SECTION 7: LOCAL POSITION DISCRIMINATION
# =============================================================================
# PI blurs nearby positions because high frequencies are compressed.
# We measure the minimum angle difference between adjacent positions
# in the highest-frequency dimension.

def local_discrimination(thetas_scaled):
    """
    Measure the angle step between adjacent positions in the
    highest-frequency dimension. Larger = better local discrimination.
    WHY? Nearby positions must be distinguishable for precise attention.
    """
    # Highest frequency = theta[0]
    step = thetas_scaled[0]  # angle difference between position m and m+1
    return step

step_orig = local_discrimination(thetas)
step_pi = local_discrimination(theta_pi)
step_ntk = local_discrimination(theta_ntk)
step_yarn = local_discrimination(theta_yarn)

print(f"\n--- Local Discrimination (highest frequency dim) ---")
print(f"Original: {step_orig:.6f} radians per position")
print(f"PI:       {step_pi:.6f} ({step_pi/step_orig:.2f}x of original)")
print(f"NTK:      {step_ntk:.6f} ({step_ntk/step_orig:.2f}x of original)")
print(f"YaRN:     {step_yarn:.6f} ({step_yarn/step_orig:.2f}x of original)")
print("Note: PI compresses local detail by exactly the scale factor.")

# =============================================================================
# SECTION 8: SIMULATED NEEDLE-IN-HAYSTACK
# =============================================================================
# We simulate the needle-in-haystack test: a special token is placed
# at various positions, and we measure how well the attention at the
# end of the sequence can "find" it. We approximate this by measuring
# the attention probability mass on the needle position.

def needle_attention_prob(angles, needle_pos, temp=1.0):
    """
    Simulate attention from the last position to a needle at needle_pos.
    Returns the attention probability on the needle.
    WHY? Needle-in-haystack tests whether the model can retrieve
    information from arbitrary positions in a long document.
    """
    seq_len = angles.shape[0]
    enc = np.concatenate([np.cos(angles), np.sin(angles)], axis=1)
    q = enc[-1:]
    k = enc

    scores = (q @ k.T) / (np.sqrt(d) * temp)
    scores = scores[0]
    causal_scores = np.where(np.arange(seq_len) <= seq_len - 1, scores, -1e9)

    exp_scores = np.exp(causal_scores - np.max(causal_scores))
    probs = exp_scores / (np.sum(exp_scores) + 1e-8)
    return probs[needle_pos]

needle_positions = np.linspace(0, target_len - 1, 9, dtype=int)
probs_pi = []
probs_ntk = []
probs_yarn = []
probs_unscaled = []

for pos in needle_positions:
    angles_pi = rope_encodings(target_len, theta_pi)
    angles_ntk = rope_encodings(target_len, theta_ntk)
    angles_yarn = rope_encodings(target_len, theta_yarn)
    angles_unscaled = rope_encodings(target_len, thetas)

    probs_pi.append(needle_attention_prob(angles_pi, pos, temp=1.0))
    probs_ntk.append(needle_attention_prob(angles_ntk, pos, temp=1.0))
    probs_yarn.append(needle_attention_prob(angles_yarn, pos, temp=temp_yarn))
    probs_unscaled.append(needle_attention_prob(angles_unscaled, pos, temp=1.0))

print(f"\n--- Simulated Needle Attention Probability ---")
print(f"{'Pos':>6} | {'Unscaled':>10} | {'PI':>10} | {'NTK':>10} | {'YaRN':>10}")
for i, pos in enumerate(needle_positions):
    print(f"{pos:6d} | {probs_unscaled[i]:10.4f} | {probs_pi[i]:10.4f} | "
          f"{probs_ntk[i]:10.4f} | {probs_yarn[i]:10.4f}")

# =============================================================================
# SECTION 9: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# Plot 1: Similarity matrix — PI
ax = axes[0, 0]
im = ax.imshow(sim_pi[:1024, :1024], cmap='viridis', aspect='auto', vmin=-1, vmax=1)
ax.set_title(f'Position Similarity: PI (s={scale_factor:.1f})')
ax.set_xlabel('Position')
ax.set_ylabel('Position')
plt.colorbar(im, ax=ax, fraction=0.046)

# Plot 2: Similarity matrix — NTK
ax = axes[0, 1]
im = ax.imshow(sim_ntk[:1024, :1024], cmap='viridis', aspect='auto', vmin=-1, vmax=1)
ax.set_title('Position Similarity: NTK')
ax.set_xlabel('Position')
ax.set_ylabel('Position')
plt.colorbar(im, ax=ax, fraction=0.046)

# Plot 3: Similarity matrix — YaRN
ax = axes[0, 2]
im = ax.imshow(sim_yarn[:1024, :1024], cmap='viridis', aspect='auto', vmin=-1, vmax=1)
ax.set_title('Position Similarity: YaRN')
ax.set_xlabel('Position')
ax.set_ylabel('Position')
plt.colorbar(im, ax=ax, fraction=0.046)

# Plot 4: Attention entropy vs. length
ax = axes[1, 0]
ax.plot(len_unscaled, ent_unscaled, 'o--', color='#e74c3c', linewidth=2, label='Unscaled', markersize=6)
ax.plot(len_pi, ent_pi, 's-', color='#3498db', linewidth=2, label='PI', markersize=6)
ax.plot(len_ntk, ent_ntk, '^-', color='#9b59b6', linewidth=2, label='NTK', markersize=6)
ax.plot(len_yarn, ent_yarn, 'D-', color='#27ae60', linewidth=2, label='YaRN', markersize=6)
ax.axvline(orig_len, color='gray', linestyle=':', alpha=0.7, label=f'Orig limit ({orig_len})')
ax.set_xlabel('Sequence Length')
ax.set_ylabel('Attention Entropy')
ax.set_title('Attention Stability vs. Length\n(Lower = sharper; Higher = flatter)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Plot 5: Needle-in-haystack probability
ax = axes[1, 1]
ax.plot(needle_positions, probs_unscaled, 'o--', color='#e74c3c', linewidth=2, label='Unscaled', markersize=6)
ax.plot(needle_positions, probs_pi, 's-', color='#3498db', linewidth=2, label='PI', markersize=6)
ax.plot(needle_positions, probs_ntk, '^-', color='#9b59b6', linewidth=2, label='NTK', markersize=6)
ax.plot(needle_positions, probs_yarn, 'D-', color='#27ae60', linewidth=2, label='YaRN', markersize=6)
ax.set_xlabel('Needle Position (tokens)')
ax.set_ylabel('Attention Probability on Needle')
ax.set_title(f'Simulated Needle Retrieval\n(Last position attends to needle at position p)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Plot 6: Local discrimination comparison
ax = axes[1, 2]
methods = ['Original', 'PI', 'NTK', 'YaRN']
steps = [step_orig, step_pi, step_ntk, step_yarn]
colors = ['#95a5a6', '#3498db', '#9b59b6', '#27ae60']
bars = ax.bar(methods, steps, color=colors, edgecolor='black', alpha=0.8)
ax.set_ylabel('Angle Step per Position (rad)')
ax.set_title('Local Position Discrimination\n(Higher = better local precision)')
for bar, val in zip(bars, steps):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.00001,
            f'{val:.5f}', ha='center', va='bottom', fontsize=9)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
os.makedirs('src/phase125', exist_ok=True)
plt.savefig('src/phase125/long_context_concepts.png', dpi=150)
print("\nSaved plot to src/phase125/long_context_concepts.png")

# =============================================================================
# SECTION 10: SUMMARY
# =============================================================================

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Scale factor: {scale_factor:.1f}x ({orig_len} -> {target_len})")
print(f"YaRN temperature: {temp_yarn:.4f}")
print(f"\nLocal discrimination (highest freq):")
print(f"  Original: {step_orig:.6f}")
print(f"  PI:       {step_pi:.6f} ({100*step_pi/step_orig:.1f}% of original)")
print(f"  NTK:      {step_ntk:.6f} ({100*step_ntk/step_orig:.1f}% of original)")
print(f"  YaRN:     {step_yarn:.6f} ({100*step_yarn/step_orig:.1f}% of original)")
print(f"\nAttention entropy at {target_len} tokens:")
print(f"  Unscaled: {ent_unscaled[-1]:.3f} (unstable)")
print(f"  PI:       {ent_pi[-1]:.3f}")
print(f"  NTK:      {ent_ntk[-1]:.3f}")
print(f"  YaRN:     {ent_yarn[-1]:.3f}")
print(f"\nNeedle retrieval probability at position {target_len//2}:")
print(f"  Unscaled: {probs_unscaled[len(probs_unscaled)//2]:.4f}")
print(f"  PI:       {probs_pi[len(probs_pi)//2]:.4f}")
print(f"  NTK:      {probs_ntk[len(probs_ntk)//2]:.4f}")
print(f"  YaRN:     {probs_yarn[len(probs_yarn)//2]:.4f}")
print("\nKey lessons:")
print("  1. RoPE scaling rescales frequencies to map long positions into known angles")
print("  2. PI is simple but destroys local precision by uniform compression")
print("  3. NTK preserves local detail better by non-uniform scaling")
print("  4. YaRN adds temperature scaling to stabilize attention variance")
print("  5. Even perfect scaling needs fine-tuning for reliable long-context retrieval")
print("  6. Needle-in-haystack is the standard benchmark for long-context quality")
print("="*70)
