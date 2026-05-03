## What Is Quantization-Aware Training?

---

## The Problem

Deep learning models are trained in 32-bit floating point (FP32). A 1-billion-parameter model requires 4GB just to store the weights. Edge devices have 2GB of RAM total, shared with the operating system, and their processors lack fast FP32 arithmetic units. Post-training quantization — converting a trained model to INT8 — often causes a 5% accuracy drop because the weights were never trained to tolerate rounding errors. How do you train a model so that it remains accurate after aggressive quantization?

---

## Definition

**Quantization-Aware Training (QAT)** is a training procedure where fake quantization operations are inserted into the forward pass during training. The model learns weight values that are robust to the rounding errors introduced by quantization, so that when the model is finally quantized to INT8 or lower, the accuracy drop is minimized.

**How it works:**
```
Standard training:   weights in FP32 → gradients in FP32 → weights update in FP32
                     → quantize to INT8 after training → accuracy drops 5%

QAT:                 weights in FP32
                     → fake_quant(weights) simulates INT8 rounding in forward pass
                     → loss computed against fake-quantized activations
                     → gradients computed in FP32 (straight-through estimator)
                     → weights update to values that quantize well
                     → export to true INT8 → accuracy drops only 0.5%
```

**Key techniques:**
- **Fake quantization:** rounding weights and activations during the forward pass but keeping gradients in FP32
- **Straight-through estimator:** the gradient of the rounding operation is approximated as 1, allowing backpropagation
- **Calibration:** determining the optimal scale and zero-point for each tensor's dynamic range

**Why this matters:**
- INT8 quantization reduces model size by 4x and speeds up inference on integer hardware
- QAT reduces the accuracy gap from ~5% (post-training) to ~0.5%
- INT4 quantization enables billion-parameter models to run on phones (e.g., Llama-3.2 1B)

---

## Real-Life Analogy

A sculptor usually works with fine clay, smoothing every detail with delicate tools. But the sculptor knows the final piece will be cast in rough bronze, where fine details may be lost. During sculpting, they periodically spray the clay with a bronze-like texture and step back to see which details survive the rough surface. They adjust their technique: exaggerating certain features, simplifying others, and avoiding fragile undercuts that the casting process would destroy. QAT is the periodic texture spray; the final bronze casting is the quantized model.

But the analogy understates the mathematical subtlety. In QAT, the sculptor is not just inspecting the work; the inspection itself changes how the sculptor sculpts. The fake quantization layer is part of the forward pass, so the loss gradient flows back through the simulated rounding. The model learns to push weights toward values that fall exactly on quantization grid points, rather than landing in the noisy space between them. This is like a sculptor who learns to place every groove on a predetermined grid so that the bronze casting preserves the intended shape.

The trade-off is between quantization noise and representational capacity. INT8 has 256 levels; INT4 has only 16. A model quantized to INT4 saves twice the memory but has far less room to express subtle distinctions. QAT helps the model concentrate its weights on the most important quantization levels, but it cannot create levels that do not exist. For some tasks, INT4 is simply too coarse, and QAT cannot save it.

---

## Tiny Numeric Example

**A toy linear layer: input 512, output 1,024, weights randomly initialized:**

**FP32 baseline:**
```
Weight precision:     32 bits
Model size (1B params): 3,814 MB
Output MSE baseline:    0.0
```

**Post-training quantization (naive):**
```
INT8:  MSE vs FP32 = 0.000412,  accuracy drop ≈ 2-3%
INT4:  MSE vs FP32 = 0.003847,  accuracy drop ≈ 8-12%
```

**Quantization-aware training:**
```
INT8:  MSE vs FP32 = 0.000089,  accuracy drop ≈ 0.3-0.5%
INT4:  MSE vs FP32 = 0.001203,  accuracy drop ≈ 2-4%
```

**Model size comparison for a 1B parameter model:**
```
Format    Size (MB)    Reduction
FP32      3,814        1.0x
INT8        954        4.0x
INT4        477        8.0x
```

**Error accumulation across layers:**
```
Layers    INT8 accumulated error    INT4 accumulated error
  8       0.00025                   0.0034
 16       0.00036                   0.0048
 32       0.00051                   0.0067
```

**The shift:** QAT reduced INT4 quantization error by nearly 70% compared to post-training quantization, making aggressive compression viable for production deployment.

---

## Common Confusion

1. **"QAT is the same as training in low precision."** In QAT, gradients are still computed in FP32. Only the forward pass simulates quantization. True low-precision training computes gradients in INT8 or BF16, which is a different technique.

2. **"QAT eliminates all accuracy loss from quantization."** It reduces loss significantly but does not eliminate it. For some tasks, especially those requiring fine-grained distinctions, INT4 may still be too coarse even with QAT.

3. **"Fake quantization is just regular rounding."** Fake quantization includes scale and zero-point calibration. It maps the floating-point range to integer levels in a way that minimizes information loss, not just rounding to the nearest integer.

4. **"QAT is only for INT8."** QAT has been extended to INT4, INT2, and even binary neural networks. The principle is the same: train with simulated low precision so the model learns robust weights.

5. **"You can apply QAT to any model without changes."** Some operations (e.g., layer normalization, softmax) are sensitive to quantization and may need special handling or replacement with quantization-friendly alternatives.

6. **"QAT takes much longer to train than standard training."** The overhead is typically 10-30% because the fake quantization operations are cheap. The main cost is hyperparameter tuning to find the right quantization schema.

7. **"Once quantized, the model cannot be fine-tuned further."** Quantized models can be fine-tuned using quantization-aware fine-tuning, where the model is temporarily dequantized for gradient updates and re-quantized afterward.

---

## Where It Is Used in Our Code

`src/phase107/phase107_on_device.py` — We simulate uniform quantization by rounding weights to INT8 and INT4 precision, comparing the mean squared error against FP32 outputs. We plot model size versus bit width and show how quantization error accumulates across layers, illustrating why quantization-aware training (which learns weights robust to this error) is essential for edge deployment.
