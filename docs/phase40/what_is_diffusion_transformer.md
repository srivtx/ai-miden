## What Is a Diffusion Transformer (DiT)?

---

### The Problem

Diffusion models traditionally use U-Net backbones (Phase 31) with convolutions. But convolutions are local and struggle to capture global relationships in high-resolution images. Transformers excel at global reasoning. Can we replace the U-Net with a Transformer for generative modeling?

---

### Definition

A **Diffusion Transformer (DiT)** is a generative model that uses a Transformer backbone instead of a U-Net. It was introduced by Peebles & Xie in 2023 and powers modern models like Stable Diffusion 3 and Sora.

**Architecture:**
```
Input image → Patchify into tokens → Add positional embeddings → Transformer blocks → Unpatchify → Output noise/velocity
```

**Key differences from U-Net:**
- **No convolutions:** Images are treated as sequences of patches (like ViT)
- **Global attention:** Every patch can attend to every other patch
- **Better scaling:** Transformers scale more predictably to billions of parameters
- **Adaptive layer norm:** Class/text conditioning is injected through adaLN

---

### Real-Life Analogy

A painter working on a mural.
- **U-Net approach:** The painter works section by section, using local brush strokes. They can see nearby details clearly but must work hard to keep the overall composition consistent.
- **DiT approach:** The painter steps back and sees the entire mural as a grid of tiles. They plan globally — adjusting color balance, perspective, and lighting across all tiles simultaneously using attention. Every tile knows about every other tile.

The DiT painter produces more coherent global structure but requires more compute per step.

---

### Tiny Numeric Example

**Image:** 8×8 pixels

**U-Net approach:**
```
Apply 3×3 convolution → captures local edges
Apply 3×3 convolution → captures local textures
Downsample → compress
Upsample → expand
```
Each pixel only directly influences its 3×3 neighborhood.

**DiT approach:**
```
Patchify into 4 patches of 4×4 pixels each → [p1, p2, p3, p4]
Add positional embeddings → [p1+e1, p2+e2, p3+e3, p4+e4]
Self-attention: p1 attends to p2, p3, p4 (global)
Transformer block: process all patches
Unpatchify back to 8×8 image
```

A pixel in the top-left corner (in p1) can directly influence a pixel in the bottom-right corner (in p4) through attention.

---

### Common Confusion

1. **"DiT replaces diffusion entirely."** No. DiT replaces only the backbone architecture. The diffusion/flow matching process remains the same.

2. **"DiT is slower than U-Net because attention is O(N²)."** Per step, yes. But DiT achieves better quality with fewer parameters, and global attention reduces the total steps needed for coherent generation.

3. **"DiT only works for images."** No. Sora uses DiT for video. Audio diffusion models use Transformer backbones. Any modality that can be tokenized can use DiT.

4. **"DiT requires more training data than U-Net."** Transformers generally benefit more from scale (data + parameters) than CNNs. A small DiT might underperform a small U-Net, but a large DiT outperforms a large U-Net.

5. **"DiT cannot capture fine details without convolutions."** In practice, patchifying at high resolution (small patches) preserves fine details. A 512×512 image with 4×4 patches produces 16,384 tokens — enough resolution for fine features.

---

### Where It Is Used in Our Code

`src/phase40/phase40_flow_matching.py` — A simplified "patchify → Transformer → unpatchify" demonstration on 1D sequences shows how global attention replaces local convolutions.
