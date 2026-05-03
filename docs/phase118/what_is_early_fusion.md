## What Is Early Fusion?

---

### The Problem

Most multimodal models today bolt a vision encoder onto a frozen language model. The image is processed separately, compressed into a few vectors, and then injected into the text model through a projection layer. This is late fusion. It works for captioning and simple VQA, but the language model never truly "sees" the image in its early layers. Fine-grained spatial relationships and cross-modal reasoning are bottlenecked by the narrow projection. How do you build a model where images and text are first-class citizens from layer one?

---

### Definition

**Early fusion** is an architecture in which images and text are tokenized into the same discrete vocabulary and processed by a single, shared transformer from the first layer. There is no separate vision encoder or projection layer; image patches and text tokens live in the same embedding space and attend to each other through the exact same self-attention mechanism.

**How it works:**
```
Text:   "A cat sits on a..."
Image:  [patch_1, patch_2, ..., patch_256]
        ↓ VQ-VAE tokenizer ↓
        [token_502, token_17, ..., token_8991]
Sequence: ["A", "cat", "sits", "on", "a", <image>, 502, 17, ..., 8991, "and", "looks", "outside"]
        ↓ Single transformer ↓
Output: interleaved text and image tokens
```

**Key techniques:**
- **Unified vocabulary:** a single codebook covers both text subwords and image patches.
- **Interleaved pretraining:** documents with mixed text and images are fed as one long token sequence.
- **Shared self-attention:** every token—whether from text or image—attends to every other token in the same layer.

**Why this matters:**
- Late fusion models reason about images *through* text embeddings; early fusion models reason about both modalities natively.
- True interleaved generation (generate text, then an image, then more text) requires early fusion because there is no separate image encoder to call on demand.
- The same scaling laws that apply to text-only transformers apply directly to early-fusion multimodal models.

---

### Real-Life Analogy

Consider a bilingual person who learned two languages simultaneously from birth versus someone who learned one language first and then translated everything into the second. The simultaneous bilingual thinks in concepts that are neither purely language A nor purely language B. When they describe a painting, the visual and verbal concepts are fused from the start. The late learner must first translate the image into words, losing texture and color nuance along the way. Early fusion is the simultaneous bilingual. The model does not "look at the image and then describe it"; it processes image tokens and text tokens as a single stream of meaning. The trade-off is that early fusion requires a new tokenizer and pretraining pipeline; you cannot simply attach a vision encoder to an existing LLM.

---

### Tiny Numeric Example

**Late fusion (LLaVA-style):**
```
Image (256 patches) → ViT → 256 continuous vectors → Linear projection → 256 "text-like" embeddings
Text (10 tokens)    → Text embed layer → 10 embeddings
Concatenate → 266 tokens → 32-layer LLM
Total parameters:  ViT (300M) + Projection (50M) + LLM (7B)
```

**Early fusion (Chameleon-style):**
```
Image (256 patches) → VQ-VAE codebook lookup → 256 discrete tokens from vocab size 8192
Text (10 tokens)    → Same embedding table → 10 embeddings
Total tokens: 266 → 8-layer shared transformer
Total parameters:  VQ-VAE (100M) + Shared transformer (7B) + Embedding table (shared)
```

**Key difference:** Early fusion has no projection bottleneck. The 256 image tokens are native tokens in the same space as the word "cat." In layer 3, the attention head connecting "sits" to the patch tokens is the exact same operation as the head connecting "sits" to "on."

---

### Common Confusion

1. **"Early fusion means the image is fed into the model earlier in the prompt."** No. It means the image and text representations are fused in the early layers of the network, not concatenated late.

2. **"Early fusion requires more parameters."** Often it requires fewer because there is no separate vision encoder and no projection layer.

3. **"LLaVA is an early fusion model."** LLaVA is a canonical late-fusion model: CLIP vision encoder + projection + LLM.

4. **"Early fusion is only for generation tasks."** Early fusion improves understanding tasks equally because the same attention mechanism binds text to image features from the bottom up.

5. **"Interleaved data is optional for early fusion."** Interleaved pretraining is the main training regime that makes early fusion powerful; without it, the model rarely sees images and text interacting in context.

6. **"Early fusion models cannot leverage pre-trained LLMs."** They can, but the embedding table must be expanded to include image tokens, which requires continued pretraining.

7. **"A shared vocabulary means text tokens look like images."** The tokens share an embedding space, but the semantic content is different. The network learns to interpret token 502 as a visual patch in image contexts and as a subword in text contexts.

---

### Where It Is Used in Our Code

`src/phase118/phase118_multimodal_concepts.py` — We simulate an 8x8 image, tokenize it into discrete patches using a tiny codebook, and interleave those image tokens with text tokens in a single sequence. We then simulate a single self-attention layer processing the mixed sequence to show that no projection layer is needed.
