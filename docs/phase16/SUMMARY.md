← [Previous: Phase 15: Word Embeddings](docs/phase15/SUMMARY.md) | [Next: Phase 17: Attention](docs/phase17/SUMMARY.md) →

---

# Phase 16 Summary: Seq2Seq — Encoder-Decoder Architecture

## What This Phase Taught

How do we translate a sentence when input and output have different lengths? Seq2Seq solves this with two RNNs: an encoder that compresses input into a thought vector, and a decoder that expands the thought vector into output.

## Key Concepts

- **Seq2Seq**: Two RNNs working together — encoder reads input, decoder writes output.
- **Encoder**: Compresses variable-length input into a fixed-size thought vector.
- **Decoder**: Expands thought vector into variable-length output, one step at a time.
- **Teacher Forcing**: During training, feed ground truth to the decoder instead of its own predictions.
- **Thought Vector**: A fixed-size summary of the entire input sequence.

## The Code

**Local (NumPy):** `src/phase16/phase16_seq2seq.py` — Complete encoder-decoder architecture with LSTM cells. Shows forward pass and architecture diagram. Full BPTT training is too complex for raw NumPy.

**Colab T4 (PyTorch GPU):** `src/phase16/phase16_seq2seq_colab.py` — Trains a real Seq2Seq model on character reversal. Uses teacher forcing, gradient clipping, and batching. Achieves near-perfect accuracy in ~15 epochs.

## Results

**Local:** The architecture is correctly implemented. The encoder produces a thought vector. The decoder generates sequences. Training requires PyTorch infrastructure.

**Colab:** Trains on 10,000 word pairs in minutes on T4 GPU. Learns to reverse words with >95% accuracy.

## The Analogy

A UN interpreter team. One person listens to English and takes notes (encoder). Another person reads the notes and speaks French (decoder). The notes (thought vector) must capture everything important from the speech.

## Connection to Previous Phase

Phase 15 gave us word embeddings. Phase 16 uses those embeddings in an encoder-decoder to handle variable-length input/output.

## Connection to Next Phase

Phase 17 asks: "The thought vector is a bottleneck. For long sentences, information gets lost. How can the decoder focus on relevant input words?" The answer: Attention.

---

← [Previous: Phase 15: Word Embeddings](docs/phase15/SUMMARY.md) | [Next: Phase 17: Attention](docs/phase17/SUMMARY.md) →