# FRONTIER TRACK: Phase 136 — Neural Scaling Laws Beyond Chinchilla (Concepts)
# LOCAL NumPy concept demonstration
# WHY: NumPy makes the trade-offs between training, inference, and overtraining visible.

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# WHY: Reproducibility matters for educational demos.
np.random.seed(136)

# -----------------------------------------------------------------------------
# PART 1: SCALING LAW SURFACE
# WHY: Loss is a function of both model size (N) and data size (D).
# We use the standard parametric form: L(N,D) = A/N^alpha + B/D^beta + E
# -----------------------------------------------------------------------------
A = 0.5
B = 0.5
alpha = 0.34
beta = 0.28
E = 1.5  # irreducible entropy

def loss(N, D):
    """Compute loss given params N and data tokens D."""
    return A / (N ** alpha) + B / (D ** beta) + E

# Parameter and data ranges (log-spaced)
N_vals = np.logspace(7, 11, 50)  # 10M to 100B params
D_vals = np.logspace(9, 13, 50)  # 1B to 10T tokens
N_grid, D_grid = np.meshgrid(N_vals, D_vals)
L_grid = loss(N_grid, D_grid)

# -----------------------------------------------------------------------------
# PART 2: CHINCHILLA-OPTIMAL LINE
# WHY: Chinchilla says N and D should grow together: D ~ 20 * N (in tokens).
# We plot this line on the loss surface.
# -----------------------------------------------------------------------------
N_chinchilla = np.logspace(7, 11, 100)
D_chinchilla = 20.0 * N_chinchilla
L_chinchilla = loss(N_chinchilla, D_chinchilla)

# -----------------------------------------------------------------------------
# PART 3: INFERENCE-AWARE OPTIMAL FRONTIER
# WHY: Total cost = training_cost + inference_cost * queries.
# Training cost ~ 6ND. Inference cost per token ~ 2N.
# We compute total cost for different query volumes and find the minimum.
# -----------------------------------------------------------------------------

def total_cost(N, D, queries, cost_per_flop=1.0):
    """
    WHY: Training is 6ND FLOP. Inference is 2N FLOP per token.
    We assume average query length of 500 tokens.
    """
    train_cost = 6.0 * N * D * cost_per_flop
    infer_cost = 2.0 * N * 500.0 * queries * cost_per_flop
    return train_cost + infer_cost

# For a fixed compute budget, find the model size that minimizes total cost
query_volumes = [1e6, 1e9, 1e12]
optimal_N = {}

fixed_compute = 1e24  # total FLOP budget for training

for q in query_volumes:
    costs = []
    for N in N_vals:
        # Given N and fixed compute, D = compute / (6N)
        D = fixed_compute / (6.0 * N)
        if D < 1e9:
            D = 1e9
        c = total_cost(N, D, q)
        costs.append(c)
    costs = np.array(costs)
    optimal_N[q] = N_vals[np.argmin(costs)]

# -----------------------------------------------------------------------------
# PART 4: OVERTRAINING BENEFIT
# WHY: Training beyond Chinchilla-optimal (more D for fixed N) improves
# downstream accuracy even when loss improvement is small.
# -----------------------------------------------------------------------------

N_fixed = 1e9  # 1B params
D_range = np.logspace(10, 14, 100)  # 10B to 100T tokens
L_overtrain = loss(N_fixed, D_range)

# Simulate downstream accuracy: plateaus slower than loss
# Accuracy = 1 - k * L^gamma, but with a bonus for high D/N ratio
downstream_acc = 1.0 - 0.3 * (L_overtrain / L_overtrain[0]) ** 1.5
# Add overtraining bonus: extra data helps generalization beyond what loss predicts
overtrain_bonus = 0.05 * np.log10(D_range / (20 * N_fixed))
overtrain_bonus = np.clip(overtrain_bonus, 0, 0.15)
downstream_acc += overtrain_bonus
downstream_acc = np.clip(downstream_acc, 0, 1)

