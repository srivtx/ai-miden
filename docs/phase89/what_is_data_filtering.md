## What Is Data Filtering?

---

## The Problem

The internet is full of low-quality text: spam, ads, garbled HTML, code snippets with no context, and pages written by bots. Feeding this noise into a language model teaches it bad grammar, biases, and nonsensical patterns. Garbage in, garbage out. How do you keep only the signal and discard the noise?

---

## Definition

**Data filtering** is the process of selecting training examples that meet quality, length, language, and content criteria while discarding the rest.

**How it works:**
```
Filtering pipeline:
  1. Collect raw corpus (e.g., 10 million documents from web crawl)
  2. Apply heuristic filters:
       - length < 100 characters → discard
       - punctuation_ratio > 0.5 → discard
       - language != target_language → discard
       - excessive repetition → discard
  3. Score remaining documents with quality classifier or perplexity model
  4. Keep top K percent or those above a threshold score
  5. Output cleaned corpus for training
```

**Why this matters:**
- A mediocre architecture trained on clean, diverse data often beats a state-of-the-art architecture trained on noisy duplicates.
- Filtering reduces the dataset size, which directly lowers training cost and time.
- Language-specific filters prevent English-centric rules from destroying valid text in other languages.

---

## Real-Life Analogy

A gold panner sifts river sediment through a mesh, letting sand and pebbles wash away while retaining gold flakes. Data filtering is the mesh: it lets low-quality documents wash away while retaining valuable training text.

Consider a library acquisitions department receiving ten thousand donated books. Many are water-damaged, out-of-date travel guides, or photocopied pamphlets. The librarians do not add every book to the catalog. They set criteria: books must have intact bindings, be published within the last twenty years for science sections, and be written in a language the patrons read. The rejected books are sold or recycled. The remaining collection is smaller but far more useful to readers. Data filtering performs the same curation on text corpora: it enforces minimum standards so the model learns from the best available material.

**The trade-off:** Aggressive filtering can accidentally remove rare but valuable documents. A technical manual with unusual punctuation may fail a heuristic filter despite being high-quality training data. The art of filtering is setting thresholds tight enough to catch garbage but loose enough to preserve edge cases.

---

## Tiny Numeric Example

**Before filtering:**

| Document Type | Count | Average Quality Score |
|---------------|-------|----------------------|
| Short spam | 3,000,000 | 0.05 |
| Garbled HTML | 1,000,000 | 0.10 |
| Non-English | 2,000,000 | 0.15 |
| Good text | 4,000,000 | 0.85 |
| **Total** | **10,000,000** | **0.41** |

**After applying filters:**

| Filter Applied | Documents Removed | Remaining |
|----------------|-------------------|-----------|
| length < 100 | 3,000,000 | 7,000,000 |
| punct_ratio > 0.5 | 1,000,000 | 6,000,000 |
| non-English | 2,000,000 | 4,000,000 |
| **Final corpus** | — | **4,000,000** |

- Average quality score after filtering: 0.85 (up from 0.41)
- Training tokens preserved: 40% of original volume, but ~95% of high-quality tokens
- Estimated training cost reduction: 60% less compute for comparable or better model quality

---

## Common Confusion

1. **"Filtering is the same as deduplication."** Filtering removes low-quality single documents; deduplication removes redundant copies across the dataset. They are complementary steps.

2. **"Aggressive filtering guarantees a better model."** It does not. Over-filtering can strip rare but valuable documents, reducing diversity and harming the model's ability to handle niche topics.

3. **"Filtering rules are universal."** They are not. A rule that works for English may delete valid Chinese text. Code has different quality signals than prose.

4. **"Filtering is always about removing data."** Sometimes it means re-weighting or tagging examples rather than deleting them, so the model can learn to downweight noisy samples.

5. **"Manual filtering scales to web size."** It does not. At web scale, filtering must be automated with heuristics or classifier models. Manual review of a billion documents would take decades.

6. **"One pass of filtering is enough."** New crawls introduce new noise patterns. Filtering pipelines must be monitored and updated continuously as the data distribution shifts.

7. **"Filtering fixes all data quality problems."** It catches broad categories of noise, but subtle biases, toxic content, and private information may still slip through and require additional mitigation steps.

---

## Where It Is Used in Our Code

`src/phase89/phase89_data_pipelines.py` — We define a `quality_score` function that penalizes short texts and texts with excessive punctuation. We apply it to an array of document statistics and print which documents pass or fail the filter. This demonstrates the same pipeline structure used in production: compute a score, set a threshold, and keep only documents that meet the criteria.
