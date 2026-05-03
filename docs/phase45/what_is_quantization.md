## What Is Quantization?

---

### The Problem

A 70-billion parameter model in FP32 (32-bit floating point) requires 280 GB of memory just to store the weights. The best consumer GPU has 24 GB. Even data-center GPUs top out at 80 GB. How do you run these models at all?

---

### Definition

**Quantization** is the process of reducing the precision of model weights (and sometimes activations) from high-precision formats like FP32 or FP16 to lower-precision formats like INT8 or INT4.

**Memory savings:**
```
FP32: 32 bits per parameter
FP16: 16 bits per parameter  (2× smaller)
INT8:  8 bits per parameter  (4× smaller)
INT4:  4 bits per parameter  (8× smaller)

Llama-3-70B:
  FP16: 140 GB
  INT8:  70 GB
  INT4:  35 GB
```

**Why this works:**
- Neural network weights are not uniformly distributed. They cluster around zero with a bell-curve shape.
- You can map the full range of FP16 values to 256 INT8 bins or 16 INT4 bins with minimal loss.
- The model's representational power comes from the pattern of weights, not their 16th decimal place.

**Two types of quantization:**
1. **Post-Training Quantization (PTQ):** Quantize an already-trained model. Fast, no retraining needed.
2. **Quantization-Aware Training (QAT):** Train with quantization in the loop. Slower but higher quality.

---

### Real-Life Analogy

A high-resolution photograph.
- **FP32:** A RAW image file. 50 MB. Every pixel has full color depth.
- **FP16:** A high-quality PNG. 25 MB. Slightly less color depth, but your eye cannot tell the difference.
- **INT8:** A good JPEG. 12 MB. Some subtle gradients are lost, but the image is clearly recognizable.
- **INT4:** A heavily compressed JPEG. 6 MB. Blocky in places, but you can still tell it is a photo of a cat.

For most purposes, the JPEG is fine. You only need the RAW if you are doing professional color grading. Similarly, you only need FP16 if you are doing gradient descent. For inference, INT4 is often enough.

---

### Tiny Numeric Example

**Original FP16 weights:**
```
[0.0234, -0.8912, 1.4567, -0.0034, 0.5678]
Range: [-0.8912, 1.4567]
```

**INT8 quantization (8 bits = 256 values):**
```
scale = (max - min) / 255 = (1.4567 - (-0.8912)) / 255 = 0.00921
zero_point = round(-min / scale) = round(0.8912 / 0.00921) = 97

quantized = round((weight - min) / scale)
[ (0.0234 + 0.8912)/0.00921, (-0.8912 + 0.8912)/0.00921, ... ]
= [99, 0, 255, 94, 158]

Dequantized:
[ (99-97)×0.00921 - 0.8912, (0-97)×0.00921 - 0.8912, ... ]
= [0.0212, -0.8912, 1.4567, -0.0208, 0.5630]
```

**Error per weight:**
```
[0.0022, 0.0, 0.0, 0.0174, 0.0048]
Mean absolute error: 0.0049
```

The error is tiny compared to the weight magnitudes. And for inference, the model is robust to small perturbations.

---

### Common Confusion

1. **"Quantization destroys model quality."** Not necessarily. INT8 quantization typically causes <1% accuracy loss. INT4 causes 1-3% loss. For many applications, this is acceptable.

2. **"Quantization is just rounding."** It is more than rounding. It involves finding optimal scale factors, zero points, and sometimes grouping weights to handle outliers.

3. **"All weights should use the same scale."** No. Per-channel or per-group scaling handles outliers much better. One layer might have weights in [-0.1, 0.1] while another has [-10, 10].

4. **"Quantized models are slower."** Usually faster on hardware with INT8/INT4 support (modern GPUs, Apple Neural Engine, Qualcomm DSP). On unsupported hardware, dequantization overhead can slow things down.

5. **"You need the original FP16 model to run quantization."** Yes for post-training quantization. But once quantized, the model runs standalone.

6. **"Quantization and pruning are the same."** No. Quantization reduces precision. Pruning removes weights entirely (sets them to zero).

---

### Where It Is Used in Our Code

`src/phase45/phase45_quantization.py` — We quantize a trained neural network to INT8 and INT4 using per-channel scaling, then compare accuracy before and after quantization.
