"""
Phase 134: Self-Alignment — NumPy Concept Simulation
======================================================
We simulate iterative self-improvement. A toy linear model generates
response vectors, critiques them against a hidden target, revises them,
and updates its weights. We track quality across rounds and show the
characteristic plateau.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

np.random.seed(134)

# ---------------------------------------------------------------------------
# 1. SETUP
# WHY: A linear model with a hidden target is the simplest setting where
# self-critique can be defined as distance to an objective.
# ---------------------------------------------------------------------------
input_dim = 6
output_dim = 5
n_prompts = 100
n_rounds = 5

# Hidden target vector: the "ideal" answer the model tries to learn.
target = np.random.randn(output_dim)

# True world mapping: ideal response = W_true @ x + b_true
W_true = np.random.randn(input_dim, output_dim) * 0.5
b_true = np.random.randn(output_dim) * 0.2

# Model starts with random weights.
W = np.random.randn(input_dim, output_dim) * 0.1
b = np.zeros(output_dim)


def generate_response(x, W, b):
    """Model forward pass."""
    return x @ W + b


def critique(response, target_estimate):
    """
    Self-critique: identify dimensions with largest errors.
    WHY: A useful critique pinpoints specific problems, not just a scalar score.
    """
    error = target_estimate - response
    # Find the two dimensions with largest absolute deviation
    abs_err = np.abs(error)
    top_indices = np.argsort(abs_err)[-2:]
    critique_text = f"Dimensions {top_indices.tolist()} are off by {error[top_indices].round(2).tolist()}"
    return critique_text, error


def revise(response, error, step_size=0.4):
    """
    Revision moves the response toward the estimated target.
    WHY: The critique gives a direction; revision walks along it.
    """
    return response + step_size * error


# ---------------------------------------------------------------------------
# 2. ITERATIVE SELF-IMPROVEMENT LOOP
# WHY: Repeating generate-critique-revise-train lets us observe convergence.
# ---------------------------------------------------------------------------
round_quality = []
round_flaws = []
round_losses = []

for round_idx in range(n_rounds):
    # Generate a fresh batch of prompts
    X = np.random.randn(n_prompts, input_dim)
    ideal = X @ W_true + b_true

    responses = generate_response(X, W, b)

    # Critique uses a noisy estimate of the true target (the model does not
    # know the true target perfectly; it only knows its own guess).
    target_estimates = ideal + np.random.randn(n_prompts, output_dim) * 0.3

    critiques = []
    revised = []
    total_flaws = 0
    for i in range(n_prompts):
        _, error = critique(responses[i], target_estimates[i])
        # Count how many dimensions have error > 0.5 as "flaws found"
        flaws = int((np.abs(error) > 0.5).sum())
        total_flaws += flaws
        rev = revise(responses[i], error, step_size=0.4)
        revised.append(rev)

    revised = np.stack(revised)

    # Quality = negative mean distance to ideal (higher is better)
    distances = np.linalg.norm(revised - ideal, axis=1)
    quality = -distances.mean()
    round_quality.append(quality)
    round_flaws.append(total_flaws / n_prompts)

    # Train: simple gradient descent on MSE toward revised responses
    lr = 0.02
    pred = generate_response(X, W, b)
    loss = np.mean((pred - revised) ** 2)
    round_losses.append(loss)

    grad_W = X.T @ (pred - revised) / n_prompts
    grad_b = (pred - revised).mean(axis=0)

    W -= lr * grad_W
    b -= lr * grad_b

    print(f"Round {round_idx + 1}: quality={quality:.3f}, "
          f"flaws/response={total_flaws / n_prompts:.2f}, loss={loss:.4f}")

# ---------------------------------------------------------------------------
# 3. VISUALIZATION 1 — Quality Curve
# WHY: The classic self-improvement graph is rapid rise then flat plateau.
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].plot(range(1, n_rounds + 1), round_quality, marker='o', color='steelblue', linewidth=2)
axes[0].set_title('Quality Over Self-Improvement Rounds')
axes[0].set_xlabel('Round')
axes[0].set_ylabel('Mean Quality (-distance to ideal)')
axes[0].grid(True, linestyle='--', alpha=0.4)

# ---------------------------------------------------------------------------
# 4. VISUALIZATION 2 — Flaws Found and Training Loss
# WHY: Declining flaws and flattening loss both signal the plateau.
# ---------------------------------------------------------------------------
ax2 = axes[1]
ax2.plot(range(1, n_rounds + 1), round_flaws, marker='s', color='crimson', label='Flaws per response')
ax2.set_xlabel('Round')
ax2.set_ylabel('Flaws per response', color='crimson')
ax2.tick_params(axis='y', labelcolor='crimson')
ax2.grid(True, linestyle='--', alpha=0.4)

ax2b = ax2.twinx()
ax2b.plot(range(1, n_rounds + 1), round_losses, marker='^', color='forestgreen', label='Training loss')
ax2b.set_ylabel('MSE Loss', color='forestgreen')
ax2b.tick_params(axis='y', labelcolor='forestgreen')

ax2.set_title('Flaws Found and Training Loss per Round')

# Add legend manually
lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2b.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), 'phase134_quality_curve.png')
plt.savefig(out_path, dpi=150)
plt.close()
print("Saved plot to", out_path)

# ---------------------------------------------------------------------------
# 5. VISUALIZATION 3 — Loss Curve Alone
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(range(1, n_rounds + 1), round_losses, marker='o', color='forestgreen', linewidth=2)
ax.set_title('Training Loss Over Rounds')
ax.set_xlabel('Round')
ax.set_ylabel('MSE Loss')
ax.grid(True, linestyle='--', alpha=0.4)
plt.tight_layout()
out_path2 = os.path.join(os.path.dirname(__file__), 'phase134_loss_curve.png')
plt.savefig(out_path2, dpi=150)
plt.close()
print("Saved plot to", out_path2)

print("\nDone.")
