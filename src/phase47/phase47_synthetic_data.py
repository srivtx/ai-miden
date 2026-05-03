#!/usr/bin/env python3
"""
Phase 47: Synthetic Data & Self-Improvement — NumPy Concept Demo
=================================================================
This script demonstrates how a model can generate its own training
data, filter it with an automatic verifier, and iteratively improve
itself without new human labels.

Key insight: Even a mediocre model generates some correct answers.
If you filter aggressively and train only on the correct ones, the
model improves. Each generation produces better synthetic data than
the last.

Concepts demonstrated:
  - Synthetic data generation (model writes its own training set)
  - Rejection sampling (verifier filters bad outputs)
  - Iterative self-improvement (train on best outputs, repeat)
  - Constitutional AI (enforcing a principle like "prefer shorter answers")

Why this matters:
  High-quality human data is finite and expensive. Synthetic data
  breaks the bottleneck, enabling models to scale beyond human
  knowledge. This is how AlphaGo surpassed human Go players.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(47)

# =============================================================================
# SECTION 1: BASE MODEL AND VERIFIER
# =============================================================================
# We use a tiny linear model as the "generator" and an exact arithmetic
# checker as the "verifier." The generator learns to solve a + b problems.

class TinySolver:
    def __init__(self):
        self.w = np.random.randn(2) * 0.1
        self.b = 0.0

    def predict(self, a, b):
        """Predict a + b from inputs [a, b]."""
        x = np.array([a, b])
        return x @ self.w + self.b

    def train(self, X, y, lr=0.01, epochs=50):
        for _ in range(epochs):
            preds = X @ self.w + self.b
            errors = preds - y
            grad_w = X.T @ errors / len(y)
            grad_b = np.mean(errors)
            self.w -= lr * grad_w
            self.b -= lr * grad_b

# Verifier: exact arithmetic check
def verifier(a, b, predicted):
    """Returns True if prediction equals a + b."""
    return abs(predicted - (a + b)) < 0.5

# =============================================================================
# SECTION 2: HUMAN BASELINE DATASET
# =============================================================================

print("="*60)
print("Phase 47: Synthetic Data & Self-Improvement")
print("="*60)

# Small human-labeled dataset
np.random.seed(47)
human_a = np.random.randint(1, 10, size=100)
human_b = np.random.randint(1, 10, size=100)
human_X = np.column_stack([human_a, human_b])
human_y = human_a + human_b

print(f"\nHuman-labeled dataset: {len(human_y)} examples")

# =============================================================================
# SECTION 3: BASELINE — TRAIN ON HUMAN DATA ONLY
# =============================================================================

model_human = TinySolver()
model_human.train(human_X, human_y, lr=0.01, epochs=200)

# Test on held-out problems
test_a = np.random.randint(1, 10, size=50)
test_b = np.random.randint(1, 10, size=50)
correct_human = sum(verifier(test_a[i], test_b[i], model_human.predict(test_a[i], test_b[i])) for i in range(50))
print(f"Model trained on human data: {correct_human}/50 correct ({correct_human/50:.0%})")

# =============================================================================
# SECTION 4: SYNTHETIC DATA GENERATION + REJECTION SAMPLING
# =============================================================================

def generate_synthetic(model, n_candidates=100):
    """
    Generate synthetic training data by sampling problems,
    running the model, and keeping only verified correct answers.
    """
    synth_X = []
    synth_y = []
    accepted = 0
    for _ in range(n_candidates):
        a = np.random.randint(1, 10)
        b = np.random.randint(1, 10)
        pred = model.predict(a, b)
        if verifier(a, b, pred):
            synth_X.append([a, b])
            synth_y.append(a + b)
            accepted += 1
    return np.array(synth_X), np.array(synth_y), accepted

# Generate synthetic dataset from the human-trained model
synth_X, synth_y, accepted = generate_synthetic(model_human, n_candidates=500)
print(f"\nSynthetic generation: {accepted}/500 candidates passed verification ({accepted/500:.1%})")
print(f"Synthetic dataset size: {len(synth_y)} examples")

# =============================================================================
# SECTION 5: ITERATIVE SELF-IMPROVEMENT
# =============================================================================

print("\n--- Iterative Self-Improvement ---")
iterations = 5
history = {
    'iteration': [0],
    'accuracy': [correct_human / 50],
    'synthetic_size': [len(human_y)]
}

current_model = TinySolver()
current_model.w = model_human.w.copy()
current_model.b = model_human.b

for it in range(1, iterations + 1):
    # Generate synthetic data from current model
    synth_X, synth_y, accepted = generate_synthetic(current_model, n_candidates=500)

    if len(synth_y) < 5:
        print(f"Iteration {it}: Too few synthetic samples ({len(synth_y)}). Stopping.")
        break

    # Train on synthetic data
    current_model.train(synth_X, synth_y, lr=0.01, epochs=100)

    # Evaluate
    correct = sum(verifier(test_a[i], test_b[i], current_model.predict(test_a[i], test_b[i])) for i in range(50))
    acc = correct / 50
    history['iteration'].append(it)
    history['accuracy'].append(acc)
    history['synthetic_size'].append(len(synth_y))
    print(f"Iteration {it}: {correct}/50 correct ({acc:.0%}), synthetic data: {len(synth_y)}")

# =============================================================================
# SECTION 6: CONSTITUTIONAL AI DEMONSTRATION
# =============================================================================

print("\n--- Constitutional AI Principle ---")
print("Principle: 'Prefer answers closer to the true integer value'")

# Model without constitution: rounds to nearest integer
# Model with constitution: penalizes distance from integer

class ConstitutionalSolver(TinySolver):
    def train_with_principle(self, X, y, lr=0.01, epochs=50):
        """Train while penalizing non-integer predictions (conciseness principle)."""
        for _ in range(epochs):
            preds = X @ self.w + self.b
            # MSE loss + penalty for distance from nearest integer
            round_error = np.abs(preds - np.round(preds))
            errors = (preds - y) + 0.5 * round_error
            grad_w = X.T @ errors / len(y)
            grad_b = np.mean(errors)
            self.w -= lr * grad_w
            self.b -= lr * grad_b

const_model = ConstitutionalSolver()
const_model.w = model_human.w.copy()
const_model.b = model_human.b
const_model.train_with_principle(human_X, human_y, lr=0.01, epochs=200)

correct_const = sum(verifier(test_a[i], test_b[i], const_model.predict(test_a[i], test_b[i])) for i in range(50))
print(f"Model with constitutional principle: {correct_const}/50 correct ({correct_const/50:.0%})")
print("(Principle pushes predictions toward clean integers)")

# =============================================================================
# SECTION 7: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Plot 1: Self-improvement curve
ax = axes[0]
ax.plot(history['iteration'], history['accuracy'], 'b-o', linewidth=2, markersize=8)
ax.axhline(y=correct_human/50, color='gray', linestyle='--', label='Human-only baseline')
ax.set_xlabel('Self-Improvement Iteration')
ax.set_ylabel('Accuracy on Test Problems')
ax.set_title('Iterative Self-Improvement via Synthetic Data')
ax.set_ylim(0, 1.0)
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Synthetic dataset size per iteration
ax = axes[1]
ax.bar(history['iteration'], history['synthetic_size'], color='#3498db', alpha=0.7)
ax.set_xlabel('Iteration')
ax.set_ylabel('Synthetic Training Examples')
ax.set_title('Synthetic Data Yield per Iteration')
ax.grid(True, alpha=0.3)

plt.tight_layout()
os.makedirs('src/phase47', exist_ok=True)
plt.savefig('src/phase47/synthetic_data.png', dpi=150)
print("\nSaved plot to src/phase47/synthetic_data.png")

# =============================================================================
# SECTION 8: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Human-only baseline: {history['accuracy'][0]:.0%}")
print(f"After {len(history['iteration'])-1} self-improvement iterations: {history['accuracy'][-1]:.0%}")
print("\nKey insight: A model generates its own training data,")
print("a verifier filters correct answers, and the model trains")
print("on its own best outputs. Each iteration raises quality.")
print("This breaks the dependence on scarce human-labeled data.")
