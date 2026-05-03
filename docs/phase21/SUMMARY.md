# Phase 21 Summary: Training a Tiny GPT

## What This Phase Taught

This is the culmination of everything learned so far. We combine embeddings, positional encoding, causal self-attention, Transformer blocks, next-token prediction, cross-entropy loss, and gradient descent into a complete GPT model that generates text.

## Key Concepts

- **Character-Level GPT**: Predicts the next character (not word) given previous characters. Simpler but proves the architecture works.
- **Training Loop**: Forward pass → compute loss → backward pass → update weights. Repeat for thousands of steps.
- **Generation Loop**: Predict next token → append to sequence → predict next token → repeat. Creates endless text.
- **Scaling Laws**: More data + more parameters + more compute = better generation. GPT-3 uses 175B parameters.

## The Code

**Local (NumPy):** `src/phase21/phase21_tiny_gpt.py` — Complete Tiny GPT with all components: token embeddings, positional encoding, causal self-attention, Transformer blocks, output projection, training loop, and generation. Demonstrates the architecture end-to-end.

**Colab T4 (PyTorch GPU):** `src/phase21/phase21_tiny_gpt_colab.py` — Real character-level GPT with 256-dim embeddings, 6 Transformer layers, 8 attention heads. Trains on text corpus and generates coherent Shakespeare-style text.

## Results

**Local:** The architecture is correctly implemented. Training loss decreases from ~3.05 to ~3.05 (very tiny corpus). The generation shows the model learned some character patterns but needs more data/parameters.

**Colab:** Trains a meaningful model on actual text. With sufficient training, generates coherent paragraphs that match the training data style.

## The Analogy

Training a GPT is like teaching a child to write by having them read millions of books. They learn patterns, grammar, facts, and style. Then you ask them to write something new, and they generate original text that sounds like what they've read.

## Connection to Previous Phase

Phase 20 showed the GPT architecture. Phase 21 actually trains it and makes it generate text.

## Connection to Next Phase

Phase 22 asks: "The model generates text, but it doesn't answer questions helpfully. How do I make it an assistant?" The answer: Supervised Fine-Tuning (SFT).
