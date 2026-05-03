## What Is a Projection Layer?

---

### The Problem

The vision encoder outputs embeddings in one vector space (e.g., 768 dimensions from CLIP). The language model expects embeddings in a different space (e.g., 4096 dimensions from Llama). They speak different languages. How do you translate between them?

---

### Definition

A **projection layer** is a simple linear transformation (or small MLP) that maps vision embeddings into the language model's embedding space.

```
image_embedding_lm = image_embedding_vision @ W_projection
```

**Why it works:**
- Both spaces encode semantic information
- A linear map can align the two representations
- The projection is learned during VLM training
- It is small: for CLIP (768-dim) → Llama (4096-dim), only 768×4096 ≈ 3M parameters

**In LLaVA:**
- Vision encoder: frozen CLIP ViT-L/14 (768-dim output)
- Language model: frozen Llama-2 (4096-dim input)
- Projection: single linear layer 768 → 4096 (trained)

---

### Real-Life Analogy

A conference with English and Japanese speakers.
- The **vision encoder** speaks Japanese (CLIP's embedding space)
- The **language model** speaks English (Llama's embedding space)
- The **projection layer** is the translator

The translator does not need to be a literary genius. They just need to map concepts accurately: when the Japanese speaker says "aoi sora" (blue sky), the English speaker hears "blue sky." A simple mapping works because both speakers are talking about the same world.

---

### Tiny Numeric Example

**Vision embedding:** `v = [0.5, -0.3, 0.8]` (3 dims)

**Projection matrix** (3 → 4):
```
W = [[0.1, 0.3, 0.5, 0.2],
     [0.2, 0.1, 0.4, 0.3],
     [0.3, 0.5, 0.2, 0.1]]

projected = v @ W
          = [0.5×0.1 + (-0.3)×0.2 + 0.8×0.3,
             0.5×0.3 + (-0.3)×0.1 + 0.8×0.5,
             0.5×0.5 + (-0.3)×0.4 + 0.8×0.2,
             0.5×0.2 + (-0.3)×0.3 + 0.8×0.1]
          = [0.05 - 0.06 + 0.24,
             0.15 - 0.03 + 0.40,
             0.25 - 0.12 + 0.16,
             0.10 - 0.09 + 0.08]
          = [0.23, 0.52, 0.29, 0.09]
```

**Language model embedding for word "the":** `e = [0.1, 0.2, 0.3, 0.4]`

**Concatenated input:**
```
[projected, e] = [[0.23, 0.52, 0.29, 0.09],
                   [0.10, 0.20, 0.30, 0.40]]
```

The language model processes both the projected image information and the text token together.

---

### Common Confusion

1. **"The projection layer is complex."** No. In LLaVA it is literally one matrix multiplication. Some variants use a small 2-layer MLP, but it remains tiny compared to the language model.

2. **"Projection layers are trained from scratch."** Yes, but with frozen vision and language models. Only the projection layer weights update.

3. **"Projection is the same as adapter."** Similar idea (bridging two representations), but adapters typically modify internal layers. Projection connects two separate models.

4. **"Any linear map works."** No. It must be learned on image-text pairs so that semantically similar concepts align.

5. **"Projection layers add significant compute."** No. They are tiny. For 196 image tokens × 768 → 4096, it is just one matrix multiplication — negligible compared to the language model's attention.

---

### Where It Is Used in Our Code

`src/phase41/phase41_vlm.py` — The `ProjectionLayer` class maps synthetic vision embeddings to the language model's input space. Only this layer is trained during VLM fine-tuning.
