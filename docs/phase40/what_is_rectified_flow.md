## What Is Rectified Flow?

---

### The Problem

Flow matching can use any path from noise to data. Curved paths are complicated and require many sampling steps. Straight-line paths are simpler and faster. How do we ensure the flow follows straight lines?

---

### Definition

**Rectified Flow** is a specific type of flow matching that uses **straight-line paths** between noise and data:

```
x_t = (1-t) × x_0 + t × x_1
```

Where:
- x_0 is the data point
- x_1 is the noise
- t goes from 0 (data) to 1 (noise)

**The velocity is constant along the path:**
```
u_t = x_1 - x_0
```

**Why straight lines matter:**
- Simpler to learn (constant velocity)
- Faster to sample (ODE solvers can take larger steps)
- Theoretically optimal (optimal transport)

**Iterative refinement:**
If the learned flow is not perfectly straight, you can "rectify" it:
1. Generate samples using the current flow
2. Train a new flow on straight-line paths between these samples and fresh noise
3. Repeat — each iteration makes the flow straighter

This is called **Reflow** and can reduce sampling to a single step!

---

### Real-Life Analogy

Flying from New York to London.
- **Curved path (general flow matching):** The plane takes a meandering route, adjusting course frequently. The flight takes 8 hours.
- **Straight-line path (Rectified Flow):** The plane flies the great-circle route directly. The flight takes 6.5 hours.
- **Perfectly straight path (Reflow):** A teleportation device moves instantly along the direct line. One step.

Rectified Flow finds the shortest path. Reflow iteratively improves the path until it is nearly instantaneous.

---

### Tiny Numeric Example

**Data point:** x₀ = [2.0, 3.0]
**Noise:** x₁ = [0.0, 0.0]

**Rectified Flow path:**
```
t=0.0: x = [2.0, 3.0]        (pure data)
t=0.5: x = [1.0, 1.5]        (halfway)
t=1.0: x = [0.0, 0.0]        (pure noise)
```

**Velocity (constant):**
```
u = x_1 - x_0 = [0.0, 0.0] - [2.0, 3.0] = [-2.0, -3.0]
```

**Verification at t=0.5:**
```
x_{0.5} = x_0 + 0.5 × u = [2.0, 3.0] + 0.5 × [-2.0, -3.0] = [1.0, 1.5]
```
Matches the linear interpolation.

**Non-rectified (curved) path:**
```
t=0.0: x = [2.0, 3.0]
t=0.5: x = [0.8, 1.2]        (not halfway!)
t=1.0: x = [0.0, 0.0]
```

The curved path is harder to learn and slower to sample because the velocity changes at each point.

---

### Common Confusion

1. **"Rectified Flow is a different model architecture."** No. It is a training objective. You can train a U-Net, Transformer, or MLP with Rectified Flow.

2. **"Reflow creates a perfect one-step model."** In theory, yes. In practice, 2–4 reflow iterations get close but perfect one-step generation is still hard.

3. **"Straight lines are always better than curves."** For sampling speed, yes. But curved paths might be easier to learn in some cases because they avoid regions where the velocity field is discontinuous.

4. **"Rectified Flow is only for continuous data."** It is designed for continuous data (images, audio). For discrete data like text, different approaches are needed.

5. **"Reflow is the same as distillation."** Both iterate, but differently. Reflow straightens the sampling path. Distillation trains a small model to mimic a large one.

---

### Where It Is Used in Our Code

`src/phase40/phase40_flow_matching.py` — Demonstrates straight-line interpolation and compares rectified flow paths to curved paths. Shows how constant velocity simplifies learning.
