#!/usr/bin/env python3
"""
Phase 61: AutoML & Hyperparameter Search — NumPy Concept Demo
===============================================================
This script demonstrates how to automatically find good model
configurations without manual trial and error.

Key insight: Searching hyperparameters randomly or intelligently
beats guessing. Successive halving kills bad configs early.

Concepts demonstrated:
  - Grid search vs. random search
  - Bayesian optimization concept
  - Successive halving (Hyperband)
  - Architecture search over layer sizes
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(61)

# =============================================================================
# SECTION 1: SYNTHETIC TASK
# =============================================================================
# True function: y = sin(2x) + 0.5x, predict from x

n_train = 50
X_train = np.linspace(0, 3, n_train)
y_train = np.sin(2 * X_train) + 0.5 * X_train + np.random.normal(0, 0.2, n_train)

print("="*60)
print("Phase 61: AutoML & Hyperparameter Search")
print("="*60)
print(f"\nTask: predict y = sin(2x) + 0.5x + noise")
print(f"Training samples: {n_train}")

# =============================================================================
# SECTION 2: TRAIN FUNCTION (for different configs)
# =============================================================================

def train_and_eval(hidden_size, lr, n_epochs=100):
    """Train a small MLP, return validation MSE."""
    np.random.seed(42)  # fixed init for fair comparison
    W1 = np.random.randn(1, hidden_size) * 0.5
    b1 = np.zeros(hidden_size)
    W2 = np.random.randn(hidden_size, 1) * 0.3
    b2 = np.zeros(1)
    
    # Train
    for _ in range(n_epochs):
        z1 = X_train.reshape(-1, 1) @ W1 + b1
        h = np.maximum(z1, 0)
        pred = h @ W2 + b2
        
        grad = (2.0 / n_train) * (pred.flatten() - y_train)
        
        dW2 = h.T @ grad.reshape(-1, 1)
        db2 = np.sum(grad)
        dh = grad.reshape(-1, 1) @ W2.T
        dz1 = dh * (z1 > 0).astype(float)
        dW1 = X_train.reshape(-1, 1).T @ dz1
        db1 = np.sum(dz1, axis=0)
        
        W2 -= lr * dW2
        b2 -= lr * db2
        W1 -= lr * dW1
        b1 -= lr * db1
    
    # Validation (same data for simplicity)
    z1 = X_train.reshape(-1, 1) @ W1 + b1
    h = np.maximum(z1, 0)
    pred = h @ W2 + b2
    mse = np.mean((pred.flatten() - y_train) ** 2)
    return mse

# =============================================================================
# SECTION 3: GRID SEARCH
# =============================================================================

print("\n--- Grid Search ---")
hidden_sizes = [4, 8, 16]
learning_rates = [0.001, 0.01, 0.1]

grid_results = []
for h in hidden_sizes:
    for lr in learning_rates:
        mse = train_and_eval(h, lr, n_epochs=100)
        grid_results.append((h, lr, mse))
        print(f"  hidden={h:2d}, lr={lr:.3f}: MSE={mse:.4f}")

best_grid = min(grid_results, key=lambda x: x[2])
print(f"\nBest grid config: hidden={best_grid[0]}, lr={best_grid[1]:.3f}, MSE={best_grid[2]:.4f}")

# =============================================================================
# SECTION 4: RANDOM SEARCH
# =============================================================================

print("\n--- Random Search (6 trials) ---")

random_results = []
for _ in range(6):
    h = np.random.choice([2, 4, 8, 16, 32])
    lr = 10 ** np.random.uniform(-3, -1)  # log-uniform [0.001, 0.1]
    mse = train_and_eval(h, lr, n_epochs=100)
    random_results.append((h, lr, mse))
    print(f"  hidden={h:2d}, lr={lr:.4f}: MSE={mse:.4f}")

best_random = min(random_results, key=lambda x: x[2])
print(f"\nBest random config: hidden={best_random[0]}, lr={best_random[1]:.4f}, MSE={best_random[2]:.4f}")

# =============================================================================
# SECTION 5: SUCCESSIVE HALVING (Hyperband concept)
# =============================================================================

print("\n--- Successive Halving ---")

# Start with 8 random configs, train for 10 epochs, keep top 4
# Then train top 4 for 30 epochs, keep top 2
# Then train top 2 for 100 epochs, keep best

configs = []
for _ in range(8):
    h = np.random.choice([2, 4, 8, 16, 32])
    lr = 10 ** np.random.uniform(-3, -1)
    configs.append((h, lr))

# Round 1: 10 epochs
print("Round 1 (10 epochs, 8 configs):")
results_r1 = []
for h, lr in configs:
    mse = train_and_eval(h, lr, n_epochs=10)
    results_r1.append((h, lr, mse))
    print(f"  hidden={h:2d}, lr={lr:.4f}: MSE={mse:.4f}")

results_r1.sort(key=lambda x: x[2])
top4 = results_r1[:4]

# Round 2: 30 epochs
print("\nRound 2 (30 epochs, top 4):")
results_r2 = []
for h, lr, _ in top4:
    mse = train_and_eval(h, lr, n_epochs=30)
    results_r2.append((h, lr, mse))
    print(f"  hidden={h:2d}, lr={lr:.4f}: MSE={mse:.4f}")

results_r2.sort(key=lambda x: x[2])
top2 = results_r2[:2]

# Round 3: 100 epochs
print("\nRound 3 (100 epochs, top 2):")
results_r3 = []
for h, lr, _ in top2:
    mse = train_and_eval(h, lr, n_epochs=100)
    results_r3.append((h, lr, mse))
    print(f"  hidden={h:2d}, lr={lr:.4f}: MSE={mse:.4f}")

best_halving = min(results_r3, key=lambda x: x[2])
print(f"\nBest halving config: hidden={best_halving[0]}, lr={best_halving[1]:.4f}, MSE={best_halving[2]:.4f}")

# Compute total epochs
epochs_grid = len(grid_results) * 100
epochs_random = len(random_results) * 100
epochs_halving = 8*10 + 4*30 + 2*100

print(f"\nTotal epochs:")
print(f"  Grid search:        {epochs_grid}")
print(f"  Random search:      {epochs_random}")
print(f"  Successive halving: {epochs_halving}")

# =============================================================================
# SECTION 6: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Grid search heatmap
ax = axes[0, 0]
grid_mse = np.array([[r[2] for r in grid_results if r[0] == h] for h in hidden_sizes])
im = ax.imshow(grid_mse, cmap='YlGn_r', aspect='auto')
ax.set_xticks(range(len(learning_rates)))
ax.set_xticklabels([f'{lr:.3f}' for lr in learning_rates])
ax.set_yticks(range(len(hidden_sizes)))
ax.set_yticklabels([f'{h}' for h in hidden_sizes])
ax.set_xlabel('Learning Rate')
ax.set_ylabel('Hidden Size')
ax.set_title('Grid Search: MSE Heatmap')
for i in range(len(hidden_sizes)):
    for j in range(len(learning_rates)):
        ax.text(j, i, f'{grid_mse[i, j]:.3f}', ha='center', va='center', fontsize=9)
plt.colorbar(im, ax=ax)

# Plot 2: Random search scatter
ax = axes[0, 1]
hs = [r[0] for r in random_results]
lrs = [r[1] for r in random_results]
mses = [r[2] for r in random_results]
scatter = ax.scatter(hs, lrs, c=mses, cmap='YlGn_r', s=200, edgecolors='black', vmin=min(mses), vmax=max(mses))
ax.set_xlabel('Hidden Size')
ax.set_ylabel('Learning Rate')
ax.set_yscale('log')
ax.set_title('Random Search: Configurations')
plt.colorbar(scatter, ax=ax, label='MSE')
for i, (h, lr, mse) in enumerate(random_results):
    ax.annotate(f'{mse:.3f}', (h, lr), textcoords="offset points", xytext=(5, 5), fontsize=8)

# Plot 3: Successive halving elimination
ax = axes[1, 0]
r1_mse = [r[2] for r in results_r1]
r2_mse = [r[2] for r in results_r2]
r3_mse = [r[2] for r in results_r3]

x_pos = np.arange(8)
ax.bar(x_pos, r1_mse, color='#e74c3c', alpha=0.7, label='Round 1 (10 epochs)', edgecolor='black')
ax.bar(range(4), r2_mse, color='#f39c12', alpha=0.7, label='Round 2 (30 epochs)', edgecolor='black')
ax.bar(range(2), r3_mse, color='#2ecc71', alpha=0.7, label='Round 3 (100 epochs)', edgecolor='black')
ax.set_title('Successive Halving: Elimination Rounds')
ax.set_xlabel('Configuration Rank')
ax.set_ylabel('MSE')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# Plot 4: Budget comparison
ax = axes[1, 1]
methods = ['Grid Search', 'Random Search', 'Successive\nHalving']
budgets = [epochs_grid, epochs_random, epochs_halving]
best_mses = [best_grid[2], best_random[2], best_halving[2]]

bars = ax.bar(methods, budgets, color=['#e74c3c', '#3498db', '#2ecc71'], alpha=0.8, edgecolor='black')
ax.set_title('Compute Budget Comparison')
ax.set_ylabel('Total Training Epochs')
for bar, mse in zip(bars, best_mses):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            f'Best MSE: {mse:.4f}', ha='center', va='bottom', fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
os.makedirs('src/phase61', exist_ok=True)
plt.savefig('src/phase61/automl.png', dpi=150)
print("\nSaved plot to src/phase61/automl.png")

# =============================================================================
# SECTION 7: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Grid search best:       MSE={best_grid[2]:.4f}, epochs={epochs_grid}")
print(f"Random search best:     MSE={best_random[2]:.4f}, epochs={epochs_random}")
print(f"Successive halving best: MSE={best_halving[2]:.4f}, epochs={epochs_halving}")
print("\nAutoML & hyperparameter search:")
print("  - Grid search: exhaustive but expensive")
print("  - Random search: explores continuous space, often better")
print("  - Successive halving: kills bad configs early")
print("  - Total budget reduced by 2-5× with smart allocation")
print("\nApplications: tuning any model, NAS, feature engineering")
