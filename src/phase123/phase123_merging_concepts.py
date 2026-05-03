"""
Phase 123: Model Merging at Scale — Concepts (Local NumPy)
Simulates specialist model vectors, task arithmetic, sign conflicts, and interference.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Reproducible synthetic weights
np.random.seed(42)

# Dimensionality of simulated weight vector
DIM = 2000

# Simulate base pre-trained weights (approximately Gaussian)
base = np.random.normal(loc=0.0, scale=0.02, size=DIM)

# Math specialist delta: strong signal on first quadrant, small noise elsewhere
math_mask = np.zeros(DIM)
math_mask[:DIM // 4] = 1.0
math_delta = math_mask * 0.05 + np.random.normal(0.0, 0.005, size=DIM)

# Code specialist delta: strong signal on second quadrant, small noise elsewhere
code_mask = np.zeros(DIM)
code_mask[DIM // 4:DIM // 2] = 1.0
code_delta = code_mask * 0.05 + np.random.normal(0.0, 0.005, size=DIM)

# Generalist (third model) is base with tiny perturbation
general_delta = np.random.normal(0.0, 0.001, size=DIM)

# Build specialist weight vectors
w_math = base + math_delta
w_code = base + code_delta
w_general = base + general_delta

# Task arithmetic: merged = base + (math - base) + (code - base)
# This adds both task-specific deltas to the shared starting point
w_merged = base + math_delta + code_delta

# Define task probes (ground-truth directions) to measure simulated performance
math_probe = math_mask + np.random.normal(0.0, 0.01, size=DIM)
code_probe = code_mask + np.random.normal(0.0, 0.01, size=DIM)

def cosine_sim(a, b):
    """Cosine similarity as a proxy for task performance."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12)

# Compute performance scores (higher = better alignment with task)
perf_base_math = cosine_sim(base, math_probe)
perf_math_math = cosine_sim(w_math, math_probe)
perf_merged_math = cosine_sim(w_merged, math_probe)

perf_base_code = cosine_sim(base, code_probe)
perf_code_code = cosine_sim(w_code, code_probe)
perf_merged_code = cosine_sim(w_merged, code_probe)

# Sign-conflict analysis: dimensions where both deltas are active but opposite
threshold = 0.01
active = (np.abs(math_delta) > threshold) & (np.abs(code_delta) > threshold)
conflict_dims = active & (np.sign(math_delta) != np.sign(code_delta))
num_conflicts = np.sum(conflict_dims)
conflict_ratio = num_conflicts / np.sum(active) if np.sum(active) > 0 else 0.0

# Interference magnitude: how much signal is cancelled in conflicting dimensions
interference = np.where(conflict_dims, np.minimum(np.abs(math_delta), np.abs(code_delta)), 0.0)
total_interference = np.sum(interference)

# Output directory for plots (same folder as script)
out_dir = Path(__file__).parent
out_dir.mkdir(parents=True, exist_ok=True)

# Plot 1: Weight distributions
plt.figure(figsize=(10, 6))
plt.hist(base, bins=100, alpha=0.5, label="Base")
plt.hist(w_math, bins=100, alpha=0.5, label="Math Specialist")
plt.hist(w_code, bins=100, alpha=0.5, label="Code Specialist")
plt.hist(w_merged, bins=100, alpha=0.5, label="Task-Arithmetic Merged")
plt.xlabel("Weight Value")
plt.ylabel("Count")
plt.title("Weight Distributions: Base, Specialists, and Merged Model")
plt.legend()
plt.tight_layout()
plt.savefig(out_dir / "phase123_weight_distributions.png", dpi=150)
plt.close()

