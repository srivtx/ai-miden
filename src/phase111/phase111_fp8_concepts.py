#!/usr/bin/env python3
"""
FRONTIER TRACK: Phase 111 — FP8 Format Concepts
LOCAL NumPy demonstration of FP8 E4M3 and E5M2 formats.

This script simulates the two FP8 variants in pure NumPy to show:
  - Bit layouts and representable values
  - Quantization error across magnitude ranges
  - Dynamic range comparison with FP32, BF16, INT8
  - Delayed scaling: how scale factors adapt to tensor statistics

Why NumPy? Because understanding the numerics requires inspecting
individual bits and errors, not training a model. The GPU tensor
cores hide these details; we expose them.
"""

import os
import numpy as np

# Use non-interactive backend so this script runs headless on any machine.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. FP8 FORMAT DEFINITIONS
# ---------------------------------------------------------------------------
# We define the exact codebook for E4M3 and E5M2. These are small enough
# (at most 256 codes each) that we can enumerate them explicitly.

def build_fp8_e4m3_codebook():
    """
    E4M3: 1 sign bit, 4 exponent bits, 3 mantissa bits.
    Bias = 7. All-ones exponent is used for NaN (only when mantissa != 0).
    The maximum finite value is extended by using all-ones exponent with
    the largest mantissa, giving ~448.
    """
    values = []
    for code in range(256):
        sign = (code >> 7) & 1
        exponent = (code >> 3) & 0xF
        mantissa = code & 0x7
        s = -1.0 if sign else 1.0

        if exponent == 0:
            # Subnormal: no implicit leading 1
            val = s * (2 ** (-6)) * (mantissa / 8.0)
        elif exponent == 0b1111:
            # Specials: NaN if mantissa != 0, else max normal extended
            if mantissa == 0b111:
                val = s * 448.0  # max finite
            elif mantissa == 0:
                val = np.nan  # Actually some implementations use this for NaN
                # For simplicity we treat code 0b01111111 and 0b11111111 as NaN
                # but we will filter them out.
                continue
            else:
                val = np.nan
                continue
        else:
            # Normal: implicit leading 1
            val = s * (2 ** (exponent - 7)) * (1.0 + mantissa / 8.0)
        values.append(val)
    return np.array(sorted(set(v for v in values if not np.isnan(v))))


def build_fp8_e5m2_codebook():
    """
    E5M2: 1 sign bit, 5 exponent bits, 2 mantissa bits.
    Bias = 15. Follows IEEE-754 conventions: all-ones exponent means
    Inf (mantissa == 0) or NaN (mantissa != 0).
    Max finite is with exponent 0b11110 and mantissa 0b11.
    """
    values = []
    for code in range(256):
        sign = (code >> 7) & 1
        exponent = (code >> 2) & 0x1F
        mantissa = code & 0x3
        s = -1.0 if sign else 1.0

        if exponent == 0:
            val = s * (2 ** (-14)) * (mantissa / 4.0)
        elif exponent == 0b11111:
            if mantissa == 0:
                val = s * np.inf
            else:
                val = np.nan
            continue
        else:
            val = s * (2 ** (exponent - 15)) * (1.0 + mantissa / 4.0)
        values.append(val)
    return np.array(sorted(set(v for v in values if not np.isnan(v) and not np.isinf(v))))


def build_int8_codebook():
    """INT8 is just the integers -128 to 127, but we usually symmetrically
    quantize to -127..127 to avoid asymmetry issues."""
    return np.arange(-127, 128, dtype=np.float64)


# ---------------------------------------------------------------------------
# 2. QUANTIZATION FUNCTIONS
# ---------------------------------------------------------------------------
# Given a codebook and a scale, we quantize by finding the nearest code.
# This mimics what FP8 tensor cores do: multiply by scale, round to nearest
# representable value, then divide by scale for dequantization.

