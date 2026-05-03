#!/usr/bin/env python3
"""
Phase 65: QLoRA & Memory-Efficient Training — NumPy Concept Demo
=================================================================
This script demonstrates the core mechanics of QLoRA:
  1. Quantizing FP32 weights to 4-bit integers (simulated)
  2. Dequantizing back to FP32 for computation
  3. Measuring quantization error and memory reduction
  4. Training LoRA adapters on top of quantized weights
  5. Visualizing error distributions

Key insight: The base model is frozen and stored in 4-bit.
Only tiny LoRA adapters are trained in full precision.
This lets us fine-tune models that would not otherwise fit in memory.

Concepts demonstrated:
  - 4-bit uniform quantization (simplified)
  - Block-wise scaling
  - Memory reduction (32-bit vs 4-bit)
  - Quantization error distribution
  - LoRA on quantized weights
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(65)

# =============================================================================
# SECTION 1: BASE WEIGHTS (pre-trained, frozen)
# =============================================================================
# Simulate a layer of pre-trained weights. Real LLM weights are
# approximately normally distributed with mean 0 and small std.

d = 32          # dimension (small for demo, real models use 4096+)
block_size = 8  # quantize in blocks for local scale adaptation
n_blocks = d * d // block_size

W = np.random.randn(d, d) * 0.3  # ~N(0, 0.3^2), frozen pre-trained weights

print("="*60)
print("Phase 65: QLoRA & Memory-Efficient Training")
print("="*60)
print(f"\nBase weight matrix: {W.shape} ({d*d} parameters)")
print(f"Block size: {block_size} weights per block")
print(f"Number of blocks: {n_blocks}")

# =============================================================================
# SECTION 2: 4-BIT QUANTIZATION (uniform, simplified)
# =============================================================================
# Real QLoRA uses NF4 (non-uniform quantiles matched to N(0,1)).
# Here we use uniform 4-bit for clarity: 16 levels, indices 0-15.
# We still use block-wise scaling, which is the critical technique.

def quantize_4bit(weights, block_size):
    """
    Quantize a weight matrix to 4-bit with block-wise scaling.
    WHY block-wise: Different regions of a matrix have different
    value ranges. One global scale would waste precision.
    """
    rows, cols = weights.shape
    n_blocks_r = rows // block_size
    n_blocks_c = cols // block_size

    # Storage: 4-bit indices (as uint8 for NumPy convenience)
    quantized = np.zeros((rows, cols), dtype=np.uint8)
    scales = []      # one scale per block
    zero_points = [] # one zero-point per block

    for br in range(n_blocks_r):
        for bc in range(n_blocks_c):
            # Extract block
            block = weights[
                br*block_size:(br+1)*block_size,
                bc*block_size:(bc+1)*block_size
            ]
            # Compute block statistics
            w_min = block.min()
            w_max = block.max()
            scale = (w_max - w_min) / 15.0  # 16 levels -> 15 intervals
            if scale == 0:
                scale = 1e-8  # avoid division by zero

            # Quantize: map to 0-15
            q = np.round((block - w_min) / scale).astype(np.uint8)
            q = np.clip(q, 0, 15)

            quantized[
                br*block_size:(br+1)*block_size,
                bc*block_size:(bc+1)*block_size
            ] = q
            scales.append(scale)
            zero_points.append(w_min)

    return quantized, np.array(scales), np.array(zero_points), n_blocks_r, n_blocks_c


def dequantize_4bit(quantized, scales, zero_points, block_size, n_blocks_r, n_blocks_c):
    """
    Dequantize 4-bit indices back to float using block-wise scales.
    WHY: Matmul requires float values. We decompress on-the-fly.
    """
    rows, cols = quantized.shape
    deq = np.zeros((rows, cols), dtype=np.float32)
    idx = 0
    for br in range(n_blocks_r):
        for bc in range(n_blocks_c):
            q = quantized[
                br*block_size:(br+1)*block_size,
                bc*block_size:(bc+1)*block_size
            ]
            deq[
                br*block_size:(br+1)*block_size,
                bc*block_size:(bc+1)*block_size
            ] = q.astype(np.float32) * scales[idx] + zero_points[idx]
            idx += 1
    return deq


quantized, scales, zero_points, nbr, nbc = quantize_4bit(W, block_size)
W_deq = dequantize_4bit(quantized, scales, zero_points, block_size, nbr, nbc)

# =============================================================================
# SECTION 3: MEMORY COMPARISON
# =============================================================================
# 32-bit float: 4 bytes per weight
# 4-bit quantized: 0.5 bytes per weight + scale/zero_point per block

mem_fp32 = W.nbytes
mem_4bit_weights = quantized.nbytes  # stored as uint8, but conceptually 4-bit
mem_4bit_constants = scales.nbytes + zero_points.nbytes
mem_4bit_total = mem_4bit_weights + mem_4bit_constants

print("\n--- Memory Comparison ---")
print(f"FP32 storage:        {mem_fp32:>6} bytes ({mem_fp32/1024:.2f} KB)")
print(f"4-bit weights:       {mem_4bit_weights:>6} bytes ({mem_4bit_weights/1024:.2f} KB)")
print(f"4-bit constants:     {mem_4bit_constants:>6} bytes ({mem_4bit_constants/1024:.2f} KB)")
print(f"4-bit total:         {mem_4bit_total:>6} bytes ({mem_4bit_total/1024:.2f} KB)")
print(f"Reduction ratio:     {mem_fp32 / mem_4bit_total:.2f}×")

# =============================================================================
# SECTION 4: QUANTIZATION ERROR ANALYSIS
# =============================================================================
# The difference between original and dequantized weights tells us
# how much precision we lost. Small, symmetric error is ideal.

error = W - W_deq
mse = np.mean(error ** 2)
max_error = np.max(np.abs(error))

print("\n--- Quantization Error ---")
print(f"MSE:          {mse:.6f}")
print(f"Max abs error: {max_error:.6f}")
print(f"Mean error:   {np.mean(error):.6f} (should be ~0, unbiased)")

# =============================================================================
# SECTION 5: SIMULATE LORA ON QUANTIZED WEIGHTS
# =============================================================================
# This is the heart of QLoRA: train B and A in full precision
# while the base W stays frozen in 4-bit.

r = 2  # LoRA rank
n_samples = 200
lr = 0.05

# Synthetic task: y = W @ x + noise
X = np.random.randn(n_samples, d) * 0.3
y_true = X @ W.T + np.random.normal(0, 0.02, (n_samples, d))

# LoRA matrices (full precision, trainable)
B = np.zeros((d, r))
A = np.random.randn(r, d) * 0.01

# Freeze quantized base weights (simulated by using W_deq, no grad)
W_base = W_deq.copy()  # frozen

print("\n--- LoRA Training on Quantized Weights ---")
losses_quantized = []
for epoch in range(300):
    # Forward: h = W_deq @ x + B @ A @ x
    delta_W = B @ A
    pred = X @ (W_base + delta_W).T
    loss = np.mean((pred - y_true) ** 2)
    losses_quantized.append(loss)

    # Backprop through LoRA only (W_base is frozen)
    grad_pred = (2.0 / n_samples) * (pred - y_true)
    grad_delta = X.T @ grad_pred

    grad_B = grad_delta @ A.T
    grad_A = B.T @ grad_delta

    # Gradient clipping
    gnorm = np.sqrt(np.sum(grad_B**2) + np.sum(grad_A**2))
    if gnorm > 1.0:
        grad_B /= gnorm
        grad_A /= gnorm

    B -= lr * grad_B
    A -= lr * grad_A

print(f"Final loss (quantized base + LoRA): {losses_quantized[-1]:.4f}")

# =============================================================================
# SECTION 6: BASELINE: LORA ON FULL-PRECISION WEIGHTS
# =============================================================================
# Compare against training LoRA on unquantized weights.
# If QLoRA works well, the loss should be nearly identical.

B_fp = np.zeros((d, r))
A_fp = np.random.randn(r, d) * 0.01
W_fp = W.copy()  # frozen full-precision base

losses_fp = []
for epoch in range(300):
    delta_W = B_fp @ A_fp
    pred = X @ (W_fp + delta_W).T
    loss = np.mean((pred - y_true) ** 2)
    losses_fp.append(loss)

    grad_pred = (2.0 / n_samples) * (pred - y_true)
    grad_delta = X.T @ grad_pred
    grad_B = grad_delta @ A_fp.T
    grad_A = B_fp.T @ grad_delta

    gnorm = np.sqrt(np.sum(grad_B**2) + np.sum(grad_A**2))
    if gnorm > 1.0:
        grad_B /= gnorm
        grad_A /= gnorm

    B_fp -= lr * grad_B
    A_fp -= lr * grad_A

print(f"Final loss (full-precision base + LoRA): {losses_fp[-1]:.4f}")
print(f"Loss gap due to quantization: {abs(losses_quantized[-1] - losses_fp[-1]):.4f}")

# =============================================================================
# SECTION 7: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Memory comparison bar chart
ax = axes[0, 0]
labels = ['FP32\n(Base)', '4-bit Weights', '4-bit\nConstants', '4-bit\nTotal']
values = [mem_fp32, mem_4bit_weights, mem_4bit_constants, mem_4bit_total]
colors = ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6']
bars = ax.bar(labels, values, color=colors, edgecolor='black', alpha=0.8)
ax.set_title('Memory Usage: FP32 vs. 4-bit Quantization')
ax.set_ylabel('Bytes')
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + mem_fp32*0.01,
            f'{val}', ha='center', va='bottom', fontweight='bold', fontsize=9)
ax.grid(True, alpha=0.3, axis='y')

# Plot 2: Quantization error histogram
ax = axes[0, 1]
ax.hist(error.flatten(), bins=30, color='#e67e22', edgecolor='black', alpha=0.8)
ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Zero error')
ax.set_title('Quantization Error Distribution')
ax.set_xlabel('Error (W_original - W_dequantized)')
ax.set_ylabel('Count')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Original vs. Dequantized weights scatter
ax = axes[1, 0]
sample_idx = np.random.choice(d*d, min(200, d*d), replace=False)
ax.scatter(W.flat[sample_idx], W_deq.flat[sample_idx],
           alpha=0.6, color='#3498db', edgecolor='black', s=40)
# Perfect reconstruction line
lims = [min(W.min(), W_deq.min()), max(W.max(), W_deq.max())]
ax.plot(lims, lims, 'r--', linewidth=2, label='Perfect reconstruction')
ax.set_title('Original vs. Dequantized Weights')
ax.set_xlabel('Original FP32 Weight')
ax.set_ylabel('Dequantized Weight')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Training loss comparison
ax = axes[1, 1]
ax.plot(losses_quantized, 'b-', linewidth=2, label='4-bit base + LoRA')
ax.plot(losses_fp, 'g--', linewidth=2, label='FP32 base + LoRA')
ax.set_title('LoRA Training: Quantized vs. Full-Precision Base')
ax.set_xlabel('Epoch')
ax.set_ylabel('MSE Loss')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
os.makedirs('src/phase65', exist_ok=True)
plt.savefig('src/phase65/qlora.png', dpi=150)
print("\nSaved plot to src/phase65/qlora.png")

# =============================================================================
# SECTION 8: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Weight matrix: {d}×{d} = {d*d} parameters")
print(f"Memory reduction: {mem_fp32 / mem_4bit_total:.2f}× (FP32 → 4-bit)")
print(f"Quantization MSE: {mse:.6f}")
print(f"LoRA params: {2*d*r} (vs. {d*d} full fine-tuning)")
print(f"LoRA on 4-bit loss: {losses_quantized[-1]:.4f}")
print(f"LoRA on FP32 loss:  {losses_fp[-1]:.4f}")
print(f"Quality gap: {abs(losses_quantized[-1] - losses_fp[-1]):.4f} (tiny!)")
print("\nQLoRA insight:")
print("  - Freeze base model in 4-bit (massive memory savings)")
print("  - Dequantize on-the-fly for computation")
print("  - Train tiny LoRA adapters in full precision")
print("  - Fine-tune 7B models on 8GB GPUs")
print("\nProduction workflow: bnb_4bit + LoRA + gradient_checkpointing")
