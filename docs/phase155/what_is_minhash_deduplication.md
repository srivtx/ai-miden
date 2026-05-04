## What Is MinHash Deduplication?

**The Problem:**
You have 10 million documents. Many are near-duplicates: the same article mirrored on different sites, template pages with slight variations, or boilerplate text repeated across pages. Exact string matching misses these. How do you find documents that are 90% similar without comparing every document to every other document?

**Definition:**
**MinHash deduplication** is an algorithm that estimates the Jaccard similarity between two documents by comparing hash signatures of their word shingles. It uses Locality Sensitive Hashing (LSH) to group likely duplicates into buckets, avoiding the O(N²) cost of pairwise comparison.

**Real-life analogy:**
MinHash is like a fingerprint database for criminals. Instead of comparing a crime scene fingerprint to every person in the country (impossible), the system hashes the fingerprint into bins based on ridge patterns. Only fingerprints in the same bin are compared in detail. MinHash does the same for text: it hashes documents into bins based on their shingles, and only documents in the same bin are checked for similarity.

**Tiny numeric example:**
Document A: "The quick brown fox jumps"
Document B: "The quick brown fox jumps over the lazy dog"
Shingles (size=3):
- A: {"The quick brown", "quick brown fox", "brown fox jumps"}
- B: {"The quick brown", "quick brown fox", "brown fox jumps", "fox jumps over", ...}
Jaccard similarity = |A ∩ B| / |A ∪ B| = 3 / 6 = 0.5
MinHash estimates this as ~0.5 by comparing 128 hash values.

**Common confusion:**
- **"MinHash finds exact duplicates."** No. It finds near-duplicates. Exact duplicates are trivial to find with a hash table. MinHash shines at finding 85-95% similar documents.
- **"MinHash is deterministic."** The hash functions are deterministic for a given seed, but the similarity estimate is probabilistic. More hash bands = higher accuracy.
- **"LSH is the same as MinHash."** MinHash creates signatures. LSH buckets signatures to find candidate pairs. They work together but are distinct steps.
- **"Deduplication removes too much data."** In practice, web corpora are 30-60% duplicate. Removing them improves model quality and reduces training cost.
- **"Shingle size does not matter."** Size-5 shingles catch paragraph-level similarity. Size-10 shingles catch document-level similarity. The choice depends on your duplicate definition.

**Where it appears in our code:**
`src/phase155/phase155_data_curation.py` — Extracts word shingles, computes MinHash signatures with 128 hashes, buckets them with LSH (16 bands), and removes documents with estimated Jaccard similarity >= 0.85.
