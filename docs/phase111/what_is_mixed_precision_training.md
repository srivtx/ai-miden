## What Is Mixed Precision Training?

---

### The Problem

Training a large transformer in pure FP32 is stable but wasteful. Every matrix multiplication moves 4 bytes per operand across the memory bus, and the tensor cores on modern GPUs sit idle because they are optimized for narrower types. Training in pure FP16 or BF16 is faster but fragile: weight updates can underflow to zero, and gradient spikes can overflow to infinity. The challenge is to use fast low-precision arithmetic for the heavy lifting while keeping enough high-precision state to prevent divergence.

---

### Definition

**Mixed precision training** is a training strategy where the forward and backward passes execute in a low-precision format (FP16, BF16, or FP8) while a master copy of the weights and the optimizer state remain in FP32. After each forward-backward cycle, the low-precision gradients are used to update the high-precision master weights, which are then cast back down for the next step.

**How it works (Transformer Engine recipe):**
```
1. Master weights stored in FP32
2. Forward pass:
   a. Cast weights to FP8 (E4M3) with per-tensor scaling
   b. Run matmul on FP8 tensor cores
   c. Cast activations back to FP32 for loss computation
3. Backward pass:
   a. Gradients computed in FP8 (E5M2) with per-tensor scaling
   b. Cast gradients to FP32
4. Optimizer step:
   a. Update FP32 master weights with FP32 gradients
   b. Update FP32 optimizer state (Adam momentum, variance)
5. Repeat
```

**Delayed scaling:**
```
Instead of computing the exact max absolute value of a tensor every layer,
delayed scaling uses the max from the *previous* iteration to choose the scale.
This avoids a synchronization point and keeps the matmul pipeline full.
Recipe:
  scale = max_fp8 / max_abs_previous
  quantized = round(tensor * scale)
  next iteration: update max_abs from quantized tensor
```

**Per-tensor vs per-block scaling:**
- **Per-tensor:** one scale factor for the entire weight matrix. Simple, but outliers in a single row force the whole tensor to waste precision.
- **Per-block (tile):** one scale factor per 128x128 tile of a matrix. Outliers are isolated, and the rest of the tensor keeps finer precision. Used in Transformer Engine and Blackwell.

---

### Real-Life Analogy

Imagine a construction crew building a skyscraper.

**The master blueprint (FP32 weights)** lives in the architect's office in perfect detail. Every column width, beam angle, and bolt size is specified to the millimeter. The crew on the ground does not carry the full blueprint to every floor; they carry a compressed pocket guide (FP8 weights) that lists dimensions in centimeters. The pocket guide is faster to pass around and fits in a hip pouch.

When the crew measures a beam and finds it is 10.03 meters, they round it to 10.0 meters in the pocket guide, build it, and report the error back to the architect. The architect updates the master blueprint with the exact 10.03 meter measurement, then prints a new pocket guide for tomorrow. The building never drifts from the master plan because the high-precision source of truth is preserved.

**Delayed scaling** is like the architect noticing that yesterday's beams were all within 1% of spec, so today's pocket guide uses a coarser rounding grid. They do not remeasure every beam before printing the guide; they trust yesterday's distribution.

**The trade-off:** the crew works faster with the pocket guide, but if a single beam is an outlier (a 50-meter spire where everything else is 10 meters), the coarse grid snaps it to a wildly wrong value. Per-block scaling is like giving the spire crew a separate, finer guide while the rest of the building uses the coarse one.

---

### Tiny Numeric Example

**A weight tensor before and after FP8 quantization with scaling:**
```
Original FP32 weights:   [0.01, 0.5, 1.0, 5.0, 50.0]
Max abs = 50.0
Scale = 448 / 50.0 = 8.96

Scaled before round:     [0.0896, 4.48, 8.96, 44.8, 448.0]
E4M3 quantized:          [0.0898, 4.5, 9.0, 44.0, 448.0]   ← nearest representable
Dequantized (divide by scale):
                         [0.0100, 0.502, 1.005, 4.911, 50.0]
Quantization error:      [0.0000, 0.002, 0.005, -0.089, 0.000]
```

**Without scaling (naive cast):**
```
Original:  [0.01, 0.5, 1.0, 5.0, 50.0]
E4M3 cast: [0.0, 0.5, 1.0, 5.0, 48.0]    ← 0.01 underflows to 0, 50 clips to 48
Error:     [-0.01, 0.0, 0.0, 0.0, -2.0]
```

**Delayed scaling across two steps:**
```
Step 1: max_abs = 50.0 (from history), scale = 8.96
  Tensor max_abs actual = 60.0
  60.0 * 8.96 = 537.6 → clips to 448 → dequantized = 50.0 (error: -10.0)
  Update history: max_abs = 60.0

Step 2: max_abs = 60.0, scale = 7.47
  Tensor max_abs actual = 60.0
  60.0 * 7.47 = 448.2 → clips to 448 → dequantized = 60.0 (error: 0.0)
```

**The shift:** scaling transforms the FP8 grid so that the tensor's actual dynamic range maps to the format's representable range. Delayed scaling accepts one step of clipping to avoid a synchronization stall, then corrects on the next step.

---

### Common Confusion

1. **"Mixed precision means some layers use FP32 and others use FP8."** No. Mixed precision means the *compute* uses FP8 while the *state* uses FP32. Every layer participates in both: the matmul is FP8, but the weight update is FP32.

2. **"Delayed scaling is just guessing the scale."** It is not a guess; it is a one-step-delayed exact measurement. The scale from iteration t-1 is exact for iteration t-1. If tensor statistics are stable across steps, the delay is harmless. If statistics shift suddenly, one step clips before correction.

3. **"Master weights in FP32 double the memory footprint."** They increase it by 50%, not 100%. For every 1 byte of FP8 weights, you need 4 bytes of FP32 master weights, but activations and gradients are still FP8. The total increase is roughly 1.5x the FP8-only footprint, not 2x.

4. **"Per-block scaling is always better than per-tensor."** Per-block requires storing one scale per block, which adds memory overhead and complicates the kernel fusion. For small matrices, the overhead outweighs the precision gain. Transformer Engine switches strategies based on tensor size.

5. **"Mixed precision training is only for FP16."** The original NVIDIA Apex implementation used FP16. Modern systems use BF16 (better range) or FP8 (faster tensor cores). The principle is identical: low-precision compute, high-precision state.

6. **"FP8 mixed precision is automatic and requires no code changes."** It requires explicit casting, scaling, and format selection. Transformer Engine provides abstractions, but you still choose E4M3 vs E5M2, per-tensor vs per-block, and delayed vs immediate scaling. Misconfiguration causes NaN within minutes.

7. **"If a gradient overflows in FP8, the run is dead."** Transformer Engine detects infinities and NaNs, skips the update, and increases the scale factor for the next step. This is called automatic loss scaling in FP16, and the same recovery logic applies to FP8.

---

### Where It Is Used in Our Code

`src/phase111/phase111_fp8_training_colab.py` — We simulate mixed precision training on GPT-2 124M by keeping master weights in FP32, casting to simulated FP8 for forward and backward passes, and updating the FP32 master weights with FP32 gradients. We compare delayed scaling against no scaling to show how overflow and underflow behave, and we plot loss curves to demonstrate that FP8-simulated training tracks FP32 training.