# Plot 2: Delta distributions
plt.figure(figsize=(10, 6))
plt.hist(math_delta, bins=100, alpha=0.5, label="Math Delta")
plt.hist(code_delta, bins=100, alpha=0.5, label="Code Delta")
plt.hist(math_delta + code_delta, bins=100, alpha=0.5, label="Summed Delta (Merged)")
plt.xlabel("Delta Value")
plt.ylabel("Count")
plt.title("Specialist Deltas and Their Sum")
plt.legend()
plt.tight_layout()
plt.savefig(out_dir / "phase123_delta_distributions.png", dpi=150)
plt.close()

# Plot 3: Sign conflict map (sampled dimensions)
sample_idx = np.random.choice(DIM, size=200, replace=False)
sample_idx.sort()
sign_map = np.zeros((1, len(sample_idx)))
for i, idx in enumerate(sample_idx):
    if conflict_dims[idx]:
        sign_map[0, i] = -1
    elif active[idx]:
        sign_map[0, i] = 1
plt.figure(figsize=(12, 4))
plt.imshow(sign_map, aspect="auto", cmap="RdYlGn", vmin=-1, vmax=1)
plt.colorbar(label="1 = Agreement, -1 = Conflict, 0 = Inactive")
plt.xlabel("Dimension Index (sampled)")
plt.title(f"Sign Conflicts: {num_conflicts} conflicts ({conflict_ratio:.1%} of active dims)")
plt.yticks([])
plt.tight_layout()
plt.savefig(out_dir / "phase123_sign_conflicts.png", dpi=150)
plt.close()

# Plot 4: Merge quality bar chart
plt.figure(figsize=(8, 5))
tasks = ["Math Task", "Code Task"]
base_perf = [perf_base_math, perf_base_code]
spec_perf = [perf_math_math, perf_code_code]
merged_perf = [perf_merged_math, perf_merged_code]
x = np.arange(len(tasks))
width = 0.25
plt.bar(x - width, base_perf, width, label="Base Model")
plt.bar(x, spec_perf, width, label="Single Specialist")
plt.bar(x + width, merged_perf, width, label="Task-Arithmetic Merged")
plt.ylabel("Cosine Similarity to Task Probe")
plt.title("Merge Quality: Performance Retention on Each Task")
plt.xticks(x, tasks)
plt.legend()
plt.ylim(0, max(max(base_perf), max(spec_perf), max(merged_perf)) * 1.2)
plt.tight_layout()
plt.savefig(out_dir / "phase123_merge_quality.png", dpi=150)
plt.close()

# Plot 5: Interference magnitude per dimension (sorted)
plt.figure(figsize=(10, 5))
plt.bar(range(DIM), sorted(interference, reverse=True), width=1.0)
plt.xlabel("Dimension (sorted by interference magnitude)")
plt.ylabel("Cancelled Magnitude")
plt.title("Interference Magnitude Across Dimensions (Task Arithmetic)")
plt.xlim(0, DIM)
plt.tight_layout()
plt.savefig(out_dir / "phase123_interference.png", dpi=150)
plt.close()

# Summary console output
print("=" * 60)
print("PHASE 123: MODEL MERGING AT SCALE — CONCEPTS SUMMARY")
print("=" * 60)
print(f"Weight vector dimensionality: {DIM}")
print(f"Active overlapping dimensions: {np.sum(active)}")
print(f"Sign conflicts among overlaps: {num_conflicts} ({conflict_ratio:.2%})")
print(f"Total interference (cancelled magnitude): {total_interference:.4f}")
print("-" * 60)
print("Performance (cosine similarity to task probe):")
print(f"  Base on Math:   {perf_base_math:.4f}")
print(f"  Math Spec:      {perf_math_math:.4f}")
print(f"  Merged on Math: {perf_merged_math:.4f}")
print(f"  Base on Code:   {perf_base_code:.4f}")
print(f"  Code Spec:      {perf_code_code:.4f}")
print(f"  Merged on Code: {perf_merged_code:.4f}")
print("-" * 60)
print("Saved plots:")
for f in out_dir.glob("phase123_*.png"):
    print(f"  {f.name}")
print("=" * 60)
