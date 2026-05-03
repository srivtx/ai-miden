## What Is Quantization-Aware Training?

---

### The Problem

Post-training quantization takes a model trained in FP32 and compresses it to INT8 or FP8. The weights were never told that rounding would happen, so values that sit halfway between quantization grid points suffer large errors. When those errors propagate through thirty transformer layers, the output distribution drifts. The accuracy drop is acceptable for some classifiers but catastrophic for language models, where a single misplaced logit changes the next token from "treat" to "terminate." The question is not whether to quantize, but how to make the model learn weights that are already near grid points before quantization ever happens.

---

### Definition

**Quantization-Aware Training (QAT)** is a training procedure in which fake quantization operations are inserted into the forward pass so the model experiences quantization noise during training. The gradients flow back through the rounding function using the straight-through estimator, and the weights evolve toward values that quantize with minimal error. LSQ (Learned Step Size Quantization) extends this by making the scale factor a learnable parameter.

**How it works:**
```
Standard training:
  weights_FP32 → matmul → loss → gradients_FP32 → update weights_FP32
  → quantize to INT8 later → accuracy drop

QAT:
  weights_FP32 → fake_quant(weights_FP32) → matmul → loss
  → gradients through fake_quant via straight-through estimator
  → update weights_FP32 toward quantization-friendly values
  → export to true INT8 → accuracy preserved
```

**Straight-through estimator (STE):**
```
Forward:   y = round(x / scale) * scale
Backward:  dy/dx = 1  (treat round as identity)
```
The STE is a lie in the backward pass: rounding is not differentiable. But the approximation works because the gradient signal still pushes weights toward regions where rounding error is small.

**LSQ (Learned Step Size Quantization):**
```
Instead of fixing scale = max_abs / 2^(bits-1),
make scale a trainable parameter s.
Forward:   y = round(x / s) * s
Backward:  dy/ds = sum( (x/s - round(x/s)) * sign(s) )
The model learns the step size that minimizes quantization error.
```

---

### Real-Life Analogy

Imagine a pianist practicing for a concert on a perfectly tuned grand piano, but the actual performance will be on an old upright with three sticky keys.

**Standard training** is practicing only on the grand piano. The pianist learns delicate passages that use every key smoothly. On the night of the concert, the sticky keys ruin the performance because the pianist never adapted to them.

**QAT** is practicing on the grand piano while randomly jamming three keys during rehearsal. The pianist learns to avoid those keys, rewrite passages to skip them, and apply extra force when they must be used. The performance on the upright is still not perfect, but it is recognizable.

**LSQ** goes further: instead of guessing which three keys are sticky, the pianist experiments with different key weights and regulations during practice, learning exactly how hard to press each sticky key to produce the right note. The step size is not imposed by the instrument; it is co-adapted with the music.

**The trade-off:** QAT adds noise to every forward pass, which acts as a regularizer. Some models actually generalize better with QAT than without it. But the training convergence is slower because the loss landscape becomes staircase-shaped around quantization boundaries.

---

### Tiny Numeric Example

**A single weight updated with STE:**
```
Target grid: INT8 with scale = 0.1
Weight w = 0.23
Forward quantized: round(0.23 / 0.1) * 0.1 = 0.2
Loss gradient dL/dy = -0.5
STE backward: dL/dw = dL/dy * 1 = -0.5
Weight update (lr=0.1): w_new = 0.23 - 0.1*(-0.5) = 0.28

Next step:
Forward quantized: round(0.28 / 0.1) * 0.1 = 0.3
The weight climbed from 0.23 toward 0.3, a grid point.
```

**Without QAT, the weight might settle at 0.23:**
```
Post-training quantization: round(0.23 / 0.1) * 0.1 = 0.2
Quantization error: 0.03 per weight
Across 1B weights: accumulated MSE = 0.03^2 * 1e9 = 9e5
```

**LSQ learning the step size:**
```
Initial scale s = 0.2
Weight w = 0.35
Quantized: round(0.35/0.2)*0.2 = 0.4
Error: (0.4 - 0.35)^2 = 0.0025
Gradient wrt s: (0.35/0.2 - 2) * sign(0.2) = -0.25
Update s (lr=0.01): s_new = 0.2 - 0.01*(-0.25) = 0.2025

After convergence, s settles near 0.175, giving finer resolution
where weights cluster and coarser resolution in the tails.
```

**The shift:** QAT does not just tolerate quantization; it reshapes the weight distribution to align with the quantization grid. LSQ further refines the grid itself.

---

### Common Confusion

1. **"QAT is the same as training in low precision."** No. In QAT, the matmul is still performed in FP32. Only the forward pass simulates quantization. True low-precision training computes matmuls in FP8 or INT8, which requires hardware support and different numerical recipes.

2. **"The straight-through estimator is mathematically correct."** It is not. The gradient of round(x) is zero almost everywhere and undefined at half-integers. STE approximates it as 1 because the exact gradient would kill all learning. It is a hack that happens to work.

3. **"QAT eliminates quantization error entirely."** It reduces error by pushing weights toward grid points, but it cannot create new grid points. If the optimal weight for a task is 0.23 and the grid is [0.2, 0.3], QAT may settle on 0.2 or 0.3, accepting a small bias to minimize variance.

4. **"LSQ is just grid search for the scale factor."** LSQ uses gradient descent on the scale, just like any other parameter. The scale is updated via backpropagation, not brute force. This allows per-layer or even per-channel scales to adapt during training.

5. **"QAT is only useful for INT8."** QAT applies to any quantization grid: INT4, INT8, FP8, or even ternary {-1, 0, 1}. The fake quantization operation simply changes its rounding function to match the target format.

6. **"QAT requires training from scratch."** You can apply QAT during fine-tuning. Start from a pretrained FP32 model, insert fake quantization, and fine-tune for a few epochs. This is common for adapting large models to edge deployment.

7. **"QAT makes training unstable because of the staircase loss."** The staircase effect is real, but modern optimizers (AdamW with weight decay) handle it well. The noise from fake quantization often acts as a regularizer that improves validation accuracy.

---

### Where It Is Used in Our Code

`src/phase111/phase111_fp8_training_colab.py` — We simulate QAT for FP8 by applying fake quantization to weights and activations during the forward pass of GPT-2 124M, using the straight-through estimator for gradients. We compare training with fake quantization against standard FP32 training to show that the model learns to tolerate FP8 rounding, keeping loss curves nearly identical.
