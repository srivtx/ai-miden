## What Is a Vision Encoder?

---

### The Problem

A language model processes text tokens. But images are grids of pixels, not sequences of discrete tokens. How do you convert an image into a format that a language model can understand?

---

### Definition

A **vision encoder** is a neural network (typically a Vision Transformer like CLIP ViT) that converts an image into a sequence of dense vector embeddings.

**Process:**
1. **Patchify:** Divide the image into non-overlapping patches (e.g., 16×16 pixels)
2. **Embed:** Each patch is flattened and projected to an embedding vector
3. **Add positional embeddings:** So the model knows where each patch came from
4. **Transformer blocks:** Process all patch tokens with self-attention
5. **Output:** A sequence of patch embeddings representing the image

**Example for a 224×224 image:**
- Patch size: 16×16
- Number of patches: (224/16)² = 196
- Output: 196 embedding vectors, each 768 dimensions

---

### Real-Life Analogy

An art conservator documenting a painting.
- The conservator divides the painting into a grid of small squares (patches).
- For each square, they write a note describing colors, textures, and visible details (embedding).
- They number each note by position so they know which square it came from (positional embedding).
- They review all notes together to understand the full painting (Transformer processing).
- The final notes are a complete description of the image in textual form.

---

### Tiny Numeric Example

**Image:** 4×4 pixels (grayscale for simplicity)
```
[[10, 20, 30, 40],
 [15, 25, 35, 45],
 [20, 30, 40, 50],
 [25, 35, 45, 55]]
```

**Patch size:** 2×2

**Patches:**
```
P1 = [10, 20, 15, 25]  (top-left)
P2 = [30, 40, 35, 45]  (top-right)
P3 = [20, 30, 25, 35]  (bottom-left)
P4 = [40, 50, 45, 55]  (bottom-right)
```

**Embedding projection (4 → 3):**
```
W = [[0.1, 0.2, 0.3],
     [0.2, 0.1, 0.4],
     [0.3, 0.4, 0.1],
     [0.4, 0.3, 0.2]]

E1 = P1 @ W = [10×0.1 + 20×0.2 + 15×0.3 + 25×0.4,
               10×0.2 + 20×0.1 + 15×0.4 + 25×0.3,
               10×0.3 + 20×0.4 + 15×0.1 + 25×0.2]
   = [1.0 + 4.0 + 4.5 + 10.0, 2.0 + 2.0 + 6.0 + 7.5, 3.0 + 8.0 + 1.5 + 5.0]
   = [19.5, 17.5, 17.5]
```

**Positional embedding for top-left:** `[0.1, 0.0, 0.0]`

**Final patch token:** `E1 + pos = [19.6, 17.5, 17.5]`

---

### Common Confusion

1. **"Vision encoders output a single vector."** Some do (pooled output), but for VLM applications they output a sequence of patch embeddings.

2. **"Vision encoders are trained with the language model."** In LLaVA, the vision encoder is pre-trained (CLIP) and frozen. Only the projection layer is trained.

3. **"Higher resolution always helps."** Yes, but at quadratic cost in compute. 2× resolution = 4× tokens = 16× attention cost.

4. **"All vision encoders use the same patch size."** No. CLIP uses 14×14 or 16×16. SigLIP uses different sizes. The choice affects token count and detail level.

5. **"Vision encoders understand images like humans."** No. They detect statistical patterns correlated with objects. They do not have visual experience or understanding.

---

### Where It Is Used in Our Code

`src/phase41/phase41_vlm.py` — A synthetic vision encoder converts 2D "images" into patch embeddings using simple linear projection.
