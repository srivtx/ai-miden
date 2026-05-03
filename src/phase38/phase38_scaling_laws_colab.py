"""
Phase 38: Scaling Laws & Compute-Optimal Training — Colab T4 PyTorch Version
================================================================================
Run this on Google Colab with a T4 GPU.

This script demonstrates scaling laws through both simulation and small-scale
empirical experiments:
1. Train tiny MLPs on MNIST with varying model sizes and training epochs
2. Measure final test loss for each configuration
3. Fit power laws to the empirical data
4. Visualize the Chinchilla-optimal frontier
5. Show the data wall projection

Note: The empirical models are tiny (MNIST MLPs) because real scaling law
experiments require millions of dollars. The power law shape is the key insight.
================================================================================
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# ==============================================================================
# DATA: MNIST (subset for fast experiments)
# ==============================================================================

transform = transforms.ToTensor()
train_full = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
test_full = datasets.MNIST(root='./data', train=False, download=True, transform=transform)

# Use subset for speed
train_subset = Subset(train_full, range(5000))
test_subset = Subset(test_full, range(1000))

test_loader = DataLoader(test_subset, batch_size=256, shuffle=False)

# ==============================================================================
# MODELS OF VARYING SIZE
# ==============================================================================

def make_model(hidden_size):
    return nn.Sequential(
        nn.Flatten(),
        nn.Linear(784, hidden_size),
        nn.ReLU(),
        nn.Linear(hidden_size, 10)
    ).to(device)

def count_params(model):
    return sum(p.numel() for p in model.parameters())

# ==============================================================================
# TRAINING FUNCTION
# ==============================================================================

def train_and_eval(hidden_size, n_epochs, train_data_size):
    model = make_model(hidden_size)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    # Use subset of training data
    data_subset = Subset(train_full, range(train_data_size))
    loader = DataLoader(data_subset, batch_size=128, shuffle=True)

    for epoch in range(n_epochs):
        model.train()
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            logits = model(x)
            loss = F.cross_entropy(logits, y)
            loss.backward()
            optimizer.step()

    # Evaluate
    model.eval()
    total_loss = 0
    with torch.no_grad():
        for x, y in test_loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            total_loss += F.cross_entropy(logits, y).item() * x.size(0)

    avg_loss = total_loss / len(test_subset)
    return avg_loss, count_params(model)

# ==============================================================================
# EMPIRICAL SCALING EXPERIMENT
# ==============================================================================
# We train models with different hidden sizes and data amounts.
# This is a tiny proxy for the real scaling law experiments.
# ==============================================================================

configs = [
    # (hidden_size, epochs, data_size)
    (16, 5, 500),
    (16, 10, 500),
    (16, 5, 2000),
    (32, 5, 500),
    (32, 10, 500),
    (32, 5, 2000),
    (64, 5, 500),
    (64, 10, 500),
    (64, 5, 2000),
    (128, 5, 500),
    (128, 10, 500),
    (128, 5, 2000),
    (256, 5, 500),
    (256, 10, 500),
    (256, 5, 2000),
]

print("Running empirical scaling experiments...")
empirical_results = []
for hidden, epochs, data_size in configs:
    loss, n_params = train_and_eval(hidden, epochs, data_size)
    empirical_results.append((n_params, data_size * epochs, loss))
    print(f"  Params={n_params:5d}, Data={data_size*epochs:5d}, Loss={loss:.4f}")

emp_N = np.array([r[0] for r in empirical_results])
emp_D = np.array([r[1] for r in empirical_results])
emp_loss = np.array([r[2] for r in empirical_results])

# ==============================================================================
# FIT POWER LAWS
# ==============================================================================
# Fit: loss = a * N^(-alpha) + b * D^(-beta) + c
# We do this by fitting in log space for simplicity.

# Fit loss vs N (fixed approximate D)
log_N = np.log(emp_N)
log_loss = np.log(emp_loss)
coef_N = np.polyfit(log_N, log_loss, 1)
alpha_fit = -coef_N[0]

# Fit loss vs D (fixed approximate N)
log_D = np.log(emp_D)
coef_D = np.polyfit(log_D, log_loss, 1)
beta_fit = -coef_D[0]

print(f"\nFitted exponents:")
print(f"  alpha (model size): {alpha_fit:.3f}")
print(f"  beta  (data size):  {beta_fit:.3f}")
print(f"  (Chinchilla: alpha~0.34, beta~0.28)")

# ==============================================================================
# SIMULATION: CHINCHILLA FRONTIERS
# ==============================================================================

def simulated_loss(N, D):
    A, B, alpha, beta, L_inf = 2.5, 1.8, 0.34, 0.28, 1.5
    return A / (N ** alpha) + B / (D ** beta) + L_inf

compute_budgets = np.logspace(18, 22, 50)
N_chin = compute_budgets ** 0.5 / np.sqrt(6 * 20)
D_chin = 20 * N_chin
loss_chin = simulated_loss(N_chin, D_chin)

N_kap = compute_budgets ** 0.73 / (6 ** 0.73)
D_kap = compute_budgets / (6 * N_kap)
loss_kap = simulated_loss(N_kap, D_kap)

# ==============================================================================
# VISUALIZATION
# ==============================================================================

fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Plot 1: Empirical Loss vs. Parameters
ax = axes[0, 0]
scatter = ax.scatter(emp_N, emp_loss, c=np.log(emp_D), cmap='viridis', s=100)
ax.set_xlabel('Parameters')
ax.set_ylabel('Test Loss')
ax.set_title('Empirical: Loss vs. Model Size')
ax.set_xscale('log')
plt.colorbar(scatter, ax=ax, label='log(Training tokens)')
ax.grid(True, alpha=0.3)

# Plot 2: Empirical Loss vs. Data
ax = axes[0, 1]
scatter = ax.scatter(emp_D, emp_loss, c=np.log(emp_N), cmap='plasma', s=100)
ax.set_xlabel('Training Tokens')
ax.set_ylabel('Test Loss')
ax.set_title('Empirical: Loss vs. Data Size')
ax.set_xscale('log')
plt.colorbar(scatter, ax=ax, label='log(Parameters)')
ax.grid(True, alpha=0.3)

# Plot 3: Chinchilla vs. Kaplan
ax = axes[0, 2]
ax.plot(N_chin, loss_chin, 'g-', linewidth=3, label='Chinchilla optimal')
ax.plot(N_kap, loss_kap, 'r--', linewidth=2, label='Kaplan optimal')
ax.scatter(emp_N, emp_loss, c='blue', s=50, alpha=0.5, label='Empirical')
ax.set_xlabel('Parameters')
ax.set_ylabel('Loss')
ax.set_title('Compute-Optimal Frontiers')
ax.set_xscale('log')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: D/N Ratio for Empirical Runs
ax = axes[1, 0]
ratios = emp_D / emp_N
colors = ['red' if r < 10 else ('green' if r < 100 else 'blue') for r in ratios]
ax.scatter(emp_N, ratios, c=colors, s=100)
ax.axhline(y=20, color='black', linestyle='--', linewidth=2, label='Chinchilla D/N=20')
ax.set_xlabel('Parameters')
ax.set_ylabel('D/N Ratio')
ax.set_title('Empirical D/N Ratios')
ax.set_xscale('log')
ax.set_yscale('log')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 5: Compute Contours
ax = axes[1, 1]
N_grid = np.logspace(2, 5, 50)
D_grid = np.logspace(3, 7, 50)
N_mesh, D_mesh = np.meshgrid(N_grid, D_grid)
loss_mesh = simulated_loss(N_mesh, D_mesh)
C_mesh = 6 * N_mesh * D_mesh

contour = ax.contour(N_mesh, D_mesh, np.log10(C_mesh), levels=8, cmap='viridis')
plt.colorbar(contour, ax=ax, label='log10(Compute)')
ax.plot(N_chin, D_chin, 'r--', linewidth=2, label='Chinchilla')
ax.set_xlabel('Parameters')
ax.set_ylabel('Training Tokens')
ax.set_title('Compute Budget Contours')
ax.set_xscale('log')
ax.set_yscale('log')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 6: Data Wall
ax = axes[1, 2]
years = np.array([2020, 2021, 2022, 2023, 2024, 2025, 2026])
model_params = np.array([175, 280, 70, 1000, 400, 1000, 2000]) * 1e9
needed_data = 20 * model_params
available = np.array([5, 6, 7, 8, 9, 10, 11]) * 1e12

ax.plot(years, needed_data / 1e12, 'o-', color='red', linewidth=2, label='Data needed (T)')
ax.plot(years, available / 1e12, 's-', color='blue', linewidth=2, label='Available data (T)')
ax.fill_between(years, available / 1e12, needed_data / 1e12,
                where=(needed_data > available), alpha=0.3, color='red')
ax.set_xlabel('Year')
ax.set_ylabel('Tokens (Trillions)')
ax.set_title('The Data Wall')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('phase38_scaling_results.png', dpi=150, bbox_inches='tight')
print("\nSaved: phase38_scaling_results.png")
plt.close()

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================
print("\n" + "=" * 70)
print("FINAL RESULTS")
print("=" * 70)
print(f"Fitted alpha (model): {alpha_fit:.3f} (Chinchilla: ~0.34)")
print(f"Fitted beta (data):   {beta_fit:.3f} (Chinchilla: ~0.28)")
print("\nKey scaling law insights:")
print("1. Loss improves predictably with both model size and data size.")
print("2. Chinchilla: D ~ 20N is compute-optimal for fixed budgets.")
print("3. Kaplan-style undertraining (large N, small D) is inefficient.")
print("4. Over-training (Llama 3 style) improves quality beyond Chinchilla.")
print("5. The data wall: natural text is finite (~10T tokens).")
print("6. Future scaling requires synthetic data and better curation.")
print("=" * 70)

# To run in Colab:
# 1. Upload this file or paste into a cell
# 2. Runtime -> Change runtime type -> GPU
# 3. Run all cells
# Training takes ~2 minutes on T4.
