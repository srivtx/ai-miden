## What Is a Learning Rate Schedule?

---

### The Problem

If the learning rate is too high, the model bounces around and never settles. If it is too low, training takes forever. But what if the ideal learning rate changes during training? At the start, you want large steps to make fast progress. Near the end, you want tiny steps to fine-tune the solution. Can the learning rate change automatically?

---

### Definition

A **learning rate schedule** is a function that changes the learning rate over the course of training.

**Common schedules:**

**1. Step Decay:**
```
LR = initial_LR × drop_factor^(epoch // drop_every)
```
Every N epochs, multiply LR by 0.1 (or 0.5).

**2. Exponential Decay:**
```
LR = initial_LR × e^(-decay_rate × epoch)
```
Smooth, continuous decay.

**3. Cosine Annealing:**
```
LR = LR_min + 0.5 × (LR_max - LR_min) × (1 + cos(π × epoch / total_epochs))
```
Starts at LR_max, smoothly decreases to LR_min following a cosine curve. Popular for vision models.

**4. Warmup + Cosine (used in LLMs):**
```
Phase 1 (warmup): LR linearly increases from 0 to peak over first W steps
Phase 2 (cosine): LR follows cosine decay from peak to near-zero
```

**Why schedules matter:**
- **High LR early:** Escape bad local minima, make rapid progress
- **Low LR late:** Settle into the minimum, avoid oscillation
- **Warmup:** Prevents early instability (gradients are large and noisy at step 0)

---

### Real-Life Analogy

Driving to a destination.
- **Constant LR:** You drive at exactly 60 mph the entire trip. On the highway, this is fine. In a parking lot, you crash. In a school zone, you get a ticket.
- **Step decay:** You drive 60 mph on the highway, then 30 mph on city streets, then 10 mph in the parking lot. Discontinuous but effective.
- **Cosine annealing:** You smoothly decelerate from 60 mph to 0 mph as you approach your destination. No sudden braking.
- **Warmup + cosine:** You start at 0 mph, accelerate smoothly to 60 mph over the first minute (warmup), then smoothly decelerate to 0 mph as you arrive.

The best drivers adjust speed continuously based on where they are in the journey.

---

### Tiny Numeric Example

**Training for 100 epochs, initial LR = 0.1:**

**Step decay (drop by 0.5 every 30 epochs):**
```
Epoch 0-29:  LR = 0.100
Epoch 30-59: LR = 0.050
Epoch 60-89: LR = 0.025
Epoch 90-99: LR = 0.0125
```

**Cosine annealing:**
```
Epoch 0:  LR = 0.100
Epoch 25: LR = 0.079
Epoch 50: LR = 0.050
Epoch 75: LR = 0.021
Epoch 99: LR = 0.0005
```

**Warmup (10 epochs) + cosine (90 epochs):**
```
Epoch 0:  LR = 0.000 (warmup start)
Epoch 5:  LR = 0.050 (warmup mid)
Epoch 10: LR = 0.100 (peak, warmup end)
Epoch 50: LR = 0.050 (cosine mid)
Epoch 99: LR = 0.0005 (cosine end)
```

**Impact on training:**
- Without schedule: loss plateaus at 0.15 after 50 epochs
- With cosine: loss reaches 0.08 after 100 epochs
- With warmup + cosine: loss reaches 0.06 (warmup prevents early divergence)

---

### Common Confusion

1. **"LR schedules are optional."** For small datasets, yes. For training large models to convergence, they are essential. GPT-4, Llama, and all frontier models use schedules.

2. **"Lower LR is always better at the end.""** Generally yes, but some techniques like "restarts" (SGDR) temporarily increase LR to escape local minima.

3. **"Warmup is only for large models."** Warmup helps at all scales, but it is critical for large models where early gradients can be enormous.

4. **"All schedules work equally well."** Cosine is generally best for vision. Warmup + cosine is standard for LLMs. Step decay is simpler but sometimes less optimal.

5. **"The schedule is part of the optimizer."** It is separate. The optimizer uses the current LR. The schedule decides what the current LR should be.

---

### Where It Is Used in Our Code

`src/phase49/phase49_advanced_optimizers.py` — We compare constant LR, step decay, and cosine annealing on a deep network. Cosine with warmup converges to the lowest loss.
