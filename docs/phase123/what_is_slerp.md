## What Is SLERP?

---

### The Problem

When you merge two models by simple linear interpolation — averaging their weights point-by-point — the result is often worse than either parent model. The averaged model produces confused, low-quality outputs. Why? Because neural network weights live on a high-dimensional manifold, and a straight line through Euclidean space cuts through regions where the model behaves badly. You need a path that stays ON the manifold of good models.

---

### Definition

**SLERP (Spherical Linear Interpolation)** is a method for interpolating between two points on a sphere (or hypersphere) instead of along a straight line. For model merging, it treats the weight vectors as points on a high-dimensional sphere and finds the shortest great-circle path between them. This preserves the magnitude and angular relationships of the weights, which keeps the model's internal representations coherent.

**How it works:**
```
Given two weight vectors: w1 and w2

1. Normalize both vectors to unit length:
   u1 = w1 / ||w1||
   u2 = w2 / ||w2||

2. Compute the angle between them:
   omega = arccos(clip(u1 . u2, -1, 1))

3. Interpolate at parameter t (0 <= t <= 1):
   w_slerp = (sin((1-t)*omega) / sin(omega)) * w1 + (sin(t*omega) / sin(omega)) * w2
```

**Key insight:**
- Linear interpolation: `w_lin = (1-t)*w1 + t*w2` — cuts through the interior
- SLERP: follows the surface of the sphere — stays on the manifold
- When omega is small, SLERP approximates linear interpolation
- When omega is large, SLERP preserves the geometry much better

**Why this matters:**
- SLERP produces merged models that retain more of each parent's quality
- It is the standard for creating model blends in the open-source community
- It generalizes to merging more than two models via recursive pairwise SLERP

---

### Real-Life Analogy

Flying between two cities on Earth.
- **Linear interpolation:** Digging a straight tunnel through the Earth from New York to London. The midpoint of that tunnel is deep underground in hot mantle rock. It is the shortest Euclidean path, but it goes through a place where no human can survive.
- **SLERP:** Flying along the Earth's surface, following the great-circle route. The path is longer in Euclidean terms but stays on the surface where humans (and airplanes) actually live.
- **Model weights:** A good model is like habitable surface. The interior of the Earth is like the space of bad weight configurations where outputs are gibberish. Linear interpolation dives into the mantle. SLERP stays in the atmosphere.

---

### Tiny Numeric Example

**Two 2D weight vectors (simplified for visualization):**
```
w1 = [3.0, 0.0]     ||w1|| = 3.0
w2 = [0.0, 4.0]     ||w2|| = 4.0
```

**Linear interpolation at t = 0.5:**
```
w_lin = 0.5 * [3, 0] + 0.5 * [0, 4] = [1.5, 2.0]
||w_lin|| = sqrt(1.5^2 + 2.0^2) = 2.5
```
The magnitude dropped from 3-4 down to 2.5. In a neural network, this dampening can suppress activations and make outputs weak or uncertain.

**SLERP at t = 0.5:**
```
u1 = [1.0, 0.0]
u2 = [0.0, 1.0]
omega = arccos(0) = 90 degrees = pi/2 radians

w_slerp = (sin(pi/4)/sin(pi/2)) * [3, 0] + (sin(pi/4)/sin(pi/2)) * [0, 4]
        = (0.707 / 1.0) * [3, 0] + (0.707 / 1.0) * [0, 4]
        = [2.12, 2.83]
||w_slerp|| = sqrt(2.12^2 + 2.83^2) = 3.54
```

**Comparison:**
```
Method        Result          Magnitude
Linear        [1.5, 2.0]      2.5  (shrunk)
SLERP         [2.12, 2.83]    3.54 (preserved geometry)
```

In a real model with millions of dimensions, the magnitude collapse from linear interpolation is subtle but pervasive. SLERP prevents it by respecting the angular structure.

---

### Common Confusion

1. **"SLERP is just a fancy name for averaging."** No. Averaging is linear interpolation. SLERP follows a geodesic on the hypersphere. The math is fundamentally different and produces different results, especially when the parent models are dissimilar.

2. **"SLERP only works for exactly two models."** You can merge N models by recursively applying SLERP: merge A and B into AB, then merge AB and C into ABC, and so on. There are also extensions like "multi-SLERP" that handle multiple points simultaneously.

3. **"SLERP preserves model quality perfectly."** It preserves geometry better than linear interpolation, but it does not eliminate task interference. If two models have fundamentally incompatible weights, neither SLERP nor linear interpolation will save the merge.

4. **"You need to normalize the entire model as one vector."** In practice, you apply SLERP layer-by-layer or even parameter-by-parameter, not to the flattened model as a single vector. This is because different layers live on different scales.

5. **"SLERP is slower than linear interpolation."** The extra cost is negligible: one dot product, one arccos, and a few sines per parameter group. The bottleneck is loading models into memory, not the interpolation math.

6. **"SLERP requires the models to be the same size."** True, but this is true of ALL weight-space merging. You cannot merge a 7B model with a 13B model in weight space. You would need knowledge distillation or other techniques.

7. **"SLERP is only for model weights, not activations."** The technique is general. It can interpolate embeddings, hidden states, or even token probability distributions. In diffusion models, SLERP is used to interpolate latent noise vectors for smooth image transitions.

---

### Where It Is Used in Our Code

`src/phase123/phase123_merging_concepts.py` — We simulate two specialist models, compute both linear interpolation and SLERP between them, and compare the resulting weight magnitudes and angular deviations. We show that SLERP preserves the L2 norm and cosine similarity much better than linear blending.

`src/phase123/phase123_merging_colab.py` — We merge two LoRA adapters using both naive averaging and SLERP, then evaluate the merged models on held-out tasks. The SLERP merge consistently outperforms linear interpolation when the specialist adapters diverge significantly.

(End of file - total 97 lines)