def quantize_tensor(tensor, codebook, scale=1.0):
    """
    Simulate FP8 quantization with a scaling factor.
    Why scale? Because FP8 has a fixed codebook. To represent values
    outside the raw codebook range, we rescale the tensor so its max
    maps to the codebook max.
    """
    scaled = tensor * scale
    # Find nearest codebook entry for each value
    idx = np.argmin(np.abs(codebook[:, None] - scaled[None, :]), axis=0)
    quantized = codebook[idx]
    dequantized = quantized / scale
    return quantized, dequantized


def simulate_delayed_scaling(tensor, codebook, prev_max_abs, max_fp8):
    """
    Delayed scaling uses the previous step's max abs to set the scale.
    If the current tensor has a larger max, clipping occurs this step,
    and the scale is corrected for the next step.
    """
    scale = max_fp8 / prev_max_abs if prev_max_abs > 0 else 1.0
    _, dequantized = quantize_tensor(tensor, codebook, scale)
    actual_max_abs = float(np.max(np.abs(tensor)))
    return dequantized, actual_max_abs


# ---------------------------------------------------------------------------
# 3. BUILD CODEBOOKS
# ---------------------------------------------------------------------------
e4m3_codes = build_fp8_e4m3_codebook()
e5m2_codes = build_fp8_e5m2_codebook()
int8_codes = build_int8_codebook()

print("=" * 70)
print("PHASE 111: FP8 Format Concepts")
print("=" * 70)

print("\n--- E4M3 codebook stats ---")
print(f"Count: {len(e4m3_codes)}")
print(f"Max finite: {np.max(e4m3_codes):.3f}")
print(f"Min positive normal: {np.min(e4m3_codes[e4m3_codes > 0]):.6f}")

print("\n--- E5M2 codebook stats ---")
print(f"Count: {len(e5m2_codes)}")
print(f"Max finite: {np.max(e5m2_codes):.3f}")
print(f"Min positive normal: {np.min(e5m2_codes[e5m2_codes > 0]):.6f}")

# ---------------------------------------------------------------------------
# 4. DYNAMIC RANGE COMPARISON
# ---------------------------------------------------------------------------
# We generate a log-spaced range of values and show which formats can
# represent them without clipping or underflow.

print("\n--- Dynamic range stress test ---")
test_values = np.logspace(-8, 5, 14)
print(f"{'Value':>12}  {'E4M3 OK?':>8}  {'E5M2 OK?':>8}  {'INT8 OK?':>8}")
for v in test_values:
    e4_ok = "YES" if (np.min(np.abs(e4m3_codes - v)) / (v + 1e-12) < 0.5) else "NO"
    e5_ok = "YES" if (np.min(np.abs(e5m2_codes - v)) / (v + 1e-12) < 0.5) else "NO"
    # INT8 with scale to [-1,1] for fair comparison? We'll just show raw.
    int_ok = "YES" if abs(v) <= 127 else "NO"
    print(f"{v:12.2e}  {e4_ok:>8}  {e5_ok:>8}  {int_ok:>8}")

# ---------------------------------------------------------------------------
# 5. QUANTIZATION ERROR VISUALIZATION
# ---------------------------------------------------------------------------
# We create a synthetic weight tensor with outliers and compare
# quantization error for E4M3 and E5M2, with and without scaling.

np.random.seed(42)
weights = np.random.normal(loc=0.0, scale=1.0, size=1000).astype(np.float32)
# Add a few outliers to simulate gradient spikes or large weights
weights[np.random.choice(1000, 20, replace=False)] *= 50.0

# E4M3 without scaling (naive)
_, e4m3_naive = quantize_tensor(weights, e4m3_codes, scale=1.0)
# E4M3 with scaling (per-tensor, immediate)
max_e4m3 = float(np.max(np.abs(e4m3_codes)))
scale_e4m3 = max_e4m3 / np.max(np.abs(weights))
_, e4m3_scaled = quantize_tensor(weights, e4m3_codes, scale=scale_e4m3)

# E5M2 without scaling
_, e5m2_naive = quantize_tensor(weights, e5m2_codes, scale=1.0)
max_e5m2 = float(np.max(np.abs(e5m2_codes)))
scale_e5m2 = max_e5m2 / np.max(np.abs(weights))
_, e5m2_scaled = quantize_tensor(weights, e5m2_codes, scale=scale_e5m2)

