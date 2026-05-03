## What Is FP8 Format?

---

### The Problem

Frontier language models now exceed one trillion parameters. Training at FP32 requires 4 bytes per parameter just for weights, plus activations, gradients, and optimizer states. At scale, memory bandwidth — not compute — becomes the bottleneck. BF16 halves the footprint but still wastes bits on values that do not need 16 bits of precision. INT8 saves memory but lacks dynamic range: a single outlier value collapses the entire tensor. FP8 was designed to split the difference, but it comes in two incompatible flavors. Pick the wrong one and your training run either underflows to zero or overflows to NaN.

---

### Definition

**FP8** is an 8-bit floating-point format defined by NVIDIA and adopted in the H100/H200 and Blackwell architectures. It encodes a sign bit, an exponent, and a mantissa in two variants: **E4M3** (4 exponent bits, 3 mantissa bits) and **E5M2** (5 exponent bits, 2 mantissa bits).

**Bit layouts:**
```
E4M3:  S EEEE MMM  (1 sign, 4 exponent, 3 mantissa)
E5M2:  S EEEEE MM  (1 sign, 5 exponent, 2 mantissa)
```

**Value formula (normalized numbers):**
```
value = (-1)^S * 2^(exponent - bias) * (1 + mantissa / 2^m_bits)
E4M3 bias = 7
E5M2 bias = 15
```

**Why E4M3 for weights and E5M2 for gradients:**
- **Weights** cluster near small magnitudes and need fine precision. E4M3 provides ~0.0625 granularity around 1.0 but only reaches ~448 in magnitude.
- **Gradients** have heavy-tailed distributions with occasional spikes. E5M2 reaches ~57,344 in magnitude, sacrificing precision to avoid overflow.

**Dynamic range comparison:**
```
Format    Min positive normal    Max finite    Bits
FP32      1.18e-38              3.40e38       32
BF16      1.18e-38              3.39e38       16
FP8 E4M3  1.53e-05              4.48e02       8
FP8 E5M2  6.10e-05              5.73e04       8
INT8      1.00e00 (quant step)  2.55e02       8
```

---

### Real-Life Analogy

Imagine two different measuring tapes.

**E4M3** is a tailor's tape measured in millimeters but only two meters long. It is incredibly precise for hems and cuffs, but if you try to measure a football field it simply runs out of tape. This is why it works for weights: most weights in a neural network are small values near zero, and the millimeter precision matters.

**E5M2** is a surveyor's tape measured in centimeters but stretching two kilometers. You lose the millimeter precision, but you can measure a runway without snapping the tape. Gradients during backpropagation are like surveying a landscape: most terrain is gentle, but occasional cliffs (exploding gradients) would break a short tape.

**The trade-off:** you cannot have both extreme precision and extreme range in eight bits. Frontier training frameworks like Transformer Engine automatically route weights through E4M3 and gradients through E5M2, treating the two formats as a matched pair rather than alternatives.

---

### Tiny Numeric Example

**Representable values near 1.0:**
```
Format    Neighbor below 1.0    Neighbor above 1.0    Gap
FP32      0.99999994            1.00000012            1.8e-07
BF16      0.99609375            1.00390625            7.8e-03
E4M3      0.87500000            1.00000000            1.3e-01
E5M2      0.75000000            1.00000000            2.5e-01
INT8      0.99607843            1.00392157            7.8e-03  (if scaled to [0,1])
```

**Quantizing a small tensor with both formats:**
```
Original values: [0.1, 0.5, 1.0, 10.0, 100.0]
E4M3 quantized:  [0.125, 0.5, 1.0, 10.0, 96.0]    ← 100.0 clipped to max 448
E5M2 quantized:  [0.125, 0.5, 1.0, 10.0, 96.0]    ← coarser around 1.0, handles 100.0 fine
```

**Dynamic range stress test:**
```
Value     E4M3 result        E5M2 result
0.001     0.00195 (rounded)  0.00195 (rounded)
1.0       1.0 (exact)        1.0 (exact)
100.0     96.0 (clipped)     112.0 (rounded)
1000.0    448.0 (clipped)    960.0 (rounded)
10000.0   448.0 (clipped)    8192.0 (rounded)
50000.0   448.0 (clipped)    49152.0 (rounded)
```

**The shift:** E4M3 preserves precision at the cost of range. E5M2 sacrifices precision to protect against overflow. A training system that uses only one format for everything would fail within the first hundred steps.

---

### Common Confusion

1. **"FP8 is just INT8 with a sign bit."** No. INT8 is a linear integer grid with uniform spacing. FP8 has exponential spacing: many representable values near zero and few near the maximum. The exponent gives it a dynamic range hundreds of times wider than INT8 at the same bit width.

2. **"E4M3 and E5M2 are interchangeable."** They are not. E4M3 has finer precision but clips at ~448. E5M2 reaches ~57,344 but its gaps near 1.0 are twice as large. Training frameworks assign them to different tensors explicitly.

3. **"FP8 is only for inference quantization."** FP8 tensor cores exist on H100 specifically for training. Inference-only quantization typically uses INT4 or INT8. FP8 training is what makes trillion-parameter models economically feasible.

4. **"If BF16 works, FP8 is unnecessary."** BF16 is 16 bits. FP8 is 8 bits. At scale, that is a 2x memory bandwidth saving and a 2x speedup on FP8 tensor cores. The difference between training a 400B model in three months versus six months is the difference between shipping and missing the market.

5. **"FP8 always degrades model quality."** When paired with delayed scaling and FP32 master weights, FP8 training reaches parity with BF16 training on most large language model benchmarks. The quality loss is measured in fractions of a percent, not points.

6. **"You can represent the same numbers in E4M3 and E5M2, just with different encodings."** They have different exponent biases, different mantissa widths, and different special-value rules. E4M3 uses all-ones exponent to extend the normal range; E5M2 reserves all-ones exponent for Inf and NaN. The formats are mathematically distinct.

7. **"FP8 is only supported on H100."** H100 was the first GPU with native FP8 tensor cores, but support has expanded to H200 and Blackwell. Cloud providers now offer FP8 instances as standard. However, older GPUs like T4 or V100 cannot run native FP8.

---

### Where It Is Used in Our Code

`src/phase111/phase111_fp8_concepts.py` — We simulate E4M3 and E5M2 quantization in pure NumPy, showing which real-valued numbers map to which FP8 codes. We compare dynamic range across FP32, BF16, FP8 E4M3, FP8 E5M2, and INT8, and we visualize the representable grids to illustrate why each format is suited to different tensors.
