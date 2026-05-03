"""
Phase 124: Advanced Quantization Concepts (Local NumPy)
Simulates uniform quantization, optimal clipping, and block-wise quantization.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

np.random.seed(42)

# Simulate realistic weight tensor: Gaussian core + heavy outliers
num_weights = 50000
weights = np.random.normal(loc=0.0, scale=0.05, size=num_weights)
outlier_idx = np.random.choice(num_weights, size=int(0.001 * num_weights), replace=False)
weights[outlier_idx] *= 10.0

def uniform_symmetric_quantize(w, bits):
    """Round-to-nearest symmetric uniform quantizer."""
    max_abs = np.max(np.abs(w))
    step = max_abs / (2 ** (bits - 1) - 1) if max_abs > 0 else 1.0
    w_q = np.round(w / step) * step
    w_q = np.clip(w_q, -max_abs, max_abs)
    return w_q, step

def optimal_clipping_quantize(w, bits, search_steps=50):
    """
    Search for the clipping threshold that minimizes MSE.
    This emulates the core idea behind optimal rounding / GPTQ:
    limiting the range reduces granularity loss caused by outliers.
    """
    max_abs = np.max(np.abs(w))
    thresholds = np.linspace(max_abs * 0.5, max_abs, search_steps)
    best_mse = np.inf
    best_w_q = None
    for thresh in thresholds:
        w_clipped = np.clip(w, -thresh, thresh)
        step = thresh / (2 ** (bits - 1) - 1) if thresh > 0 else 1.0
        w_q = np.round(w_clipped / step) * step
        w_q = np.clip(w_q, -thresh, thresh)
        mse = np.mean((w - w_q) ** 2)
        if mse < best_mse:
            best_mse = mse
            best_w_q = w_q
    return best_w_q, best_mse

def blockwise_quantize(w, bits, block_size=128):
    """Independent uniform quantization per block (like GPTQ/AWQ block scales)."""
    w_q = np.zeros_like(w)
    for i in range(0, len(w), block_size):
        block = w[i:i + block_size]
        w_q_block, _ = uniform_symmetric_quantize(block, bits)
        w_q[i:i + block_size] = w_q_block
    return w_q

# Evaluate schemes across bit-widths
schemes = {}
bit_widths = [2, 3, 4, 8]

for bits in bit_widths:
    w_q_naive, _ = uniform_symmetric_quantize(weights, bits)
    mse_naive = np.mean((weights - w_q_naive) ** 2)
    schemes[f"{bits}bit_naive"] = {"w_q": w_q_naive, "mse": mse_naive}

    w_q_opt, mse_opt = optimal_clipping_quantize(weights, bits)
    schemes[f"{bits}bit_optclip"] = {"w_q": w_q_opt, "mse": mse_opt}

w_q_block = blockwise_quantize(weights, bits=4, block_size=128)
mse_block = np.mean((weights - w_q_block) ** 2)
schemes["4bit_blockwise"] = {"w_q": w_q_block, "mse": mse_block}

# Output directory
out_dir = Path(__file__).parent
out_dir.mkdir(parents=True, exist_ok=True)

# Plot 1: Original vs Quantized distributions
plt.figure(figsize=(10, 6))
plt.hist(weights, bins=200, alpha=0.4, label="Original", density=True)
plt.hist(schemes["4bit_naive"]["w_q"], bins=200, alpha=0.4, label="4-bit Naive", density=True)
plt.hist(schemes["4bit_optclip"]["w_q"], bins=200, alpha=0.4, label="4-bit Optimal Clip", density=True)
plt.hist(schemes["4bit_blockwise"]["w_q"], bins=200, alpha=0.4, label="4-bit Block-wise", density=True)
plt.xlabel("Weight Value")
plt.ylabel("Density")
plt.title("Weight Distributions: Original vs Quantized (4-bit)")
plt.legend()
plt.tight_layout()
plt.savefig(out_dir / "phase124_weight_distributions.png", dpi=150)
plt.close()

# Plot 2: Error histograms
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
titles = ["8-bit Naive", "4-bit Naive", "4-bit Block-wise"]
keys = ["8bit_naive", "4bit_naive", "4bit_blockwise"]
for ax, title, key in zip(axes, titles, keys):
    error = weights - schemes[key]["w_q"]
    ax.hist(error, bins=200, color="coral", edgecolor="black", alpha=0.7)
    ax.set_title(f"{title}\nMSE={schemes[key]['mse']:.2e}")
    ax.set_xlabel("Quantization Error")
    ax.set_ylabel("Count")
plt.tight_layout()
plt.savefig(out_dir / "phase124_error_histograms.png", dpi=150)
plt.close()

# Plot 3: MSE vs Bit-width
plt.figure(figsize=(8, 5))
naive_mses = [schemes[f"{b}bit_naive"]["mse"] for b in bit_widths]
opt_mses = [schemes[f"{b}bit_optclip"]["mse"] for b in bit_widths]
plt.plot(bit_widths, naive_mses, marker="o", label="Naive Uniform")
plt.plot(bit_widths, opt_mses, marker="s", label="Optimal Clipping")
plt.axhline(y=mse_block, color="green", linestyle="--", label="4-bit Block-wise")
plt.xlabel("Bit-width")
plt.ylabel("Mean Squared Error")
plt.title("Quantization Error vs Precision")
plt.yscale("log")
plt.legend()
plt.tight_layout()
plt.savefig(out_dir / "phase124_mse_vs_bits.png", dpi=150)
plt.close()

# Plot 4: Zoomed weight slice
x = np.arange(500)
plt.figure(figsize=(12, 5))
plt.plot(x, weights[:500], label="Original", alpha=0.8)
plt.plot(x, schemes["4bit_naive"]["w_q"][:500], label="4-bit Naive", alpha=0.8)
plt.plot(x, schemes["4bit_blockwise"]["w_q"][:500], label="4-bit Block-wise", alpha=0.8)
plt.xlabel("Weight Index")
plt.ylabel("Value")
plt.title("Original vs Quantized Weights (First 500)")
plt.legend()
plt.tight_layout()
plt.savefig(out_dir / "phase124_weight_slice.png", dpi=150)
plt.close()

print("=" * 60)
print("PHASE 124: QUANTIZATION CONCEPTS SUMMARY")
print("=" * 60)
for key, val in schemes.items():
    print(f"{key:20s} MSE = {val['mse']:.6e}")
print("-" * 60)
print("Saved plots:")
for f in out_dir.glob("phase124_*.png"):
    print(f"  {f.name}")
print("=" * 60)
