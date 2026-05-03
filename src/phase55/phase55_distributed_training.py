#!/usr/bin/env python3
"""
Phase 55: Distributed Training — NumPy Concept Demo
=====================================================
This script demonstrates how to train models across multiple workers.

Key insight: Large models and datasets require more than one GPU.
Distributed training splits either the data, the model, or both.

Concepts demonstrated:
  - Data parallelism (split batch across workers)
  - Model parallelism (split layers across workers)
  - Gradient accumulation (large batch on limited memory)
  - Ring all-reduce (synchronizing gradients across workers)
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(55)

# =============================================================================
# SECTION 1: SETUP — LINEAR REGRESSION DATASET
# =============================================================================
# True model: y = 2x + 1
# We use 16 examples to make batch splitting clean

n_samples = 16
X = np.linspace(0, 3, n_samples).reshape(-1, 1)  # (16, 1)
y_true = 2.0 * X + 1.0 + np.random.normal(0, 0.3, (n_samples, 1))

print("="*60)
print("Phase 55: Distributed Training")
print("="*60)
print(f"\nDataset: {n_samples} samples, 1 feature")
print(f"True model: y = 2x + 1 (with noise)")

# =============================================================================
# SECTION 2: DATA PARALLELISM
# =============================================================================
# Split 16 samples across 4 workers, each computes local gradient,
# then all-reduce to average.

print("\n--- Data Parallelism (4 workers) ---")

n_workers = 4
samples_per_worker = n_samples // n_workers
w = np.array([[0.0]])  # initial weight
b = np.array([0.0])    # initial bias
lr = 0.05

# Single step of distributed SGD
local_grads_w = []
local_grads_b = []
local_losses = []

for worker_id in range(n_workers):
    start = worker_id * samples_per_worker
    end = start + samples_per_worker
    X_local = X[start:end]
    y_local = y_true[start:end]
    
    # Forward
    pred = X_local @ w + b
    loss = np.mean((pred - y_local) ** 2)
    
    # Backward
    grad_w = (2.0 / samples_per_worker) * X_local.T @ (pred - y_local)
    grad_b = (2.0 / samples_per_worker) * np.sum(pred - y_local)
    
    local_grads_w.append(grad_w)
    local_grads_b.append(grad_b)
    local_losses.append(loss)
    
    print(f"  Worker {worker_id}: loss={loss:.3f}, grad_w={grad_w[0,0]:.3f}, grad_b={grad_b:.3f}")

# All-reduce: average gradients across workers
global_grad_w = np.mean(local_grads_w, axis=0)
global_grad_b = np.mean(local_grads_b)

print(f"\n  After all-reduce: grad_w={global_grad_w[0,0]:.3f}, grad_b={global_grad_b:.3f}")

# Verify: single-worker gradient on full batch should match
pred_full = X @ w + b
grad_w_full = (2.0 / n_samples) * X.T @ (pred_full - y_true)
grad_b_full = (2.0 / n_samples) * np.sum(pred_full - y_true)
print(f"  Full-batch gradient: grad_w={grad_w_full[0,0]:.3f}, grad_b={grad_b_full:.3f}")
print(f"  Match: {np.allclose(global_grad_w, grad_w_full) and np.isclose(global_grad_b, grad_b_full)}")

# Update
w = w - lr * global_grad_w
b = b - lr * global_grad_b

# =============================================================================
# SECTION 3: MODEL PARALLELISM
# =============================================================================
# Split a 2-layer MLP across 2 "workers."
# Worker 1 computes layer 1, sends activations to Worker 2 which computes layer 2.

print("\n--- Model Parallelism (2 workers, 2-layer MLP) ---")

# Small MLP: 1 → 4 → 1
W1 = np.random.randn(1, 4) * 0.1  # Worker 1
b1 = np.zeros(4)
W2 = np.random.randn(4, 1) * 0.1  # Worker 2
b2 = np.zeros(1)

x_sample = X[0:1]  # single example
y_sample = y_true[0:1]

# Forward: Worker 1
z1 = x_sample @ W1 + b1
h1 = np.maximum(z1, 0)  # ReLU
print(f"  Worker 1 output (activations): {h1[0]}")

# Forward: Worker 2 (receives h1)
pred_mp = h1 @ W2 + b2
print(f"  Worker 2 output (prediction): {pred_mp[0,0]:.3f} (true: {y_sample[0,0]:.3f})")

# Backward: Worker 2
grad_pred = 2 * (pred_mp - y_sample) / 1.0
grad_W2 = h1.T @ grad_pred
grad_h1 = grad_pred @ W2.T

print(f"  Worker 2 sends grad_h1 back to Worker 1")

# Backward: Worker 1 (receives grad_h1)
grad_z1 = grad_h1 * (z1 > 0).astype(float)  # ReLU derivative
grad_W1 = x_sample.T @ grad_z1

print(f"  Worker 1 computed grad_W1 shape: {grad_W1.shape}")
print(f"  Worker 2 computed grad_W2 shape: {grad_W2.shape}")
print("  Neither worker holds the full model — they split layers.")

# =============================================================================
# SECTION 4: GRADIENT ACCUMULATION
# =============================================================================
# Desired batch size: 16
# Memory limit: 4 per mini-batch
# Accumulation steps: 4

print("\n--- Gradient Accumulation (batch=16, mini-batch=4) ---")

w_acc = np.array([[0.0]])
b_acc = np.array([0.0])
mini_batch_size = 4
accum_steps = n_samples // mini_batch_size

acc_grad_w = np.zeros_like(w_acc)
acc_grad_b = np.zeros_like(b_acc)

for step in range(accum_steps):
    start = step * mini_batch_size
    end = start + mini_batch_size
    X_mini = X[start:end]
    y_mini = y_true[start:end]
    
    pred_mini = X_mini @ w_acc + b_acc
    grad_w = (2.0 / mini_batch_size) * X_mini.T @ (pred_mini - y_mini)
    grad_b = (2.0 / mini_batch_size) * np.sum(pred_mini - y_mini)
    
    acc_grad_w += grad_w
    acc_grad_b += grad_b
    
    print(f"  Step {step+1}: local grad_w={grad_w[0,0]:.3f}, acc grad_w={acc_grad_w[0,0]:.3f}")

# Average over accumulation steps
acc_grad_w /= accum_steps
acc_grad_b /= accum_steps

print(f"\n  Averaged accumulated grad_w={acc_grad_w[0,0]:.3f}")

# Compare to full batch
pred_full = X @ w_acc + b_acc
grad_w_full = (2.0 / n_samples) * X.T @ (pred_full - y_true)
print(f"  Full-batch grad_w={grad_w_full[0,0]:.3f}")
print(f"  Match: {np.allclose(acc_grad_w, grad_w_full)}")

# =============================================================================
# SECTION 5: RING ALL-REDUCE SIMULATION
# =============================================================================
# 4 workers, each holds a gradient vector of length 4.
# Ring all-reduce: scatter-reduce then all-gather.

print("\n--- Ring All-Reduce (4 workers, 4 chunks) ---")

n_workers = 4
n_chunks = 4

# Each worker has a unique gradient
gradients = []
for i in range(n_workers):
    g = np.array([float(i*4 + j + 1) for j in range(n_chunks)])
    gradients.append(g)
    print(f"  Worker {i} initial: {g}")

# True average
true_avg = np.mean(gradients, axis=0)
print(f"\n  True average: {true_avg}")

# Simplified all-reduce simulation (naive average for clarity)
# Real ring all-reduce is complex; we show the conceptual result
ring_result = []
for i in range(n_workers):
    ring_result.append(true_avg.copy())
    
print(f"  After all-reduce, every worker has: {ring_result[0]}")
print(f"  All match: {all(np.allclose(ring_result[i], true_avg) for i in range(n_workers))}")

# =============================================================================
# SECTION 6: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Data shards for data parallelism
ax = axes[0, 0]
colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']
for worker_id in range(n_workers):
    start = worker_id * samples_per_worker
    end = start + samples_per_worker
    ax.scatter(X[start:end], y_true[start:end], c=colors[worker_id], 
               label=f'Worker {worker_id}', s=80, edgecolors='black')
x_line = np.linspace(0, 3, 100)
ax.plot(x_line, 2*x_line + 1, 'k--', label='True: y=2x+1', linewidth=2)
ax.set_title('Data Parallelism: Each Worker Gets a Shard')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Model parallelism pipeline
ax = axes[0, 1]
ax.text(0.5, 0.75, 'Worker 1\nLayer 1\nW1: 1→4', ha='center', va='center',
        bbox=dict(boxstyle='round', facecolor='#3498db', alpha=0.3), fontsize=12)
ax.arrow(0.5, 0.6, 0.0, -0.15, head_width=0.05, head_length=0.03, fc='black', ec='black')
ax.text(0.5, 0.4, 'Activations\n(4-dim vector)', ha='center', va='center', fontsize=10, style='italic')
ax.arrow(0.5, 0.3, 0.0, -0.15, head_width=0.05, head_length=0.03, fc='black', ec='black')
ax.text(0.5, 0.15, 'Worker 2\nLayer 2\nW2: 4→1', ha='center', va='center',
        bbox=dict(boxstyle='round', facecolor='#e74c3c', alpha=0.3), fontsize=12)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_title('Model Parallelism: Layers Split Across Workers')
ax.axis('off')

# Plot 3: Gradient accumulation steps
ax = axes[1, 0]
steps = list(range(1, accum_steps + 1))
acc_vals = []
for step in range(accum_steps):
    start = step * mini_batch_size
    end = start + mini_batch_size
    X_mini = X[start:end]
    y_mini = y_true[start:end]
    pred_mini = X_mini @ w_acc + b_acc
    grad_w = (2.0 / mini_batch_size) * X_mini.T @ (pred_mini - y_mini)
    acc_vals.append(grad_w[0,0])
ax.bar(steps, acc_vals, color='#3498db', edgecolor='black', alpha=0.7)
ax.axhline(y=grad_w_full[0,0], color='red', linestyle='--', linewidth=2, label=f'Full-batch = {grad_w_full[0,0]:.3f}')
ax.set_title('Gradient Accumulation: Local Gradients per Step')
ax.set_xlabel('Accumulation Step')
ax.set_ylabel('Local Gradient (dL/dw)')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: All-reduce speedup (conceptual)
ax = axes[1, 1]
workers = [1, 2, 4, 8, 16]
# Ideal speedup is linear; realistic has communication overhead
ideal = workers
realistic = [w * 0.95 ** (w-1) for w in workers]  # diminishing returns
ax.plot(workers, ideal, 'g--', marker='o', label='Ideal (linear)', linewidth=2)
ax.plot(workers, realistic, 'b-', marker='s', label='Realistic (comm. overhead)', linewidth=2)
ax.set_title('Distributed Training Speedup')
ax.set_xlabel('Number of Workers')
ax.set_ylabel('Speedup Relative to 1 Worker')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xticks(workers)

plt.tight_layout()
os.makedirs('src/phase55', exist_ok=True)
plt.savefig('src/phase55/distributed_training.png', dpi=150)
print("\nSaved plot to src/phase55/distributed_training.png")

# =============================================================================
# SECTION 7: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("\nDistributed training scales AI beyond single-GPU limits:")
print("  - Data parallelism: split batch across workers, identical to large batch")
print("  - Model parallelism: split layers across workers, needed for huge models")
print("  - Gradient accumulation: simulate large batch on limited memory")
print("  - All-reduce: every worker gets the same averaged gradient")
print("\nGPT-4 used data + model + pipeline parallelism across thousands of GPUs.")
print("These techniques are the foundation of all large-scale AI training.")
