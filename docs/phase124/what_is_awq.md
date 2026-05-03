## What Is AWQ?

---

### The Problem

GPTQ quantizes all weights uniformly, treating every parameter as equally important. But in a neural network, some weight channels have outsized impact on the output. A small error in a "salient" channel — one that corresponds to a frequently activated feature — can cause a large drop in accuracy. Meanwhile, many other channels are rarely activated and can tolerate aggressive quantization. How do you protect the important 1% of weights while quantizing the rest aggressively?

---

### Definition

**AWQ (Activation-aware Weight Quantization)** is a quantization method that protects salient weight channels by scaling them before quantization. It identifies which channels matter most by looking at activation magnitudes (not just weight magnitudes), then applies a per-channel scaling factor that reduces the quantization error on those critical channels.

**How it works:**
```
1. Run calibration data through the layer and collect activation statistics
2. Identify salient channels: those with the largest average activation magnitudes
3. Find optimal per-channel scaling factors s_c by grid search:
   s_c minimizes: || activation * (w / s_c quantized then rescaled - w) ||
4. Scale weights: w_scaled = w * s_c
5. Quantize scaled weights to 4-bit: q = round(w_scaled / scale)
6. At inference, de-quantize and divide by s_c: w_eff = (q * scale) / s_c
```

**Key insight:**
- Salient channels are determined by ACTIVATIONS, not weights
- A weight with small magnitude but large activation gradient is more important than a large weight on a dead neuron
- Scaling before quantization moves the weight distribution away from quantization grid boundaries, reducing round-off error on critical channels
- AWQ typically outperforms GPTQ on small models (1B–7B) where every channel matters

**Why this matters:**
- AWQ preserves more quality than GPTQ for models under 7B parameters
- It requires no backpropagation or retraining — it is purely post-training
- It is the default recommendation for deploying small models on edge devices

---

### Real-Life Analogy

A museum restoring an old painting.
- **The painting:** Has a detailed face in the center and a blurry background.
- **Naive restoration (GPTQ):** You compress the entire image to the same resolution. The face loses critical detail, and the blurry background is stored at unnecessarily high quality. The result looks bad because the important part was treated the same as the unimportant part.
- **AWQ approach:** You identify the face as the "salient" region. You store the face at high resolution and the background at very low resolution. To do this without changing the file format, you digitally "scale up" the face region before compression, then scale it back down when displaying. The compression sees the face as larger values and allocates more bits to it.
- **Result:** The same total file size, but the face looks crisp and the background is still blurry (which is fine because it was blurry originally).

---

### Tiny Numeric Example

**Two weight channels with identical weight distributions but different activation magnitudes:**
```
Channel A (salient, high activation):
  Weights: [0.31, -0.29, 0.33, -0.27]
  Average activation magnitude: 12.5

Channel B (non-salient, low activation):
  Weights: [0.31, -0.29, 0.33, -0.27]
  Average activation magnitude: 0.8
```

**Quantization grid (4-bit, scale = 0.2): valid values are ..., -0.4, -0.2, 0.0, 0.2, 0.4, ...**

**Naive rounding (GPTQ):**
```
Channel A quantized: [0.2, -0.2, 0.4, -0.2]
Channel A error:     [0.11, -0.09, -0.07, -0.07]
Weighted output error: |error| * activation = [1.38, 1.13, 0.88, 0.88] = total 4.27

Channel B quantized: [0.2, -0.2, 0.4, -0.2]
Channel B error:     [0.11, -0.09, -0.07, -0.07]
Weighted output error: |error| * activation = [0.09, 0.07, 0.06, 0.06] = total 0.27
```

**AWQ with scaling factor s = 2.0 for Channel A:**
```
Channel A scaled weights: [0.62, -0.58, 0.66, -0.54]
Channel A quantized:      [0.6, -0.6, 0.6, -0.4]  (grid: ..., -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, ...)
Wait — with scale=0.2, quantized values are multiples of 0.2.
Better: scaled weights / 0.2 = [3.1, -2.9, 3.3, -2.7] → round → [3, -3, 3, -3]
De-quantized scaled: [0.6, -0.6, 0.6, -0.6]
Rescale by 1/s:      [0.30, -0.30, 0.30, -0.30]

Channel A AWQ error: [0.01, 0.01, 0.03, 0.03]
Weighted output error: [0.13, 0.13, 0.38, 0.38] = total 1.01
```

**Comparison:**
```
Method     Channel A error    Channel B error
Naive      4.27               0.27
AWQ        1.01               0.27
```

AWQ reduced the salient channel's error by 76% while leaving the non-salient channel unchanged. In a full model, this protection of critical channels adds up to significantly better perplexity and generation quality.

---

### Common Confusion

1. **"AWQ needs to know the downstream task."** No. AWQ uses only activation statistics from generic calibration data. It does not need labels or task-specific data. The salience is determined by how often a channel activates, not by task accuracy.

2. **"AWQ is slower than GPTQ at inference."** They are comparable. The per-channel scaling in AWQ is fused into the de-quantization kernel. The extra multiply-by-scale is negligible compared to the memory bandwidth savings of 4-bit weights.

3. **"AWQ protects weights with large magnitudes."** Not necessarily. AWQ protects weights in channels with large ACTIVATIONS. A small weight on a highly active channel is more important than a large weight on a dead channel.

4. **"AWQ requires retraining."** No. Like GPTQ, AWQ is post-training. It finds scaling factors via grid search on calibration data. No gradients, no backpropagation.

5. **"AWQ only works for 4-bit."** It is most commonly used at 4-bit, but the principle applies to any quantization level. The benefit over uniform quantization is largest when bit width is small.

6. **"AWQ and GPTQ are mutually exclusive."** They can be combined. Some implementations use GPTQ's optimal rounding within AWQ's scaled framework, getting the best of both: salient-channel protection plus error compensation.

7. **"AWQ scaling factors are learned per layer."** They are learned per CHANNEL within each layer. A layer with 4096 output channels has 4096 scaling factors. This fine granularity is why AWQ outperforms coarse methods.

---

### Where It Is Used in Our Code

`src/phase124/phase124_quantization_concepts.py` — We simulate two weight channels with identical weights but different activation magnitudes, quantize them with naive rounding and with AWQ-style scaling, and compare the output error. We show that AWQ reduces error on salient channels without wasting precision on inactive ones.

`src/phase124/phase124_quantization_colab.py` — We load a real model, quantize it with both GPTQ-style uniform quantization and AWQ-style activation-aware quantization, and compare perplexity on wikitext-2. The AWQ-quantized model achieves lower perplexity, especially at 4-bit precision.

(End of file - total 97 lines)
