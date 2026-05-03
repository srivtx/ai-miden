## What Is Flow Matching?

---

### The Problem

DDPM diffusion (Phase 31) works but trains the model to predict noise — an indirect objective. Sampling requires 1000 small steps. Can we train a generative model with a simpler, more direct objective that also allows faster sampling?

---

### Definition

**Flow matching** trains a neural network to model a **probability flow** — a continuous path that transforms noise into data. Instead of predicting noise, the model learns the **velocity field** that describes how to move from noise to data:

```
dx/dt = v(x_t, t)
```

**Training objective:**
```
L = E[||v_θ(x_t, t) - u_t(x_t)||²]
```

Where `u_t` is the true velocity. For a straight-line path (optimal transport):
```
x_t = (1-t) × x_0 + t × x_1     (linear interpolation from data to noise)
u_t = x_1 - x_0                  (constant velocity)
```

The model learns to predict this velocity.

**Sampling:**
```
x_1 ~ N(0, I)          # start from noise
for t from 1 to 0:
    dx = v_θ(x_t, t) × dt
    x_{t-dt} = x_t - dx
```

With adaptive ODE solvers, only 10–50 steps are needed instead of 1000.

---

### Real-Life Analogy

**DDPM (Phase 31):** A restorer removes dust from a photo by guessing how much dust is on it at each step. They iterate 1000 times, slowly refining their guess.

**Flow matching:** A sculptor starts with a block of marble (noise) and knows exactly what the statue should look like (data). Instead of chipping randomly and checking, they learn the optimal carving path — which direction to move each point at every moment. They use a motorized tool (ODE solver) that adapts its speed to the complexity of each region, finishing in 20 smooth passes instead of 1000 tentative chips.

---

### Tiny Numeric Example

**Data point:** x₀ = [3.0, 2.0]
**Noise:** x₁ = [0.5, -0.5]

**Flow at t = 0.3:**
```
x_t = (1 - 0.3) × [3.0, 2.0] + 0.3 × [0.5, -0.5]
    = 0.7 × [3.0, 2.0] + 0.3 × [0.5, -0.5]
    = [2.1, 1.4] + [0.15, -0.15]
    = [2.25, 1.25]

u_t = x_1 - x_0 = [0.5, -0.5] - [3.0, 2.0] = [-2.5, -2.5]
```

**Model prediction:** v_θ([2.25, 1.25], 0.3) should equal [-2.5, -2.5]

**Loss:**
```
L = ||v_θ(x_t, t) - u_t||² = ||[-2.3, -2.4] - [-2.5, -2.5]||²
  = ||[0.2, 0.1]||² = 0.04 + 0.01 = 0.05
```

**Sampling step (dt = 0.1):**
```
x_{0.2} = x_{0.3} - v_θ(x_{0.3}, 0.3) × 0.1
        = [2.25, 1.25] - [-2.3, -2.4] × 0.1
        = [2.25, 1.25] - [-0.23, -0.24]
        = [2.48, 1.49]
```

The sample moves toward the data point x₀ = [3.0, 2.0].

---

### Common Confusion

1. **"Flow matching is completely different from diffusion."** No. It is a reformulation. Both gradually transform noise into data. Flow matching just uses a different training objective and sampling procedure.

2. **"Flow matching requires fewer steps because each step is cheaper."** No. Each step costs the same (one forward pass). The speedup comes from needing 20 steps instead of 1000 because ODE solvers can take larger steps in smooth regions.

3. **"Flow matching only works for images."** No. It works for any continuous data: audio, video, 3D shapes, molecular structures, and even text (in continuous token embeddings).

4. **"All flow matching uses straight lines."** Straight-line paths (Rectified Flow) are the simplest. General flow matching can use curved paths, but straight lines work well in practice.

5. **"Flow matching eliminates the need for neural networks."** No. You still need a neural network to predict the velocity field. The innovation is in the training objective, not the architecture.

---

### Where It Is Used in Our Code

`src/phase40/phase40_flow_matching.py` — A toy 2D flow matching model that learns straight-line paths from noise to data points. Visualizes flow lines and compares sampling steps to DDPM.