# -----------------------------------------------------------------------------
# PART 5: PLOTTING
# WHY: Humans learn from surfaces and frontiers. We show the full landscape.
# -----------------------------------------------------------------------------
fig = plt.figure(figsize=(16, 12))

# Plot 1: Loss surface with Chinchilla line
ax = fig.add_subplot(2, 2, 1)
contour = ax.contourf(np.log10(N_grid), np.log10(D_grid), L_grid, levels=20, cmap='viridis')
ax.plot(np.log10(N_chinchilla), np.log10(D_chinchilla), 'r--', linewidth=2, label='Chinchilla-optimal')
ax.set_xlabel('log10(Parameters)')
ax.set_ylabel('log10(Tokens)')
ax.set_title('Loss Surface: L(N, D)')
plt.colorbar(contour, ax=ax, label='Loss')
ax.legend()

# Plot 2: Total cost vs model size for different query volumes
ax = fig.add_subplot(2, 2, 2)
for q in query_volumes:
    costs = []
    for N in N_vals:
        D = fixed_compute / (6.0 * N)
        if D < 1e9:
            D = 1e9
        c = total_cost(N, D, q)
        costs.append(c)
    ax.plot(N_vals, costs, linewidth=2, label=f'{q:.0e} queries')
    ax.axvline(x=optimal_N[q], linestyle='--', alpha=0.5)
ax.set_xlabel('Parameters')
ax.set_ylabel('Total Lifetime Cost')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_title('Total Cost vs Model Size (Fixed Training Compute)')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Optimal model size vs query volume
ax = fig.add_subplot(2, 2, 3)
qs = np.logspace(6, 14, 50)
opt_ns = []
for q in qs:
    costs = []
    for N in N_vals:
        D = fixed_compute / (6.0 * N)
        if D < 1e9:
            D = 1e9
        c = total_cost(N, D, q)
        costs.append(c)
    opt_ns.append(N_vals[np.argmin(costs)])
ax.plot(qs, opt_ns, color='crimson', linewidth=2)
ax.set_xlabel('Expected Queries Over Lifetime')
ax.set_ylabel('Cost-Optimal Model Size')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_title('Inference-Aware Optimal Frontier')
ax.grid(True, alpha=0.3)

# Plot 4: Overtraining benefit
ax = fig.add_subplot(2, 2, 4)
ax2 = ax.twinx()
chinchilla_D = 20 * N_fixed
ax.axvline(x=np.log10(chinchilla_D), color='gray', linestyle='--', alpha=0.6, label='Chinchilla D')
ax.plot(np.log10(D_range), L_overtrain, color='steelblue', linewidth=2, label='Training loss')
ax2.plot(np.log10(D_range), downstream_acc, color='forestgreen', linewidth=2, label='Downstream accuracy')
ax.set_xlabel('log10(Tokens)')
ax.set_ylabel('Training Loss', color='steelblue')
ax2.set_ylabel('Downstream Accuracy', color='forestgreen')
ax.set_title(f'Overtraining Benefit (Fixed {N_fixed/1e9:.0f}B Params)')
ax.tick_params(axis='y', labelcolor='steelblue')
ax2.tick_params(axis='y', labelcolor='forestgreen')
ax.grid(True, alpha=0.3)

lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc='center right')

plt.tight_layout()
plt.savefig('src/phase136/scaling_concepts.png', dpi=150)
plt.close()

print("Plot saved to src/phase136/scaling_concepts.png")

# -----------------------------------------------------------------------------
# FINAL INSIGHT
# -----------------------------------------------------------------------------
print("\n" + "=" * 60)
print("KEY INSIGHTS:")
print("1. Chinchilla-optimal minimizes training loss, not total cost.")
print("2. As query volume rises, the cost-optimal model size shifts")
print("   toward smaller models to save inference FLOP.")
print("3. Overtraining (excess data for fixed params) yields small")
print("   loss gains but large downstream accuracy gains.")
print("4. The data wall appears when required tokens exceed available")
print("   high-quality text, forcing synthetic data or multimodal expansion.")
print("=" * 60)
