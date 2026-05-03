## What Is Embedding Retrieval?

---

### The Problem

You have a question and a million documents. You need to find the documents that answer the question. Keyword search fails when the question and document use different words for the same concept. How do you match meaning instead of words?

---

### Definition

**Embedding retrieval** is the process of:
1. Converting documents into dense vector representations (embeddings)
2. Converting the query into an embedding using the same model
3. Finding the documents whose embeddings are closest to the query embedding

**The embedding model** (e.g., BERT, E5, BGE) is trained so that semantically similar texts map to nearby vectors, regardless of exact word overlap.

**Distance metrics:**
- **Cosine similarity:** Measures the angle between vectors (most common)
- **Euclidean distance:** Measures straight-line distance between vectors
- **Dot product:** Measures projection of one vector onto another

---

### Real-Life Analogy

A perfume shop.
- **Keyword search:** You ask for "floral scent with roses." The clerk only shows perfumes literally named "Rose Garden." They miss "Blooming Bouquet" and "English Garden" because those names do not contain the word "rose."
- **Embedding retrieval:** The shop organizes perfumes in a scent space where distance = similarity. "Rose Garden," "Blooming Bouquet," and "English Garden" are all clustered together. When you ask for "floral scent with roses," the clerk points to the entire cluster. You find what you want even when the names differ.

---

### Tiny Numeric Example

**Embedding model output (3 dimensions for simplicity):**
```
"cat"      → [0.9, 0.1, 0.0]
"kitten"   → [0.85, 0.15, 0.0]
"feline"   → [0.88, 0.12, 0.0]
"dog"      → [0.1, 0.9, 0.0]
"puppy"    → [0.15, 0.85, 0.0]
"weather"  → [0.0, 0.0, 1.0]
```

**Query:** "kitten"
```
Embedding: [0.85, 0.15, 0.0]
```

**Distances:**
```
To "cat":      sqrt((0.9-0.85)² + (0.1-0.15)² + (0-0)²) = 0.071
To "feline":   sqrt((0.88-0.85)² + (0.12-0.15)² + (0-0)²) = 0.042
To "dog":      sqrt((0.1-0.85)² + (0.9-0.15)² + (0-0)²) = 1.06
To "weather":  sqrt((0-0.85)² + (0-0.15)² + (1-0)²) = 1.31
```

**Retrieved documents (top 2):** "feline" (dist 0.042), "cat" (dist 0.071)

The model knows "kitten," "cat," and "feline" are related even though they share no letters with "weather" or "dog."

---

### Common Confusion

1. **"Embedding retrieval understands language."** No. The embedding model understands language (to some degree). The retrieval step is just math: compute distances and sort. It has no comprehension.

2. **"Cosine similarity and dot product are the same."** Only if vectors are normalized to unit length. Cosine similarity divides by the magnitudes, so it is scale-invariant. Dot product is not.

3. **"Higher-dimensional embeddings are always better."** Not necessarily. 768-dimensional embeddings are standard, but some tasks work fine with 384 or even 128 dimensions. Higher dimensions use more memory and slow down search.

4. **"Embedding retrieval replaces the need for structured databases."** No. RAG systems often use hybrid retrieval: embedding search for semantic match + keyword search for exact match (e.g., product IDs, dates, names).

5. **"One embedding model works for all languages and domains."** No. Models trained on English text perform poorly on Chinese. Models trained on general web text perform poorly on highly technical domains. Domain-specific fine-tuning of the embedding model is often necessary.

---

### Where It Is Used in Our Code

`src/phase37/phase37_rag.py` — Documents and queries are embedded as bag-of-words vectors. Cosine similarity finds the most relevant documents for each query, demonstrating semantic matching without exact word overlap.
