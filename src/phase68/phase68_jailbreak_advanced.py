"""
Phase 68: Jailbreaking — Advanced (GCG & AutoDAN)
NumPy Concept Demo: Simulating Greedy Coordinate Gradient (GCG)

This script demonstrates the core idea of GCG in a simplified, continuous
embedding space. We optimize a suffix vector to maximize a "harmfulness"
objective while minimizing detection by a safety classifier.

 WHY THIS MATTERS:
 Real GCG operates on discrete token indices. Computing gradients through
 argmax/token-sampling is non-differentiable. GCG approximates this by
 computing gradients in the continuous embedding space and greedily swapping
the single token that most reduces loss. Here, we simulate the "greedy
coordinate" aspect by doing coordinate-wise gradient descent on a suffix
matrix.
"""

import matplotlib
matplotlib.use('Agg')  # MUST come before pyplot import; enables headless rendering
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------------------------
EMB_DIM = 16          # Dimensionality of our toy embedding space
VOCAB_SIZE = 50       # Size of toy vocabulary (not directly used in continuous sim)
SUFFIX_LEN = 5        # Length of adversarial suffix (number of token embeddings)
N_ITERATIONS = 200    # Number of GCG optimization steps
SEED = 42             # Reproducibility

np.random.seed(SEED)

# ---------------------------------------------------------------------------
# 2. SET UP THE "WORLD"
# ---------------------------------------------------------------------------
# In a real LLM, embeddings come from a learned lookup table. Here we
# invent vectors to simulate the geometry of "safe" vs "harmful" regions.

# Harmful target: the embedding direction we want the model to move toward.
# Think of this as the embedding of the harmful completion we want.
harmful_target = np.random.randn(EMB_DIM)
harmful_target /= np.linalg.norm(harmful_target)

# Safe baseline: the direction of benign/helpful responses.
safe_baseline = np.random.randn(EMB_DIM)
safe_baseline /= np.linalg.norm(safe_baseline)

# Make safe and harmful somewhat orthogonal so the task is non-trivial.
safe_baseline -= np.dot(safe_baseline, harmful_target) * harmful_target
safe_baseline /= np.linalg.norm(safe_baseline)

# Safety classifier: a linear model that scores how "safe" a prompt embedding is.
# We train it quickly so it actually separates safe vs harmful regions.
safety_w = np.random.randn(EMB_DIM) * 0.5
safety_b = 0.0

# Quick "training" of the safety classifier on a few synthetic examples:
for _ in range(100):
    # Sample a random direction
    vec = np.random.randn(EMB_DIM)
    vec /= np.linalg.norm(vec)
    
    # Label: 1.0 if closer to safe, 0.0 if closer to harmful
    label = 1.0 if np.dot(vec, safe_baseline) > np.dot(vec, harmful_target) else 0.0
    
    pred = 1.0 / (1.0 + np.exp(-(np.dot(vec, safety_w) + safety_b)))
    grad_w = (pred - label) * vec
    grad_b = (pred - label)
    safety_w -= 0.1 * grad_w
    safety_b -= 0.1 * grad_b

# Normalize classifier weights
norm_w = np.linalg.norm(safety_w)
if norm_w > 0:
    safety_w /= norm_w
    safety_b /= norm_w

# Fixed prompt embedding: the user's base query (e.g., "How do I...")
prompt_emb = np.random.randn(EMB_DIM)
prompt_emb /= np.linalg.norm(prompt_emb)

# Initialize adversarial suffix as small random perturbations.
# GCG starts from a random or hand-picked seed suffix.
suffix = np.random.randn(SUFFIX_LEN, EMB_DIM) * 0.1

# ---------------------------------------------------------------------------
# 3. DEFINE FUNCTIONS
# ---------------------------------------------------------------------------

def sequence_embedding(prompt, suffix):
    """
    Pool prompt + suffix into a single sequence embedding.
    We use mean pooling, a common simplification of how Transformers
    aggregate token information.
    """
    return (prompt + suffix.sum(axis=0)) / (1 + SUFFIX_LEN)


def harmfulness_score(seq_emb):
    """
    Score how close the sequence is to the harmful target.
    Higher = more harmful (the model is more likely to produce bad output).
    """
    return np.dot(seq_emb, harmful_target)


def safety_score(seq_emb):
    """
    Logistic safety classifier. Higher = classified as SAFE.
    We want the attacker to drive this BELOW the threshold.
    """
    z = np.dot(seq_emb, safety_w) + safety_b
    # Clip for numerical stability
    z = np.clip(z, -20, 20)
    return 1.0 / (1.0 + np.exp(-z))


def compute_loss(suffix, alpha=3.0, beta=0.5):
    """
    Attacker's objective:
      - Maximize harmfulness   => minimize -harmfulness
      - Minimize safety score  => add alpha * safety
      - Keep suffix bounded    => add beta * L2 regularization

    This mirrors the GCG loss: we want the suffix that most pushes the
    model toward the harmful target while staying under the safety radar.
    """
    seq_emb = sequence_embedding(prompt_emb, suffix)
    harm = harmfulness_score(seq_emb)
    safe = safety_score(seq_emb)
    reg = beta * np.sum(suffix ** 2)
    loss = -harm + alpha * safe + reg
    return loss, harm, safe


