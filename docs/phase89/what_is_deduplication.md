## What Is Deduplication?

---

## The Problem

Web-scale datasets contain billions of documents. Many are near-identical copies scraped from different URLs, boilerplate templates, or repeated spam. Training on duplicates wastes compute, inflates the frequency of certain phrases, and can cause the model to overfit to memorized passages. How do you remove redundancy without manually inspecting every document?

---

## Definition

**Deduplication** is the process of identifying and removing exact or near-duplicate examples from a dataset before training.

**How it works:**
```
Exact deduplication:
  1. Hash each document (e.g., SHA-256)
  2. Store hashes in a hash set
  3. If a new document's hash already exists, discard it

Near-deduplication (MinHash):
  1. Shingle each document into n-grams
  2. Apply k independent hash functions to each shingle
  3. For each hash function, record the minimum hash value
  4. The vector of k minima is the MinHash signature
  5. Compare signatures: fraction of matching minima ≈ Jaccard similarity
  6. If similarity > threshold (e.g., 0.9), flag as duplicate
```

**Why this matters:**
- Removing 20% duplicates from a 1-billion-document corpus cuts training time by roughly 20% without losing unique information.
- Deduplication reduces memorization of repeated boilerplate, improving generalization.
- At web scale, manual inspection is impossible; automated deduplication is the only viable approach.

---

## Real-Life Analogy

When you return from vacation with 500 photos, 80 of them are blurry duplicates of the same sunset. You delete the duplicates because keeping them wastes storage and makes finding the good photo harder. Deduplication does the same for text.

Imagine a photographer shooting a wedding with two cameras. Both cameras capture the same ceremony from slightly different angles, producing thousands of near-identical frames. The photographer does not deliver every single RAW file to the client. Instead, they use software that groups visually similar frames and keeps only the best one from each group. The client gets a curated album without redundancy, and the photographer saves hours of culling. Near-deduplication in data pipelines is identical: MinHash groups documents with high n-gram overlap, and the pipeline keeps only one representative from each group.

**The trade-off:** Aggressive deduplication can accidentally remove documents that are legitimate variants rather than true duplicates. Two distinct news articles reporting the same event may share 70% of their vocabulary but convey different perspectives. Setting the similarity threshold too high leaves duplicates; setting it too low discards valuable diversity.

---

## Tiny Numeric Example

**Before deduplication:**

| Metric | Value |
|--------|-------|
| Total documents | 1,000,000 |
| Estimated unique content | ~800,000 |
| Training epochs planned | 3 |
| Total token passes | 3,000,000,000 |

**After MinHash near-deduplication with threshold 0.9:**

| Metric | Value |
|--------|-------|
| Documents removed | 200,000 |
| Remaining documents | 800,000 |
| Training epochs planned | 3 |
| Total token passes | 2,400,000,000 |

- Compute saved: 20% reduction in training tokens
- Unique information preserved: ~100% (removed items were >90% similar to kept items)
- Memory for MinHash signatures: 1M docs × 100 hashes × 4 bytes = 400 MB

---

## Common Confusion

1. **"Deduplication is the same as compression."** Compression stores duplicates efficiently using encoding; deduplication removes them entirely from the dataset.

2. **"Near-deduplication is as easy as exact deduplication."** Exact matching is a simple hash lookup; near-matching requires techniques like MinHash and locality-sensitive hashing, which are probabilistic and more complex.

3. **"Removing duplicates always improves quality."** If all duplicates are high-quality, removing them only reduces volume without adding new information. The benefit is compute savings, not necessarily better model behavior.

4. **"Deduplication is a one-time step."** New data arriving continuously must also be checked against existing data, or duplicates will creep back in during the next crawl.

5. **"Jaccard similarity is the only metric for near-deduplication."** Edit distance, n-gram overlap, and embedding cosine similarity are also used depending on the domain and tolerance for paraphrase.

6. **"Exact deduplication catches everything."** Two documents with identical meaning but different word order or punctuation will have different hashes and survive exact deduplication. Near-deduplication catches these.

7. **"Deduplication only applies to text."** Image datasets also deduplicate. A photo shared across social media platforms may have different resolutions or watermarks but still depict the same scene.

---

## Where It Is Used in Our Code

`src/phase89/phase89_data_pipelines.py` — We implement a toy MinHash algorithm using simple hash functions and NumPy arrays. We compute MinHash signatures for three documents, estimate Jaccard similarity between each pair, and print the results. The script also generates a similarity matrix heatmap and saves it to `minhash_similarity.png`, visualizing which documents are near-duplicates.
