## What Is Multimodal Instruction Tuning?

---

### The Problem

You have a model that can see images and a model that can answer questions. But when you ask "Is the person in the image wearing a hat?", the model might ignore the image and hallucinate an answer. How do you train the model to actually use the image when following instructions?

---

### Definition

**Multimodal instruction tuning** fine-tunes a vision-language model on conversations that require both visual understanding and language reasoning.

**Training data format:**
```
System: You are a helpful visual assistant.
Human: <image> What is unusual about this image?
Assistant: The image shows a cat riding a bicycle, which is physically impossible for a real cat.
```

**The `<image>` token** is replaced by the vision encoder's output tokens (e.g., 576 tokens for a 24×24 patch grid). The language model learns to attend to these visual tokens when generating the answer.

**Three types of training data:**
1. **Conversation:** Multi-turn Q&A about the image
2. **Detailed description:** Generate a paragraph describing the image
3. **Complex reasoning:** Answer questions requiring visual + logical reasoning

---

### Real-Life Analogy

A blindfolded person describing objects versus a sighted person.
- **Text-only model (blindfolded):** Asked "What color is the car?" They guess: "Probably red?" They have no visual input.
- **Multimodal model (sighted):** They look at the image, see the blue car, and answer correctly.

Instruction tuning teaches the sighted person to actually look before answering, not just rely on what they know from reading about cars.

---

### Tiny Numeric Example

**Image representation** (3 projected vision tokens):
```
v1 = [0.9, 0.1, 0.0]  # "red" feature
v2 = [0.1, 0.9, 0.0]  # "round" feature
v3 = [0.0, 0.1, 0.9]  # "small" feature
```

**Question tokens:**
```
q1 = "What"  → [0.2, 0.3, 0.1]
q2 = "color" → [0.1, 0.8, 0.2]
q3 = "?"     → [0.3, 0.2, 0.4]
```

**Attention mechanism sees:**
```
[v1, v2, v3, q1, q2, q3]
```

**When generating the first answer token:**
- The model attends strongly to v1 (red feature) because q2 is "color"
- It generates token "red" with high probability

**Without instruction tuning:**
- The model might ignore v1-v3 entirely
- It generates "blue" because "blue car" is statistically common in its training data

---

### Common Confusion

1. **"Multimodal tuning is the same as pre-training."** No. Pre-training aligns vision and language (image-caption pairs). Instruction tuning teaches the model to follow conversational instructions using both modalities.

2. **"The model looks at the image token by token."** No. All image tokens are provided upfront. The model attends to them throughout generation.

3. **"Instruction tuning requires millions of images."** LLaVA used just 158K instruction-following examples. Quality matters more than quantity.

4. **"Multimodal models cannot handle multiple images."** Modern models (GPT-4V, Gemini) can process multiple images in one conversation and compare them.

5. **"Instruction tuning fixes hallucination."** It reduces but does not eliminate hallucination. The model can still misinterpret visual details.

---

### Where It Is Used in Our Code

`src/phase41/phase41_vlm.py` — The model is trained on synthetic visual Q&A tasks where the answer requires attending to image features. Accuracy improves when visual tokens are present.
