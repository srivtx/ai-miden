## What Is Contrastive Learning?

---

### The Problem

You have millions of unlabeled images. You want to train a model so that similar images have similar embeddings and different images have different embeddings. But without labels, how do you know which images are "similar"?

---

### Definition

**Contrastive learning** trains a model by creating pairs of similar (positive) and dissimilar (negative) samples from unlabeled data. The model learns to minimize the distance between positive pairs and maximize the distance between negative pairs.

**How to create positive pairs from one unlabeled image:**
```
Original image -> random crop -> random color jitter -> random flip
Original image -> different random crop -> different random color jitter
```
These two augmented views are "positive pairs" — they are the same underlying image.

**How to create negative pairs:**
```
Take the first augmented view above
Pair it with an augmented view from ANY OTHER image in the batch
```

**The InfoNCE loss:**
```
For a positive pair (x_i, x_j):
  score = exp(sim(z_i, z_j) / τ)
  negatives = sum over all other samples k: exp(sim(z_i, z_k) / τ)
  Loss = -log(score / (score + negatives))
```

Where:
- `z_i` is the embedding of sample i
- `sim` is cosine similarity
- `τ` is a temperature parameter controlling sharpness

**Why this works:**
- The model must learn invariant features (cat-ness survives crops and color changes)
- The model must learn discriminative features (distinguishing cats from dogs)
- Augmentation creates the "labels" automatically

---

### Real-Life Analogy

A police lineup.
- **Positive pair:** The same person photographed from two different angles. A good witness recognizes they are the same person despite the different views.
- **Negative pair:** Two different people. A good witness distinguishes them.
- **Training:** Show the witness thousands of such pairs. They learn to focus on features that survive viewpoint changes (face shape, not lighting) and features that distinguish individuals.

Contrastive learning is training a "witness" (encoder) to be invariant to irrelevant changes (augmentation) and discriminative to meaningful differences (different images).

---

### Tiny Numeric Example

**Embeddings (2D) for 3 samples:**
```
z_a = [1.0, 0.5]   (image A, view 1)
z_a' = [0.9, 0.6]  (image A, view 2)  <- positive pair with z_a
z_b = [-0.5, 1.0]  (image B, view 1)  <- negative with respect to z_a
```

**Similarities (dot products):**
```
sim(z_a, z_a') = 1.0×0.9 + 0.5×0.6 = 1.2
sim(z_a, z_b) = 1.0×(-0.5) + 0.5×1.0 = 0.0
```

**InfoNCE loss with temperature τ=0.5:**
```
score_pos = exp(1.2 / 0.5) = exp(2.4) = 11.0
score_neg = exp(0.0 / 0.5) = exp(0) = 1.0
Loss = -log(11.0 / (11.0 + 1.0)) = -log(0.917) = 0.087
```

**If the model makes z_a and z_b closer (bad):**
```
z_b = [0.8, 0.4]  (now similar to z_a)
sim(z_a, z_b) = 1.0×0.8 + 0.5×0.4 = 1.0
score_neg = exp(1.0 / 0.5) = exp(2) = 7.4
Loss = -log(11.0 / (11.0 + 7.4)) = -log(0.598) = 0.514
```

The loss is higher when negatives are too close. The model learns to push them apart.

---

### Common Confusion

1. **"Contrastive learning needs large batch sizes."** Yes for SimCLR (needs many negatives). Methods like MoCo use a memory queue to store negatives from past batches, reducing batch size requirements.

2. **"Any augmentation works."** No. If augmentation is too weak, the task is trivial. If too strong, the model cannot recognize the positive pair. The right augmentation is crucial.

3. **"Contrastive learning is only for pre-training."** Mostly yes. The learned encoder is typically fine-tuned on downstream tasks with labels.

4. **"All negatives are equally important."** Hard negatives (samples that look similar but are different) are more informative than easy negatives. Some methods mine hard negatives.

5. **"Contrastive learning and triplet loss are the same."** Triplet loss uses one positive and one negative per anchor. InfoNCE uses one positive and many negatives. InfoNCE is generally more stable.

---

### Where It Is Used in Our Code

`src/phase50/phase50_self_supervised_learning.py` — We implement contrastive learning on 2D point clouds using positive pairs (noisy versions of the same point) and negative pairs (other points).
