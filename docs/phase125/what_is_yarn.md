## What Is YaRN?

---

### The Problem

Position Interpolation scales all RoPE frequencies equally, which destroys the fine-grained local positional information that the model learned during pre-training. NTK-aware scaling tries to fix this by only scaling high frequencies, but it introduces another problem: when you extend context by a large factor (say 4× or 8×), the attention scores for distant tokens become unstable. The dot products between queries and keys at very long distances grow too large or too small, causing the softmax to collapse into sharp peaks or uniform mush. Temperature scaling helps in softmax, but how do you apply it specifically to the position-dependent parts of attention without breaking local behavior?

---

### Definition

**YaRN (Yet another RoPE extension)** is a RoPE scaling method that combines three ingredients: (1) frequency-aware interpolation where low frequencies are scaled less than high frequencies, (2) a computed scale factor that adjusts attention temperature based on the extension ratio, and (3) a mix of interpolation and extrapolation strategies for different frequency bands. YaRN achieves state-of-the-art perplexity when extending pretrained models to 2×-8× their original context length.

**How it works:**
```
YaRN has three components:

1. Frequency-aware interpolation:
   Instead of theta'_i = theta_i / s (PI) or the NTK formula,
   YaRN uses a piecewise approach:
   - For dimensions below a threshold: minimal scaling (preserve local detail)
   - For dimensions above a threshold: full scaling (extend range)
   - Smooth transition between the two regimes

2. Attention temperature scaling:
   The attention softmax is: softmax(Q @ K^T / sqrt(d_k))
   YaRN adds a temperature factor t to the scaled positions:
   softmax(Q @ K^T / (sqrt(d_k) * t))
   
   WHY? When positions are interpolated, the dot products Q@K^T
   are computed with compressed angles. The resulting distribution
   has different variance. Temperature scaling restores the
   variance the model was trained on.

   t is computed from the scale factor s:
   t = 0.1 * ln(s) + 1.0   (empirically derived)
   For s=2 (2× extension): t ≈ 1.07
   For s=4 (4× extension): t ≈ 1.14

3. Scale factor computation:
   s = L' / L  (new_length / original_length)
   But YaRN also supports dynamic scale factors at inference:
   the model can be trained with s=4 and then run at s=8
   with graceful degradation instead of catastrophic failure.
```

**Why this matters:**
- YaRN achieves lower perplexity than PI and NTK on long sequences
- The temperature scaling component is critical: without it, 8× extension fails
- YaRN can be applied at inference with ZERO fine-tuning (zero-shot), though fine-tuning improves quality
- It is the default scaling method in vLLM and other production serving engines for long context

---

### Real-Life Analogy

Imagine watching a movie on a small phone screen, then moving to a cinema screen that is 4× larger.

- **Position Interpolation:** You stretch the phone image to fill the cinema screen. Everything is blurry. You can see the whole picture, but you cannot read text or recognize faces. All details are smeared equally.
- **NTK-aware scaling:** You stretch only the background (the high-frequency detail) while keeping the actors at normal size. The actors look sharp, but the background texture looks weird and repetitive.
- **YaRN:** You use a smart projector that gradually changes the scaling factor from the center of the screen to the edges, AND you dim the lights slightly (temperature scaling) so the bright highlights do not blow out on the big screen. The result is watchable and natural. Some fine details are still lost at the extreme edges, but the overall experience is coherent.

The "temperature scaling" in this analogy is like dimming the lights: when you blow up an image, bright spots get painfully bright. Dimming preserves the dynamic range your eyes expect.

---

### Tiny Numeric Example

