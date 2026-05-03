## What Is Self-Supervised Learning?

---

### The Problem

Labeled data is expensive. A human labeler might annotate 1000 images per day. But the internet has billions of unlabeled images. How do you learn from unlabeled data without any human-provided labels?

---

### Definition

**Self-supervised learning (SSL)** is a training paradigm where the model creates its own supervision signal from the raw data. There are no human labels. The task is designed so that the structure of the data itself provides the answer.

**Core idea:**
```
Human supervision:  image -> human says "cat" -> model learns
Self-supervision:   image -> model predicts rotation angle -> model learns
```

**Why predicting rotation teaches vision:**
- To predict if an image is rotated 0°, 90°, 180°, or 270°, the model MUST learn what objects look like right-side-up
- A cat upside-down is still recognizable as a cat, but only if the model understands cat features
- The rotation label comes from the code, not a human

**Two major families:**

**1. Contrastive learning:** Learn to pull similar samples together and push different samples apart
- Example: SimCLR, MoCo, CLIP
- Task: "These two crops from the same image should have similar embeddings. A crop from a different image should have a dissimilar embedding."

**2. Masked prediction:** Mask parts of the input and predict them
- Example: BERT (mask words), MAE (mask image patches)
- Task: "Predict the missing pixel/word from context"

---

### Real-Life Analogy

A child learning about the world.
- **Supervised learning:** A parent points at a dog and says "dog." The child memorizes. Expensive for the parent.
- **Self-supervised learning:** The child watches videos. They notice that when a ball rolls behind a couch, it reappears on the other side. They learn object permanence without anyone teaching them. They predict "what happens next" and learn from whether they are right.

The child creates their own "labels" (predictions) and learns from reality (the actual outcome). No parent needed.

---

### Tiny Numeric Example

**Contrastive learning with 2D points:**

**Original point:** `x = [3.0, 4.0]`

**Augmented versions:**
```
x_aug1 = [3.1, 3.9]   (slightly perturbed)
x_aug2 = [2.9, 4.2]   (slightly perturbed)
x_other = [0.1, -2.0] (different point)
```

**Self-supervised task:**
```
Make embedding(x_aug1) close to embedding(x_aug2)
Make embedding(x_aug1) far from embedding(x_other)
```

**Training:**
```
Loss = ||embed(x_aug1) - embed(x_aug2)||² - ||embed(x_aug1) - embed(x_other)||²
```

**Result:** The embedding function learns that points near [3, 4] should cluster together, even with noise. It learns a useful representation without any labels.

---

### Common Confusion

1. **"Self-supervised learning is unsupervised."** It is a form of unsupervised learning, but specifically the model creates its own labels. Not all unsupervised learning is self-supervised (e.g., clustering has no labels at all).

2. **"SSL models are weaker than supervised models."** Not anymore. SSL pre-training + fine-tuning often beats pure supervised training, especially with limited labels.

3. **"SSL only works for images."** It works for text (BERT), audio (wav2vec), video, graphs, and even molecular structures.

4. **"Contrastive learning needs negative pairs.""** Modern methods like BYOL and SimSiam show you can learn without negatives, though they are harder to stabilize.

5. **"SSL eliminates the need for labeled data entirely."** Usually SSL pre-trains on unlabeled data, then a small labeled dataset fine-tunes the model. The combination is powerful.

---

### Where It Is Used in Our Code

`src/phase50/phase50_self_supervised_learning.py` — We implement contrastive learning on 2D points and masked prediction on images, showing how structure alone trains useful representations.
