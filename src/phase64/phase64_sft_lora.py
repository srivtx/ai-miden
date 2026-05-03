#!/usr/bin/env python3
"""
Phase 64: Practical SFT with LoRA — NumPy Concept Demo
========================================================
This script demonstrates how LoRA (Low-Rank Adaptation) works
by freezing a base model and training only tiny low-rank matrices.

Key insight: Instead of updating a huge weight matrix, LoRA learns
two small matrices B (d×r) and A (r×d) such that ΔW = B @ A.
This reduces trainable parameters by 100-1000×.

Concepts demonstrated:
  - LoRA low-rank decomposition
  - Freezing base weights, training only adapters
  - Multiple adapters for different tasks
  - Adapter merging into base weights
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(64)

# =============================================================================
# SECTION 1: BASE MODEL (pre-trained, frozen)
# =============================================================================
# Simulate a pre-trained linear layer: W0 (8 x 8)
# In reality this would be from Llama/GPT, but we use a toy layer.

d = 8  # hidden dimension
r = 2  # LoRA rank

W0 = np.random.randn(d, d) * 0.3  # pre-trained weights, FROZEN
print("="*60)
print("Phase 64: Practical SFT with LoRA")
print("="*60)
print(f"\nBase model weight shape: {W0.shape}")
print(f"LoRA rank: r={r}")
print(f"Full fine-tuning params: {d*d} ({d}×{d})")
print(f"LoRA params: {2*d*r} (2 × {d} × {r})")
print(f"Parameter reduction: {d*d / (2*d*r):.1f}×")

# =============================================================================
# SECTION 2: TASK DATA (two different tasks)
# =============================================================================
# Task A: y = 2*x + noise (linear, model can fit)
# Task B: y = -x + 0.5 + noise (linear, model can fit)

n_samples = 100
X = np.random.randn(n_samples, d) * 0.3

y_A = 2.0 * X + np.random.normal(0, 0.05, (n_samples, d))
y_B = -1.0 * X + 0.5 + np.random.normal(0, 0.05, (n_samples, d))

# =============================================================================
# SECTION 3: LORA TRAINING FOR TASK A
# =============================================================================

print("\n--- LoRA Training: Task A ---")

# Initialize LoRA matrices
B_A = np.zeros((d, r))
A_A = np.random.randn(r, d) * 0.01

lr = 0.01
losses_A = []

for epoch in range(200):
    # Forward: h = W0 @ x + B_A @ A_A @ x
    delta_W = B_A @ A_A
    pred = X @ (W0 + delta_W).T
    loss = np.mean((pred - y_A) ** 2)
    losses_A.append(loss)
    
    # Backprop (only through delta_W, W0 is frozen)
    grad_pred = (2.0 / n_samples) * (pred - y_A)
    grad_delta = X.T @ grad_pred  # gradient w.r.t. delta_W
    
    # Gradients for B and A using chain rule
    grad_B = grad_delta @ A_A.T
    grad_A = B_A.T @ grad_delta
    
    # Gradient clipping
    grad_norm = np.sqrt(np.sum(grad_B**2) + np.sum(grad_A**2))
    if grad_norm > 1.0:
        grad_B /= grad_norm
        grad_A /= grad_norm
    
    B_A -= lr * grad_B
    A_A -= lr * grad_A

print(f"Final Task A loss: {losses_A[-1]:.4f}")

# =============================================================================
# SECTION 4: LORA TRAINING FOR TASK B
# =============================================================================

print("\n--- LoRA Training: Task B ---")

B_B = np.zeros((d, r))
A_B = np.random.randn(r, d) * 0.01

losses_B = []
for epoch in range(200):
    delta_W = B_B @ A_B
    pred = X @ (W0 + delta_W).T
    loss = np.mean((pred - y_B) ** 2)
    losses_B.append(loss)
    
    grad_pred = (2.0 / n_samples) * (pred - y_B)
    grad_delta = X.T @ grad_pred
    grad_B = grad_delta @ A_B.T
    grad_A = B_B.T @ grad_delta
    
    grad_norm = np.sqrt(np.sum(grad_B**2) + np.sum(grad_A**2))
    if grad_norm > 1.0:
        grad_B /= grad_norm
        grad_A /= grad_norm
    
    B_B -= lr * grad_B
    A_B -= lr * grad_A

print(f"Final Task B loss: {losses_B[-1]:.4f}")

# =============================================================================
# SECTION 5: FULL FINE-TUNING BASELINE
# =============================================================================

print("\n--- Full Fine-Tuning Baseline (Task A) ---")

W_full = W0.copy()
losses_full = []
for epoch in range(200):
    pred = X @ W_full.T
    loss = np.mean((pred - y_A) ** 2)
    losses_full.append(loss)
    
    grad = (2.0 / n_samples) * X.T @ (pred - y_A)
    grad_norm = np.linalg.norm(grad)
    if grad_norm > 1.0:
        grad /= grad_norm
    W_full -= lr * grad

print(f"Final full fine-tuning loss: {losses_full[-1]:.4f}")
print(f"Full fine-tuning parameters: {d*d}")

# =============================================================================
# SECTION 6: ADAPTER MERGING
# =============================================================================

print("\n--- Adapter Merging ---")

# Merge Task A and Task B adapters into base model
delta_A = B_A @ A_A
delta_B = B_B @ A_B

# Simple addition merge
W_merged = W0 + delta_A + delta_B

# Evaluate merged model on both tasks
pred_A_merged = X @ W_merged.T
loss_A_merged = np.mean((pred_A_merged - y_A) ** 2)

pred_B_merged = X @ W_merged.T
loss_B_merged = np.mean((pred_B_merged - y_B) ** 2)

print(f"Merged model Task A loss: {loss_A_merged:.4f}")
print(f"Merged model Task B loss: {loss_B_merged:.4f}")

# Weighted merge (70% Task A, 30% Task B)
W_weighted = W0 + 0.7 * delta_A + 0.3 * delta_B
pred_A_weighted = X @ W_weighted.T
loss_A_weighted = np.mean((pred_A_weighted - y_A) ** 2)
print(f"Weighted merge (70% A) Task A loss: {loss_A_weighted:.4f}")

# =============================================================================
# SECTION 7: COMPARISON TABLE
# =============================================================================

print("\n--- Comparison ---")
print(f"{'Method':<25} {'Params':<10} {'Task A Loss':<12} {'Task B Loss':<12}")
print("-"*60)
print(f"{'Base model (frozen)':<25} {0:<10} {np.mean((X @ W0.T - y_A)**2):.4f}      {'N/A':<12}")
print(f"{'LoRA Task A':<25} {2*d*r:<10} {losses_A[-1]:.4f}      {'N/A':<12}")
print(f"{'LoRA Task B':<25} {2*d*r:<10} {'N/A':<10} {losses_B[-1]:.4f}")
print(f"{'Full fine-tune A':<25} {d*d:<10} {losses_full[-1]:.4f}      {'N/A':<12}")
print(f"{'Merged A+B':<25} {d*d:<10} {loss_A_merged:.4f}      {loss_B_merged:.4f}")

# =============================================================================
# SECTION 8: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Training curves
ax = axes[0, 0]
# Replace any NaN with a large value for plotting
losses_A_clean = np.nan_to_num(losses_A, nan=10.0)
losses_B_clean = np.nan_to_num(losses_B, nan=10.0)
losses_full_clean = np.nan_to_num(losses_full, nan=10.0)
ax.plot(losses_A_clean, 'b-', label='LoRA Task A', linewidth=2)
ax.plot(losses_B_clean, 'r-', label='LoRA Task B', linewidth=2)
ax.plot(losses_full_clean, 'g--', label='Full fine-tune A', linewidth=2)
ax.axhline(y=np.mean((X @ W0.T - y_A)**2), color='gray', linestyle=':', label='Frozen base')
ax.set_title('Training Loss: LoRA vs. Full Fine-Tuning')
ax.set_xlabel('Epoch')
ax.set_ylabel('MSE Loss')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Parameter count comparison
ax = axes[0, 1]
methods = ['LoRA\n(r=2)', 'LoRA\n(r=4)', 'LoRA\n(r=8)', 'Full\nFine-Tune']
params = [2*d*2, 2*d*4, 2*d*8, d*d]
colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
bars = ax.bar(methods, params, color=colors, edgecolor='black', alpha=0.8)
ax.set_title('Trainable Parameters: LoRA vs. Full Fine-Tuning')
ax.set_ylabel('Number of Parameters')
for bar, p in zip(bars, params):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f'{p}', ha='center', va='bottom', fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# Plot 3: Adapter matrices visualization
ax = axes[1, 0]
im = ax.imshow(delta_A, cmap='RdBu', vmin=-0.5, vmax=0.5)
ax.set_title('Task A LoRA Update (ΔW = B @ A)')
ax.set_xlabel('Input dim')
ax.set_ylabel('Output dim')
plt.colorbar(im, ax=ax)

# Plot 4: Merged vs. individual
ax = axes[1, 1]
categories = ['Task A\n(LoRA only)', 'Task A\n(Merged)', 'Task A\n(Weighted)', 'Task B\n(LoRA only)', 'Task B\n(Merged)']
losses_plot = [losses_A[-1], loss_A_merged, loss_A_weighted, losses_B[-1], loss_B_merged]
losses_plot = [np.nan_to_num(l, nan=10.0) for l in losses_plot]
colors = ['#3498db', '#e74c3c', '#f39c12', '#3498db', '#e74c3c']
bars = ax.bar(categories, losses_plot, color=colors, edgecolor='black', alpha=0.8)
ax.set_title('Adapter Merging: Individual vs. Combined')
ax.set_ylabel('MSE Loss')
for bar, loss in zip(bars, losses_plot):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
            f'{loss:.4f}', ha='center', va='bottom', fontsize=9)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
os.makedirs('src/phase64', exist_ok=True)
plt.savefig('src/phase64/sft_lora.png', dpi=150)
print("\nSaved plot to src/phase64/sft_lora.png")

# =============================================================================
# SECTION 9: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"LoRA parameters: {2*d*r} vs. full: {d*d} ({d*d/(2*d*r):.1f}× reduction)")
print(f"LoRA Task A loss: {losses_A[-1]:.4f}")
print(f"Full fine-tune loss: {losses_full[-1]:.4f}")
print(f"LoRA matches full fine-tuning: {np.isclose(losses_A[-1], losses_full[-1], rtol=0.1)}")
print("\nLoRA enables efficient fine-tuning:")
print("  - Freeze base weights, train only B and A matrices")
print("  - 100-1000× fewer parameters than full fine-tuning")
print("  - Same quality on many tasks")
print("  - Multiple adapters for different tasks")
print("  - Adapters can be merged, weighted, or swapped")
print("\nProduction workflow: base model + LoRA adapters + inference merge")
