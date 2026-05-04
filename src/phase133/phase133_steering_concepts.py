"""
Phase 133: Steering Vectors — NumPy Concept Simulation
========================================================
We build a tiny MLP, create synthetic positive/negative concept data,
extract a steering vector from middle-layer activations, and show that
adding it shifts the output distribution predictably.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

np.random.seed(133)

# ---------------------------------------------------------------------------
# 1. TOY MODEL
# WHY: A 3-layer MLP is the smallest architecture that has "middle layers"
# where concept directions can be isolated.
# ---------------------------------------------------------------------------
input_dim = 8
hidden_dim = 16
output_dim = 4

W1 = np.random.randn(input_dim, hidden_dim) * 0.4
b1 = np.zeros(hidden_dim)
W2 = np.random.randn(hidden_dim, hidden_dim) * 0.4
b2 = np.zeros(hidden_dim)
W3 = np.random.randn(hidden_dim, output_dim) * 0.4
b3 = np.zeros(output_dim)


def relu(x):
    return np.maximum(0, x)


def forward(x):
    """Return logits and intermediate activations."""
    z1 = x @ W1 + b1
    a1 = relu(z1)
    z2 = a1 @ W2 + b2
    a2 = relu(z2)
    logits = a2 @ W3 + b3
    return logits, (z1, a1, z2, a2)


# ---------------------------------------------------------------------------
# 2. SYNTHETIC CONCEPT DATA
# WHY: We need inputs where a known concept is present or absent so we can
# verify that the steering vector actually captures that concept.
# ---------------------------------------------------------------------------
n_samples = 200

# Positive inputs have high values in the first 3 dimensions.
# Negative inputs have high values in the last 3 dimensions.
# The middle 2 dimensions are neutral noise.
X_pos = np.random.randn(n_samples, input_dim)
X_pos[:, :3] += 1.5
X_pos[:, -3:] -= 0.5

X_neg = np.random.randn(n_samples, input_dim)
X_neg[:, :3] -= 0.5
X_neg[:, -3:] += 1.5

# Forward passes
logits_pos, acts_pos = forward(X_pos)
logits_neg, acts_neg = forward(X_neg)

# We will extract the steering vector from layer 2 activations (a2).
# WHY: Middle layers usually encode high-level concepts.
a2_pos = acts_pos[3]
a2_neg = acts_neg[3]

# ---------------------------------------------------------------------------
# 3. EXTRACT STEERING VECTOR
# WHY: The contrastive mean difference is the simplest and most robust
# method for isolating a concept direction in activation space.
# ---------------------------------------------------------------------------
v = a2_pos.mean(axis=0) - a2_neg.mean(axis=0)
v_norm = v / (np.linalg.norm(v) + 1e-8)

print("Steering vector norm:", np.linalg.norm(v))
print("Top 5 positive indices:", np.argsort(v)[-5:])
print("Top 5 negative indices:", np.argsort(v)[:5])

# ---------------------------------------------------------------------------
# 4. APPLY STEERING AT DIFFERENT COEFFICIENTS
# WHY: We want to see monotonic output shift, which proves the vector
# actually controls the concept rather than adding random noise.
# ---------------------------------------------------------------------------
coefficients = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])

# Define a simple "sentiment" score from the output logits.
# We treat logit index 0 as positive and index 1 as negative.
sentiment_scores = []

for coeff in coefficients:
    # We steer only the first 16 samples as a demo batch.
    z1, a1, z2, a2 = forward(X_pos[:16])[1]
    a2_steered = a2 + coeff * v
    logits_steered = a2_steered @ W3 + b3
    # Sentiment = positive logit mean - negative logit mean.
    sentiment = (logits_steered[:, 0] - logits_steered[:, 1]).mean()
    sentiment_scores.append(sentiment)

sentiment_scores = np.array(sentiment_scores)

print("\nSentiment vs coefficient:")
for c, s in zip(coefficients, sentiment_scores):
    print(f"  coeff={c:+.1f} → sentiment={s:+.3f}")

# ---------------------------------------------------------------------------
# 5. VISUALIZATION 1 — Activation Space Projection
# WHY: PCA shows whether positive and negative activations are separable
# and whether the steering vector points in a meaningful direction.
# ---------------------------------------------------------------------------
# PCA to 2D
a2_all = np.vstack([a2_pos, a2_neg])
a2_mean = a2_all.mean(axis=0)
a2_centered = a2_all - a2_mean

cov = a2_centered.T @ a2_centered / (a2_centered.shape[0] - 1)
eigvals, eigvecs = np.linalg.eigh(cov)
# Sort descending
order = np.argsort(eigvals)[::-1]
PC1 = eigvecs[:, order[0]]
PC2 = eigvecs[:, order[1]]

proj = a2_centered @ np.column_stack([PC1, PC2])
proj_pos = proj[:n_samples]
proj_neg = proj[n_samples:]

# Project steering vector
v_centered = v  # we only care about direction
v_proj = np.array([v_centered @ PC1, v_centered @ PC2])

fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(proj_pos[:, 0], proj_pos[:, 1], alpha=0.4, s=20, color='steelblue', label='Positive class')
ax.scatter(proj_neg[:, 0], proj_neg[:, 1], alpha=0.4, s=20, color='coral', label='Negative class')

# Draw steering vector arrow from origin
ax.annotate('', xy=v_proj * 2, xytext=(0, 0),
            arrowprops=dict(arrowstyle='->', color='black', lw=2))
ax.text(v_proj[0] * 2.2, v_proj[1] * 2.2, 'steering vector', fontsize=10)

ax.set_title('Activation Space PCA (Layer 2) with Steering Vector')
ax.set_xlabel('PC1')
ax.set_ylabel('PC2')
ax.legend()
ax.grid(True, linestyle='--', alpha=0.4)
ax.axhline(0, color='gray', linewidth=0.5)
ax.axvline(0, color='gray', linewidth=0.5)

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), 'phase133_activation_space.png')
plt.savefig(out_path, dpi=150)
plt.close()
print("Saved plot to", out_path)

# ---------------------------------------------------------------------------
# 6. VISUALIZATION 2 — Steering Effect on Output
# WHY: A monotonic curve proves that the coefficient acts like a dial.
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(coefficients, sentiment_scores, marker='o', color='darkgreen', linewidth=2, markersize=8)
ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
ax.set_title('Output Sentiment vs Steering Coefficient')
ax.set_xlabel('Steering Coefficient')
ax.set_ylabel('Sentiment Score (pos logit - neg logit)')
ax.grid(True, linestyle='--', alpha=0.4)

plt.tight_layout()
out_path2 = os.path.join(os.path.dirname(__file__), 'phase133_steering_effect.png')
plt.savefig(out_path2, dpi=150)
plt.close()
print("Saved plot to", out_path2)

# ---------------------------------------------------------------------------
# 7. ACTIVATION EDITING DEMONSTRATION
# WHY: We show clamp, shift, and replace to match the activation-editing
# concept taught in the docs.
# ---------------------------------------------------------------------------
# Pick one sample
x_test = X_pos[0:1]
logits_clean, acts_clean = forward(x_test)
a2_clean = acts_clean[3]

# Shift: add steering vector
a2_shift = a2_clean + 1.5 * v
logits_shift = a2_shift @ W3 + b3

# Clamp: zero out the top 3 neurons most aligned with the negative class
clamp_mask = np.argsort(v)[:3]
a2_clamp = a2_clean.copy()
a2_clamp[:, clamp_mask] = 0.0
logits_clamp = a2_clamp @ W3 + b3

# Replace: swap a2 with the mean positive activation
a2_replace = a2_pos.mean(axis=0, keepdims=True)
logits_replace = a2_replace @ W3 + b3

print("\nActivation editing demo (single sample):")
print(f"  Clean   positive logit: {logits_clean[0, 0]:.3f}")
print(f"  Shift   positive logit: {logits_shift[0, 0]:.3f}")
print(f"  Clamp   positive logit: {logits_clamp[0, 0]:.3f}")
print(f"  Replace positive logit: {logits_replace[0, 0]:.3f}")

print("\nDone.")
