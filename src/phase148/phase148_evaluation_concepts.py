#!/usr/bin/env python3
"""
Phase 148: Evaluation Science for LLMs — NumPy Concept Demo
============================================================
This script demonstrates why benchmark scores do not predict real-world
performance. We simulate:

  1. Ten models with weakly correlated benchmark and real-world scores
  2. Contamination: training on test data inflates benchmark scores only
  3. Multi-metric divergence: the "best" model depends on which metric you trust
  4. The recommendation gap: which model should you actually deploy?

Key insight: Lab benchmarks measure a narrow slice of capability. Real-world
evaluation measures utility. The model you want on a leaderboard is often
not the model you want in production.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(148)

# =============================================================================
# SECTION 1: SIMULATE MODELS WITH BENCHMARK AND REAL-WORLD SCORES
# =============================================================================
# We create 20 models. Each has a "true capability" latent variable.
# Benchmark scores correlate weakly with true capability (r ~ 0.5).
# Real-world scores correlate moderately (r ~ 0.6).
# The two are only weakly correlated with each other (r ~ 0.35).
# This is the central tragedy of evaluation: lab and field diverge.

n_models = 20
true_capability = np.random.randn(n_models)

# Benchmark score = some true signal + heavy memorization noise + luck
benchmark_score = 0.5 * true_capability + 0.4 * np.random.randn(n_models) + 0.3
benchmark_score = np.clip(benchmark_score, 0, 1)

# Real-world score = true signal + user interaction noise
realworld_score = 0.6 * true_capability + 0.35 * np.random.randn(n_models) + 0.2
realworld_score = np.clip(realworld_score, 0, 1)

# Task completion = real-world skill + integration friction
task_completion = 0.7 * realworld_score + 0.2 * np.random.randn(n_models) + 0.1
task_completion = np.clip(task_completion, 0, 1)

print("="*60)
print("Phase 148: Evaluation Science for LLMs")
print("="*60)
print(f"\nSimulated models: {n_models}")
print(f"Benchmark vs. real-world correlation: r = {np.corrcoef(benchmark_score, realworld_score)[0,1]:.3f}")
print(f"Benchmark vs. task completion correlation: r = {np.corrcoef(benchmark_score, task_completion)[0,1]:.3f}")
print(f"Real-world vs. task completion correlation: r = {np.corrcoef(realworld_score, task_completion)[0,1]:.3f}")

# =============================================================================
# SECTION 2: CONTAMINATION INFLATION
# =============================================================================
# Half the models are "contaminated": they were trained on the benchmark test
# set. This adds +0.15 to their benchmark score but 0 to real-world score.
# This is invisible unless you run a contamination check.

contaminated = np.random.rand(n_models) < 0.4
benchmark_contaminated = benchmark_score.copy()
benchmark_contaminated[contaminated] += 0.15
benchmark_contaminated = np.clip(benchmark_contaminated, 0, 1)

inflation = np.mean(benchmark_contaminated[contaminated]) - np.mean(benchmark_score[contaminated])
print(f"\nContaminated models: {np.sum(contaminated)}")
print(f"Average benchmark inflation from contamination: +{inflation:.3f}")
print(f"Real-world score change from contamination: 0.000 (no effect)")

# =============================================================================
# SECTION 3: RANKING DIVERGENCE
# =============================================================================
# We pick two models to highlight: the benchmark champion and the practical
# champion. They are different models. This is the core argument of the phase.

bench_champ_idx = np.argmax(benchmark_contaminated)
practical_champ_idx = np.argmax(realworld_score)

print("\n--- Model Rankings ---")
print(f"Benchmark champion (Model {bench_champ_idx}):")
print(f"  Contaminated benchmark: {benchmark_contaminated[bench_champ_idx]:.3f}")
print(f"  Real-world score:       {realworld_score[bench_champ_idx]:.3f}")
print(f"  Task completion:        {task_completion[bench_champ_idx]:.3f}")
print(f"  Contaminated:           {contaminated[bench_champ_idx]}")

print(f"\nPractical champion (Model {practical_champ_idx}):")
print(f"  Contaminated benchmark: {benchmark_contaminated[practical_champ_idx]:.3f}")
print(f"  Real-world score:       {realworld_score[practical_champ_idx]:.3f}")
print(f"  Task completion:        {task_completion[practical_champ_idx]:.3f}")
print(f"  Contaminated:           {contaminated[practical_champ_idx]}")

# =============================================================================
# SECTION 4: VISUALIZATION
# =============================================================================
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Benchmark vs. Real-World scatter
ax = axes[0, 0]
colors = ['#e74c3c' if c else '#3498db' for c in contaminated]
ax.scatter(benchmark_contaminated, realworld_score, c=colors, s=120, alpha=0.8,
           edgecolors='black', linewidth=0.5)
ax.scatter(benchmark_contaminated[bench_champ_idx], realworld_score[bench_champ_idx],
           marker='*', s=300, color='gold', edgecolors='black', linewidth=1.5,
           label='Benchmark champion', zorder=5)
ax.scatter(benchmark_contaminated[practical_champ_idx], realworld_score[practical_champ_idx],
           marker='D', s=150, color='#2ecc71', edgecolors='black', linewidth=1.5,
           label='Practical champion', zorder=5)
ax.set_xlabel('Benchmark Score (possibly contaminated)')
ax.set_ylabel('Real-World Performance')
ax.set_title('Benchmark vs. Real-World Performance\n(Weak Correlation, Different Champions)')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Contamination effect
ax = axes[0, 1]
mean_clean_bench = np.mean(benchmark_score[~contaminated])
mean_contam_bench = np.mean(benchmark_contaminated[contaminated])
mean_clean_rw = np.mean(realworld_score[~contaminated])
mean_contam_rw = np.mean(realworld_score[contaminated])

x_pos = np.arange(2)
width = 0.35
ax.bar(x_pos - width/2, [mean_clean_bench, mean_clean_rw], width,
       label='Clean models', color='#3498db', alpha=0.8, edgecolor='black')
ax.bar(x_pos + width/2, [mean_contam_bench, mean_contam_rw], width,
       label='Contaminated models', color='#e74c3c', alpha=0.8, edgecolor='black')
ax.set_xticks(x_pos)
ax.set_xticklabels(['Benchmark Score', 'Real-World Score'])
ax.set_ylabel('Average Score')
ax.set_title('Contamination Inflates Benchmarks Only\n(Real-World Scores Unchanged)')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# Plot 3: Multi-metric ranking for two selected models
ax = axes[1, 0]
metrics = ['Benchmark', 'Real-World', 'Task Completion', 'User Satisfaction']
model_b = [benchmark_contaminated[bench_champ_idx],
           realworld_score[bench_champ_idx],
           task_completion[bench_champ_idx],
           (realworld_score[bench_champ_idx] + task_completion[bench_champ_idx]) / 2]
model_p = [benchmark_contaminated[practical_champ_idx],
           realworld_score[practical_champ_idx],
           task_completion[practical_champ_idx],
           (realworld_score[practical_champ_idx] + task_completion[practical_champ_idx]) / 2]

x = np.arange(len(metrics))
width = 0.35
ax.bar(x - width/2, model_b, width, label='Benchmark Champion', color='#e74c3c', alpha=0.8)
ax.bar(x + width/2, model_p, width, label='Practical Champion', color='#2ecc71', alpha=0.8)
ax.set_xticks(x)
ax.set_xticklabels(metrics, rotation=15, ha='right')
ax.set_ylabel('Score')
ax.set_title('Multi-Metric Comparison\n(Best Model Depends on What You Measure)')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# Plot 4: Correlation matrix heatmap
ax = axes[1, 1]
data_matrix = np.vstack([benchmark_contaminated, benchmark_score, realworld_score, task_completion])
corr_matrix = np.corrcoef(data_matrix)
im = ax.imshow(corr_matrix, cmap='RdYlGn', vmin=-1, vmax=1)
labels = ['Bench (contam.)', 'Bench (clean)', 'Real-World', 'Task Comp.']
ax.set_xticks(np.arange(len(labels)))
ax.set_yticks(np.arange(len(labels)))
ax.set_xticklabels(labels, rotation=45, ha='right')
ax.set_yticklabels(labels)
for i in range(len(labels)):
    for j in range(len(labels)):
        text = ax.text(j, i, f'{corr_matrix[i, j]:.2f}',
                       ha='center', va='center', color='black', fontsize=10)
ax.set_title('Metric Correlation Matrix\n(Benchmarks Diverge from User Outcomes)')
fig.colorbar(im, ax=ax, shrink=0.8)

plt.tight_layout()
os.makedirs('src/phase148', exist_ok=True)
plt.savefig('src/phase148/evaluation_concepts.png', dpi=150)
print("\nSaved plot to src/phase148/evaluation_concepts.png")

# =============================================================================
# SECTION 5: DEPLOYMENT RECOMMENDATION ENGINE
# =============================================================================
# We build a simple scoring formula that weights real-world metrics higher
# than benchmark scores, reflecting a production-oriented mindset.

deployment_score = 0.2 * benchmark_contaminated + 0.4 * realworld_score + 0.4 * task_completion
best_deploy_idx = np.argmax(deployment_score)

print("\n" + "="*60)
print("DEPLOYMENT RECOMMENDATION")
print("="*60)
print(f"Benchmark champion:      Model {bench_champ_idx} (bench={benchmark_contaminated[bench_champ_idx]:.3f})")
print(f"Practical champion:      Model {practical_champ_idx} (realworld={realworld_score[practical_champ_idx]:.3f})")
print(f"Recommended for deploy:  Model {best_deploy_idx} (composite={deployment_score[best_deploy_idx]:.3f})")
print("\nWeighting used: 20% benchmark + 40% real-world + 40% task completion")
print("\nKey lessons:")
print("  1. Benchmark scores and real-world performance are weakly correlated")
print("  2. Contamination inflates benchmarks without improving user outcomes")
print("  3. The 'best' model depends entirely on which metrics you prioritize")
print("  4. A composite score weighted toward user outcomes beats any single metric")
print("  5. Always run contamination checks before trusting a benchmark claim")
print("  6. Deploy the model that helps users, not the one that tops a leaderboard")
