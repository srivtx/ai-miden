## What Is Warmup?

---

### The Problem

At the very start of training, gradients can be huge and chaotic. The model's weights are random, so every layer produces nonsense activations. If you use a high learning rate immediately, the model diverges — loss explodes to NaN. But if you use a low learning rate, training is unnecessarily slow after the first few steps. How do you start safely and then speed up?

---

### Definition

**Warmup** is a training phase where the learning rate starts at zero (or near zero) and linearly increases to the target learning rate over the first W steps or epochs.

**Linear warmup formula:**
```
LR(step) = target_LR × min(step / warmup_steps, 1.0)
```

**Example:**
```
Target LR = 0.001, warmup_steps = 1000
Step 0:    LR = 0.0
Step 250:  LR = 0.00025
Step 500:  LR = 0.0005
Step 750:  LR = 0.00075
Step 1000: LR = 0.001 (warmup complete)
```

**Why warmup is essential:**
- Early gradients are large because the model is far from any good solution
- Small LR prevents the model from jumping to a terrible region of parameter space
- Once the model stabilizes (after ~1000 steps), full LR accelerates progress
- Without warmup, training large transformers often diverges

**Variants:**
- **Linear warmup:** Straight-line increase (most common)
- **Exponential warmup:** LR increases faster near the end of warmup
- **Constant warmup:** LR stays at a small constant for W steps, then jumps

---

### Real-Life Analogy

Warming up a car engine.
- **No warmup:** You start the car and immediately floor the accelerator. Cold oil has not reached the engine parts. The engine stalls or gets damaged.
- **Warmup:** You start the car and let it idle for 30 seconds. Oil circulates, temperature rises, parts expand to proper tolerances. Then you accelerate smoothly. The engine performs optimally.

Neural networks are the same. The first steps are "cold" — gradients are chaotic, batch statistics are unstable, activations are extreme. Warmup lets the model "idle" until the optimization landscape becomes navigable.

---

### Tiny Numeric Example

**Model with one parameter, true value = 5.0.**

**Without warmup (LR = 0.1 from step 0):**
```
Step 0: w = 0.0, gradient = -50.0 (huge because far from target)
        update = -0.1 × (-50) = +5.0
        w = 5.0 (by luck, perfect!)
Step 1: gradient = +2.0 (noisy)
        update = -0.1 × 2 = -0.2
        w = 4.8
Step 2: gradient = -3.0
        update = +0.3
        w = 5.1
```
The model oscillates around the target because the LR is too high for the noisy gradient.

**With warmup (LR increases from 0 to 0.1 over 5 steps):**
```
Step 0: LR = 0.0,  w stays at 0.0
Step 1: LR = 0.02, gradient = -50, update = +1.0, w = 1.0
Step 2: LR = 0.04, gradient = -40, update = +1.6, w = 2.6
Step 3: LR = 0.06, gradient = -24, update = +1.44, w = 4.04
Step 4: LR = 0.08, gradient = -10, update = +0.8, w = 4.84
Step 5: LR = 0.10, gradient = -2, update = +0.2, w = 5.04
```
The approach is smoother and more stable. The model does not overshoot as wildly.

---

### Common Confusion

1. **"Warmup is only for huge models."** It helps at all scales, but divergence without warmup is catastrophic for large models.

2. **"Warmup slows down training."** It adds steps, but prevents divergence that would require restarting training. Net effect: faster overall.

3. **"Warmup should be 10% of total training."** Typical is 1-3% of total steps (e.g., 2000 warmup steps out of 100,000 total). Some use 0.5%.

4. **"You can use warmup with any schedule."** Yes. Warmup is almost always combined with cosine decay or step decay. It is the "start phase" of the schedule.

5. **"Warmup fixes bad initialization."** It helps, but does not fix terrible initialization. Good init + warmup is the combination.

---

### Where It Is Used in Our Code

`src/phase49/phase49_advanced_optimizers.py` — We show training with and without warmup. Without warmup, a deep network diverges in the first 10 steps. With warmup, it converges smoothly.