# INT8 symmetric quantized
scale_int8 = 127.0 / np.max(np.abs(weights))
_, int8_scaled = quantize_tensor(weights, int8_codes, scale=scale_int8)

error_e4_naive = np.abs(weights - e4m3_naive)
error_e4_scaled = np.abs(weights - e4m3_scaled)
error_e5_naive = np.abs(weights - e5m2_naive)
error_e5_scaled = np.abs(weights - e5m2_scaled)
error_int8 = np.abs(weights - int8_scaled)

print("\n--- Quantization error (mean abs error) ---")
print(f"E4M3 naive:    {np.mean(error_e4_naive):.6f}")
print(f"E4M3 scaled:   {np.mean(error_e4_scaled):.6f}")
print(f"E5M2 naive:    {np.mean(error_e5_naive):.6f}")
print(f"E5M2 scaled:   {np.mean(error_e5_scaled):.6f}")
print(f"INT8 scaled:   {np.mean(error_int8):.6f}")

# ---------------------------------------------------------------------------
# 6. PLOT: DYNAMIC RANGE COMPARISON
# ---------------------------------------------------------------------------
os.makedirs("src/phase111", exist_ok=True)

fig, ax = plt.subplots(figsize=(10, 6))
# Plot representable positive values for each format
ax.scatter(np.log10(np.maximum(e4m3_codes[e4m3_codes > 0], 1e-12)),
           np.ones_like(e4m3_codes[e4m3_codes > 0]) * 3,
           s=8, label='FP8 E4M3', alpha=0.7)
ax.scatter(np.log10(np.maximum(e5m2_codes[e5m2_codes > 0], 1e-12)),
           np.ones_like(e5m2_codes[e5m2_codes > 0]) * 2,
           s=8, label='FP8 E5M2', alpha=0.7)
ax.scatter(np.log10(np.maximum(int8_codes[int8_codes > 0], 1e-12)),
           np.ones_like(int8_codes[int8_codes > 0]) * 1,
           s=8, label='INT8', alpha=0.7)

# BF16 is dense; sample a subset for visualization
bf16_pos = np.unique(np.abs(np.random.randn(5000).astype(np.float32).astype(np.float16).astype(np.float32)))
ax.scatter(np.log10(np.maximum(bf16_pos[bf16_pos > 0], 1e-12)),
           np.ones_like(bf16_pos[bf16_pos > 0]) * 0,
           s=2, label='BF16 (sample)', alpha=0.3)

ax.set_yticks([0, 1, 2, 3])
ax.set_yticklabels(['BF16', 'INT8', 'E5M2', 'E4M3'])
ax.set_xlabel('log10(magnitude)')
ax.set_title('Representable Positive Values by Format')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('src/phase111/fp8_dynamic_range.png', dpi=150)
plt.close()
print("\nSaved: src/phase111/fp8_dynamic_range.png")

# ---------------------------------------------------------------------------
# 7. PLOT: QUANTIZATION ERROR HISTOGRAMS
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(14, 8))
axes = axes.flatten()

def plot_hist(ax, data, title, color):
    ax.hist(np.log10(np.maximum(data, 1e-12)), bins=50, color=color, alpha=0.7)
    ax.set_title(title)
    ax.set_xlabel('log10(abs error)')
    ax.set_ylabel('count')

plot_hist(axes[0], error_e4_naive, 'E4M3 naive', 'C0')
plot_hist(axes[1], error_e4_scaled, 'E4M3 scaled', 'C1')
plot_hist(axes[2], error_e5_naive, 'E5M2 naive', 'C2')
plot_hist(axes[3], error_e5_scaled, 'E5M2 scaled', 'C3')
plot_hist(axes[4], error_int8, 'INT8 scaled', 'C4')
axes[5].axis('off')

plt.suptitle('Quantization Error Distributions (with outliers)')
plt.tight_layout()
plt.savefig('src/phase111/fp8_quantization_error.png', dpi=150)
plt.close()
print("Saved: src/phase111/fp8_quantization_error.png")

