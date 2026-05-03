## What Is Image Tokenization?

---

### The Problem

Transformers are sequence models. They expect a one-dimensional list of discrete tokens. Images are two-dimensional grids of continuous pixel values. You cannot feed raw pixels directly into a standard transformer attention layer and expect efficient scaling. How do you turn an image into a token sequence that a transformer can process just like text?

---

### Definition

**Image tokenization** is the process of converting an image into a sequence of discrete or continuous tokens, typically by dividing the image into patches and mapping each patch to a vector in a learned codebook. Once tokenized, an image behaves like a sentence: it has a length, a vocabulary, and can be embedded into the same space as text.

**How it works:**
```
Image (64x64 pixels)
  → Split into 8x8 patches (each 8x8x3 = 192 numbers)
  → Encoder compresses each patch to a latent vector
  → Vector Quantization: find nearest vector in a learned codebook
  → Output: sequence of integer indices [42, 7, 15, ..., 89]
  → Decoder maps indices back to patches to reconstruct the image
```

**Key techniques:**
- **VQ-VAE:** vector quantization variational autoencoder that learns a discrete codebook of visual primitives.
- **Patch embedding (ViT):** flatten patches into vectors without quantization, producing continuous tokens.
- **Perceptual losses:** train the tokenizer to preserve semantic structure, not just pixel values.

**Why this matters:**
- Discretization allows images and text to share the same embedding table and next-token prediction objective.
- A 256x256 image becomes 256 tokens instead of 196,608 pixel values—a massive compression that makes self-attention feasible.
- The quality of the tokenizer sets an upper bound on the multimodal model's visual fidelity.

---

### Real-Life Analogy

Mosaic art. A painter could store a portrait as a high-resolution photograph with millions of pixels. Instead, a mosaic artist uses a limited catalog of colored tiles. The portrait becomes a grid of tile IDs: "row 1: red-12, blue-5, gold-3..." The tile shop only stocks 8,192 colors, but that is enough to represent almost any scene. The artist does not think about chemical pigment formulas; they think in tiles. A transformer with image tokenization is the same. It does not process raw pixels; it processes "visual tiles" from a learned catalog. The reconstruction is lossy, but the discrete representation is exactly what the sequence model needs.

---

### Tiny Numeric Example

**Raw image representation:**
```
64x64 RGB image = 64 * 64 * 3 = 12,288 floating-point numbers
```

**VQ-VAE tokenization:**
```
Patch size: 8x8 → 8 patches per side → 64 patches total
Codebook size: 512 vectors, each dimension 192
Each patch → nearest codebook index → 1 integer
Total representation: 64 integers in range [0, 511]
Reconstruction MSE: 0.02
Compression ratio: 12,288 floats → 64 ints (roughly 192:1)
```

**Sequence form:**
```
Text:   [101, 234, 56]
Image:  [42, 7, 15, 89, 301, 12, ...]  (64 tokens)
Mixed:  [101, 234, 56, 42, 7, 15, ..., 12]
```

---

### Common Confusion

1. **"Image tokenization is just JPEG compression."** JPEG is optimized for human perception and decompression. VQ-VAE is optimized for transformer training; its codebook vectors are learned to preserve semantics.

2. **"VQ-VAE tokens are interpretable like words."** Unlike text tokens, you cannot look up token 42 in a dictionary. It represents a learned visual primitive, not a named concept.

3. **"Bigger patches are always better."** Larger patches mean fewer tokens and faster training, but they lose fine-grained detail. The choice is a trade-off between resolution and sequence length.

4. **"You need a separate tokenizer for every image."** One codebook is trained on millions of images and generalizes to new ones.

5. **"Tokenization loses too much information to be useful."** Modern VQ-VAEs reconstruct images with high fidelity. The loss is comparable to a moderate JPEG and is more than acceptable for high-level reasoning.

6. **"Vision Transformer patches are discrete tokens."** Standard ViT uses continuous patch embeddings. Only VQ-VAE variants produce discrete tokens that can share a vocabulary with text.

7. **"Only images can be tokenized."** The same principle applies to audio spectrograms, video frames, protein structures, and 3D point clouds. Tokenization is a universal bridge between continuous data and sequence models.

---

### Where It Is Used in Our Code

`src/phase118/phase118_multimodal_concepts.py` — We construct a tiny 8x8 image, split it into 2x2 patches, quantize each patch against a small learned codebook, and reconstruct the image. We compare the original pixels to the reconstruction to show the lossy but useful nature of visual tokenization.
