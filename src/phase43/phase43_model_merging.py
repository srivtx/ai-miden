#!/usr/bin/env python3
"""
Phase 43: Model Merging & Ensembles — NumPy Concept Demo
===========================================================
This script demonstrates how multiple fine-tuned models can be
combined into a single model without any additional training.

Key insight: Fine-tuned models stay near the base model in weight
space. Their differences (task vectors) encode task-specific knowledge.
By averaging or selecting these differences, we create a multi-task
model that runs at the speed of a single model.

Concepts demonstrated:
  - Simple weight averaging
  - Task arithmetic (base + weighted task vectors)
  - SLERP (spherical linear interpolation)
  - TIES-Merging (Trim, Elect, Sign, Merge)

Why this matters:
  MergeKit and similar tools create powerful multi-task models
  by combining open-source fine-tunes in seconds on a CPU.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(43)

# =============================================================================
# SECTION 1: BASE MODEL AND THREE TASKS
# =============================================================================
# We create a simple linear model: y = W @ x + b
# The base model is trained on a general task.
# Then we fine-tune three copies on three specialized tasks.

input_dim = 8
output_dim = 3
num_samples = 200

class LinearModel:
    """Simple linear classifier with softmax output."""
    def __init__(self):
        self.W = np.random.randn(input_dim, output_dim) * 0.1
        self.b = np.zeros(output_dim)

    def forward(self, X):
        """X shape: (n_samples, input_dim). Returns logits."""
        return X @ self.W + self.b

    def predict(self, X):
        logits = self.forward(X)
        return np.argmax(logits, axis=1)

    def accuracy(self, X, y):
        preds = self.predict(X)
        return np.mean(preds == y)

    def copy(self):
        m = LinearModel()
        m.W = self.W.copy()
        m.b = self.b.copy()
        return m

    def get_params(self):
        return np.concatenate([self.W.flatten(), self.b.flatten()])

    def set_params(self, params):
        self.W = params[:input_dim * output_dim].reshape(input_dim, output_dim)
        self.b = params[input_dim * output_dim:]

def generate_task_data(task_id):
    """
    Generate synthetic data where each task has a different
    discriminative feature. Task 0: first 2 features matter.
    Task 1: next 2 features matter. Task 2: last 2 features matter.
    """
    X = np.random.randn(num_samples, input_dim)
    # Create labels based on different feature subsets for each task
    if task_id == 0:
        logits = 3.0 * X[:, 0] + 2.0 * X[:, 1]
    elif task_id == 1:
        logits = 3.0 * X[:, 2] + 2.0 * X[:, 3]
    else:
        logits = 3.0 * X[:, 4] + 2.0 * X[:, 5]
    # Add noise and create 3-class problem
    y = np.zeros(num_samples, dtype=int)
    y[logits > 0.5] = 1
    y[logits < -0.5] = 2
    return X, y

# =============================================================================
# SECTION 2: TRAIN BASE MODEL AND FINE-TUNE ON THREE TASKS
# =============================================================================

def train_model(model, X, y, lr=0.05, epochs=100):
    """Train with vanilla SGD and cross-entropy loss."""
    n = len(y)
    for epoch in range(epochs):
        logits = model.forward(X)
        # Softmax
        exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
        # Gradient of CE loss
        grad_logits = probs.copy()
        grad_logits[np.arange(n), y] -= 1
        grad_logits /= n
        # Backprop
        grad_W = X.T @ grad_logits
        grad_b = np.sum(grad_logits, axis=0)
        # Update
        model.W -= lr * grad_W
        model.b -= lr * grad_b

# Generate data for all tasks
X_tasks = []
y_tasks = []
for t in range(3):
    X, y = generate_task_data(t)
    X_tasks.append(X)
    y_tasks.append(y)

# Train base model on mixed data
print("Training base model on mixed tasks...")
X_mixed = np.vstack(X_tasks)
y_mixed = np.hstack(y_tasks)
base_model = LinearModel()
train_model(base_model, X_mixed, y_mixed, lr=0.1, epochs=150)
print(f"Base model accuracies: " + ", ".join([
    f"Task {t}={base_model.accuracy(X_tasks[t], y_tasks[t]):.2%}"
    for t in range(3)
]))

# Fine-tune three copies on individual tasks
fine_tuned = []
for t in range(3):
    model = base_model.copy()
    print(f"Fine-tuning model {t} on Task {t}...")
    train_model(model, X_tasks[t], y_tasks[t], lr=0.1, epochs=80)
    fine_tuned.append(model)
    accs = [model.accuracy(X_tasks[i], y_tasks[i]) for i in range(3)]
    print(f"  Task {t} model accuracies: Task0={accs[0]:.2%}, Task1={accs[1]:.2%}, Task2={accs[2]:.2%}")

# =============================================================================
# SECTION 3: MERGING TECHNIQUES
# =============================================================================

def simple_average_merge(models):
    """Average all weights directly."""
    merged = LinearModel()
    merged.W = np.mean([m.W for m in models], axis=0)
    merged.b = np.mean([m.b for m in models], axis=0)
    return merged

def task_arithmetic_merge(base, models, lambdas):
    """
    Task arithmetic: base + sum(lambda_i * (model_i - base))
    """
    merged = base.copy()
    for m, lam in zip(models, lambdas):
        merged.W += lam * (m.W - base.W)
        merged.b += lam * (m.b - base.b)
    return merged

def slerp_merge(model_a, model_b, t=0.5):
    """
    Spherical Linear Interpolation between two models.
    t=0 gives model_a, t=1 gives model_b.
    """
    # Flatten to vectors
    a_params = model_a.get_params()
    b_params = model_b.get_params()

    # Compute angle
    dot = np.dot(a_params, b_params)
    norm_a = np.linalg.norm(a_params)
    norm_b = np.linalg.norm(b_params)
    cos_theta = dot / (norm_a * norm_b + 1e-10)
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    theta = np.arccos(cos_theta)

    if theta < 1e-6:
        # Models are identical
        return model_a.copy()

    # SLERP formula
    sin_theta = np.sin(theta)
    w1 = np.sin((1 - t) * theta) / sin_theta
    w2 = np.sin(t * theta) / sin_theta
    merged_params = w1 * a_params + w2 * b_params

    merged = LinearModel()
    merged.set_params(merged_params)
    return merged

def ties_merge(base, models, trim_threshold=0.05):
    """
    TIES-Merging: Trim, Elect Sign, Merge.
    Processes W and b jointly as a single parameter vector per model.
    """
    merged = base.copy()
    n_models = len(models)

    # Concatenate W and b into single parameter vector per model
    def get_params(m):
        return np.concatenate([m.W.flatten(), m.b.flatten()])

    base_params = get_params(base)
    n_params = len(base_params)

    # Compute deltas
    deltas = [get_params(m) - base_params for m in models]

    # Step 1: Trim small-magnitude changes
    trimmed = []
    for d in deltas:
        mask = np.abs(d) >= trim_threshold
        trimmed.append(d * mask)

    # Step 2: Elect majority sign per parameter
    elected = np.zeros((n_models, n_params))
    for i in range(n_params):
        signs = []
        for m in range(n_models):
            if trimmed[m][i] != 0:
                signs.append(np.sign(trimmed[m][i]))
        if len(signs) == 0:
            continue
        majority_sign = np.sign(np.sum(signs))
        if majority_sign == 0:
            majority_sign = 1.0
        for m in range(n_models):
            if trimmed[m][i] != 0 and np.sign(trimmed[m][i]) == majority_sign:
                elected[m, i] = trimmed[m][i]

    # Step 3: Merge (average elected changes)
    merged_delta = np.zeros(n_params)
    for i in range(n_params):
        vals = elected[:, i]
        non_zero = vals[vals != 0]
        if len(non_zero) > 0:
            merged_delta[i] = np.mean(non_zero)

    # Unflatten back to W and b
    w_size = input_dim * output_dim
    merged.W = base.W + merged_delta[:w_size].reshape(input_dim, output_dim)
    merged.b = base.b + merged_delta[w_size:]
    return merged

# =============================================================================
# SECTION 4: EVALUATE ALL MERGE METHODS
# =============================================================================

print("\n" + "="*60)
print("MERGING RESULTS")
print("="*60)

methods = {}

# Simple average
methods['Simple Average'] = simple_average_merge(fine_tuned)

# Task arithmetic
methods['Task Arithmetic'] = task_arithmetic_merge(base_model, fine_tuned, [0.5, 0.5, 0.5])

# SLERP (sequential: merge 0+1, then result with 2)
slerp_01 = slerp_merge(fine_tuned[0], fine_tuned[1], t=0.5)
methods['SLERP'] = slerp_merge(slerp_01, fine_tuned[2], t=0.33)

# TIES
try:
    methods['TIES-Merging'] = ties_merge(base_model, fine_tuned, trim_threshold=0.02)
except Exception as e:
    print(f"TIES merge error: {e}")

# Evaluate
results = []
for name, model in methods.items():
    accs = [model.accuracy(X_tasks[t], y_tasks[t]) for t in range(3)]
    mean_acc = np.mean(accs)
    results.append((name, accs, mean_acc))
    print(f"{name:20s} | Task0={accs[0]:.2%} Task1={accs[1]:.2%} Task2={accs[2]:.2%} | Mean={mean_acc:.2%}")

# Also show individual models and base
print(f"\n{'Base Model':20s} | " + " ".join([f"Task{t}={base_model.accuracy(X_tasks[t], y_tasks[t]):.2%}" for t in range(3)]))
for t in range(3):
    accs = [fine_tuned[t].accuracy(X_tasks[i], y_tasks[i]) for i in range(3)]
    print(f"{'Task ' + str(t) + ' Fine-tune':20s} | " + " ".join([f"Task{i}={accs[i]:.2%}" for i in range(3)]))

# =============================================================================
# SECTION 5: VISUALIZATION
# =============================================================================

# Bar chart comparing mean accuracy across methods
fig, ax = plt.subplots(figsize=(10, 5))
names = [r[0] for r in results]
mean_accs = [r[2] for r in results]
colors = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6']

bars = ax.bar(names, mean_accs, color=colors[:len(names)])
ax.set_ylabel('Mean Accuracy Across 3 Tasks')
ax.set_title('Model Merging: Multi-Task Performance Comparison')
ax.set_ylim(0, 1.0)
ax.axhline(y=base_model.accuracy(X_mixed, y_mixed), color='gray', linestyle='--', label='Base Model (mixed training)')
ax.legend()

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height:.1%}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom')

plt.tight_layout()
os.makedirs('src/phase43', exist_ok=True)
plt.savefig('src/phase43/model_merging.png', dpi=150)
print("\nSaved plot to src/phase43/model_merging.png")

# =============================================================================
# SECTION 6: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("Model merging combines fine-tuned models without retraining.")
print("Each method trades off simplicity vs. sophistication:")
print("  - Simple Average: Easy, but dilutes base model knowledge")
print("  - Task Arithmetic: Preserves base, adds task-specific deltas")
print("  - SLERP: Respects weight space geometry, preserves norms")
print("  - TIES-Merging: Removes noise and resolves sign conflicts")
print("\nKey insight: Merged models run at 1× inference cost,")
print("while ensembles run at N× cost. MergeKit creates powerful")
print("multi-task models in seconds on a CPU.")
