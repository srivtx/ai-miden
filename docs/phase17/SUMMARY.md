← [Previous: Phase 16: Seq2Seq](docs/phase16/SUMMARY.md) | [Next: Phase 18: Transformer](docs/phase18/SUMMARY.md) →

---

# Phase 17 Summary: Attention Mechanism — Focusing on What Matters

## What This Phase Taught

Seq2Seq's thought vector is a bottleneck. For long sentences, information gets lost. Attention fixes this by letting the decoder dynamically focus on relevant encoder positions at every step.

## Key Concepts

- **Attention**: A mechanism that computes weighted combinations of encoder states based on relevance to the current decoder step.
- **Query/Key/Value**: Query = what am I looking for? Key = what do I contain? Value = what information do I have?
- **Attention Weights**: Computed by softmax(dot(Query, Key)). Sum to 1.0.
- **Context Vector**: Weighted sum of Values, weighted by attention weights.

## The Code

**Local (NumPy):** `src/phase17/phase17_attention.py` — Complete dot-product attention with Query/Key/Value. Demonstrates translation with synthetic encoder/decoder states. Shows mathematical walkthrough with real numbers.

**Colab T4 (PyTorch GPU):** `src/phase17/phase17_attention_colab.py` — Full Seq2Seq with additive attention. Trains on character reversal. Visualizes attention weights as heatmaps showing which input character each output character focuses on.

## Results

**Local:** The attention mechanism correctly focuses on the right words. Query for "Le" (article) focuses on "The" (article). Query for "chat" (animal) focuses on "cat" (animal).

**Colab:** Trains on 20,000 word pairs. Attention heatmaps clearly show the diagonal pattern (first output char focuses on last input char, etc.) for reversal task.

## The Analogy

Attention is like reading a book with a highlighter. When answering a question, you don't re-read the whole book — you look at the highlighted passages most relevant to the question.

## Connection to Previous Phase

Phase 16 built Seq2Seq with a bottleneck thought vector. Phase 17 replaces that bottleneck with dynamic attention.

## Connection to Next Phase

Phase 18 asks: "Attention is great, but RNNs are slow. Can we process ALL words at once instead of one at a time?" The answer: The Transformer.

---

← [Previous: Phase 16: Seq2Seq](docs/phase16/SUMMARY.md) | [Next: Phase 18: Transformer](docs/phase18/SUMMARY.md) →