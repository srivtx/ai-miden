# Phase 19 Summary: BERT — Bidirectional Encoder Representations

## What This Phase Taught

The Transformer has both an encoder and a decoder. BERT uses ONLY the encoder. It reads text in BOTH directions simultaneously and is pre-trained to predict masked words. This makes it incredibly powerful for understanding tasks.

## Key Concepts

- **BERT**: Bidirectional Encoder Representations from Transformers. Uses only the Transformer encoder.
- **Masked Language Modeling (MLM)**: Randomly mask 15% of words and train the model to predict them from surrounding context.
- **Bidirectional**: The model sees both left and right context simultaneously when predicting a masked word.

## The Code

**Local (NumPy):** `src/phase19/phase19_bert.py` — Bidirectional encoder block, masked language modeling demonstration with synthetic embeddings, BERT vs GPT comparison, architecture visualization.

**Colab T4 (PyTorch GPU):** `src/phase19/phase19_bert_colab.py` — Full BERT encoder trained on masked word prediction. Tests masked predictions after training.

## Results

**Local:** Demonstrates how bidirectional context helps prediction. Shows that looking at both "The [MASK]" and "sat on the mat" together makes "cat" the most likely answer.

**Colab:** Trains a 128-dim, 4-layer BERT on word masking. Achieves good accuracy on predicting masked words from a small corpus.

## The Analogy

BERT is like a student who reads the entire textbook (forward and backward) before the exam. They can answer questions about any part because they've seen all the context. GPT is like an author writing a novel — they can only see what they've already written.

## Connection to Previous Phase

Phase 18 built the full Transformer (encoder + decoder). Phase 19 asks: "What if we use ONLY the encoder for understanding tasks?"

## Connection to Next Phase

Phase 20 asks: "BERT understands text but cannot generate it. What does a purely generative model look like?" The answer: GPT.
