#!/usr/bin/env python3
"""
Phase 140: Neural Architecture Search Concepts — NumPy Simulation
==================================================================
This script demonstrates three search strategies for finding optimal
model architectures:

  1. Grid search — exhaustive but expensive.
  2. Random search — cheap but blind.
  3. Evolutionary search — directed, gradient-free, and parallelizable.

We simulate a ground-truth accuracy surface over depth and width.
Each "evaluation" is a lookup, which mirrors the zero-cost inference
of a trained supernet. We then plot:

  - The true accuracy landscape.
  - The Pareto frontier of accuracy vs. FLOPs.
  - How each method explores the space.
  - The best architectures found by each method.

Key insight: Evolutionary search often outperforms grid search because
it can allocate more evaluations to promising regions, while grid search
wastes budget on obviously poor configurations.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(140)

# =============================================================================
# SECTION 1: DEFINE SEARCH SPACE AND GROUND-TRUTH OBJECTIVE
# =============================================================================
# WHY synthetic? We need a known ground truth to compare search algorithms
# fairly. In real NAS, the ground truth is unknown and expensive to sample.

depthes = np.array([2, 4, 6, 8, 10])
widths = np.array([32, 64, 96, 128, 160, 192, 224, 256])

# Create meshgrid for plotting the true surface
D_grid, W_grid = np.meshgrid(depthes, widths, indexing='ij')

# Ground-truth accuracy: increases with depth and width, but with diminishing
# returns and small noise. This mimics real model scaling laws.
noise = np.random.randn(*D_grid.shape) * 0.015
accuracy = (
    0.45
    + 0.25 * (1 - np.exp(-D_grid / 6.0))
    + 0.20 * (1 - np.exp(-W_grid / 120.0))
    + 0.05 * (D_grid / 10.0) * (W_grid / 256.0)
    + noise
)
accuracy = np.clip(accuracy, 0, 1)

# FLOPs proxy: proportional to depth * width^2 (dominated by matrix ops)
flops = D_grid * (W_grid / 32.0) ** 2

print("="*70)
print("PHASE 140: NEURAL ARCHITECTURE SEARCH CONCEPTS")
print("="*70)
print(f"Search space: {len(depthes)} depths x {len(widths)} widths = {len(depthes)*len(widths)} configs")
print(f"Ground-truth best accuracy: {accuracy.max():.4f}")
print(f"Ground-truth best config: depth={depthes[np.unravel_index(accuracy.argmax(), accuracy.shape)[0]]}, width={widths[np.unravel_index(accuracy.argmax(), accuracy.shape)[1]]}")

# Helper to look up accuracy and FLOPs for a single config
def evaluate(depth, width):
    d_idx = np.where(depthes == depth)[0][0]
    w_idx = np.where(widths == width)[0][0]
    return accuracy[d_idx, w_idx], flops[d_idx, w_idx]

# =============================================================================
# SECTION 2: GRID SEARCH (EXHAUSTIVE)
# =============================================================================
# WHY include grid search? It is the gold standard for small spaces.
# It guarantees finding the global optimum but costs O(|space|) evaluations.

grid_results = []
for d in depthes:
    for w in widths:
        acc, fl = evaluate(d, w)
        grid_results.append((d, w, acc, fl))

grid_results = np.array(grid_results)  # columns: depth, width, acc, flops
print(f"\nGrid search evaluated {len(grid_results)} configs.")

# =============================================================================
# SECTION 3: RANDOM SEARCH
# =============================================================================
# WHY random search? It is the simplest baseline. Surprisingly, it often
# finds 90% of the quality of grid search with far fewer evaluations.
# We sample 10 configs uniformly at random.

random_budget = 10
random_results = []
for _ in range(random_budget):
    d = int(np.random.choice(depthes))
    w = int(np.random.choice(widths))
    acc, fl = evaluate(d, w)
    random_results.append((d, w, acc, fl))
random_results = np.array(random_results)
print(f"Random search evaluated {len(random_results)} configs.")

# =============================================================================
# SECTION 4: EVOLUTIONARY SEARCH
# =============================================================================
# WHY evolutionary? Architecture choices are discrete and non-differentiable.
# Evolution handles this naturally via mutation and selection.
# We use a small population, elitism, and simple mutation operators.

pop_size = 6
generations = 8
mutation_prob = 0.7

# Initialize population randomly
population = []
for _ in range(pop_size):
    d = int(np.random.choice(depthes))
    w = int(np.random.choice(widths))
    acc, fl = evaluate(d, w)
    population.append({'depth': d, 'width': w, 'acc': acc, 'flops': fl})

history = []  # track best accuracy per generation

for gen in range(generations):
    # Sort by accuracy descending
    population.sort(key=lambda x: x['acc'], reverse=True)
    history.append(population[0]['acc'])

    # Elitism: keep top 2
    survivors = population[:2]

    # Create offspring by mutating survivors
    offspring = []
    while len(offspring) < pop_size - len(survivors):
        parent = survivors[np.random.randint(len(survivors))]
        d, w = parent['depth'], parent['width']

        # Mutate depth: move one step left or right in the depth array
        if np.random.rand() < mutation_prob:
            d_idx = np.where(depthes == d)[0][0]
            delta = np.random.choice([-1, 1])
            new_idx = np.clip(d_idx + delta, 0, len(depthes)-1)
            d = int(depthes[new_idx])

        # Mutate width: move one step left or right in the width array
        if np.random.rand() < mutation_prob:
            w_idx = np.where(widths == w)[0][0]
            delta = np.random.choice([-1, 1])
            new_idx = np.clip(w_idx + delta, 0, len(widths)-1)
            w = int(widths[new_idx])

        acc, fl = evaluate(d, w)
        offspring.append({'depth': d, 'width': w, 'acc': acc, 'flops': fl})

    population = survivors + offspring

# Final sort
population.sort(key=lambda x: x['acc'], reverse=True)
history.append(population[0]['acc'])

evo_results = np.array([[p['depth'], p['width'], p['acc'], p['flops']] for p in population])
print(f"Evolutionary search evaluated {pop_size * generations} configs (including repeats).")
print(f"Evolutionary best accuracy: {population[0]['acc']:.4f} (depth={population[0]['depth']}, width={population[0]['width']})")

# =============================================================================
# SECTION 5: PARETO FRONTIER COMPUTATION
# =============================================================================
# WHY Pareto? In NAS we care about both accuracy and efficiency. A model
# that is slightly less accurate but 10x faster may be preferred for mobile.
# The Pareto frontier contains all architectures where no other architecture
# dominates it on both metrics.

def compute_pareto(results):
    """
    results: Nx4 array [depth, width, accuracy, flops]
    Returns boolean mask of Pareto-optimal points.
    We want to MAXIMIZE accuracy and MINIMIZE flops.
    """
    pareto = np.ones(len(results), dtype=bool)
    for i in range(len(results)):
        for j in range(len(results)):
            if i == j:
                continue
            # j dominates i if j has >= accuracy and <= flops, with at least one strict
            if results[j, 2] >= results[i, 2] and results[j, 3] <= results[i, 3]:
                if results[j, 2] > results[i, 2] or results[j, 3] < results[i, 3]:
                    pareto[i] = False
                    break
    return pareto

pareto_grid = compute_pareto(grid_results)
pareto_random = compute_pareto(random_results)
pareto_evo = compute_pareto(evo_results)

# =============================================================================
# SECTION 6: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 11))

# --- Plot 1: Ground-truth accuracy heatmap ---
ax = axes[0, 0]
im = ax.imshow(accuracy, cmap='viridis', aspect='auto', origin='lower')
ax.set_xticks(range(len(widths)))
ax.set_xticklabels(widths)
ax.set_yticks(range(len(depthes)))
ax.set_yticklabels(depthes)
ax.set_xlabel('Width')
ax.set_ylabel('Depth')
ax.set_title('Ground-Truth Accuracy Landscape')
plt.colorbar(im, ax=ax)

# --- Plot 2: Search exploration scatter ---
ax = axes[0, 1]
ax.scatter(grid_results[:, 3], grid_results[:, 2], c='lightgray', s=30, label='Grid (all)', alpha=0.5)
ax.scatter(random_results[:, 3], random_results[:, 2], c='orange', s=80, marker='s', label='Random search', edgecolors='black')
ax.scatter(evo_results[:, 3], evo_results[:, 2], c='green', s=80, marker='^', label='Evolutionary', edgecolors='black')
ax.set_xlabel('FLOPs (proxy)')
ax.set_ylabel('Accuracy')
ax.set_title('Architecture Search: Where Each Method Looks')
ax.legend()
ax.grid(True, alpha=0.3)

# --- Plot 3: Pareto frontier comparison ---
ax = axes[1, 0]
# Full grid Pareto
pg = grid_results[pareto_grid]
pg = pg[np.argsort(pg[:, 3])]
ax.plot(pg[:, 3], pg[:, 2], 'o-', color='gray', linewidth=2, label='Grid Pareto')

# Random Pareto
pr = random_results[pareto_random]
if len(pr) > 0:
    pr = pr[np.argsort(pr[:, 3])]
    ax.plot(pr[:, 3], pr[:, 2], 's--', color='orange', linewidth=2, label='Random Pareto')

# Evo Pareto
pe = evo_results[pareto_evo]
if len(pe) > 0:
    pe = pe[np.argsort(pe[:, 3])]
    ax.plot(pe[:, 3], pe[:, 2], '^--', color='green', linewidth=2, label='Evo Pareto')

ax.set_xlabel('FLOPs (proxy)')
ax.set_ylabel('Accuracy')
ax.set_title('Pareto Frontier: Accuracy vs. Efficiency')
ax.legend()
ax.grid(True, alpha=0.3)

# --- Plot 4: Evolutionary convergence ---
ax = axes[1, 1]
ax.plot(range(len(history)), history, 'o-', color='green', linewidth=2)
ax.axhline(y=accuracy.max(), color='red', linestyle='--', label='Global best')
ax.set_xlabel('Generation')
ax.set_ylabel('Best Accuracy in Population')
ax.set_title('Evolutionary Search Convergence')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
os.makedirs('src/phase140', exist_ok=True)
plt.savefig('src/phase140/nas_concepts.png', dpi=150, bbox_inches='tight')
print("\nSaved plot to src/phase140/nas_concepts.png")
plt.close()

# =============================================================================
# SECTION 7: SUMMARY
# =============================================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

best_grid = grid_results[np.argmax(grid_results[:, 2])]
print(f"Grid search best:   depth={int(best_grid[0])}, width={int(best_grid[1])}, acc={best_grid[2]:.4f}, flops={best_grid[3]:.1f}")

best_random = random_results[np.argmax(random_results[:, 2])]
print(f"Random search best: depth={int(best_random[0])}, width={int(best_random[1])}, acc={best_random[2]:.4f}, flops={best_random[3]:.1f}")

best_evo = population[0]
print(f"Evolutionary best:  depth={best_evo['depth']}, width={best_evo['width']}, acc={best_evo['acc']:.4f}, flops={best_evo['flops']:.1f}")

print(f"\nPareto-optimal architectures (grid): {pareto_grid.sum()} of {len(grid_results)}")

print("\nKey lessons:")
print("  1. Grid search is reliable but wastes budget on poor regions.")
print("  2. Random search is cheap and often finds good configs by luck.")
print("  3. Evolutionary search directs budget toward promising regions.")
print("  4. The Pareto frontier reveals that smaller models can be optimal.")
print("  5. NAS is not about finding one best model; it is about mapping trade-offs.")
print("="*70)
