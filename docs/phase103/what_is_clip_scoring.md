## What Is CLIP Scoring?

---

## The Problem

You have scraped 1 billion image-text pairs from the internet. Most pairs are garbage: an image of a cat paired with the caption "click here for more," or a product photo paired with HTML navigation text. Manual inspection is impossible. How do you automatically measure whether an image and a caption actually belong together semantically, at scale?

---

## Definition

**CLIP Scoring** is the method used by the CLIP model to measure semantic alignment between images and text. An image encoder and a text encoder project both modalities into a shared embedding space. The similarity between an image embedding and a text embedding (typically cosine similarity or dot product) is the CLIP score.

**How it works:**
```
Image encoder:   photo of a dog  →  [0.12, -0.34, 0.88, ..., 0.05]  (512-dim)
Text encoder:    "a dog playing"  →  [0.15, -0.30, 0.85, ..., 0.02]  (512-dim)
CLIP score:      dot product = 0.85  (high alignment)

Text encoder:    "a red sports car"  →  [-0.20, 0.80, -0.10, ..., 0.60]
CLIP score:      dot product = 0.12  (low alignment)
```

**Key properties:**
- **Shared space:** both modalities live in the same vector space, enabling direct comparison
- **Zero-shot:** no task-specific labels are needed; the score is general-purpose
- **Differentiable:** the scoring function is part of the model, enabling end-to-end training

**Why this matters:**
- CLIP scoring filters noisy web data without human annotation
- It enables zero-shot image classification by comparing an image to class-name text prompts
- It is the foundation of modern text-to-image retrieval and generation systems

---

## Real-Life Analogy

Imagine a universal translator that converts every language into a common symbolic language. A French sentence and a German sentence that mean the same thing produce nearly identical symbol strings. A French sentence about dogs and a German sentence about cars produce completely different symbols. You can compare the symbol strings directly without understanding French or German. The shared symbolic space is the CLIP embedding space.

But the analogy has limits. The universal translator does not guarantee factual correctness. If the French sentence says "the dog is 50 meters tall," the German translation will still score highly with an image of a normal dog because the symbols encode "dog," not "50 meters." CLIP scores semantic relatedness, not factual truth. This distinction matters when building systems that retrieve images for medical or legal queries. A high CLIP score means the concepts overlap; it does not mean the caption is accurate.

The trade-off is between sensitivity and specificity. A lenient CLIP threshold keeps more data but lets through incorrect matches. A strict threshold improves precision but may discard valid pairs where the caption is abstract or metaphorical. There is no universal threshold: a threshold of 0.3 works for natural images, while 0.5 may be needed for technical diagrams.

---

## Tiny Numeric Example

**A dataset of 2,000 image-text pairs:**

**Aligned pairs (low noise):**
```
Image embedding: shared latent + small noise
Text embedding:  shared latent + small noise
Average dot product: 0.72
```

**Noisy pairs (anti-correlated):**
```
Image embedding:  shared latent + large noise
Text embedding:  -shared latent + large noise
Average dot product: -0.15
```

**Score distributions before filtering:**
```
Category        Mean score    Std dev
Aligned pairs      0.72        0.18
Noisy pairs       -0.15        0.42
```

**After filtering at the 75th percentile threshold:**
```
Retention:           top 25% by score
Precision:           94% of retained pairs are aligned (up from 50%)
Dataset size:        500 pairs (down from 2,000)
```

**Downstream zero-shot classification accuracy:**
```
Unfiltered dataset:    61%
Filtered dataset:      78%
```

**The shift:** Filtering by CLIP score increased downstream accuracy by 17 percentage points by removing cross-modal noise.

---

## Common Confusion

1. **"A high CLIP score means the caption is factually correct."** CLIP measures semantic relatedness, not factual accuracy. "A dog" and "a golden retriever" both score highly on the same image, even though only one is precisely correct.

2. **"CLIP scoring requires training a new model from scratch."** Pre-trained CLIP models are publicly available. You can compute scores using frozen encoders without any additional training.

3. **"CLIP scores are probabilities."** CLIP scores are unnormalized dot products or cosine similarities. They are relative measures, not probabilities. A score of 0.8 is only meaningful in comparison to other scores in the same batch.

4. **"CLIP works equally well for all domains."** CLIP is trained on natural images and web text. It underperforms on medical imaging, satellite imagery, and technical diagrams where the visual vocabulary differs from its training distribution.

5. **"Cosine similarity and dot product give the same ranking."** Only if all vectors have unit length. In practice, CLIP encoders may produce unnormalized vectors, and dot product can be dominated by vector magnitude rather than direction.

6. **"CLIP scoring replaces human curation entirely."** CLIP filters coarse noise effectively but misses subtle errors. A caption describing a 2010 photo as "current" will score highly despite being temporally wrong. Human spot-checking remains necessary.

7. **"CLIP scoring is only for image-text pairs."** The same principle applies to audio-text, video-text, and any multimodal pair where both modalities can be embedded into a shared space.

---

## Where It Is Used in Our Code

`src/phase103/phase103_multimodal_data.py` — We simulate CLIP-style scoring using synthetic image and text embeddings derived from shared latent vectors. We compute dot-product similarities, plot the score distributions for aligned versus noisy pairs, and measure how filtering by score improves the precision of the retained dataset.
