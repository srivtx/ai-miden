## What Is Instruction Tuning for Vision?

---

### The Problem

A vision-language model can look at an image and describe it accurately: "A kitchen with white cabinets, a stainless steel refrigerator, and a bowl of fruit on the counter." But when you ask "How many apples are in the bowl?" it answers "There are bananas and oranges." It generated a generic caption instead of following your specific instruction. The model understands pixels and language, but it has not learned to ground its answers in visual details when given a task. How do you teach it to answer exactly what was asked, using only the visual evidence?

---

### Definition

**Instruction Tuning for Vision** is the process of fine-tuning a multimodal model on datasets where each example contains an image, a natural-language instruction, and a desired response. It teaches the model to follow diverse visual instructions (counting, comparing, locating, reasoning) rather than generating generic captions. The training signal is the standard next-token prediction loss, but the data format forces the model to attend to specific regions and relationships in the image.

**How it works:**
```
Input:  <image> + "How many apples are in the bowl?"
Target: "There are 3 apples."
Loss:   cross-entropy on the target tokens

The model must:
1. Encode the image through the vision tower
2. Project visual tokens into language space
3. Attend to the bowl region (not the refrigerator)
4. Count red round objects
5. Emit the number "3" instead of describing the whole scene
```

**Key techniques:**
- **Visual question answering (VQA):** the canonical instruction-tuning task
- **Visual grounding:** drawing bounding boxes or pointing to regions mentioned in text
- **Multimodal chain-of-thought:** teaching the model to reason step-by-step about images

**Why this matters:**
- Generic captioning is useless for robotics, where the robot needs to know "pick the red cup, not the blue one"
- Medical diagnosis requires answering specific questions like "Is there pleural effusion in the right lung?"
- Document understanding needs extraction, not summary

---

### Real-Life Analogy

A museum guide.
- **Untrained captioning model:** A guide who walks into a room and recites a memorized script about every painting. If you ask "Which painting was stolen in 1990?" they continue describing brushstrokes because they were never trained to answer questions.
- **Instruction-tuned vision model:** A guide who listens to your question and answers exactly that. "Which painting was stolen in 1990?" → "The one on the far left, the small Vermeer." They ground every answer in what is actually visible and relevant to your instruction.
- **The trade-off:** The instruction-tuned guide might give shorter answers. If you ask "Tell me about this room," they might say "It has four paintings" instead of a poetic essay. Instruction tuning optimizes for accuracy and relevance, not verbosity.

---

### Tiny Numeric Example

**Generic caption output:**
```
"A kitchen with white cabinets and a bowl of fruit."
```

**Instruction:**
```
"How many apples are in the bowl?"
```

**Desired response:**
```
"There are 3 apples."
```

**Training example format:**
```
Tokens:  [image_start] How many apples ... ? [answer_start] There are 3 apples.
Labels:  [-100, -100, ..., -100, 0.2, 0.1, 0.9, ...]  # loss only on answer
```

**Before instruction tuning:**
```
Model output: "The kitchen has white cabinets..."
Loss on target: 2.8 (high)
```

**After 500 instruction-tuning steps:**
```
Model output: "There are 3 apples."
Loss on target: 0.4 (low)
```

**The shift:** The model learned to attend to the bowl region and the count token, ignoring background cabinets. The probability mass shifted from generic caption tokens to specific answer tokens.

---

### Common Confusion

1. **"Instruction tuning vision is the same as captioning."** Captioning generates a single description. Instruction tuning teaches the model to handle diverse tasks: counting, comparing, locating, OCR, and reasoning. The data format is fundamentally different.

2. **"You need millions of unique images."** Not necessarily. You can create multiple instruction-answer pairs for the same image. One image of a kitchen can yield 20 training examples: count the apples, name the appliance brand, identify the color of the cabinets, etc.

3. **"The model sees the image the same way a human does."** It sees a grid of patches. If an object is small or occluded, the model might miss it. Instruction tuning improves attention but does not give the model human-like visual resolution.

4. **"Visual instruction data is cheap to collect."** It is not. Each example requires a human to look at an image, write a question, and verify the answer. Synthetic data (e.g., generating questions from captions) helps but introduces noise.

5. **"Instruction tuning fixes hallucinations completely."** It reduces hallucinations for the instructed task, but the model can still hallucinate details outside the instruction's scope. If you ask about apples, it might still hallucinate a nonexistent knife.

6. **"You can instruction-tune without a pre-trained projection layer."** Technically yes, but it is extremely inefficient. A random projection forces the LLM to learn both alignment and instruction following simultaneously, which requires far more data.

7. **"All VQA datasets are equally useful."** No. Synthetic VQA (questions generated from captions) is easier to collect but teaches shallow pattern matching. Real human-written VQA requires deeper reasoning and grounding.

---

### Where It Is Used in Our Code

`src/phase127/phase127_vl_colab.py` — We load a real LLaVA model, freeze the vision tower and LLM, train only the projection layer on real VQAv2 examples, and evaluate accuracy before and after. We also test the model on a custom image to show that instruction following improved.
