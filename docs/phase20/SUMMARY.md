← [Previous: Phase 19: BERT](docs/phase19/SUMMARY.md) | [Next: Phase 21: Training a Tiny GPT](docs/phase21/SUMMARY.md) →

---

# Phase 20 Summary: GPT Architecture — Generative Pre-trained Transformer

## What This Phase Taught

While BERT uses the encoder for understanding, GPT uses the decoder for generation. GPT applies a causal mask that blocks future positions, forcing left-to-right text generation. At each step, it predicts the next token and feeds it back as input.

## Key Concepts

- **GPT**: Generative Pre-trained Transformer. Uses only the Transformer decoder.
- **Causal Masking**: A triangular mask that makes attention weights for future positions = 0. Position i can only attend to positions 0, 1, ..., i-1.
- **Autoregressive Generation**: Predicting the next token, feeding it back, and repeating. This creates an endless generation loop.

## The Code

**Local (NumPy):** `src/phase20/phase20_gpt.py` — Causal mask creation, causal self-attention, text generation demonstration, detailed BERT vs GPT comparison with architecture diagrams.

**Colab T4 (PyTorch GPU):** `src/phase20/phase20_gpt_colab.py` — Full GPT decoder trained on next-token prediction. Generates text from seed phrases.

## Results

**Local:** The causal mask correctly creates a triangular pattern. Position 0 attends only to itself. Position 2 attends to positions 0, 1, and 2. The BERT vs GPT comparison table clearly shows the architectural split.

**Colab:** Trains a 64-dim, 2-layer GPT on word sequences. Successfully generates coherent continuations from seed phrases.

## The Analogy

GPT is like an author writing a novel. They can re-read what they've written (past tokens), but cannot peek at the next chapter (future tokens). They predict the next sentence based on everything so far.

## Connection to Previous Phase

Phase 19 showed BERT (encoder, bidirectional, understanding). Phase 20 shows GPT (decoder, unidirectional, generation).

## Connection to Next Phase

Phase 21 puts everything together and actually trains a tiny GPT that generates text.

---

← [Previous: Phase 19: BERT](docs/phase19/SUMMARY.md) | [Next: Phase 21: Training a Tiny GPT](docs/phase21/SUMMARY.md) →