# ---------------------------------------------------------------------------
# 8. DELAYED SCALING SIMULATION
# ---------------------------------------------------------------------------
# We simulate 20 training steps where weight statistics drift.
# At each step, we apply delayed scaling (using previous max) and
# track the clipping error.

np.random.seed(7)
num_steps = 20
prev_max = 10.0  # initial guess
true_max_history = []
clipped_error_history = []
scale_history = []

for step in range(num_steps):
    # Simulate weights growing over time (e.g., early training instability)
    true_max = 10.0 + step * 2.5 + np.random.normal(0, 3.0)
    true_max = max(true_max, 1.0)
    true_max_history.append(true_max)

    # Delayed scaling uses previous max
    scale = max_e4m3 / prev_max if prev_max > 0 else 1.0
    scale_history.append(scale)

    # Generate a synthetic tensor with this max
    tensor = np.random.normal(0, true_max / 3.0, size=500).astype(np.float32)
    tensor = np.clip(tensor, -true_max, true_max)

    _, dequant = quantize_tensor(tensor, e4m3_codes, scale)
    clipped_error = float(np.max(np.abs(tensor - dequant)))
    clipped_error_history.append(clipped_error)

    # Update prev_max for next step (this is what delayed scaling does)
    prev_max = true_max

# Plot delayed scaling behavior
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
axes[0].plot(true_max_history, label='True max abs', marker='o')
axes[0].set_title('Tensor Max Abs Over Steps')
axes[0].set_xlabel('Step')
axes[0].set_ylabel('Max abs')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(scale_history, label='Scale factor', marker='s', color='C1')
axes[1].set_title('Delayed Scaling Factor')
axes[1].set_xlabel('Step')
axes[1].set_ylabel('Scale = max_fp8 / prev_max')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

axes[2].plot(clipped_error_history, label='Max quantization error', marker='^', color='C2')
axes[2].set_title('Clipping Error per Step')
axes[2].set_xlabel('Step')
axes[2].set_ylabel('Max abs error')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.suptitle('Delayed Scaling Simulation (E4M3)')
plt.tight_layout()
plt.savefig('src/phase111/fp8_delayed_scaling.png', dpi=150)
plt.close()
print("Saved: src/phase111/fp8_delayed_scaling.png")

# ---------------------------------------------------------------------------
# 9. VISUALIZE WHICH RANGES EACH FORMAT CAN REPRESENT
# ---------------------------------------------------------------------------
# Create a heatmap showing relative quantization error across magnitudes.

magnitudes = np.logspace(-6, 4, 100)
errors_e4 = []
errors_e5 = []
errors_int = []
for m in magnitudes:
    # Scale each format to cover this magnitude
    s4 = max_e4m3 / m
    s5 = max_e5m2 / m
    si = 127.0 / m
    _, dq4 = quantize_tensor(np.array([m]), e4m3_codes, s4)
    _, dq5 = quantize_tensor(np.array([m]), e5m2_codes, s5)
    _, dqi = quantize_tensor(np.array([m]), int8_codes, si)
    errors_e4.append(abs(float(dq4[0] - m)))
    errors_e5.append(abs(float(dq5[0] - m)))
    errors_int.append(abs(float(dqi[0] - m)))

fig, ax = plt.subplots(figsize=(10, 5))
ax.loglog(magnitudes, errors_e4, label='E4M3', alpha=0.8)
ax.loglog(magnitudes, errors_e5, label='E5M2', alpha=0.8)
ax.loglog(magnitudes, errors_int, label='INT8', alpha=0.8)
ax.set_xlabel('Input magnitude')
ax.set_ylabel('Quantization error (abs)')
ax.set_title('Quantization Error vs Magnitude (scaled to fit)')
ax.legend()
ax.grid(True, alpha=0.3, which='both')
plt.tight_layout()
plt.savefig('src/phase111/fp8_magnitude_error.png', dpi=150)
plt.close()
print("Saved: src/phase111/fp8_magnitude_error.png")

print("\n" + "=" * 70)
print("Phase 111 concepts demonstration complete.")
print("=" * 70)
