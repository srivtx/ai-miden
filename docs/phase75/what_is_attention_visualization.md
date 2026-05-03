# What is Attention Visualization?

## 1. Why it exists (THE PROBLEM)

Transformer models use self-attention to mix information across tokens, but the attention matrix itself is just a grid of numbers. How do you turn that grid into an explanation?

**Attention visualization** plots the attention weights as a heatmap so humans can see which tokens "looked at" which other tokens. It is one of the most intuitive ways to peek inside a Transformer.

## 2. Definition (very simple)

**Attention visualization** is the practice of displaying the attention weight matrix as a colored heatmap, where rows represent *query* tokens and columns represent *key* tokens. Bright cells mean strong attention; dark cells mean weak attention.

It answers: *"When producing token i, which input tokens did the model focus on?"*

Common variants:
- **Single-head visualization**: Show one attention head's matrix.
- **Averaged heads**: Average across all heads for a cleaner picture.
- **Attention rollout**: Propagate attention through layers to show influence across the full depth of the model.

## 3. Real-life analogy

You are in a group discussion with 5 people. Every time someone speaks, you look at different people for cues.

- When Alice speaks, she mostly looks at Bob (maybe she is addressing him).
- When Carol speaks, she glances at everyone equally (she is summarizing).
- When Dave speaks, he only looks at his notes (he is self-contained).

An attention heatmap is a snapshot of "who looked at whom" during the conversation. It does not tell you *why*, but it tells you where the information flowed.

## 4. Tiny numeric example

A 3-token sequence: `[The, cat, sat]`

Attention scores (before softmax):
```
        The   cat   sat
The    [2.0,  1.0,  0.5]
cat    [1.0,  3.0,  1.5]
sat    [0.5,  1.5,  2.5]
```

After row-wise softmax:
```
        The   cat   sat
The    [0.60, 0.22, 0.18]
cat    [0.16, 0.60, 0.24]
sat    [0.14, 0.32, 0.54]
```

**Visualization**: A 3x3 heatmap where:
- The cell (cat, cat) is brightest (0.60) — the word "cat" attends most to itself.
- The cell (sat, sat) is bright (0.54) — "sat" attends to itself.
- The cell (sat, cat) is moderately bright (0.32) — "sat" also looks back at "cat," which makes grammatical sense.

## 5. Common confusion (5+ bullet points)

- **Attention is not explanation by default**: Attention weights show correlation, not causation. A model can attend to a token and still ignore its content. Studies have shown that zeroing out attended tokens sometimes does not change the prediction.
- **Different heads do different things**: Averaging across heads can wash out interesting patterns. One head might track syntax, another might track coreference. Always inspect individual heads first.
- **Attention rollout is not the same as raw attention**: In deep models, attention in layer 2 depends on the mixed representations from layer 1. Rollout multiplies attention matrices across layers to approximate the total influence of an input token on an output token.
- **Vertical vs. horizontal axes**: Some papers plot queries on the x-axis and keys on the y-axis; others do the opposite. Always check the axis labels.
- **Scale matters**: If one head has very sharp attention (one weight near 1.0) and another has diffuse attention (all weights ~0.2), averaging them creates a misleading middle ground.
- **Attention does not show negative influence**: Attention weights are non-negative (thanks to softmax). A token can suppress a prediction through its value vector while still receiving high attention, and the heatmap will not reveal that.

## 6. Where it is used in our code

- `src/phase75/phase75_xai_numpy.py` — Implements a tiny single-head self-attention block on a 4-token synthetic sequence. Computes Q, K, V, softmax attention, and plots the heatmap with token labels.
- `src/phase75/phase75_xai_colab.py` — Uses PyTorch to build a small Transformer and visualizes multi-head attention with `matplotlib`.
