# Research: Vision-Language Instruction Tuning (LLaVA)

**Status:** Missing from course. Should be Phase 41, extension of Phase 28.
**Last Updated:** May 2026
**Sources:** Liu et al. (2023) LLaVA, GPT-4V, Claude 3, Gemini

---

## 1. The Problem

You have a model that understands images (ViT/CLIP) and a model that understands text (GPT). But when a user asks "What color is the cat in this image?", you need a single model that both sees the image AND answers in natural language. How do you connect vision and language so the model can have conversations about images?

## 2. What It Is

**Vision-Language Models (VLMs)** like LLaVA combine:
1. A **vision encoder** (CLIP ViT) that converts images into embeddings
2. A **projection layer** that maps vision embeddings into the language model's embedding space
3. A **language model** (Llama, Mistral) that generates text conditioned on both image and text tokens

**LLaVA's key insight:** You do not need to train the vision encoder or language model from scratch. Just add a small projection layer and fine-tune on instruction-following data.

**Training in two stages:**
1. **Pre-training:** Align vision and language with image-caption pairs (cheap data)
2. **Instruction tuning:** Fine-tune on visual question-answering, reasoning, and conversation data

## 3. Real-World Analogy

A translator at an art museum.
- The **vision encoder** is like a security camera that sees the painting and notes visual features: "blue sky, three figures, oil on canvas."
- The **projection layer** is the translator converting the camera's technical notes into words the tour guide understands.
- The **language model** is the tour guide who speaks to visitors: "This painting shows three figures under a vivid blue sky. Notice how the artist uses light..."

Before LLaVA, the camera and tour guide spoke different languages. The projection layer teaches them to communicate.

## 4. Key Technical Details

### Architecture
```
Image → CLIP ViT → [vision tokens] → Projection MLP → [language embeddings]
                                                          ↓
Text prompt → Tokenizer → [text embeddings] → Language Model → Generated response
```

The vision tokens and text tokens are concatenated and fed to the language model together.

### Training Data Format
```
Human: <image> What is unusual about this image?
Assistant: The image shows a cat riding a bicycle, which is physically impossible for a real cat.
```

The `<image>` token is replaced by the vision encoder's output tokens (typically 576 tokens for a 24×24 patch grid).

### Instruction Tuning
- GPT-4V is used to generate training conversations about images
- Three types of data: conversation, detailed description, complex reasoning
- The language model is fine-tuned with standard next-token prediction on these conversations

## 5. Common Confusion

- **VLMs are not just CLIP.** CLIP matches images to text labels. VLMs generate free-form text about images.
- **The vision encoder is usually frozen.** In LLaVA, only the projection layer and language model are trained. The vision encoder (CLIP) stays frozen.
- **Not all VLMs use the same architecture.** Some (like Flamingo) use cross-attention to condition the LM on images. Some (like Qwen-VL) use unified token streams.
- **VLMs can hallucinate visual details.** They might confidently describe objects that are not in the image. This is an active research area.
- **Resolution matters.** Higher-resolution images require more vision tokens, increasing compute. Some models use tiling to handle arbitrary resolutions.

## 6. What We Would Build

A toy VLM where:
- Synthetic "images" are 2D feature grids
- A projection layer maps visual features to a language model's input space
- The model answers questions about the image's content
- Show that adding vision improves accuracy on visual questions

## 7. Why It Matters Now

- **GPT-4V, Claude 3, Gemini** are all multimodal
- **LLaVA** is the most widely used open-source VLM
- **OCR, chart understanding, document QA** all use VLM architectures
- **Robotics** uses VLMs to translate visual perception into action plans

## 8. Connection to Existing Phases

- **Phase 28 (Multimodal):** We covered CLIP and shared embedding spaces. VLM instruction tuning is the next step.
- **Phase 22 (SFT):** VLM instruction tuning is supervised fine-tuning with visual inputs.
- **Phase 18 (Transformer):** VLMs use the same Transformer architecture with multimodal token sequences.

---

## References

- Liu et al. (2023): "Visual Instruction Tuning" (LLaVA)
- Liu et al. (2023): "Improved Baselines with Visual Instruction Tuning" (LLaVA-1.5)
- Alayrac et al. (2022): "Flamingo: a Visual Language Model for Few-Shot Learning"
