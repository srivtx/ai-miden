#!/usr/bin/env python3
"""
Phase 62: Active Learning — NumPy Concept Demo
================================================
This script demonstrates how to intelligently select which data
to label when labeling is expensive.

Key insight: Not all labels are equally valuable. Labeling examples
where the model is uncertain improves accuracy faster than random
sampling.

Concepts demonstrated:
  - Pool-based active learning loop
  - Uncertainty sampling (least confident, margin, entropy)
  - Comparison with random sampling
  - Accuracy vs. number of labels curve
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(62)

# =============================================================================
# SECTION 1: GENERATE 2D CLASSIFICATION DATA
# =============================================================================

n_total = 300
X_all = np.random.randn(n_total, 2)
# True boundary: x0 + x1 > 0
y_all = (X_all[:, 0] + X_all[:, 1] > 0).astype(int)

print("="*60)
print("Phase 62: Active Learning")
print("="*60)
print(f"\nDataset: {n_total} points, 2D, binary classification")
print(f"True boundary: x0 + x1 = 0")

# Start with 10 labeled points
n_initial = 10
initial_idx = np.random.choice(n_total, n_initial, replace=False)
pool_idx = np.setdiff1d(np.arange(n_total), initial_idx)

# =============================================================================
# SECTION 2: MODEL (Logistic Regression)
# =============================================================================

def train_model(X, y):
    """Train logistic regression with L2 regularization."""
    n, d = X.shape
    w = np.zeros(d)
    b = 0.0
    lr = 0.1
    for _ in range(200):
        logits = X @ w + b
        preds = 1 / (1 + np.exp(-logits))
        grad_w = X.T @ (preds - y) / n + 0.01 * w
        grad_b = np.mean(preds - y)
        w -= lr * grad_w
        b -= lr * grad_b
    return w, b

def predict_proba(X, w, b):
    logits = X @ w + b
    return 1 / (1 + np.exp(-logits))

def predict(X, w, b):
    return (predict_proba(X, w, b) > 0.5).astype(int)

# =============================================================================
# SECTION 3: ACTIVE LEARNING WITH UNCERTAINTY SAMPLING
# =============================================================================

print("\n--- Active Learning (Uncertainty Sampling) ---")

labeled_idx = list(initial_idx)
acc_al_history = []

# Budget: label 100 more points in rounds of 10
budget = 100
batch_size = 10
n_rounds = budget // batch_size

for round_idx in range(n_rounds):
    # Train on current labeled set
    X_labeled = X_all[labeled_idx]
    y_labeled = y_all[labeled_idx]
    w, b = train_model(X_labeled, y_labeled)
    
    # Evaluate on ALL data (we know true labels for comparison)
    acc = np.mean(predict(X_all, w, b) == y_all)
    acc_al_history.append(acc)
    
    if len(pool_idx) == 0:
        break
    
    # Compute uncertainty on pool
    probs = predict_proba(X_all[pool_idx], w, b)
    
    # Least confident sampling
    uncertainty = 1 - np.maximum(probs, 1 - probs)
    
    # Select most uncertain
    selected_in_pool = np.argsort(uncertainty)[-batch_size:]
    selected_global = pool_idx[selected_in_pool]
    
    # Add to labeled set, remove from pool
    labeled_idx.extend(selected_global)
    pool_idx = np.setdiff1d(pool_idx, selected_global)
    
    if round_idx < 3 or round_idx == n_rounds - 1:
        print(f"  Round {round_idx+1}: {len(labeled_idx)} labeled, accuracy = {acc*100:.1f}%")

# =============================================================================
# SECTION 4: RANDOM SAMPLING BASELINE
# =============================================================================

print("\n--- Random Sampling ---")

# Reset pool
pool_idx_random = np.setdiff1d(np.arange(n_total), initial_idx)
labeled_idx_random = list(initial_idx)
acc_random_history = []

for round_idx in range(n_rounds):
    X_labeled = X_all[labeled_idx_random]
    y_labeled = y_all[labeled_idx_random]
    w, b = train_model(X_labeled, y_labeled)
    
    acc = np.mean(predict(X_all, w, b) == y_all)
    acc_random_history.append(acc)
    
    if len(pool_idx_random) == 0:
        break
    
    # Random selection
    selected = np.random.choice(pool_idx_random, size=min(batch_size, len(pool_idx_random)), replace=False)
    labeled_idx_random.extend(selected)
    pool_idx_random = np.setdiff1d(pool_idx_random, selected)
    
    if round_idx < 3 or round_idx == n_rounds - 1:
        print(f"  Round {round_idx+1}: {len(labeled_idx_random)} labeled, accuracy = {acc*100:.1f}%")

# =============================================================================
# SECTION 5: MARGIN SAMPLING COMPARISON
# =============================================================================

print("\n--- Margin Sampling ---")

pool_idx_margin = np.setdiff1d(np.arange(n_total), initial_idx)
labeled_idx_margin = list(initial_idx)
acc_margin_history = []

for round_idx in range(n_rounds):
    X_labeled = X_all[labeled_idx_margin]
    y_labeled = y_all[labeled_idx_margin]
    w, b = train_model(X_labeled, y_labeled)
    
    acc = np.mean(predict(X_all, w, b) == y_all)
    acc_margin_history.append(acc)
    
    if len(pool_idx_margin) == 0:
        break
    
    probs = predict_proba(X_all[pool_idx_margin], w, b)
    # Margin: |p - 0.5|, smaller = more uncertain
    margins = np.abs(probs - 0.5)
    selected_in_pool = np.argsort(margins)[:batch_size]
    selected_global = pool_idx_margin[selected_in_pool]
    
    labeled_idx_margin.extend(selected_global)
    pool_idx_margin = np.setdiff1d(pool_idx_margin, selected_global)

print(f"  Final margin sampling accuracy: {acc_margin_history[-1]*100:.1f}%")

# =============================================================================
# SECTION 6: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Accuracy vs. number of labels
ax = axes[0, 0]
n_labels = [n_initial + i*batch_size for i in range(len(acc_al_history))]
ax.plot(n_labels, [a*100 for a in acc_al_history], 'b-o', linewidth=2, label='Uncertainty (least confident)', markersize=6)
ax.plot(n_labels, [a*100 for a in acc_random_history], 'r-s', linewidth=2, label='Random sampling', markersize=6)
ax.plot(n_labels, [a*100 for a in acc_margin_history], 'g-^', linewidth=2, label='Margin sampling', markersize=6)
ax.axhline(y=100, color='gray', linestyle='--', alpha=0.5)
ax.set_title('Accuracy vs. Number of Labeled Examples')
ax.set_xlabel('Number of labeled examples')
ax.set_ylabel('Accuracy (%)')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Selected points visualization (active learning)
ax = axes[0, 1]
# Train final model
w_al, b_al = train_model(X_all[labeled_idx], y_all[labeled_idx])
xx, yy = np.meshgrid(np.linspace(-3, 3, 100), np.linspace(-3, 3, 100))
grid = np.c_[xx.ravel(), yy.ravel()]
probs_grid = predict_proba(grid, w_al, b_al).reshape(xx.shape)
ax.contourf(xx, yy, probs_grid, levels=20, cmap='RdBu', alpha=0.4)
ax.scatter(X_all[initial_idx, 0], X_all[initial_idx, 1], c='yellow', s=100, 
           edgecolors='black', marker='*', label='Initial labeled', zorder=5)
# Show some selected points
selected_later = labeled_idx[n_initial:n_initial+30]
ax.scatter(X_all[selected_later, 0], X_all[selected_later, 1], c='lime', s=50,
           edgecolors='black', marker='s', label='Active selected', zorder=4)
ax.scatter(X_all[:, 0], X_all[:, 1], c=y_all, cmap='RdBu', alpha=0.3, s=10)
ax.set_title('Active Learning: Selected Points Near Boundary')
ax.set_xlabel('x1')
ax.set_ylabel('x2')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Random selected points
ax = axes[1, 0]
w_rand, b_rand = train_model(X_all[labeled_idx_random], y_all[labeled_idx_random])
probs_grid_rand = predict_proba(grid, w_rand, b_rand).reshape(xx.shape)
ax.contourf(xx, yy, probs_grid_rand, levels=20, cmap='RdBu', alpha=0.4)
selected_rand = labeled_idx_random[n_initial:n_initial+30]
ax.scatter(X_all[selected_rand, 0], X_all[selected_rand, 1], c='orange', s=50,
           edgecolors='black', marker='s', label='Random selected', zorder=4)
ax.scatter(X_all[:, 0], X_all[:, 1], c=y_all, cmap='RdBu', alpha=0.3, s=10)
ax.set_title('Random Sampling: Selected Points Spread Out')
ax.set_xlabel('x1')
ax.set_ylabel('x2')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Gain over random
ax = axes[1, 1]
gain = [(al - rand) * 100 for al, rand in zip(acc_al_history, acc_random_history)]
ax.bar(range(len(gain)), gain, color='#2ecc71' if gain[-1] > 0 else '#e74c3c', 
       alpha=0.7, edgecolor='black')
ax.axhline(y=0, color='black', linewidth=0.5)
ax.set_title('Accuracy Gain: Active vs. Random')
ax.set_xlabel('Round')
ax.set_ylabel('Accuracy Gain (%)')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
os.makedirs('src/phase62', exist_ok=True)
plt.savefig('src/phase62/active_learning.png', dpi=150)
print("\nSaved plot to src/phase62/active_learning.png")

# =============================================================================
# SECTION 7: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Final accuracy with {n_initial + budget} labels:")
print(f"  Uncertainty sampling: {acc_al_history[-1]*100:.1f}%")
print(f"  Margin sampling:      {acc_margin_history[-1]*100:.1f}%")
print(f"  Random sampling:      {acc_random_history[-1]*100:.1f}%")
print(f"  Gain over random:     {(acc_al_history[-1] - acc_random_history[-1])*100:.1f} percentage points")
print("\nActive learning:")
print("  - Model selects which examples to label")
print("  - Uncertainty sampling focuses on decision boundary")
print("  - Margin sampling picks examples where top-2 classes tie")
print("  - Pool-based: evaluate all unlabeled, pick best batch")
print("  - Can achieve same accuracy with 30-50% fewer labels")
print("\nApplications: medical labeling, legal annotation, scientific curation")
