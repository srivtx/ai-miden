#!/usr/bin/env python3
"""
Phase 59: Federated Learning — NumPy Concept Demo
===================================================
This script demonstrates how models learn from decentralized data
without sharing raw data.

Key insight: Multiple clients train locally, then a central server
averages their model updates. No client ever sees another's data.

Concepts demonstrated:
  - Federated learning with local training
  - Federated averaging (FedAvg)
  - Non-IID data effects
  - Differential privacy (gradient clipping + noise)
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(59)

# =============================================================================
# SECTION 1: GLOBAL DATASET (simulated)
# =============================================================================
# True model: y = 2x + 1

n_total = 500
X_all = np.linspace(0, 5, n_total)
y_all = 2.0 * X_all + 1.0 + np.random.normal(0, 0.5, n_total)

print("="*60)
print("Phase 59: Federated Learning")
print("="*60)
print(f"\nTrue model: y = 2x + 1")
print(f"Total data: {n_total} samples")

# =============================================================================
# SECTION 2: DISTRIBUTE DATA TO 5 CLIENTS (Non-IID)
# =============================================================================
# Each client gets a different slice of the x-range (feature skew)

n_clients = 5
client_data = []

for i in range(n_clients):
    start = i * (n_total // n_clients)
    end = start + (n_total // n_clients)
    X_client = X_all[start:end]
    y_client = y_all[start:end]
    client_data.append((X_client, y_client))
    print(f"  Client {i}: x range [{X_client[0]:.1f}, {X_client[-1]:.1f}], {len(X_client)} samples")

# =============================================================================
# SECTION 3: CENTRALIZED BASELINE
# =============================================================================
# Train a single model on all data (the ideal we compare against)

w_central = np.array([0.0, 0.0])  # [slope, intercept]
lr = 0.01
for epoch in range(200):
    pred = w_central[0] * X_all + w_central[1]
    grad_w = (2.0 / n_total) * np.sum((pred - y_all) * X_all)
    grad_b = (2.0 / n_total) * np.sum(pred - y_all)
    w_central[0] -= lr * grad_w
    w_central[1] -= lr * grad_b

print(f"\n--- Centralized Baseline ---")
print(f"Slope: {w_central[0]:.3f}, Intercept: {w_central[1]:.3f}")

# =============================================================================
# SECTION 4: FEDERATED LEARNING (FedAvg)
# =============================================================================

def local_train(X, y, w_global, epochs=20):
    """Train on local data starting from global model."""
    w = w_global.copy()
    n = len(X)
    for _ in range(epochs):
        pred = w[0] * X + w[1]
        grad_w = (2.0 / n) * np.sum((pred - y) * X)
        grad_b = (2.0 / n) * np.sum(pred - y)
        w[0] -= lr * grad_w
        w[1] -= lr * grad_b
    return w

# Federated averaging rounds
n_rounds = 30
w_global = np.array([0.0, 0.0])
fedavg_history = [w_global.copy()]

for r in range(n_rounds):
    local_updates = []
    local_sizes = []
    
    for X_c, y_c in client_data:
        w_local = local_train(X_c, y_c, w_global, epochs=10)
        local_updates.append(w_local)
        local_sizes.append(len(X_c))
    
    # FedAvg: weighted average by data size
    total_size = sum(local_sizes)
    w_global = np.zeros(2)
    for w_local, size in zip(local_updates, local_sizes):
        w_global += (size / total_size) * w_local
    
    fedavg_history.append(w_global.copy())

fedavg_history = np.array(fedavg_history)
print(f"\n--- Federated Learning (FedAvg) ---")
print(f"After {n_rounds} rounds:")
print(f"Slope: {w_global[0]:.3f}, Intercept: {w_global[1]:.3f}")

# =============================================================================
# SECTION 5: DIFFERENTIAL PRIVACY VERSION
# =============================================================================
# Clip gradients and add noise

clip_bound = 1.0
noise_std = 0.3

w_global_dp = np.array([0.0, 0.0])
fedavg_dp_history = [w_global_dp.copy()]

for r in range(n_rounds):
    local_updates = []
    local_sizes = []
    
    for X_c, y_c in client_data:
        w_local = local_train(X_c, y_c, w_global_dp, epochs=10)
        # Compute update delta
        delta = w_local - w_global_dp
        # Clip
        norm = np.linalg.norm(delta)
        if norm > clip_bound:
            delta = delta * (clip_bound / norm)
        # Add noise
        delta += np.random.normal(0, noise_std, 2)
        local_updates.append(w_global_dp + delta)
        local_sizes.append(len(X_c))
    
    total_size = sum(local_sizes)
    w_global_dp = np.zeros(2)
    for w_local, size in zip(local_updates, local_sizes):
        w_global_dp += (size / total_size) * w_local
    
    fedavg_dp_history.append(w_global_dp.copy())

fedavg_dp_history = np.array(fedavg_dp_history)
print(f"\n--- Federated Learning with Differential Privacy ---")
print(f"After {n_rounds} rounds:")
print(f"Slope: {w_global_dp[0]:.3f}, Intercept: {w_global_dp[1]:.3f}")

# =============================================================================
# SECTION 6: COMPARISON
# =============================================================================

# Final MSE on global test set
X_test = np.linspace(0, 5, 100)
y_test = 2.0 * X_test + 1.0

def mse(w, X, y):
    pred = w[0] * X + w[1]
    return np.mean((pred - y) ** 2)

mse_central = mse(w_central, X_test, y_test)
mse_fed = mse(w_global, X_test, y_test)
mse_fed_dp = mse(w_global_dp, X_test, y_test)

print(f"\n--- Final Test MSE ---")
print(f"Centralized:     {mse_central:.4f}")
print(f"FedAvg:          {mse_fed:.4f}")
print(f"FedAvg + DP:     {mse_fed_dp:.4f}")

# =============================================================================
# SECTION 7: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Client data distributions
ax = axes[0, 0]
colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
for i, (X_c, y_c) in enumerate(client_data):
    ax.scatter(X_c, y_c, c=colors[i], alpha=0.5, s=20, label=f'Client {i}')
ax.plot(X_all, 2*X_all + 1, 'k--', linewidth=2, label='True: y=2x+1')
ax.set_title('Non-IID Data Distribution Across Clients')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Convergence of slope
ax = axes[0, 1]
ax.axhline(y=2.0, color='black', linestyle='--', linewidth=2, label='True slope = 2.0')
ax.plot(fedavg_history[:, 0], 'b-', linewidth=2, label='FedAvg')
ax.plot(fedavg_dp_history[:, 0], 'r-', linewidth=2, label='FedAvg + DP')
ax.set_title('Convergence: Slope Parameter')
ax.set_xlabel('Round')
ax.set_ylabel('Slope')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Convergence of intercept
ax = axes[1, 0]
ax.axhline(y=1.0, color='black', linestyle='--', linewidth=2, label='True intercept = 1.0')
ax.plot(fedavg_history[:, 1], 'b-', linewidth=2, label='FedAvg')
ax.plot(fedavg_dp_history[:, 1], 'r-', linewidth=2, label='FedAvg + DP')
ax.set_title('Convergence: Intercept Parameter')
ax.set_xlabel('Round')
ax.set_ylabel('Intercept')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Test MSE comparison
ax = axes[1, 1]
categories = ['Centralized', 'FedAvg', 'FedAvg + DP']
mse_values = [mse_central, mse_fed, mse_fed_dp]
bars = ax.bar(categories, mse_values, color=['#2ecc71', '#3498db', '#e74c3c'], 
              edgecolor='black', alpha=0.8)
ax.set_title('Test MSE Comparison')
ax.set_ylabel('Mean Squared Error')
for bar, val in zip(bars, mse_values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f'{val:.3f}', ha='center', va='bottom', fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
os.makedirs('src/phase59', exist_ok=True)
plt.savefig('src/phase59/federated_learning.png', dpi=150)
print("\nSaved plot to src/phase59/federated_learning.png")

# =============================================================================
# SECTION 8: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Centralized:     slope={w_central[0]:.3f}, intercept={w_central[1]:.3f}, MSE={mse_central:.4f}")
print(f"FedAvg:          slope={w_global[0]:.3f}, intercept={w_global[1]:.3f}, MSE={mse_fed:.4f}")
print(f"FedAvg + DP:     slope={w_global_dp[0]:.3f}, intercept={w_global_dp[1]:.3f}, MSE={mse_fed_dp:.4f}")
print("\nFederated learning:")
print("  - Clients train locally on private data")
print("  - Server averages model updates (FedAvg)")
print("  - Non-IID data slows convergence")
print("  - Differential privacy adds noise for formal guarantees")
print("  - Trade-off: privacy vs. model accuracy")
print("\nApplications: medical AI, mobile keyboards, IoT, finance")
