## What Is a Pretext Task?

---

### The Problem

In self-supervised learning, you need a task that forces the model to learn useful representations. But the task itself is not the goal — the goal is the representation. What kinds of tasks work? How do you design them?

---

### Definition

A **pretext task** is a self-supervised training objective designed specifically to teach the model useful representations. The task is a "pretext" — an excuse to learn — not the final application.

**Common pretext tasks:**

**For images:**
- **Rotation prediction:** Rotate image by 0/90/180/270°, predict angle
- **Jigsaw puzzle:** Shuffle image patches, predict original order
- **Colorization:** Convert grayscale to color
- **Inpainting:** Fill in missing image regions
- **Instance discrimination:** Treat augmented views of the same image as positive pairs

**For text:**
- **Next sentence prediction:** Predict if sentence B follows sentence A
- **Masked language modeling:** Predict hidden words from context (BERT)
- **Causal language modeling:** Predict next token (GPT)

**For audio:**
- **Temporal order prediction:** Predict if audio clips are in correct order
- **Contrastive predictive coding:** Predict future audio frames from past

**Why pretext tasks work:**
- They force the model to learn invariant features (what stays the same across augmentation)
- They force the model to learn semantic features (what distinguishes different inputs)
- The labels are free (generated automatically from the data)

---

### Real-Life Analogy

Learning a language by solving crossword puzzles.
- **The pretext task:** Fill in the crossword. The puzzle gives you partial letters and clues.
- **What you actually learn:** Vocabulary, spelling, word relationships, synonyms, context clues.
- **The downstream task:** Writing essays, having conversations, reading books.

You never trained on essay-writing directly. But solving crosswords taught you the language. The crossword was the pretext.

---

### Tiny Numeric Example

**Pretext task: predict if a sequence is in original or reversed order.**

**Original:** `[3, 1, 4, 1, 5]` -> label = 1 (original)
**Reversed:** `[5, 1, 4, 1, 3]` -> label = 0 (reversed)

**Model must learn:**
- Numerical ordering
- Sequence structure
- Forward vs. backward patterns

**After training on 1M sequences:**
```
Downstream task: sort sequences
Accuracy without pretext pre-training: 45%
Accuracy with pretext pre-training: 78%
```

The pretext task taught the model about sequence structure, which transferred to sorting.

---

### Common Confusion

1. **"Pretext tasks are the same as auxiliary tasks."** Similar, but pretext tasks are specifically for self-supervised pre-training. Auxiliary tasks can be used during supervised training too.

2. **"Any pretext task works equally well."** No. Some tasks teach better representations than others. Instance discrimination (contrastive learning) generally outperforms rotation prediction for vision.

3. **"Pretext tasks need to be hard."** They need to be hard enough to force learning, but not so hard that the model fails completely. Masking 75% of patches is hard but achievable.

4. **"Pretext tasks are only for pre-training."** Mostly yes. After pre-training, the model is fine-tuned or evaluated on the real downstream task.

5. **"The pretext task accuracy matters."** Not directly. A model with 30% pretext accuracy might learn better representations than one with 80%, if the harder task forces deeper understanding.

---

### Where It Is Used in Our Code

`src/phase50/phase50_self_supervised_learning.py` — We design a pretext task (predicting relative position of patches) and show that the learned representations improve downstream classification accuracy compared to training from scratch.
