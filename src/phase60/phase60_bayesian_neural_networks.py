#!/usr/bin/env python3
"""
Phase 60: Bayesian Neural Networks — NumPy Concept Demo
=========================================================
This script demonstrates how to quantify uncertainty in model
predictions using Bayesian methods.

Key insight: A standard neural network is overconfident. A Bayesian
neural network knows when it is guessing, which is critical for
safety-critical applications.

Concepts demonstrated:
  - Bayesian linear regression (exact posterior)
  - Monte Carlo Dropout for uncertainty estimation
  - Epistemic vs. aleatoric uncertainty
  - Out-of-distribution detection via uncertainty
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(60)

# =============================================================================
# SECTION 1: TRAINING DATA (nonlinear function with noise)
# =============================================================================
# True function: y = sin(x) + 0.1x, with Gaussian noise

n_train = 30
X_train = np.sort(np.random.uniform(-3, 3, n_train))
y_train = np.sin(X_train) + 0.1 * X_train + np.random.normal(0, 0.2, n_train)

print("="*60)
print("Phase 60: Bayesian Neural Networks")
print("="*60)
print(f"\nTraining data: {n_train} points")
print(f"True function: y = sin(x) + 0.1x + noise(σ=0.2)")

# =============================================================================
# SECTION 2: BAYESIAN LINEAR REGRESSION (exact posterior)
# =============================================================================
# We use a polynomial basis: [1, x, x^2, x^3]
# Bayesian update: posterior precision = prior precision + data precision

def design_matrix(X):
    return np.column_stack([np.ones(len(X)), X, X**2, X**3])

Phi = design_matrix(X_train)
y = y_train.reshape(-1, 1)

# Prior: p(w) = N(0, αI)
alpha = 1.0  # prior precision
beta = 25.0  # likelihood precision (1/noise_variance)

# Posterior: p(w|D) = N(μ_n, Σ_n)
# Σ_n = (αI + βΦ^TΦ)^{-1}
# μ_n = βΣ_n Φ^T y

Sigma_inv = alpha * np.eye(4) + beta * Phi.T @ Phi
Sigma = np.linalg.inv(Sigma_inv)
mu = beta * Sigma @ Phi.T @ y

print(f"\n--- Bayesian Linear Regression ---")
print(f"Posterior mean weights: {mu.flatten()}")
print(f"Posterior covariance diagonal: {np.diag(Sigma)}")

# Predict with uncertainty
X_test = np.linspace(-6, 6, 200)
Phi_test = design_matrix(X_test)

# Mean prediction
y_mean = (Phi_test @ mu).flatten()

# Predictive variance: var = 1/β + Φ_test Σ Φ_test^T
y_var = []
for i in range(len(X_test)):
    phi = Phi_test[i:i+1]  # (1, 4)
    var = 1.0/beta + phi @ Sigma @ phi.T
    y_var.append(var[0, 0])
y_var = np.array(y_var)
y_std = np.sqrt(y_var)

# =============================================================================
# SECTION 3: MONTE CARLO DROPOUT APPROXIMATION
# =============================================================================
# Train a small MLP with dropout, then run multiple forward passes
# at inference time to estimate uncertainty.

# Train a simple 1-hidden-layer network with dropout
n_hidden = 20
dropout_rate = 0.2

W1_mcd = np.random.randn(1, n_hidden) * 0.5
b1_mcd = np.zeros(n_hidden)
W2_mcd = np.random.randn(n_hidden, 1) * 0.3
b2_mcd = np.zeros(1)

def relu(x):
    return np.maximum(x, 0)

def forward_mcd(x, training=True):
    z1 = x @ W1_mcd + b1_mcd
    h = relu(z1)
    if training:
        mask = (np.random.rand(*h.shape) > dropout_rate).astype(float)
        h = h * mask / (1 - dropout_rate)
    z2 = h @ W2_mcd + b2_mcd
    return z2.flatten()

# Train
lr = 0.01
for epoch in range(3000):
    # Forward with dropout
    z1 = X_train.reshape(-1, 1) @ W1_mcd + b1_mcd
    h = relu(z1)
    mask = (np.random.rand(*h.shape) > dropout_rate).astype(float)
    h_drop = h * mask / (1 - dropout_rate)
    pred = h_drop @ W2_mcd + b2_mcd
    
    # MSE loss
    loss_grad = (2.0 / n_train) * (pred.flatten() - y_train)
    
    # Backprop
    dW2 = h_drop.T @ loss_grad.reshape(-1, 1)
    db2 = np.sum(loss_grad)
    dh = loss_grad.reshape(-1, 1) @ W2_mcd.T
    dh = dh * mask / (1 - dropout_rate)
    dz1 = dh * (z1 > 0).astype(float)
    dW1 = X_train.reshape(-1, 1).T @ dz1
    db1 = np.sum(dz1, axis=0)
    
    W2_mcd -= lr * dW2
    b2_mcd -= lr * db2
    W1_mcd -= lr * dW1
    b1_mcd -= lr * db1

# MC Dropout inference (T samples)
T = 50
mcd_predictions = []
for _ in range(T):
    pred = forward_mcd(X_test.reshape(-1, 1), training=True)
    mcd_predictions.append(pred)

mcd_predictions = np.array(mcd_predictions)
mcd_mean = np.mean(mcd_predictions, axis=0)
mcd_std = np.std(mcd_predictions, axis=0)

print(f"\n--- Monte Carlo Dropout ---")
print(f"In-distribution uncertainty (|x|<3): {mcd_std[np.abs(X_test)<3].mean():.3f}")
print(f"Out-of-distribution uncertainty (|x|>4): {mcd_std[np.abs(X_test)>4].mean():.3f}")

# =============================================================================
# SECTION 4: STANDARD NEURAL NETWORK (no uncertainty)
# =============================================================================

# Same architecture, no dropout
W1_std = np.random.randn(1, n_hidden) * 0.5
b1_std = np.zeros(n_hidden)
W2_std = np.random.randn(n_hidden, 1) * 0.3
b2_std = np.zeros(1)

for epoch in range(3000):
    z1 = X_train.reshape(-1, 1) @ W1_std + b1_std
    h = relu(z1)
    pred = h @ W2_std + b2_std
    
    loss_grad = (2.0 / n_train) * (pred.flatten() - y_train)
    
    dW2 = h.T @ loss_grad.reshape(-1, 1)
    db2 = np.sum(loss_grad)
    dh = loss_grad.reshape(-1, 1) @ W2_std.T
    dz1 = dh * (z1 > 0).astype(float)
    dW1 = X_train.reshape(-1, 1).T @ dz1
    db1 = np.sum(dz1, axis=0)
    
    W2_std -= lr * dW2
    b2_std -= lr * db2
    W1_std -= lr * dW1
    b1_std -= lr * db1

# Standard prediction (single forward pass)
z1_std = X_test.reshape(-1, 1) @ W1_std + b1_std
h_std = relu(z1_std)
std_pred = (h_std @ W2_std + b2_std).flatten()

# =============================================================================
# SECTION 5: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Bayesian Linear Regression with uncertainty
ax = axes[0, 0]
ax.scatter(X_train, y_train, c='red', s=50, zorder=5, label='Training data')
ax.plot(X_test, np.sin(X_test) + 0.1*X_test, 'g--', linewidth=2, label='True function', alpha=0.7)
ax.plot(X_test, y_mean, 'b-', linewidth=2, label='Posterior mean')
ax.fill_between(X_test, y_mean - 2*y_std, y_mean + 2*y_std, alpha=0.3, color='blue', label='95% credible interval')
ax.axvline(x=3, color='gray', linestyle=':', alpha=0.5)
ax.axvline(x=-3, color='gray', linestyle=':', alpha=0.5)
ax.set_title('Bayesian Linear Regression: Uncertainty Grows Far from Data')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: MC Dropout uncertainty
ax = axes[0, 1]
ax.scatter(X_train, y_train, c='red', s=50, zorder=5, label='Training data')
ax.plot(X_test, np.sin(X_test) + 0.1*X_test, 'g--', linewidth=2, label='True function', alpha=0.7)
ax.plot(X_test, mcd_mean, 'b-', linewidth=2, label='MC Dropout mean')
ax.fill_between(X_test, mcd_mean - 2*mcd_std, mcd_mean + 2*mcd_std, alpha=0.3, color='blue', label='95% uncertainty')
ax.axvline(x=3, color='gray', linestyle=':', alpha=0.5)
ax.axvline(x=-3, color='gray', linestyle=':', alpha=0.5)
ax.set_title('Monte Carlo Dropout: Uncertainty in Unseen Regions')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Comparison of all methods
ax = axes[1, 0]
ax.scatter(X_train, y_train, c='red', s=50, zorder=5, label='Training data')
ax.plot(X_test, std_pred, 'k-', linewidth=2, label='Standard NN (no uncertainty)')
ax.plot(X_test, mcd_mean, 'b-', linewidth=2, label='MC Dropout')
ax.plot(X_test, y_mean, 'm-', linewidth=2, label='Bayesian LR')
ax.set_title('Model Comparison: Standard vs. Bayesian')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Uncertainty magnitude comparison
ax = axes[1, 1]
in_dist_mask = np.abs(X_test) <= 3
ood_mask = np.abs(X_test) > 4

ax.bar(['In-Distribution\nBayesian', 'Out-of-Distribution\nBayesian'],
       [y_std[in_dist_mask].mean(), y_std[ood_mask].mean()],
       color=['#3498db', '#e74c3c'], alpha=0.7, edgecolor='black', width=0.4)
ax.bar(['In-Distribution\nMC Dropout', 'Out-of-Distribution\nMC Dropout'],
       [mcd_std[in_dist_mask].mean(), mcd_std[ood_mask].mean()],
       color=['#2ecc71', '#f39c12'], alpha=0.7, edgecolor='black', width=0.4)
ax.set_title('Uncertainty: In-Distribution vs. Out-of-Distribution')
ax.set_ylabel('Mean Standard Deviation')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
os.makedirs('src/phase60', exist_ok=True)
plt.savefig('src/phase60/bayesian_neural_networks.png', dpi=150)
print("\nSaved plot to src/phase60/bayesian_neural_networks.png")

# =============================================================================
# SECTION 6: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Bayesian LR in-dist uncertainty:  {y_std[in_dist_mask].mean():.3f}")
print(f"Bayesian LR OOD uncertainty:      {y_std[ood_mask].mean():.3f}")
print(f"MC Dropout in-dist uncertainty:   {mcd_std[in_dist_mask].mean():.3f}")
print(f"MC Dropout OOD uncertainty:       {mcd_std[ood_mask].mean():.3f}")
print("\nBayesian neural networks quantify uncertainty:")
print("  - Standard NNs are overconfident everywhere")
print("  - Bayesian LR has exact posterior, uncertainty grows away from data")
print("  - MC Dropout approximates Bayesian inference with any dropout network")
print("  - Epistemic uncertainty is high where data is scarce")
print("  - Aleatoric uncertainty is constant (data noise)")
print("\nApplications: medical diagnosis, autonomous driving, scientific discovery")
