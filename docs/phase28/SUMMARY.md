← [Previous: Phase 27: Agentic AI](docs/phase27/SUMMARY.md) | [Next: Phase 29: Generative Models — VAEs](docs/phase29/SUMMARY.md) →

---

## Phase 28 Summary: Multimodal AI

**The Question:** "My model only understands text. Can it see images too?"

---

### What We Learned

1. **Vision Transformer (ViT)**
   - Splits images into patches and treats them like word tokens
   - Pure Transformer — no convolutions needed
   - Needs more data than CNNs but scales better at large scale
   - CLS token (like BERT) handles image classification

2. **CLIP**
   - Trained on 400M image-text pairs from the internet
   - Learns to embed images and captions into the SAME vector space
   - Enables zero-shot classification: describe the label in text
   - Contrastive loss pushes matching pairs together, non-matching pairs apart

3. **Shared Embedding Space**
   - Images and text occupy the same high-dimensional coordinates
   - "Dog" (text) and a dog photo (image) are neighbors
   - Requires joint training to align the modalities
   - Generalizes to audio, video, 3D — any modality can share space

4. **DALL-E / Stable Diffusion**
   - Generate images from text descriptions
   - Start with noise and iteratively denoise, guided by text embeddings
   - Stable Diffusion uses latent diffusion (faster, in compressed space)
   - Prompt engineering dramatically affects output quality

5. **GPT-4o (Unified Multimodal)**
   - Single model processes text, images, audio, and video natively
   - No conversion to intermediate text representations
   - Real-time voice conversation with sub-second latency
   - Native audio tokenization removes traditional speech-to-text pipelines

---

### Results

- Tiny ViT correctly classified 8x8 shape images from 2x2 patches
- CLIP-like model achieved 100% alignment between shape images and text descriptions
- Shared embedding space showed dog text 18x closer to dog image than cat image
- Simulated diffusion produced a clear red circle from random noise in 10 steps
- Unified multimodal attention processed image patches and text tokens together

---

### Phase 28 Files

| File | Purpose |
|---|---|
| `docs/phase28/what_is_vision_transformer.md` | Applying Transformers directly to image patches |
| `docs/phase28/what_is_clip.md` | Learning shared space for text and images |
| `docs/phase28/what_is_shared_embedding_space.md` | Images and text mapped to same vectors |
| `docs/phase28/what_is_dalle_stable_diffusion.md` | Generating images from text descriptions |
| `docs/phase28/what_is_gpt4o.md` | Unified multimodal reasoning |
| `src/phase28/phase28_multimodal_ai.py` | Demonstrations of all five concepts |

---

### Connects To

- **Phase 27:** Agentic AI — Agents with vision can navigate GUIs, read documents, and understand the physical world.
- **Phase 29:** Generative Models (VAEs) — We can see images. Now we learn to CREATE them.

---

← [Previous: Phase 27: Agentic AI](docs/phase27/SUMMARY.md) | [Next: Phase 29: Generative Models — VAEs](docs/phase29/SUMMARY.md) →