**Attention score variance without and with temperature scaling:**
```
Suppose we extend from 4K to 8K (s=2).

Without temperature scaling:
  Original attention at position 100 vs 200:
    Q_100 @ K_200^T = 12.5
  After PI scaling, same relative distance:
    Q'_100 @ K'_200^T = 11.2  (slightly different due to compression)
  But at the NEW maximum distance (8000 apart):
    Q'_0 @ K'_8000^T = 4.1    (model has never seen this magnitude)
  
  The variance of attention scores across all pairs changes.
  The softmax was trained on a specific score distribution.
  New distribution → softmax misbehaves.

With YaRN temperature scaling (t=1.07):
  Adjusted attention: (Q' @ K'^T) / t
  
  At original-scale distances:
    11.2 / 1.07 = 10.47  (close to original behavior)
  At new maximum distance:
    4.1 / 1.07 = 3.83    (scaled proportionally)
  
  The entire score distribution is scaled down by ~7%,
  preserving the relative shape the softmax expects.
```

**Scale factor and temperature for common extensions:**
```
Extension | Scale s | YaRN temp t | PI quality | YaRN quality
----------|---------|-------------|------------|-------------
2× (4K→8K) | 2.0   | 1.07        | Good       | Excellent
4× (4K→16K)| 4.0   | 1.14        | Poor       | Good
8× (4K→32K)| 8.0   | 1.21        | Broken     | Acceptable
16× (4K→64K)|16.0  | 1.28        | Broken     | Degraded
```

**The pattern:** YaRN temperature scaling is the difference between "works" and "broken" at 4×+ extension. PI falls off a cliff because it has no mechanism to correct attention variance.

---

### Common Confusion

1. **"YaRN is just NTK with a fancy name."** No. While both are frequency-aware, YaRN adds the critical attention temperature scaling component. NTK-aware scaling without temperature adjustment fails on 8× extensions. The temperature formula is derived empirically and is not present in pure NTK scaling.

2. **"YaRN requires training the temperature parameter."** The temperature formula is closed-form: t = 0.1 * ln(s) + 1.0. You compute it from the scale factor. There is nothing to train. However, fine-tuning the model WITH the computed temperature allows the attention layers to adapt to the scaled distribution.

3. **"Temperature scaling in YaRN is the same as softmax temperature in sampling."** Related concept, different application. Sampling temperature controls output randomness. YaRN temperature controls the sharpness of the attention distribution during the forward pass. Both divide logits by a scalar, but they serve different purposes and are applied at different stages.

4. **"YaRN works equally well for all model sizes."** Smaller models (3B-7B) benefit more from YaRN because their attention patterns are less robust. Large models (70B+) have learned more generalizable position representations and can sometimes extrapolate better even with simple PI. But YaRN still improves perplexity across all sizes.

5. **"YaRN can extend any context length indefinitely."** False. There is a hard limit based on how the model was trained. Beyond 8×-16× extension, even YaRN degrades because the feedforward layers and layer norms were never exposed to such long-range dependencies. YaRN fixes the embedding problem, not the representation problem.

6. **"YaRN needs the original training data to work."** No. YaRN is a mathematical transformation of the RoPE formula. You can apply it to any RoPE-based model without knowing anything about its training data. Fine-tuning does require long-sequence data, but the scaling itself is model-agnostic.

7. **"YaRN is slower than standard RoPE at inference."** The overhead is negligible — one extra division per attention head per layer. The temperature factor is a constant scalar. Real serving engines like vLLM implement YaRN with <1% latency overhead compared to standard RoPE.

---

### Where It Is Used in Our Code

`src/phase125/phase125_long_context_concepts.py` — We implement the YaRN attention temperature scaling formula and compare it against PI and NTK on simulated long sequences. We measure attention entropy (how sharp or flat the attention distribution is) across different context lengths, showing that YaRN preserves stable attention patterns where PI causes collapse.

`src/phase125/phase125_long_context_colab.py` — We configure the LLaMA-3.2-3B model with YaRN scaling parameters (scale factor, temperature) and fine-tune it on 8K token sequences. We evaluate needle-in-haystack recall accuracy across different positions, demonstrating that YaRN maintains attention stability even at tokens 6000-8000 where unscaled models fail completely.
