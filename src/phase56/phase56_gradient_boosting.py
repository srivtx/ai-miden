#!/usr/bin/env python3
"""
Phase 56: Gradient Boosting — NumPy Concept Demo
==================================================
This script demonstrates ensemble learning: combining many weak
models into one strong predictor.

Key insight: A single weak model is useless. But many weak models,
each fixing the errors of the previous ones, can match or beat
a single complex model.

Concepts demonstrated:
  - Ensemble learning (bagging and boosting)
  - Gradient boosting on regression (sequential residual fitting)
  - AdaBoost-style reweighting on classification
  - Regularized leaf weights (XGBoost-style)
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(56)

# =============================================================================
# SECTION 1: SYNTHETIC REGRESSION DATA (nonlinear)
# =============================================================================
# True function: y = sin(2x) + 0.5x

n_samples = 40
X = np.linspace(0, 3, n_samples)
y_true = np.sin(2 * X) + 0.5 * X
y_noisy = y_true + np.random.normal(0, 0.2, n_samples)

print("="*60)
print("Phase 56: Gradient Boosting")
print("="*60)
print(f"\nDataset: {n_samples} samples")
print(f"True function: y = sin(2x) + 0.5x")

# =============================================================================
# SECTION 2: DECISION STUMP (weak learner)
# =============================================================================
# A stump is a tree with exactly 1 split (2 leaves).
# It is weak but fast, and boosting makes it strong.

def train_stump(X, y, weights=None):
    """Find the best split point that minimizes squared error."""
    best_loss = float('inf')
    best_split = None
    best_left_val = None
    best_right_val = None
    
    if weights is None:
        weights = np.ones(len(y)) / len(y)
    
    # Try every possible split point between consecutive unique x values
    sorted_indices = np.argsort(X)
    X_sorted = X[sorted_indices]
    y_sorted = y[sorted_indices]
    w_sorted = weights[sorted_indices]
    
    for i in range(1, len(X_sorted)):
        split = (X_sorted[i-1] + X_sorted[i]) / 2
        
        left_mask = X_sorted <= split
        right_mask = ~left_mask
        
        if left_mask.sum() == 0 or right_mask.sum() == 0:
            continue
        
        left_val = np.average(y_sorted[left_mask], weights=w_sorted[left_mask])
        right_val = np.average(y_sorted[right_mask], weights=w_sorted[right_mask])
        
        # Weighted MSE
        left_loss = np.sum(w_sorted[left_mask] * (y_sorted[left_mask] - left_val) ** 2)
        right_loss = np.sum(w_sorted[right_mask] * (y_sorted[right_mask] - right_val) ** 2)
        loss = left_loss + right_loss
        
        if loss < best_loss:
            best_loss = loss
            best_split = split
            best_left_val = left_val
            best_right_val = right_val
    
    return best_split, best_left_val, best_right_val

def predict_stump(X, split, left_val, right_val):
    """Predict using a trained stump."""
    return np.where(X <= split, left_val, right_val)

# =============================================================================
# SECTION 3: GRADIENT BOOSTING (Regression)
# =============================================================================

print("\n--- Gradient Boosting (Regression) ---")

n_rounds = 20
learning_rate = 0.3

# Initial prediction: mean of y
F = np.full(n_samples, np.mean(y_noisy))
residuals = y_noisy - F

print(f"Initial prediction (mean): {F[0]:.3f}")
print(f"Initial MSE: {np.mean(residuals**2):.3f}")

stumps = []
history = [F.copy()]
mse_history = [np.mean(residuals**2)]

for round_idx in range(n_rounds):
    # Train stump on residuals
    split, left_val, right_val = train_stump(X, residuals)
    stumps.append((split, left_val, right_val))
    
    # Predict residuals
    pred_residuals = predict_stump(X, split, left_val, right_val)
    
    # Update ensemble prediction
    F += learning_rate * pred_residuals
    residuals = y_noisy - F
    
    history.append(F.copy())
    mse = np.mean(residuals**2)
    mse_history.append(mse)
    
    if round_idx < 3 or round_idx == n_rounds - 1:
        print(f"  Round {round_idx+1}: MSE = {mse:.4f}")

print(f"\nFinal MSE after {n_rounds} rounds: {mse_history[-1]:.4f}")
print(f"Improvement: {mse_history[0]:.4f} → {mse_history[-1]:.4f}")

# =============================================================================
# SECTION 4: REGULARIZED LEAF WEIGHTS (XGBoost-style)
# =============================================================================
# Instead of using the raw mean residual as leaf value,
# shrink it by (n + lambda) to regularize.

print("\n--- XGBoost-Style Regularized Leaves ---")

def train_stump_regularized(X, y, weights=None, lam=2.0):
    """Train stump with L2 regularization on leaf weights."""
    best_loss = float('inf')
    best_split = None
    best_left_val = None
    best_right_val = None
    
    if weights is None:
        weights = np.ones(len(y)) / len(y)
    
    sorted_indices = np.argsort(X)
    X_sorted = X[sorted_indices]
    y_sorted = y[sorted_indices]
    w_sorted = weights[sorted_indices]
    
    for i in range(1, len(X_sorted)):
        split = (X_sorted[i-1] + X_sorted[i]) / 2
        left_mask = X_sorted <= split
        right_mask = ~left_mask
        
        if left_mask.sum() == 0 or right_mask.sum() == 0:
            continue
        
        # Regularized leaf values: sum / (count + lambda)
        left_val = np.sum(w_sorted[left_mask] * y_sorted[left_mask]) / (np.sum(w_sorted[left_mask]) + lam)
        right_val = np.sum(w_sorted[right_mask] * y_sorted[right_mask]) / (np.sum(w_sorted[right_mask]) + lam)
        
        left_loss = np.sum(w_sorted[left_mask] * (y_sorted[left_mask] - left_val) ** 2)
        right_loss = np.sum(w_sorted[right_mask] * (y_sorted[right_mask] - right_val) ** 2)
        loss = left_loss + right_loss
        
        if loss < best_loss:
            best_loss = loss
            best_split = split
            best_left_val = left_val
            best_right_val = right_val
    
    return best_split, best_left_val, best_right_val

F_reg = np.full(n_samples, np.mean(y_noisy))
residuals_reg = y_noisy - F_reg
mse_reg_history = [np.mean(residuals_reg**2)]

for round_idx in range(n_rounds):
    split, left_val, right_val = train_stump_regularized(X, residuals_reg, lam=2.0)
    pred_residuals = predict_stump(X, split, left_val, right_val)
    F_reg += learning_rate * pred_residuals
    residuals_reg = y_noisy - F_reg
    mse_reg_history.append(np.mean(residuals_reg**2))

print(f"Regularized final MSE: {mse_reg_history[-1]:.4f}")
print(f"Unregularized final MSE: {mse_history[-1]:.4f}")
print(f"Regularization prevents overfitting on noise.")

# =============================================================================
# SECTION 5: ADABOOST (Classification)
# =============================================================================
# Demonstrate adaptive reweighting on a simple 1D binary problem.

print("\n--- AdaBoost (Classification) ---")

# Binary data: positive if y > median, negative otherwise
median_y = np.median(y_noisy)
labels = (y_noisy > median_y).astype(int) * 2 - 1  # -1 or +1

# Weak stumps: predict +1 if x > threshold, else -1
thresholds = X.copy()
weights = np.ones(n_samples) / n_samples

adaboost_stumps = []
alphas = []

for t in range(10):
    best_error = float('inf')
    best_thresh = None
    best_direction = None
    
    for thresh in thresholds:
        for direction in [1, -1]:
            preds = np.where(X > thresh, direction, -direction)
            error = np.sum(weights * (preds != labels))
            if error < best_error:
                best_error = error
                best_thresh = thresh
                best_direction = direction
    
    # Edge case: error = 0 or error >= 0.5
    if best_error >= 0.5 or best_error == 0:
        break
    
    alpha = 0.5 * np.log((1 - best_error) / max(best_error, 1e-10))
    alphas.append(alpha)
    adaboost_stumps.append((best_thresh, best_direction))
    
    preds = np.where(X > best_thresh, best_direction, -best_direction)
    
    # Update weights
    weights *= np.exp(-alpha * labels * preds)
    weights /= np.sum(weights)
    
    # Compute ensemble accuracy
    ensemble_pred = np.zeros(n_samples)
    for a, (thresh, direction) in zip(alphas, adaboost_stumps):
        ensemble_pred += a * np.where(X > thresh, direction, -direction)
    ensemble_pred = np.sign(ensemble_pred)
    acc = np.mean(ensemble_pred == labels)
    
    print(f"  Round {t+1}: error={best_error:.3f}, alpha={alpha:.3f}, accuracy={acc:.1%}")

print(f"\nFinal AdaBoost accuracy: {acc:.1%}")

# =============================================================================
# SECTION 6: ENSEMBLE COMPARISON
# =============================================================================
# Compare: single stump vs gradient boosting vs regularized boosting

print("\n--- Ensemble Comparison ---")

# Single best stump
split_single, left_single, right_single = train_stump(X, y_noisy)
pred_single = predict_stump(X, split_single, left_single, right_single)
mse_single = np.mean((pred_single - y_noisy)**2)

print(f"Single stump MSE:       {mse_single:.4f}")
print(f"Gradient boosting MSE:  {mse_history[-1]:.4f}")
print(f"Regularized boost MSE:  {mse_reg_history[-1]:.4f}")

# =============================================================================
# SECTION 7: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Gradient boosting progression
ax = axes[0, 0]
X_plot = np.linspace(0, 3, 200)
ax.scatter(X, y_noisy, c='gray', alpha=0.5, s=30, label='Data')
ax.plot(X, y_true, 'k--', linewidth=2, label='True function')

# Show predictions at rounds 0, 1, 5, 20
def predict_ensemble(X_test, stumps, lr, initial_mean):
    F = np.full(len(X_test), initial_mean)
    for split, left, right in stumps:
        F += lr * np.where(X_test <= split, left, right)
    return F

for round_idx in [0, 1, 5, n_rounds]:
    if round_idx == 0:
        pred = np.full(len(X_plot), np.mean(y_noisy))
        ax.plot(X_plot, pred, alpha=0.5, label=f'Round 0 (mean)')
    else:
        pred = predict_ensemble(X_plot, stumps[:round_idx], learning_rate, np.mean(y_noisy))
        ax.plot(X_plot, pred, alpha=0.7, label=f'Round {round_idx}')

ax.set_title('Gradient Boosting: Predictions Over Rounds')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: MSE over rounds
ax = axes[0, 1]
rounds = list(range(n_rounds + 1))
ax.plot(rounds, mse_history, 'b-', marker='o', label='Standard', linewidth=2)
ax.plot(rounds, mse_reg_history, 'r-', marker='s', label='Regularized (λ=2)', linewidth=2)
ax.axhline(y=mse_single, color='gray', linestyle='--', label='Single stump')
ax.set_title('MSE Decrease Over Boosting Rounds')
ax.set_xlabel('Round')
ax.set_ylabel('Mean Squared Error')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_yscale('log')

# Plot 3: AdaBoost weights evolution
ax = axes[1, 0]
ax.bar(range(n_samples), weights, color='#3498db', edgecolor='black', alpha=0.7)
ax.set_title('AdaBoost: Final Example Weights')
ax.set_xlabel('Example Index')
ax.set_ylabel('Weight')
ax.grid(True, alpha=0.3)

# Plot 4: Bagging vs Boosting concept
ax = axes[1, 1]
# Simulate bagging: average of 5 noisy predictors
x_demo = np.linspace(0, 3, 100)
base = np.sin(2 * x_demo) + 0.5 * x_demo
bagged = np.zeros_like(x_demo)
for _ in range(5):
    noise = np.random.normal(0, 0.5, len(x_demo))
    bagged += (base + noise)
bagged /= 5

ax.plot(x_demo, base, 'k--', linewidth=2, label='True function')
ax.plot(x_demo, base + np.random.normal(0, 0.5, len(x_demo)), 'gray', alpha=0.3, label='Single noisy model')
ax.plot(x_demo, bagged, 'b-', linewidth=2, label='Bagging (average of 5)')
ax.set_title('Bagging: Errors Cancel Out')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
os.makedirs('src/phase56', exist_ok=True)
plt.savefig('src/phase56/gradient_boosting.png', dpi=150)
print("\nSaved plot to src/phase56/gradient_boosting.png")

# =============================================================================
# SECTION 8: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Single stump MSE:       {mse_single:.4f}")
print(f"Gradient boosting MSE:  {mse_history[-1]:.4f}")
print(f"Regularized boost MSE:  {mse_reg_history[-1]:.4f}")
print(f"AdaBoost accuracy:      {acc:.1%}")
print("\nEnsemble learning combines weak models into strong predictors:")
print("  - Bagging: train independent models, average predictions")
print("  - Boosting: train sequentially, each fixes previous errors")
print("  - Regularization: shrink leaf weights to prevent overfitting")
print("  - AdaBoost: reweight examples, weighted majority vote")
print("\nGradient boosting dominates tabular data.")
print("XGBoost adds regularization, speed, and scalability.")
