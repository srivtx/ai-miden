## What Is MinHash?

---

### The Problem

You have 10 billion web pages. Many are duplicates or near-duplicates (same article with different ads, same product page with different prices). Training on duplicates wastes compute and causes memorization. How do you find duplicates without comparing every page to every other page (which would take forever)?

---

### Definition

**MinHash** is an algorithm for estimating the similarity between two sets using a small fingerprint. It is used for near-duplicate detection in massive datasets.

**The core idea:**
```
Jaccard similarity(A, B) = |A ∩ B| / |A ∪ B|
```

MinHash approximates Jaccard similarity by:
1. Hashing each element to a random number
2. For each set, recording the minimum hash value
3. The probability that two sets have the same minimum hash equals their Jaccard similarity

**Why MinHash is powerful:**
- Computes similarity in O(1) per pair after preprocessing
- Handles billions of documents
- Finds near-duplicates, not just exact copies

**LSH (Locality Sensitive Hashing):**
- Uses multiple MinHash functions
- Documents with similar MinHash signatures are bucketed together
- Only documents in the same bucket are compared
- Reduces comparisons from O(N²) to O(N)

---

### Real-Life Analogy

A library organizing books by genre.
- **Naive approach:** Compare every book to every other book to find duplicates. With 1 million books, that is 1 trillion comparisons.
- **MinHash approach:** Each book gets a "genre fingerprint" based on its most distinctive words. Books with the same fingerprint go in the same shelf. Only books on the same shelf are compared. You find duplicates in millions of comparisons instead of trillions.

The fingerprint is small but preserves similarity information.

---

### Tiny Numeric Example

**Document A (shingles):** {"the cat", "cat sat", "sat on", "on the", "the mat"}
**Document B (shingles):** {"the cat", "cat sat", "sat on", "on a", "a mat"}

**Hash function h(x) = (a×x + b) mod p:**
```
h("the cat") = 5
h("cat sat") = 12
h("sat on") = 3
h("on the") = 18
h("the mat") = 7
h("on a") = 15
h("a mat") = 9
```

**MinHash of A:** min(5, 12, 3, 18, 7) = 3
**MinHash of B:** min(5, 12, 3, 15, 9) = 3

**They share the same MinHash!** This suggests they are similar.

**With 100 hash functions:**
```
If 85 out of 100 MinHash values match:
Estimated Jaccard similarity = 85%
```

**Actual Jaccard:**
```
|A ∩ B| = 3 ("the cat", "cat sat", "sat on")
|A ∪ B| = 7
Jaccard = 3/7 = 42.9%
```

With more hash functions, the estimate converges to the true similarity.

---

### Common Confusion

1. **"MinHash finds exact duplicates only."** No. It finds near-duplicates by comparing sets of shingles (word n-grams).

2. **"MinHash gives exact Jaccard similarity."** It gives an unbiased estimate. The accuracy depends on the number of hash functions.

3. **"MinHash is only for text."** It works for any set data: images (feature sets), DNA sequences (k-mer sets), and user preferences (item sets).

4. **"LSH guarantees no false negatives."** No. LSH can miss some similar pairs if they do not collide in any bucket. The probability is tunable.

5. **"MinHash is slow."** Preprocessing is linear. After that, similarity checks are constant time. It is one of the fastest methods for large-scale deduplication.

---

### Where It Is Used in Our Code

`src/phase52/phase52_data_augmentation.py` — We implement a simplified MinHash algorithm for deduplicating a small corpus of text documents, showing how similarity fingerprints detect near-duplicates efficiently.
