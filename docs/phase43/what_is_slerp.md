## What Is SLERP?

---

### The Problem

When you average two model weights with simple linear interpolation, you are treating each parameter as independent. But neural network weights live in a high-dimensional space where the "straight line" between two points might pass through regions of terrible performance. Can we interpolate in a way that respects the geometry of the weight space?

---

### Definition

**SLERP (Spherical Linear Interpolation)** interpolates between two weight vectors along the great circle of a hypersphere, rather than along a straight line in Euclidean space.

**The formula:**
```
W_merged = sin((1-t) × θ) / sin(θ) × W_a + sin(t × θ) / sin(θ) × W_b
```

Where:
- `t` is the interpolation parameter (0 = all W_a, 1 = all W_b)
- `θ` is the angle between W_a and W_b: `θ = arccos( (W_a · W_b) / (||W_a|| × ||W_b||) )`

**Why SLERP is better than linear interpolation:**
- Preserves the magnitude (norm) of the weight vectors throughout interpolation
- Follows the shortest path on the sphere, which empirically correlates with better model performance
- Avoids the "shrinking" effect where linear interpolation produces smaller weights

**When to use SLERP:**
- Merging two models (not more than two directly — for N models, use sequential SLERP or other methods)
- When the two models are relatively close in weight space (small θ)
- When you want smooth interpolation for model soups or blending

---

### Real-Life Analogy

Flying from New York to Tokyo.
- **Linear interpolation:** Dig a straight tunnel through the Earth. The midpoint is deep underground in molten rock (terrible model performance).
- **SLERP:** Fly along the Earth's surface (great circle route). The midpoint is somewhere over the Arctic Circle — cold but survivable (functional model performance).

The surface of the Earth is a 2D sphere. Weight space is a million-dimensional sphere. SLERP stays on the "surface" (preserves norms) instead of cutting through the "interior" (where models perform poorly).

---

### Tiny Numeric Example

**Two weight vectors (simplified to 2D):**
```
W_a = [3.0, 0.0]     # Points along x-axis, magnitude = 3
W_b = [0.0, 3.0]     # Points along y-axis, magnitude = 3
```

**Linear interpolation at t = 0.5:**
```
W_linear = 0.5 × W_a + 0.5 × W_b = [1.5, 1.5]
Magnitude = sqrt(1.5² + 1.5²) = 2.12  # Shrunk!
```

**SLERP at t = 0.5:**
```
θ = arccos( (3×0 + 0×3) / (3 × 3) ) = arccos(0) = 90° = π/2 radians

W_slerp = sin(0.5 × π/2) / sin(π/2) × W_a + sin(0.5 × π/2) / sin(π/2) × W_b
        = sin(π/4) / 1 × [3, 0] + sin(π/4) / 1 × [0, 3]
        = 0.707 × [3, 0] + 0.707 × [0, 3]
        = [2.12, 2.12]
Magnitude = sqrt(2.12² + 2.12²) = 3.0  # Preserved!
```

**Result:**
- Linear interpolation shrinks the magnitude from 3.0 to 2.12
- SLERP preserves the magnitude at 3.0
- In neural networks, maintaining weight magnitudes often preserves activation statistics and model behavior

---

### Common Confusion

1. **"SLERP is only for 3D graphics."** It originated in graphics for quaternion interpolation, but works for any high-dimensional vector — including neural network weights.

2. **"SLERP can merge any number of models at once."** The standard formula is for two vectors. For N > 2, you can chain SLERP operations or use other methods like averaging in tangent space.

3. **"SLERP always beats linear interpolation."** Not always. For very close models (small θ), linear and SLERP are nearly identical. SLERP shines when models are moderately far apart.

4. **"SLERP preserves model performance by magic."** It preserves vector norms, which empirically correlates with better performance. But it does not guarantee the merged model will be good.

5. **"You need to normalize all weights before SLERP."** The formula handles different magnitudes automatically through the angle calculation. But models with wildly different scales may still merge poorly.

---

### Where It Is Used in Our Code

`src/phase43/phase43_model_merging.py` — The `slerp_merge()` function implements spherical linear interpolation between two fine-tuned models. We compare SLERP vs. linear interpolation on a 2D visualization of the weight trajectories.
