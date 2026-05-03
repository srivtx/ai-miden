"""
Phase 38: Scaling Laws & Compute-Optimal Training

This script demonstrates scaling laws using only NumPy and matplotlib.

We simulate:
1. Power-law relationships between loss, model size, and data size
2. The Kaplan vs. Chinchilla trade-offs for fixed compute budgets
3. The compute-optimal frontier (D = 20N)
4. The data wall: model growth vs. available training data
5. How different training strategies compare at the same compute cost

Why simulation? Real scaling law experiments require millions of dollars of
compute. We use realistic parameters to make the concepts visible.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================================
# 1. SCALING LAW PARAMETERS (based on Hoffmann et al. 2022, Chinchilla)
# ============================================================================
# Loss = A/N^alpha + B/D^beta + L_inf
# Where:
#   N = number of parameters
#   D = number of training tokens
#   L_inf = irreducible loss (~1.5 for language modeling)
# ============================================================================

A = 2.5       # model size coefficient
B = 1.8       # data size coefficient
alpha = 0.34  # model size exponent (Chinchilla)
beta = 0.28   # data size exponent (Chinchilla)
L_inf = 1.5   # irreducible loss

def compute_loss(N, D):
    """Compute predicted loss given model size N and data size D."""
    return A / (N ** alpha) + B / (D ** beta) + L_inf

print("=" * 70)
print("PHASE 38: SCALING LAWS & COMPUTE-OPTIMAL TRAINING")
print("=" * 70)
print("Scaling law: Loss = A/N^alpha + B/D^beta + L_inf")
print(f"  A={A}, B={B}, alpha={alpha}, beta={beta}, L_inf={L_inf}")
print()

# ============================================================================
# 2. COMPUTE-OPTIMAL FRONTIER
# ============================================================================
# For a fixed compute budget C = 6*N*D, what is the optimal (N, D) pair?
# Chinchilla: N_opt ~ C^0.5, D_opt ~ C^0.5
# This implies D_opt / N_opt ≈ 20
# ============================================================================

compute_budgets = np.logspace(18, 22, 50)  # 10^18 to 10^22 FLOPs

# Chinchilla-optimal: N ~ C^0.5, D ~ C^0.5
N_chinchilla = compute_budgets ** 0.5 / np.sqrt(6 * 20)
D_chinchilla = 20 * N_chinchilla

# Kaplan-optimal: N ~ C^0.73, D ~ C^0.27
N_kaplan = compute_budgets ** 0.73 / (6 ** 0.73)
D_kaplan = compute_budgets / (6 * N_kaplan)

# Loss along each frontier
loss_chinchilla = compute_loss(N_chinchilla, D_chinchilla)
loss_kaplan = compute_loss(N_kaplan, D_kaplan)

print("Compute-optimal comparison:")
print(f"  Budget 10^20 FLOPs:")
print(f"    Chinchilla: N={N_chinchilla[25]:.1e}, D={D_chinchilla[25]:.1e}, Loss={loss_chinchilla[25]:.4f}")
print(f"    Kaplan:     N={N_kaplan[25]:.1e}, D={D_kaplan[25]:.1e}, Loss={loss_kaplan[25]:.4f}")
print()

# ============================================================================
# 3. REAL MODEL COMPARISON
# ============================================================================

models = {
    'GPT-3': (175e9, 300e9),
    'Gopher': (280e9, 300e9),
    'Chinchilla': (70e9, 1400e9),
    'Llama 2 70B': (70e9, 2000e9),
    'Llama 3 8B': (8e9, 15000e9),
}

print("Real model analysis:")
for name, (N, D) in models.items():
    loss = compute_loss(N, D)
    ratio = D / N
    status = "undertrained" if ratio < 10 else ("overtrained" if ratio > 100 else "compute-optimal")
    print(f"  {name:15s}: N={N:.1e}, D={D:.1e}, D/N={ratio:6.1f}, Loss={loss:.4f} ({status})")
print()

# ============================================================================
# 4. LOSS VS. MODEL SIZE (fixed data)
# ============================================================================

N_range = np.logspace(7, 11, 100)  # 10M to 100B params
fixed_data_sizes = [1e9, 10e9, 100e9, 1000e9]  # 1B, 10B, 100B, 1T tokens

# ============================================================================
# 5. VISUALIZATION
# ============================================================================

fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# ---- Plot 1: Loss vs. Model Size (fixed data) ----
ax = axes[0, 0]
for D_fixed in fixed_data_sizes:
    losses = compute_loss(N_range, D_fixed)
    ax.plot(N_range / 1e9, losses, label=f'D={D_fixed/1e9:.0f}B tokens', linewidth=2)
ax.set_xlabel('Model Size (B parameters)')
ax.set_ylabel('Loss')
ax.set_title('Loss vs. Model Size (Fixed Data)')
ax.set_xscale('log')
ax.legend()
ax.grid(True, alpha=0.3)

# ---- Plot 2: Loss vs. Data Size (fixed model) ----
ax = axes[0, 1]
D_range = np.logspace(8, 13, 100)
fixed_model_sizes = [100e6, 1e9, 10e9, 100e9]
for N_fixed in fixed_model_sizes:
    losses = compute_loss(N_fixed, D_range)
    ax.plot(D_range / 1e9, losses, label=f'N={N_fixed/1e9:.0f}B params', linewidth=2)
ax.set_xlabel('Training Data (B tokens)')
ax.set_ylabel('Loss')
ax.set_title('Loss vs. Data Size (Fixed Model)')
ax.set_xscale('log')
ax.legend()
ax.grid(True, alpha=0.3)

# ---- Plot 3: Chinchilla vs. Kaplan Frontier ----
ax = axes[0, 2]
ax.plot(N_chinchilla / 1e9, loss_chinchilla, 'g-', linewidth=3, label='Chinchilla (D=20N)')
ax.plot(N_kaplan / 1e9, loss_kaplan, 'r--', linewidth=2, label='Kaplan (D~N^0.37)')

# Mark real models
for name, (N, D) in models.items():
    loss = compute_loss(N, D)
    ax.scatter(N / 1e9, loss, s=100, zorder=5)
    ax.annotate(name, (N / 1e9, loss), textcoords="offset points", xytext=(5, 5), fontsize=8)

ax.set_xlabel('Model Size (B parameters)')
ax.set_ylabel('Loss')
ax.set_title('Compute-Optimal Frontier')
ax.set_xscale('log')
ax.legend()
ax.grid(True, alpha=0.3)

# ---- Plot 4: D/N Ratio for Real Models ----
ax = axes[1, 0]
names = list(models.keys())
ratios = [models[n][1] / models[n][0] for n in names]
colors = ['red' if r < 10 else ('green' if r < 100 else 'blue') for r in ratios]
bars = ax.bar(range(len(names)), ratios, color=colors)
ax.axhline(y=20, color='black', linestyle='--', linewidth=2, label='Chinchilla D/N=20')
ax.set_xticks(range(len(names)))
ax.set_xticklabels(names, rotation=30, ha='right', fontsize=9)
ax.set_ylabel('D/N Ratio')
ax.set_title('Data/Parameter Ratio for Real Models')
ax.set_yscale('log')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# ---- Plot 5: Compute Budget Contours ----
ax = axes[1, 1]
N_grid = np.logspace(8, 11, 50)
D_grid = np.logspace(9, 13, 50)
N_mesh, D_mesh = np.meshgrid(N_grid, D_grid)
loss_mesh = compute_loss(N_mesh, D_mesh)
C_mesh = 6 * N_mesh * D_mesh

contour = ax.contour(N_mesh / 1e9, D_mesh / 1e9, np.log10(C_mesh), levels=10, cmap='viridis')
plt.colorbar(contour, ax=ax, label='log10(Compute FLOPs)')
ax.plot(N_chinchilla / 1e9, D_chinchilla / 1e9, 'r--', linewidth=2, label='Chinchilla optimal')
ax.set_xlabel('Model Size (B params)')
ax.set_ylabel('Data Size (B tokens)')
ax.set_title('Compute Budget Contours')
ax.set_xscale('log')
ax.set_yscale('log')
ax.legend()
ax.grid(True, alpha=0.3)

# ---- Plot 6: The Data Wall ----
ax = axes[1, 2]
years = np.array([2020, 2021, 2022, 2023, 2024, 2025, 2026])
model_params = np.array([1.75e11, 2.8e11, 7e10, 1e12, 4e11, 1e12, 2e12])  # largest model that year
chinchilla_data_needed = 20 * model_params
available_data = np.array([5e12, 6e12, 7e12, 8e12, 9e12, 1e13, 1.1e13])

ax.plot(years, chinchilla_data_needed / 1e12, 'o-', color='red', linewidth=2, label='Chinchilla data needed (T)')
ax.plot(years, available_data / 1e12, 's-', color='blue', linewidth=2, label='Estimated available data (T)')
ax.axvline(x=2024.5, color='gray', linestyle='--', alpha=0.5, label='Data wall projection')
ax.fill_between(years, available_data / 1e12, chinchilla_data_needed / 1e12,
                where=(chinchilla_data_needed > available_data), alpha=0.3, color='red')
ax.set_xlabel('Year')
ax.set_ylabel('Tokens (Trillions)')
ax.set_title('The Data Wall')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('src/phase38/scaling_laws.png', dpi=150, bbox_inches='tight')
print("Saved visualization: src/phase38/scaling_laws.png")
plt.close()

# ============================================================================
# 6. SUMMARY
# ============================================================================
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print("Key findings from scaling laws:")
print()
print("1. Loss follows a power law with both model size (N) and data size (D).")
print("2. Chinchilla (D=20N) is compute-optimal for fixed budgets.")
print("3. Kaplan favored model size over data — this was wrong.")
print("4. GPT-3 and Gopher were severely undertrained (D/N < 2).")
print("5. Llama 3 is massively over-trained (D/N = 1875) but quality improves.")
print("6. The data wall: high-quality text is finite (~10T tokens).")
print("7. Solutions: synthetic data, multi-epoch training, better curation.")
print()
print("This demonstrates the core idea of compute-optimal training:")
print("- Model size and data size should grow together")
print("- Bigger is not always better if the model is undertrained")
print("- The Chinchilla rule (D ~ 20N) guides efficient training decisions")
print("- We are approaching the limit of available natural language data")
print("=" * 70)
