## What Is RoPE?

---

### The Problem

Transformers need to know WHERE each token is in a sequence. Early approaches used absolute position embeddings (learned vectors added to token embeddings). But these do not generalize to sequences longer than training. How do you encode position in a way that naturally handles relative distances and extrapolates to unseen lengths?

---

### Definition

**RoPE (Rotary Position Embedding)** encodes position by rotating the query and key vectors in 2D subspaces using sinusoidal angles that depend on position and dimension.

**The formula for a single dimension pair (i, i+1):**
```
[ q_i'  ]   [ cos(m×θ_i)   -sin(m×θ_i) ] [ q_i ]
[ q_i+1'] = [ sin(m×θ_i)    cos(m×θ_i) ] [ q_i+1]
```

Where:
- `m` is the token position
- `θ_i = base^(-2i/d)` is the rotation angle frequency for dimension i
- `base` is typically 10,000
- `d` is the head dimension

**Key properties:**
1. **Relative distances are preserved:** The dot product of a query at position m and a key at position n depends only on (m - n), not on their absolute positions
2. **Extrapolates naturally:** The formula works for any position m, even beyond training range
3. **No learned parameters:** Unlike absolute embeddings, RoPE does not add trainable weights

**Why RoPE is special:**
- When you compute attention scores (Q @ K^T), the relative position term `m - n` appears naturally in the dot product
- This means the model learns to attend based on HOW FAR APART tokens are, not just WHERE they are
- Extending context is just a matter of using larger `m` values

---

### Real-Life Analogy

A clock face.
- **Absolute embeddings:** Each hour has a unique picture (1 = sunrise, 2 = breakfast, 3 = morning commute). If you see hour 25, you have no idea what picture to use because you were only trained on hours 1-12.
- **RoPE:** Each hour is an angle on the clock. Hour 1 is 30 degrees, hour 2 is 60 degrees, hour 13 is 390 degrees (which is 30 degrees + full circle). The clock naturally wraps around. You can extend to hour 1000 because angles just keep rotating.

The attention score between two tokens is like measuring the angle between two clock hands. It only depends on how far apart they are, not what time it is.

---

### Tiny Numeric Example

**Dimension i = 0, base = 10000, d = 4:**
```
θ_0 = 10000^(-0/4) = 10000^0 = 1.0 radian per position
```

**Query vector at position m = 2:**
```
Original q = [1.0, 0.5]
Rotation angle = m × θ_0 = 2 × 1.0 = 2.0 radians

cos(2.0) = -0.416, sin(2.0) = 0.909

q_rotated = [ cos(2.0)×1.0 - sin(2.0)×0.5,  sin(2.0)×1.0 + cos(2.0)×0.5 ]
          = [ -0.416 - 0.455,  0.909 - 0.208 ]
          = [ -0.871,  0.701 ]
```

**Key at position n = 5:**
```
Rotation angle = 5 × 1.0 = 5.0 radians
cos(5.0) = 0.284, sin(5.0) = -0.959

k_rotated = [ 0.284×1.0 - (-0.959)×0.5,  -0.959×1.0 + 0.284×0.5 ]
          = [ 0.284 + 0.480,  -0.959 + 0.142 ]
          = [ 0.764,  -0.817 ]
```

**Attention score:**
```
score = q_rotated · k_rotated = (-0.871)(0.764) + (0.701)(-0.817) = -1.238
```

This score depends on the relative distance |m - n| = 3, not on the absolute positions 2 and 5.

---

### Common Confusion

1. **"RoPE is just sinusoidal position encoding."** Sinusoidal encoding (from the original Transformer) adds position information to the input. RoPE rotates the Q and K vectors themselves. The math looks similar but the mechanism is different.

2. **"RoPE requires complex numbers."** The math can be written with complex numbers, but the implementation uses simple 2D rotation matrices (cos, sin) on pairs of real dimensions.

3. **"All dimensions use the same rotation speed."** No. Higher dimensions rotate slower (θ_i gets smaller as i increases). This creates a spectrum from fast-rotating dimensions (capture local patterns) to slow-rotating dimensions (capture global patterns).

4. **"RoPE solves the long context problem by itself."** RoPE makes extension possible, but for very long contexts you still need position interpolation or base scaling. The raw angles for position 1M would be huge and unstable.

5. **"RoPE only works for Transformers."** It was designed for Transformers, but the idea of encoding position through rotation can apply to any architecture that uses dot-product attention.

---

### Where It Is Used in Our Code

`src/phase44/phase44_long_context.py` — We implement RoPE rotation for a tiny model and visualize how the rotation angles scale with position. Then we apply position interpolation to extend the context window.
