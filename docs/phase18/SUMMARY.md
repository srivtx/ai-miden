← [Previous: Phase 17: Attention](docs/phase17/SUMMARY.md) | [Next: Phase 19: BERT](docs/phase19/SUMMARY.md) →

---

# Phase 18 Summary: The Transformer Architecture

## What This Phase Taught

RNNs process one word at a time. GPUs have thousands of cores but RNNs use only one. The Transformer removes RNNs entirely and replaces them with attention. Every word attends to every other word simultaneously.

## Key Concepts

- **Transformer**: An architecture that uses only attention mechanisms, no RNNs. Introduced in "Attention Is All You Need" (2017).
- **Self-Attention**: Each word in a sentence attends to every other word in the same sentence. Query, Key, and Value all come from the same input.
- **Multi-Head Attention**: Running attention multiple times in parallel. Each head learns a different type of relationship.
- **Positional Encoding**: Adding position information to word embeddings so the model knows word order.
- **Feed-Forward Network**: Processing each word independently after attention.

## The Code

**Local (NumPy):** `src/phase18/phase18_transformer.py` — Positional encoding, self-attention, multi-head attention, and Transformer block — all implemented from scratch. Demonstrates the architecture with synthetic data and visualizations.

**Colab T4 (PyTorch GPU):** `src/phase18/phase18_transformer_colab.py` — Full Transformer encoder with causal masking for character-level language modeling. Trains on text and generates new sequences.

## Results

**Local:** Successfully demonstrates all core components. Positional encodings are unique per position. Self-attention computes attention weights. Multi-head attention runs parallel heads.

**Colab:** Trains a small Transformer (64-dim, 4 heads, 2 layers) on character data. Learns to generate coherent character sequences.

## The Analogy

A Transformer is like a roundtable meeting. Everyone can talk to everyone simultaneously. In an RNN (passing a microphone), the last person has to wait for everyone else. In a Transformer, everyone shares their thoughts at once.

## Connection to Previous Phase

Phase 17 added attention to RNNs. Phase 18 removes RNNs entirely and uses ONLY attention.

## Connection to Next Phase

Phase 19 asks: "The Transformer encoder reads the whole sentence in both directions. Can I use ONLY this for understanding tasks?" The answer: BERT.

---

← [Previous: Phase 17: Attention](docs/phase17/SUMMARY.md) | [Next: Phase 19: BERT](docs/phase19/SUMMARY.md) →