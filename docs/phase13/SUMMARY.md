← [Previous: Phase 12: Residual Networks](docs/phase12/SUMMARY.md) | [Next: Phase 14: LSTMs](docs/phase14/SUMMARY.md) →

---

# Phase 13 Summary: RNNs — Remembering Sequences

## What This Phase Taught

Standard networks treat inputs as independent, but sequences (text, time series, audio) have order. RNNs process one element at a time and maintain a hidden state (memory) that carries forward. The same weights are used at every time step.

## Key Concepts

- **Recurrent Neural Network**: A network with a loop that processes sequences one element at a time
- **Hidden State**: A vector of numbers representing the network's memory of everything seen so far
- **Backpropagation Through Time (BPTT)**: Unrolling the RNN across time and backpropagating through all time steps
- **Parameter Sharing Across Time**: The same weights are reused at every time step

## The Code

`src/phase13/phase13_rnn.py` — A vanilla RNN that learns to predict the next character in "HELLO". It implements forward pass, BPTT, and can generate new text by feeding predictions back as input.

## Results

The RNN learned to predict "HELLO" with 100% accuracy. It successfully mapped H→E, E→L, L→L, L→O. When used to generate text, it produced sequences similar to its training data.

## The Analogy

An RNN is like a storyteller with a notepad. As they read each word, they update their notepad with what they remember. The notepad (hidden state) contains a compressed summary of the entire story so far.

## Connection to Previous Phase

Phase 12 added skip connections to deep networks. Phase 13 changes the problem domain from images to sequences.

## Connection to Next Phase

Phase 14 asks: "My RNN works for short words but forgets long sentences. How do I give it longer memory?" The answer: LSTMs.

---

← [Previous: Phase 12: Residual Networks](docs/phase12/SUMMARY.md) | [Next: Phase 14: LSTMs](docs/phase14/SUMMARY.md) →