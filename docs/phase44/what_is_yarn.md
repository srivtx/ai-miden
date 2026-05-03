## What Is YaRN?

---

### The Problem

Basic position interpolation uniformly compresses all position dimensions by the same factor. But not all dimensions are equal — some capture local relationships (nearby tokens) and some capture global relationships (far-apart tokens). Uniform compression hurts local precision. Can we interpolate different dimensions differently?

---

### Definition

**YaRN (Yet another RoPE extension method)** is a refined position interpolation technique that splits RoPE dimensions into frequency bands and applies different scaling factors to each band.

**The insight:**
- **High-frequency dimensions** (small i, fast rotation) capture local patterns. These need LESS compression to preserve local precision.
- **Low-frequency dimensions** (large i, slow rotation) capture global patterns. These need MORE compression to extend context.

**How YaRN works:**
1. Compute the original RoPE angles: `θ_i = base^(-2i/d)`
2. Determine a "frequency threshold" that separates local from global dimensions
3. For dimensions above the threshold (high-frequency): apply less scaling
4. For dimensions below the threshold (low-frequency): apply more scaling
5. Optionally adjust the attention temperature to compensate for scale changes

**The formula (simplified):**
```
θ_i' = θ_i / scale_factor(i)
```

Where `scale_factor(i)` is smaller for high-frequency dimensions and larger for low-frequency dimensions.

**Results:**
- YaRN achieves 2× better perplexity on long sequences than basic interpolation
- It requires minimal fine-tuning (often just 0.1% of original training steps)

---

### Real-Life Analogy

Photographing a panoramic landscape.
- **Basic interpolation:** You shrink the entire photo uniformly to fit a smaller frame. Fine details (leaves, textures) become blurry.
- **YaRN:** You shrink the sky and distant mountains more (they are smooth anyway), but keep the foreground flowers and rocks at higher resolution. The panorama still fits the frame, but important details stay sharp.

Different parts of the image have different "frequencies" of detail. YaRN respects this by compressing smooth regions more and detailed regions less.

---

### Tiny Numeric Example

**Model with d = 8 dimensions, trained on positions 0-4, want to extend to 0-16.**

**RoPE angles for each dimension:**
```
i=0: θ_0 = 10000^(0) = 1.0        (highest frequency)
i=1: θ_1 = 10000^(-0.25) ≈ 0.1
i=2: θ_2 = 10000^(-0.5) ≈ 0.01
i=3: θ_3 = 10000^(-0.75) ≈ 0.001   (lowest frequency)
```

**Basic interpolation (scale = 4):**
```
All dimensions: θ_i' = θ_i / 4
i=0: 0.25, i=1: 0.025, i=2: 0.0025, i=3: 0.00025
```

**YaRN interpolation:**
```
High-frequency (i=0,1): scale = 2    (less compression)
Low-frequency (i=2,3):  scale = 8    (more compression)

i=0: θ_0' = 1.0 / 2 = 0.5
i=1: θ_1' = 0.1 / 2 = 0.05
i=2: θ_2' = 0.01 / 8 = 0.00125
i=3: θ_3' = 0.001 / 8 = 0.000125
```

**Result:**
- High-frequency dimensions (local detail) rotate faster, preserving local precision
- Low-frequency dimensions (global structure) rotate slower, accommodating longer context
- The model retains better local attention while extending global reach

---

### Common Confusion

1. **"YaRN is completely different from position interpolation."** No. It is a refinement of position interpolation. The core idea (scale positions down) is the same, but the scaling factor varies per dimension.

2. **"YaRN requires training from scratch."** No. It works on any pre-trained RoPE model. You only need a small amount of fine-tuning to adapt to the new scale.

3. **"YaRN only helps for very long contexts."** It helps for any context extension, but the benefits are most noticeable when extending by large factors (8× or more).

4. **"YaRN changes the model architecture."** No. It only changes how position indices are mapped to rotation angles. The model structure (layers, heads, dimensions) stays identical.

5. **"YaRN is the only way to extend context."** NTK-aware scaling and base scaling are alternatives. YaRN is one of the best-performing methods but not the only one.

---

### Where It Is Used in Our Code

`src/phase44/phase44_long_context.py` — We compare basic position interpolation against YaRN-style frequency-aware scaling. We visualize how different dimensions are compressed at different rates and measure the impact on attention coherence.
