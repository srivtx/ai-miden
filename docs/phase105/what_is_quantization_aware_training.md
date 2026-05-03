# What is Quantization-Aware Training?

## Problem

Deep learning models are usually trained in 32-bit floating point (FP32). Deploying them on edge devices with limited memory and no FP32 hardware support requires reducing precision, but naive post-training quantization can severely degrade accuracy.

## Definition

Quantization-Aware Training (QAT) is a training procedure where fake quantization operations are inserted into the forward pass during training. The model learns weight values that are robust to the rounding errors introduced by quantization, so that when the model is finally quantized to INT8 or lower, the accuracy drop is minimized.

## Analogy

A sculptor usually works with fine clay but knows the final piece will be cast in rough bronze. During sculpting, they periodically smooth the surface with a bronze-like texture to anticipate how details will survive the casting process. QAT is the periodic smoothing; casting is the final quantization.

## Example

A mobile vision model is trained with QAT. During training, weights and activations are rounded to simulate INT8 behavior, but gradients are still computed in FP32. After convergence, the model is exported as a true INT8 graph. The accuracy drop is 0.5% instead of the 5% drop from naive quantization.

## Confusion

QAT is not the same as training a model in low precision. The compute graph still uses FP32 for gradients; only the forward pass simulates quantization. The goal is to find FP32 weights that quantize well, not to train directly in INT8.

## Code Location

See `src/phase105/phase105_tiny_ml.py` for a NumPy simulation comparing hard-label and soft-label distillation, which is often combined with quantization in Tiny ML pipelines.
