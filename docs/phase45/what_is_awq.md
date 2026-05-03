## What Is AWQ?

---

### The Problem

GPTQ quantizes all weights equally. But not all weights are equally important. Some weights have a much larger impact on the model output than others. If you could identify which weights matter most and protect them from aggressive quantization, could you get better quality at the same bit-width?

---

### Definition

**AWQ (Activation-aware Weight Quantization)** is a quantization method that protects a small fraction (typically 1%) of the most important weights by observing which weights produce the largest activations.

**The insight:**
- A weight's importance is not just its magnitude, but its magnitude TIMES the typical activation it sees.
- `importance_i = |w_i| × |activation_i|`
- Weights with high importance are kept in higher precision (FP16), while the rest are quantized to INT4 or INT3.

**How AWQ works:**
1. Run a small calibration dataset through the model
2. For each layer, compute the average activation magnitude per channel
3. Identify the top 1% of (weight × activation) products
4. Keep those weights in FP16
5. Quantize the remaining 99% to INT4
6. Apply per-channel scaling to further reduce error

**Why AWQ is powerful:**
- It achieves better accuracy than GPTQ at the same bit-width
- It can quantize to INT3 (3 bits!) with acceptable quality
- It is faster than GPTQ because it does not need the Hessian
- It is the default quantization in vLLM and TensorRT-LLM

---

### Real-Life Analogy

A symphony orchestra.
- **GPTQ:** All musicians play slightly simplified versions of their parts equally. The overall sound is decent but muddy.
- **AWQ:** The conductor identifies the 1% most critical notes — the solo violin entrance, the French horn call, the timpani crash. Those stay at full complexity. The background string section simplifies their parts more aggressively. The result sounds almost as good as the full score while requiring much less rehearsal time.

Not all notes are equal. AWQ recognizes this and protects the ones that matter most.

---

### Tiny Numeric Example

**Layer with 4 weights and typical activations:**
```
Weights:     w = [0.5, -2.0, 0.1, 0.3]
Activations: a = [1.0,  0.5, 3.0, 0.2]
```

**Importance scores:**
```
importance = [|0.5×1.0|, |-2.0×0.5|, |0.1×3.0|, |0.3×0.2|]
           = [0.5, 1.0, 0.3, 0.06]
```

**GPTQ (all weights quantized to INT4 with scale=0.5):**
```
q = [0.5, -2.0, 0.0, 0.5]
```
All weights rounded independently.

**AWQ (protect top 1 weight by importance):**
```
Most important: w_1 = -2.0 (score 1.0) -> keep in FP16
Quantize rest to INT4 with scale=0.5:
  w_0 = 0.5  -> 0.5
  w_2 = 0.1  -> 0.0
  w_3 = 0.3  -> 0.5

Result: [0.5, -2.0 (FP16), 0.0, 0.5]
```

**Why this is better:**
- w_1 = -2.0 has the highest impact on output (importance = 1.0)
- Keeping it exact prevents the largest single source of error
- The other weights have lower impact, so quantization error hurts less
- Overall output error is smaller than GPTQ's uniform approach

---

### Common Confusion

1. **"AWQ is just GPTQ with some weights skipped."** The skipping is based on activation-aware importance, not random or magnitude-based selection. And AWQ uses different scaling techniques.

2. **"AWQ needs more memory because some weights stay FP16."** Yes, slightly more than pure INT4. But the 1% FP16 weights add only 0.25 bits per parameter on average. A 4.25-bit model still uses much less memory than INT8.

3. **"AWQ works for any bit-width."** It shines at very low bit-widths (INT3, INT4). At INT8, the difference between AWQ and GPTQ is minimal.

4. **"AWQ requires the full training dataset."** No. Like GPTQ, it needs only a small calibration set (128-256 samples).

5. **"AWQ is slower at inference."** On modern GPUs with mixed-precision support, AWQ is actually faster than GPTQ because the FP16 weights can use fast tensor cores while the INT4 weights use efficient quantized paths.

---

### Where It Is Used in Our Code

`src/phase45/phase45_quantization.py` — We compute activation-aware importance scores for a small network, protect the top 10% of weights, and compare accuracy against uniform quantization.
