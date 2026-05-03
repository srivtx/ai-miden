← [Previous: Phase 14: LSTMs](docs/phase14/SUMMARY.md) | [Next: Phase 16: Seq2Seq](docs/phase16/SUMMARY.md) →

---

# Phase 15 Summary: Word Embeddings — Giving Words Meaning

## What This Phase Taught

One-hot encoding treats every word as completely unrelated. "King" and "queen" are as different as "king" and "apple." Word embeddings solve this by learning dense vectors from raw text. Words that appear in similar contexts get similar vectors.

## Key Concepts

- **Word Embedding**: A dense vector of numbers representing a word. Similar words = similar vectors.
- **Skip-Gram**: Predict context words from a center word. "The cat sat" → predict "the" and "sat" from "cat".
- **Negative Sampling**: Instead of comparing against all 50,000 vocabulary words, compare against 5 random words. Much faster.
- **Semantic Similarity**: Words that appear in similar contexts cluster together in vector space.

## The Code

**Local (NumPy):** `src/phase15/phase15_word2vec.py` — Complete Skip-gram with negative sampling on a tiny corpus. Teaches the algorithm from scratch.

**Colab T4 (PyTorch GPU):** `src/phase15/phase15_word2vec_colab.py` — Scaled-up version that trains on the text8 Wikipedia dataset (100M words) with GPU acceleration. Shows real word analogies like `king - man + woman ≈ queen`.

## Results

**Local:** The model trained successfully on 20 sentences. Loss decreased from 2.67 to ~1.23. The tiny corpus limits semantic quality but proves the algorithm works.

**Colab:** Trains on 100M words in ~5 minutes on T4 GPU. Produces high-quality embeddings showing real semantic relationships.

## The Analogy

Word embeddings are like GPS coordinates. Nearby cities (similar words) have similar coordinates. Paris and London are close. Paris and Tokyo are far. You can even do math: Paris - France + Italy = Rome.

## Connection to Previous Phase

Phase 14 built LSTMs that process sequences of one-hot vectors. Phase 15 replaces those one-hot vectors with meaningful dense vectors.

## Connection to Next Phase

Phase 16 asks: "How do I translate a sentence when input and output have different lengths?" We will build an Encoder-Decoder architecture.

---

← [Previous: Phase 14: LSTMs](docs/phase14/SUMMARY.md) | [Next: Phase 16: Seq2Seq](docs/phase16/SUMMARY.md) →