# ---------------------------------------------------------------------------
# 4. GCG-STYLE COORDINATE-WISE OPTIMIZATION
# ---------------------------------------------------------------------------
# GCG does not do full gradient descent on all tokens simultaneously.
# Instead, it computes the gradient for each token embedding coordinate,
# identifies the token whose swap would most reduce loss, and performs
# that single swap. In our continuous simulation, we approximate this
# by doing coordinate-wise gradient descent with a small step.

loss_history = []
harm_history = []
safety_history = []

LEARNING_RATE = 0.15
EPSILON = 1e-3       # For finite-difference gradient estimation
GRAD_CLIP = 25.0     # Prevent exploding gradients

print("=" * 60)
print("GCG SIMULATION: Coordinate-wise Suffix Optimization")
print("=" * 60)

for iteration in range(N_ITERATIONS):
    current_loss, current_harm, current_safe = compute_loss(suffix)
    loss_history.append(current_loss)
    harm_history.append(current_harm)
    safety_history.append(current_safe)

    # Coordinate-wise gradient estimation (GCG style)
    # We iterate through every coordinate of the suffix matrix.
    # WHY recompute loss each time: True coordinate descent updates one
    # coordinate and immediately uses the new state for the next coordinate.
    # This prevents compounding errors from an outdated baseline loss.
    for i in range(SUFFIX_LEN):
        for j in range(EMB_DIM):
            # Recompute baseline loss at the CURRENT suffix state
            baseline_loss, _, _ = compute_loss(suffix)
            
            suffix_plus = suffix.copy()
            suffix_plus[i, j] += EPSILON
            loss_plus, _, _ = compute_loss(suffix_plus)
            grad = (loss_plus - baseline_loss) / EPSILON
            
            # Clip gradient to prevent runaway updates
            grad = np.clip(grad, -GRAD_CLIP, GRAD_CLIP)
            
            # Gradient descent on this single coordinate
            suffix[i, j] -= LEARNING_RATE * grad
            
            # Immediate clipping prevents any single coordinate from exploding
            suffix[i, j] = np.clip(suffix[i, j], -3.0, 3.0)

    if iteration % 40 == 0 or iteration == N_ITERATIONS - 1:
        print(f"Iter {iteration:03d} | Loss: {current_loss:.4f} | "
              f"Harm: {current_harm:.4f} | Safety: {current_safe:.4f}")

# ---------------------------------------------------------------------------
# 5. FINAL EVALUATION
# ---------------------------------------------------------------------------
final_seq = sequence_embedding(prompt_emb, suffix)
final_harm = harmfulness_score(final_seq)
final_safety = safety_score(final_seq)

print("=" * 60)
print("FINAL EVALUATION")
print("=" * 60)
print(f"Initial Harmfulness (Iter 0): {harm_history[0]:.4f}")
print(f"Final Harmfulness:            {final_harm:.4f}")
print(f"Initial Safety Score (Iter 0): {safety_history[0]:.4f}")
print(f"Final Safety Score:            {final_safety:.4f}")
print(f"Safety Threshold (example):    0.5000")
print(f"Bypass Successful?             {'YES' if final_safety < 0.5 else 'NO'}")
print(f"Optimized Suffix L2 Norm:      {np.linalg.norm(suffix):.4f}")

# ---------------------------------------------------------------------------
# 6. PLOT OPTIMIZATION TRAJECTORY
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

axes[0].plot(loss_history, color='crimson', linewidth=2)
axes[0].set_title('GCG: Total Loss over Iterations', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Iteration')
axes[0].set_ylabel('Loss (lower = better for attacker)')
axes[0].grid(True, alpha=0.3)

axes[1].plot(harm_history, color='darkred', linewidth=2)
axes[1].set_title('Harmfulness Trajectory', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Iteration')
axes[1].set_ylabel('Harm Score (higher = more harmful)')
axes[1].grid(True, alpha=0.3)

axes[2].plot(safety_history, color='steelblue', linewidth=2, label='Safety Score')
axes[2].axhline(y=0.5, color='gray', linestyle='--', linewidth=1.5, label='Threshold')
axes[2].set_title('Safety Classifier Trajectory', fontsize=12, fontweight='bold')
axes[2].set_xlabel('Iteration')
axes[2].set_ylabel('Safety Score (lower = bypassed)')
axes[2].legend(loc='upper right')
axes[2].grid(True, alpha=0.3)

plt.suptitle('Phase 68: GCG Adversarial Suffix Optimization', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()

output_path = '/Users/zen/Desktop/building-ai/ai-miden/src/phase68/jailbreak_advanced.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"\nPlot saved to: {output_path}")
