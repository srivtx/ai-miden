"""
Minimal INT8 Quantization.

Compress float32 weights (4 bytes per param) to int8 (1 byte per param).
10M-param model goes from 38MB to 9.5MB. Runs on phones.

Two steps:
  1. Calibration: find min/max per tensor, compute scale and zero-point
  2. Quantization: convert float to int using scale and zero-point
  3. Dequantization: convert int back to float for inference

  q = round(x / scale) + zero_point
  x_hat = (q - zero_point) * scale

The error is small if the distribution is well-represented by the
quantization grid. Weights are typically well-behaved (Gaussian).
Activations are harder (outliers) and need dynamic quantization.
"""

import torch


def minmax_quantize(tensor, bits=8):
    """
    Symmetric min-max quantization.

    For weights (symmetric around zero), zero_point = 0.
    scale = max(|min|, |max|) / (2^(bits-1) - 1)
    """
    q_max = 2 ** (bits - 1) - 1  # 127 for int8
    q_min = -(2 ** (bits - 1))  # -128 for int8

    # Symmetric: scale based on max absolute value
    max_val = tensor.abs().max()
    scale = max_val / q_max
    if scale == 0:
        scale = 1.0

    # Quantize
    q = torch.clamp(torch.round(tensor / scale), q_min, q_max).to(torch.int8)
    return q, scale


def minmax_dequantize(q, scale):
    """Convert int8 back to float32."""
    return q.float() * scale


def quantize_linear_layer(layer, bits=8):
    """Quantize a linear layer's weight. Return (q_weight, scale)."""
    w = layer.weight.data
    q_w, scale = minmax_quantize(w, bits=bits)
    return q_w, scale


class QuantizedLinear:
    """A linear layer stored as int8 weights, dequantized at forward time."""

    def __init__(self, weight, bias=None, bits=8):
        self.q_weight, self.scale = minmax_quantize(weight, bits=bits)
        self.bias = bias

    def forward(self, x):
        """Dequantize weights, compute Wx + b."""
        w = minmax_dequantize(self.q_weight, self.scale)
        return nn.functional.linear(x, w, self.bias)

    def memory_saved(self):
        """Bytes saved vs float32."""
        orig = self.q_weight.numel() * 4
        quant = self.q_weight.numel() * 1 + 4  # 1 byte per weight + 4 for scale
        return orig - quant


import torch.nn as nn


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("INT8 Quantization Demo")
    print("=" * 60)

    # Toy weight matrix
    w = torch.randn(64, 64) * 0.5
    print(f"\n  Original weight: 64x64, dtype={w.dtype}")
    print(f"  Range: [{w.min().item():.3f}, {w.max().item():.3f}]")

    # Quantize
    q, scale = minmax_quantize(w, bits=8)
    print(f"\n  Quantized weight: dtype={q.dtype}")
    print(f"  Scale: {scale:.6f}")
    print(f"  Quantized range: [{q.min().item()}, {q.max().item()}]")

    # Dequantize and check error
    w_hat = minmax_dequantize(q, scale)
    err = (w - w_hat).abs()
    print(f"\n  Mean absolute error: {err.mean().item():.6f}")
    print(f"  Max absolute error:  {err.max().item():.6f}")
    print(f"  Relative error:      {100 * err.mean().item() / w.abs().mean().item():.2f}%")

    # Memory
    float32_bytes = w.numel() * 4
    int8_bytes = w.numel() * 1 + 4
    print(f"\n  Float32: {float32_bytes:,} bytes")
    print(f"  INT8:    {int8_bytes:,} bytes ({100*int8_bytes/float32_bytes:.0f}% of float32)")
    print(f"  Saved:   {float32_bytes - int8_bytes:,} bytes")

    # Compute with quantized weights
    x = torch.randn(1, 64)
    y_orig = nn.functional.linear(x, w)
    y_quant = nn.functional.linear(x, w_hat)
    diff = (y_orig - y_quant).abs().max().item()
    print(f"\n  Output max difference: {diff:.8f}")
    print(f"  Output similarity:     {'PASS' if diff < 0.01 else 'FAIL'} "
          f"(<0.01 threshold)")

    print(f"\nKey insight: INT8 quantization gives ~4x memory reduction")
    print(f"with <1% relative error for well-behaved weight distributions.")
    print(f"For a 10M-param model: 38MB -> 9.5MB. Fits on a phone.")
