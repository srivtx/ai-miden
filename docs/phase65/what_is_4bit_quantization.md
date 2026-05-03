## What Is 4-bit Quantization?

---

### The Problem

A 7-billion-parameter model stored in 32-bit floating point needs 28 GB of memory just for the weights. In 16-bit, it needs 14 GB. Even 16-bit is too large for many consumer GPUs. You need a way to compress each weight to just 4 bits (16 possible values) while preserving enough precision that the model still works. Naively rounding to 4-bit uniform integers destroys quality because neural network weights are not uniformly distributed — they cluster around zero in a bell curve.

---

### Definition

**4-bit Quantization** is the process of mapping continuous floating-point weights to 4-bit integers (0-15) using a learned or computed quantization grid, then storing and computing with those compressed values. **NF4 (Normal Float 4-bit)** is the dominant scheme for LLMs, which uses a non-uniform grid that matches the normal distribution of neural network weights.

**NF4 quantization steps:**
```
1. Block the weights into groups (e.g., 64 weights per block)
2. For each block, find the maximum absolute value (scale)
3. Map each weight to the nearest NF4 quantile value (16 precomputed levels)
4. Store: 4-bit index per weight + 16-bit scale per block + 16-bit zero-point
5. Dequantize: weight = (NF4_value[index] × scale) + zero_point
```

**NF4 quantile values (precomputed for N(0,1)):**
```
[-1.0, -0.696, -0.525, -0.394, -0.284, -0.184, -0.091, 0.0,
 0.091, 0.184, 0.284, 0.394, 0.525, 0.696, 1.0]
```

**Key insight:**
- Uniform 4-bit: 16 evenly spaced values — wastes precision in the dense center
- NF4: 16 values spaced to match the normal distribution — more precision where weights actually live
- Blocking: each 64-weight group gets its own scale, preserving local variance

**Why this matters:**
- 8× memory reduction versus FP32, 4× versus FP16
- NF4 preserves model quality far better than uniform 4-bit
- Blocking adapts to local weight distributions within each layer

---

### Real-Life Analogy

A tailor measuring customers for suits.
- **FP32 (no quantization):** You measure every customer to the nearest millimeter. Extremely precise, but you need a huge notebook to record all the numbers.
- **Uniform 4-bit:** You round every measurement to the nearest 5 centimeters. A 173cm person and a 177cm person both get recorded as 175cm. Most people are average height, so the 5cm buckets are too coarse where it matters most.
- **NF4:** You use smaller buckets near average height (1cm precision for 160-180cm) and larger buckets for extreme heights (5cm precision for very short or very tall). You still only have 16 total buckets, but they are placed where most customers actually fall.
- **Blocking:** You use different bucket sizes for men and women, because their height distributions differ. Each group gets its own tailored measurement scale.

---

### Tiny Numeric Example

**Weight block (8 values, normally distributed):**
```
W = [0.05, -0.12, 0.33, -0.45, 0.08, -0.02, 0.21, -0.30]
abs_max = 0.45  (scale for this block)
```

**NF4 quantiles (scaled to this block):**
```
quantiles = [-0.45, -0.313, -0.236, -0.177, -0.128, -0.083, -0.041, 0.0,
              0.041, 0.083, 0.128, 0.177, 0.236, 0.313, 0.45]
```

**Quantize each weight to nearest quantile index:**
```
W:        [0.05,   -0.12,   0.33,   -0.45,   0.08,   -0.02,   0.21,   -0.30]
Nearest:  [0.041,  -0.128,  0.313,  -0.45,   0.083,  -0.0,    0.236,  -0.313]
Index:    [8,       4,      13,      0,       9,      7,      12,      1]
Stored:   8 indices × 4 bits = 32 bits
          + 16-bit scale = 48 bits total
vs. FP32: 8 floats × 32 bits = 256 bits
Reduction: 256 / 48 = 5.3× for this small block (larger blocks approach 8×)
```

**Dequantize:**
```
W_deq = [0.041, -0.128, 0.313, -0.45, 0.083, 0.0, 0.236, -0.313]
Error:  [0.009, 0.008, 0.017, 0.0,   0.003, 0.02, 0.026, 0.013]
```

The errors are small and symmetric, so they largely cancel out during matrix multiplication.

---

### Common Confusion

1. **"4-bit means each weight is exactly one of 16 decimal values."** No. The values are computed from the NF4 quantiles multiplied by the block scale. The actual representable values depend on each block's scale, so different blocks have different grids.

2. **"NF4 is the same as FP4."** No. FP4 is a 4-bit floating-point format with 1 sign bit, 2 exponent bits, and 1 mantissa bit. NF4 is a data-dependent quantile-based format that assumes normally distributed weights. NF4 typically outperforms FP4 for LLM weights.

3. **"Quantization is done once and never changes."** During inference, yes. During QLoRA training, the base weights stay quantized and frozen; only the LoRA adapters (in full precision) are updated.

4. **"Blocking means quantizing layer by layer."** No. Blocking means splitting each weight matrix into small contiguous chunks (e.g., 64 values) and quantizing each chunk independently. This preserves local structure better than one global scale.

5. **"Dequantization happens once at load time."** No. In QLoRA, weights are dequantized on-the-fly during every forward pass. They stay in 4-bit storage in GPU memory and are dequantized in registers/cache just before the matmul.

6. **"4-bit quantization works for activations too."** It can, but QLoRA specifically quantizes only weights. Activation quantization (INT8, INT4) is a separate technique used in inference engines like TensorRT and ONNX Runtime.

7. **"You need the original FP16 weights to dequantize."** No. You only need the 4-bit indices + scale + zero-point per block. The original weights are discarded after quantization.

---

### Where It Is Used in Our Code

`src/phase65/phase65_qlora.py` — We implement a simplified uniform 4-bit quantizer and an NF4-like quantizer on a toy weight matrix, showing the memory reduction and quantization error distribution.

`src/phase65/phase65_qlora_colab.py` — We load a real model with `BitsAndBytesConfig(quantization_config=bnb_config, load_in_4bit=True, bnb_4bit_quant_type="nf4")`, which applies true NF4 blocking via the BitsAndBytes library.
