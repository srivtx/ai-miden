## What Is Vision-Language Instruction Tuning?

---

### The Problem

You have a model that understands images (CLIP) and a model that understands text (GPT). But when a user asks "What color is the cat in this image?", you need a single model that both sees the image AND answers in natural language. How do you connect vision and language so the model can have conversations about images?

---

### Definition

**Vision-Language Models (VLMs)** like LLaVA combine:
1. A **vision encoder** (CLIP ViT) that converts images into embeddings
2. A **projection layer** that maps vision embeddings into the language model's embedding space
3. A **language model** (Llama, Mistral) that generates text conditioned on both image and text tokens

**LLaVA's key insight:** You do not need to train the vision encoder or language model from scratch. Just add a small projection layer and fine-tune on instruction-following data.

**Training in two stages:**
1. **Pre-training:** Align vision and language with image-caption pairs
2. **Instruction tuning:** Fine-tune on visual question-answering, reasoning, and conversation data

---

### Real-Life Analogy

A translator at an art museum.
- The **vision encoder** is like a security camera that sees the painting and notes visual features: "blue sky, three figures, oil on canvas."
- The **projection layer** is the translator converting the camera's technical notes into words the tour guide understands.
- The **language model** is the tour guide who speaks to visitors: "This painting shows three figures under a vivid blue sky. Notice how the artist uses light..."

Before LLaVA, the camera and tour guide spoke different languages. The projection layer teaches them to communicate.

---

### Tiny Numeric Example

**Image patch features** (from vision encoder): `v = [0.5, -0.3, 0.8, 0.2]` (4 dims)

**Projection layer** (linear, 4 → 3):
```
W = [[0.1, 0.3, 0.5],
     [0.2, 0.1, 0.4],
     [0.3, 0.5, 0.2],
     [0.4, 0.2, 0.1]]

projected = v @ W = [0.5×0.1 + (-0.3)×0.2 + 0.8×0.3 + 0.2×0.4,
                     0.5×0.3 + (-0.3)×0.1 + 0.8×0.5 + 0.2×0.2,
                     0.5×0.5 + (-0.3)×0.4 + 0.8×0.2 + 0.2×0.1]
          = [0.05 - 0.06 + 0.24 + 0.08,
             0.15 - 0.03 + 0.40 + 0.04,
             0.25 - 0.12 + 0.16 + 0.02]
          = [0.31, 0.56, 0.31]
```

**Text token embedding** (for word "color"): `e = [0.2, 0.7, 0.1]`

**Concatenated input to language model:**
```
[projected, e] = [[0.31, 0.56, 0.31],
                   [0.20, 0.70, 0.10]]
```

The language model sees both the image representation and the question token and generates the answer.

---

### Common Confusion

1. **"VLMs are just CLIP."** No. CLIP matches images to text labels. VLMs generate free-form text about images.

2. **"The vision encoder is trained."** In LLaVA, the vision encoder (CLIP) is frozen. Only the projection layer and language model are trained.

3. **"Not all VLMs use the same architecture."** Some use cross-attention (Flamingo). Some use unified token streams (Qwen-VL). LLaVA uses simple projection + concatenation.

4. **"VLMs can hallucinate visual details."** Yes. They might describe objects not in the image. This is an active research area.

5. **"Resolution does not matter."** It does. Higher resolution requires more vision tokens, increasing compute. Some models use tiling to handle arbitrary resolutions.

---

### Where It Is Used in Our Code

`src/phase41/phase41_vlm.py` — A toy VLM where synthetic "images" are 2D feature grids, a projection layer maps them to the language model's space, and the model answers questions about image content.
