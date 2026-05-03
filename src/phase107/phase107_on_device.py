"""
Phase 107: On-Device LLMs
NumPy simulation of model size vs memory.
Show how INT4 quantization reduces model footprint by 4x.
Discuss accuracy trade-offs with a toy linear layer.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)


def model_size_mb(params, bits_per_param):
    """Calculate model size in MB given param count and bit width."""
    return (params * bits_per_param) / (8 * 1024 * 1024)


def quantize_weights(w, bits):
    """Simulate uniform quantization of weights to given bits."""
    levels = 2 ** bits
    w_min, w_max = w.min(), w.max()
    scale = (w_max - w_min) / (levels - 1)
    quantized = np.round((w - w_min) / scale) * scale + w_min
    return quantized


def main():
    # Simulate a toy linear layer: input 512, output 1024
    in_dim, out_dim = 512, 1024
    weights = np.random.randn(out_dim, in_dim).astype(np.float32)
    x = np.random.randn(1, in_dim).astype(np.float32)

    # Baseline FP32 output
    y_fp32 = x @ weights.T

    # Quantize to INT8 and INT4
    w_int8 = quantize_weights(weights, bits=8)
    w_int4 = quantize_weights(weights, bits=4)

    y_int8 = x @ w_int8.T
    y_int4 = x @ w_int4.T

    mse_int8 = np.mean((y_fp32 - y_int8) ** 2)
    mse_int4 = np.mean((y_fp32 - y_int4) ** 2)

    print("Toy Linear Layer: input_dim=512, output_dim=1024")
    print(f"FP32 MSE baseline: 0.0")
    print(f"INT8 MSE vs FP32: {mse_int8:.6f}")
    print(f"INT4 MSE vs FP32: {mse_int4:.6f}")
    print()

    # Model size comparison for a 1B parameter model
    params = 1_000_000_000
    fp32_size = model_size_mb(params, 32)
    int8_size = model_size_mb(params, 8)
    int4_size = model_size_mb(params, 4)

    print(f"1B parameter model sizes:")
    print(f"  FP32: {fp32_size:.1f} MB")
    print(f"  INT8: {int8_size:.1f} MB ({fp32_size/int8_size:.1f}x reduction)")
    print(f"  INT4: {int4_size:.1f} MB ({fp32_size/int4_size:.1f}x reduction)")
    print()

    # Plot: model size vs bit width
    bits = [32, 16, 8, 4]
    sizes = [model_size_mb(params, b) for b in bits]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar([str(b) for b in bits], sizes, color=['#e74c3c', '#f39c12', '#2ecc71', '#3498db'])
    ax.set_xlabel('Quantization bit width')
    ax.set_ylabel('Model size (MB)')
    ax.set_title('Model Size vs Quantization: 1B Parameter LLM')
    for i, s in enumerate(sizes):
        ax.text(i, s + 100, f'{s:.0f} MB', ha='center', va='bottom')
    ax.set_ylim(0, max(sizes) * 1.15)
    fig.tight_layout()
    fig.savefig('src/phase107/quantization_size_tradeoff.png')
    print("Saved plot to src/phase107/quantization_size_tradeoff.png")

    # Plot: accuracy trade-off for multiple layers
    num_layers = np.arange(1, 33)
    # Simulate error accumulation: error grows with sqrt(layers)
    error_int8 = mse_int8 * np.sqrt(num_layers) * 0.5
    error_int4 = mse_int4 * np.sqrt(num_layers) * 0.5

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.plot(num_layers, error_int8, label='INT8 accumulated error', color='green')
    ax2.plot(num_layers, error_int4, label='INT4 accumulated error', color='blue')
    ax2.set_xlabel('Number of layers')
    ax2.set_ylabel('Accumulated MSE')
    ax2.set_title('Accuracy Trade-off: Quantization Error Accumulation')
    ax2.legend()
    ax2.grid(True)
    fig2.tight_layout()
    fig2.savefig('src/phase107/quantization_accuracy_tradeoff.png')
    print("Saved plot to src/phase107/quantization_accuracy_tradeoff.png")


if __name__ == '__main__':
    main()
