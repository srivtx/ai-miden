## What Is Adam?

---

### The Problem

Vanilla SGD uses the same learning rate for every parameter and does not remember past gradients. If one parameter has consistently large gradients, it oscillates wildly. If another has tiny gradients, it barely moves. Can we give each parameter its own adaptive learning rate and use momentum to smooth out the path?

---

### Definition

**Adam (Adaptive Moment Estimation)** is an optimization algorithm that combines momentum (velocity from past gradients) with adaptive learning rates (per-parameter scaling based on gradient history).

**Adam maintains two running averages per parameter:**
1. **First moment (m):** The exponential moving average of gradients — like velocity
2. **Second moment (v):** The exponential moving average of squared gradients — like variance

**Update rule:**
```
At each step t:
  g_t = gradient at step t
  m_t = β1 × m_{t-1} + (1 - β1) × g_t       (momentum)
  v_t = β2 × v_{t-1} + (1 - β2) × g_t²      (adaptive scaling)
  
  m̂_t = m_t / (1 - β1^t)   (bias correction for m)
  v̂_t = v_t / (1 - β2^t)   (bias correction for v)
  
  θ_t = θ_{t-1} - α × m̂_t / (√v̂_t + ε)
```

**Default hyperparameters:**
- α (learning rate): 0.001
- β1 (momentum decay): 0.9
- β2 (variance decay): 0.999
- ε (numerical stability): 1e-8

**Why Adam works:**
- **Momentum:** Smooths the optimization path, reducing oscillation in high-curvature directions
- **Adaptive rates:** Parameters with consistently large gradients get smaller effective learning rates. Parameters with small gradients get larger rates.
- **Bias correction:** Compensates for initializing m and v at zero

---

### Real-Life Analogy

A hiker navigating a mountain range.
- **SGD:** The hiker takes a step based only on the current slope. In a steep, narrow valley, they zigzag back and forth across the valley floor because each step overshoots.
- **Momentum SGD:** The hiker has inertia. They roll down the valley more smoothly, but still move at the same speed in all directions.
- **Adam:** The hiker has a GPS that remembers the average steepness of every direction. In the narrow valley direction (steep, oscillating), the hiker takes tiny, careful steps. Along the valley floor (gently sloped), the hiker takes long, confident strides. They also have momentum, so they do not stop at every small bump.

Adam is the hiker with memory, inertia, and a personalized stride length for every direction.

---

### Tiny Numeric Example

**Parameter with oscillating gradients:**
```
Step 1: g = +5.0   m = 0.5,  v = 2.5,   update = -0.001 × 0.5 / √2.5 ≈ -0.0003
Step 2: g = -4.8   m = -0.43, v = 4.6,  update = -0.001 × -0.43 / √4.6 ≈ +0.0002
Step 3: g = +5.2   m = 0.38,  v = 6.9,  update = -0.001 × 0.38 / √6.9 ≈ -0.0001
```

**What happens:**
- m oscillates but with decreasing amplitude (momentum smooths it)
- v grows steadily (accumulating squared gradients)
- The effective learning rate shrinks (√v grows)
- After 10 steps, updates are tiny — the optimizer "learns" this parameter is noisy

**Parameter with consistent gradients:**
```
Step 1: g = +0.1   m = 0.01, v = 0.001, update = -0.001 × 0.01 / √0.001 ≈ -0.0003
Step 2: g = +0.1   m = 0.02, v = 0.002, update = -0.001 × 0.02 / √0.002 ≈ -0.0004
Step 3: g = +0.1   m = 0.03, v = 0.003, update = -0.001 × 0.03 / √0.003 ≈ -0.0005
```

**What happens:**
- m builds up steadily (consistent direction)
- v grows slowly (small squared gradients)
- The effective learning rate stays relatively large
- The parameter moves steadily in the right direction

---

### Common Confusion

1. **"Adam never needs learning rate tuning."** False. The default 0.001 works for many cases, but you still need to tune it. Adam just makes tuning less sensitive.

2. **"Adam is always better than SGD."** Not always. SGD with momentum + careful tuning sometimes generalizes better on vision tasks. Adam dominates NLP and most other domains.

3. **"The second moment v is the variance."** It is the exponential moving average of squared gradients, which is related to variance but not exactly the same. It tracks the magnitude of gradients, not their spread around a mean.

4. **"Adam's bias correction is optional."** Without it, the first few updates are near-zero because m and v start at 0. Bias correction compensates for this startup phase.

5. **"Adam handles all optimization problems."** It struggles with very sparse gradients (e.g., embeddings with rare words). Variants like AdamW and SparseAdam fix this.

---

### Where It Is Used in Our Code

`src/phase49/phase49_advanced_optimizers.py` — We compare SGD, Momentum SGD, RMSprop, and Adam on a challenging optimization landscape. Adam converges fastest with the least tuning.
