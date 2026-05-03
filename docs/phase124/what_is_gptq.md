## What Is GPTQ?

---

### The Problem

A 7B parameter model stored in FP16 (16-bit floating point) needs 14 gigabytes of memory. That does not fit on most consumer GPUs, and it certainly does not fit on a phone. The obvious solution is to use fewer bits per weight — 8-bit, 4-bit, or even lower. But if you simply round every weight to the nearest 4-bit value, the model's accuracy collapses. The error from naive rounding compounds across 30+ layers, and the model starts producing gibberish. How do you quantize to 4-bit without destroying quality?

---

### Definition

**GPTQ (General-purpose Post-Training Quantization)** is a layer-wise weight quantization method that treats quantization as an optimal brain surgeon problem: instead of rounding each weight independently, it rounds weights sequentially and updates the remaining unquantized weights to compensate for the error introduced by each rounding step.

**How it works:**
```
For each layer:
  1. Collect calibration activations by running a small dataset through the layer
  2. Compute the Hessian of the layer's output error with respect to its weights
  3. For each weight w_i in the layer:
     a. Round w_i to the nearest quantization grid point: q_i = round(w_i / scale) * scale
     b. Compute the quantization error: err_i = w_i - q_i
     c. Update all remaining unquantized weights to compensate:
        w_j = w_j - (H^{-1}_{ji} / H^{-1}_{ii}) * err_i
  4. The layer output stays close to the original despite 4-bit weights
```

**Key insight:**
- Naive rounding: each weight is rounded in isolation, errors accumulate
- GPTQ: each rounding step is followed by a compensation step, errors are "absorbed" by remaining weights
- It uses the inverse Hessian to find the exact linear compensation that minimizes output error
- GPTQ is one-shot: it quantizes the entire model in a single pass, no retraining needed

**Why this matters:**
- GPTQ compresses a 7B model from 14GB to ~4GB with minimal quality loss
- It runs on a single GPU in minutes, not days
- It is the foundation of most 4-bit inference stacks (AutoGPTQ, ExLlama, llama.cpp)

---

### Real-Life Analogy

Replacing expensive ingredients in a recipe.
- **Original recipe:** Uses saffron, truffles, and wagyu beef. Delicious but costs $500 per serving.
- **Naive rounding:** Replace saffron with turmeric, truffles with mushrooms, and wagyu with ground beef — independently. The result is a bland, unbalanced mess because the flavor ratios are destroyed.
- **GPTQ approach:** Replace saffron with turmeric, then adjust the amount of turmeric and modify the other spices to compensate. Replace truffles with mushrooms, then increase the garlic and butter to restore the umami balance. Each substitution is followed by a compensation step.
- **Result:** A $20 dish that tastes 95% as good as the original. The substitutions are not independent; they are carefully compensated.

---

### Tiny Numeric Example

**Layer with 3 weights (simplified):**
```
Original weights: w = [2.3, -1.7, 0.4]
Quantization grid: multiples of 1.0  (so valid values are ..., -2, -1, 0, 1, 2, 3, ...)
```

**Naive round-to-nearest:**
```
q_naive = [2.0, -2.0, 0.0]
Error per weight: [0.3, 0.3, 0.4]
Total absolute error: 1.0
```

**GPTQ-style optimal rounding (simplified):**
```
Step 1: Quantize w_0 = 2.3 → 2.0, error = +0.3
  Compensate w_1 and w_2 using inverse Hessian coefficients.
  Suppose H^{-1} suggests w_1 should decrease by 0.2 to compensate:
  w_1 becomes -1.7 - 0.2 = -1.9
  w_2 becomes 0.4 - 0.05 = 0.35

Step 2: Quantize w_1 = -1.9 → -2.0, error = -0.1
  Compensate w_2:
  w_2 becomes 0.35 + 0.08 = 0.43

Step 3: Quantize w_2 = 0.43 → 0.0, error = +0.43
  No remaining weights to compensate.

Final quantized weights: [2.0, -2.0, 0.0]
```

The final weights look the same, but the path matters. The compensation steps ensure that the LAYER OUTPUT (which depends on all weights and the input activations) stays closer to the original. The per-weight error is the same, but the output error is minimized because correlated errors were redirected.

In a real layer with 4096 x 4096 weights, GPTQ reduces output error by 30-50% compared to naive rounding.

---

### Common Confusion

1. **"GPTQ is a training method."** No. GPTQ is post-training quantization. It does not update the model with gradient descent. It uses the Hessian to find optimal rounding and compensation in one forward pass.

2. **"GPTQ requires the full training dataset."** No. It needs only a small calibration set (typically 128–256 sequences of 2048 tokens each). The calibration data teaches the method which weights are sensitive, but it does not retrain the model.

3. **"GPTQ works for activations too."** No. GPTQ quantizes weights only. Activations are still computed in FP16 or FP32 during inference. Methods like AWQ and SmoothQuant handle activations.

4. **"GPTQ is better than all other quantization methods."** Not for every case. AWQ often preserves more quality for small models (under 7B) because it protects salient weight channels. GPTQ is better for large models and is faster to run.

5. **"GPTQ-quantized models are slower than FP16."** On most hardware, 4-bit inference is actually FASTER because less memory bandwidth is used. The bottleneck in inference is often reading weights from VRAM, not compute. Smaller weights = faster loading = faster generation.

6. **"GPTQ can quantize to any bit width."** Theoretically yes, but the AutoGPTQ ecosystem focuses on 4-bit and 3-bit. 2-bit GPTQ exists but requires grouping and often loses too much quality for general use.

7. **"GPTQ error compensation is exact."** It is optimal under a local quadratic approximation (the Hessian). If the true loss landscape is highly non-quadratic, the compensation is approximate. But for neural networks, the quadratic approximation is good enough.

---

### Where It Is Used in Our Code

`src/phase124/phase124_quantization_concepts.py` — We simulate weight quantization using both naive round-to-nearest and GPTQ-style optimal rounding with error compensation. We plot the weight distributions before and after quantization, and we show that GPTQ produces lower output error on synthetic activation data.

`src/phase124/phase124_quantization_colab.py` — We load a real model in FP16, quantize it to 8-bit and 4-bit using bitsandbytes (which implements GPTQ-style optimal rounding under the hood), and compare perplexity, inference speed, and model size across precision levels.

(End of file - total 97 lines)
