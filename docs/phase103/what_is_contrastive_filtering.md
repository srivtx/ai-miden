## What Is Contrastive Filtering?

---

## The Problem

You have collected 1 billion image-text pairs from web crawls. Hidden among them are captions like "click here," "image_0034.jpg," and "Copyright 2012." These captions provide zero semantic signal. Training a multimodal model on this noise teaches it that images are unrelated to their descriptions. How do you automatically discard the junk while keeping the gems, without reading a billion captions?

---

## Definition

**Contrastive Filtering** is the process of selecting training pairs by measuring how well the two modalities contrast with or align to each other in a learned embedding space. Pairs with low cross-modal similarity are discarded, leaving a cleaner, more semantically coherent dataset.

**How it works:**
```
Step 1: Encode all images and texts into shared embeddings
Step 2: Compute similarity matrix (all images vs all texts in a batch)
Step 3: A pair is "contrastive-positive" if its image-text similarity is high
        relative to other texts for that image (and vice versa)
Step 4: Discard pairs below a threshold; keep pairs above it
Result: 700M clean pairs from 1B raw pairs
```

**Key techniques:**
- **Threshold filtering:** discard bottom 30% by raw CLIP score
- **Margin-based filtering:** keep pairs where the positive score exceeds the hardest negative by a margin
- **Self-supervised refinement:** iteratively retrain the encoder on filtered data and re-filter

**Why this matters:**
- Contrastive filtering improves zero-shot ImageNet accuracy by 5-10 points
- It removes spam, templates, and navigational text without human annotation
- Cleaner data reduces the need for larger models to compensate for noise

---

## Real-Life Analogy

Consider a language exchange program that pairs students who speak different languages. If you pair a French speaker with another French speaker, neither learns anything. If you pair a French speaker with a Mandarin speaker who is actually reading from a French phrasebook, the illusion of exchange exists but no real learning occurs. Contrastive filtering is the program coordinator who tests each pair: do they actually speak different languages? Do their conversations make sense? The coordinator removes mismatched pairs so every remaining pair is a valid learning opportunity.

But the coordinator faces a subtle challenge. Some pairs look mismatched at first but are actually valid. A caption like "the feeling of autumn" paired with a photo of falling leaves is abstract but semantically rich. A rigid coordinator might discard it for lacking literal keywords. Good contrastive filtering uses learned embeddings rather than keyword matching, capturing conceptual similarity even when surface wording differs. The embedding space understands that "autumn feeling" and falling leaves belong together, even though no word appears in both.

The trade-off is between purity and diversity. Aggressive filtering produces a dataset where every pair is obviously related, but the model trained on it becomes narrow and literal. Permissive filtering includes abstract, poetic, and culturally specific pairings that stretch the model's understanding. The optimal balance depends on the downstream task: product search needs literal alignment, while creative generation benefits from associative breadth.

---

## Tiny Numeric Example

**A synthetic dataset of 4,000 pairs (2,000 aligned + 2,000 noisy):**

**Before filtering:**
```
Total pairs:          4,000
Aligned pairs:        2,000 (50%)
Noisy pairs:          2,000 (50%)
Mean CLIP score:      0.29 (high overlap between classes)
```

**After filtering at the 50th percentile threshold:**
```
Retained pairs:       2,000 (top 50% by score)
Aligned pairs:        1,800 (90% of retained)
Noisy pairs:            200 (10% of retained)
Precision:            90% (up from 50%)
```

**After filtering at the 75th percentile threshold:**
```
Retained pairs:       1,000 (top 25% by score)
Aligned pairs:          940 (94% of retained)
Noisy pairs:             60 (6% of retained)
Precision:            94% (up from 50%)
Dataset reduction:    75%
```

**Downstream zero-shot classification accuracy:**
```
Unfiltered (4,000):    61%
Top 50%   (2,000):     73%
Top 25%   (1,000):     78%
```

**The shift:** Discarding the bottom 75% of pairs by contrastive score improved downstream accuracy by 17 points while shrinking the dataset to one-quarter of its original size.

---

## Common Confusion

1. **"Contrastive filtering is just removing duplicates."** Duplicate removal keeps one copy of repeated content. Contrastive filtering evaluates cross-modal alignment. An image and text can both be unique and high-quality individually yet form a bad pair.

2. **"Filtering by CLIP score is the same as contrastive filtering."** CLIP scoring is one component. True contrastive filtering also considers the relative difficulty of negatives within a batch, not just absolute similarity.

3. **"A higher threshold always gives better results."** Beyond a point, aggressive filtering removes valid but unusual pairs. A threshold that keeps only the safest 10% may produce a model that is literal and boring.

4. **"Contrastive filtering fixes all data quality issues."** It removes cross-modal misalignment but not intra-modal problems. A perfectly matched pair can still contain toxic text or biased imagery.

5. **"You need a perfect encoder to filter effectively."** The encoder and the dataset can be improved iteratively. Start with a weak encoder, filter, retrain on the cleaner data, and repeat. Each cycle improves both.

6. **"Contrastive filtering only applies to image-text pairs."** The same principle works for any contrastive learning setup: audio-text, video-audio, protein-ligand, or user-item recommendation.

7. **"Filtering once is enough."** Data drift and new sources require periodic re-filtering. A threshold that worked for last year's web crawl may be miscalibrated for this year's data distribution.

---

## Where It Is Used in Our Code

`src/phase103/phase103_multimodal_data.py` — We simulate contrastive filtering by generating aligned and noisy image-text embedding pairs, computing dot-product similarities, and measuring how precision improves as we raise the filtering threshold. We plot the score distributions and report the fraction of aligned pairs retained at each percentile cutoff.
