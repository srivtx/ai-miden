## What Is Causal Language Modeling?

---

### The Problem

Supervised learning needs labels. But the internet contains trillions of words with no labels attached. How do you train a model on that scale without paying humans to annotate every sentence? If you cannot use labels, what signal do you optimize?

---

### Definition

**Causal Language Modeling (CLM)** is a self-supervised training objective where the model learns to predict the next token in a sequence given all preceding tokens. Because the future is hidden from the model, the prediction is "causal" — it can only look backward in time, never forward.

**How it works:**
```
Input sequence:  [The, cat, sat, on, the, ...]
Model sees:      [The, cat, sat, on]
Target:          [cat, sat, on, the]
Loss:            cross_entropy(predicted_next_token, actual_next_token)
```

At every position `i`, the model outputs a probability distribution over the vocabulary for token `i+1`. The training loss is the average negative log-likelihood of the true next token across all positions in the batch.

**Key techniques:**
- **Autoregressive masking:** the attention mechanism uses a causal (lower-triangular) mask so position `i` cannot attend to positions `j > i`
- **Shift-by-one:** inputs are the sequence shifted left by one; targets are the sequence shifted right by one
- **Data efficiency:** every token in the corpus serves as a training example, so a 1B-token corpus yields 1B training examples with zero labeling cost

**Why this matters:**
- CLM is the foundation of GPT, Llama, Qwen, and every major generative language model.
- It scales linearly with data: more text means more signal with no annotation bottleneck.
- The autoregressive structure naturally produces a generative model: you can sample from it indefinitely by feeding each prediction back as the next input.

---

### Real-Life Analogy

Reading a book with a bookmark covering the future pages.
- **Causal language modeling:** You read "The cat sat on the..." and guess the next word before you turn the page. If you guess "mat," you are rewarded. If you guess "refrigerator," you learn from the mistake. You never peek ahead. Every word in the book is a practice problem.
- **Masked language modeling:** You read a page with some words blacked out. You guess the blacked-out words using the surrounding context. This is useful (BERT does this), but it does not teach you to write stories from left to right.
- **The difference:** The bookmark reader learns to generate coherent sequences. The blackout reader learns to fill gaps. Generative assistants need the bookmark method.

---

### Tiny Numeric Example

**Vocabulary: [the, cat, sat, on, mat, dog]**

**Input sequence token IDs:** `[0, 1, 2, 3]` (the, cat, sat, on)
**Target token IDs:** `[1, 2, 3, 4]` (cat, sat, on, mat)

**Model logits at position 3 (predicting token after "on"):**
```
the:    0.5
cat:    1.2
sat:    0.8
on:     0.3
mat:    2.4   <- target
dog:    0.1
```

**Softmax probabilities:**
```
the:    0.08
cat:    0.15
sat:    0.11
on:     0.06
mat:    0.54   <- target probability
dog:    0.05
```

**Cross-entropy loss at position 3:** `-log(0.54) = 0.616`

**Average loss over all 4 positions:** `(2.10 + 0.89 + 0.45 + 0.616) / 4 = 1.01`

**Perplexity:** `exp(1.01) = 2.75` (the model is equivalent to having a vocabulary of 2.75 equally likely choices at each step)

---

### Common Confusion

1. **"Causal language modeling needs labeled data."** No. The labels are the text itself, shifted by one position. The supervision is free because the correct answer is literally the next word in the sentence.

2. **"CLM and masked LM are the same thing."** They are fundamentally different. CLM predicts the future from the past. Masked LM predicts missing tokens from bidirectional context. CLM produces generative decoders; masked LM produces encoders.

3. **"The model learns grammar explicitly."** It does not. It learns that "the cat sat" has a higher probability than "the cat satted." Grammar emerges as a statistical regularity, not as a rule.

4. **"A lower perplexity always means a better model."** Lower perplexity on the training distribution means better compression of that distribution. But it can also mean the model memorized the training data or collapsed to repetitive patterns. Perplexity must be paired with diversity and downstream benchmarks.

5. **"CLM only works for text."** False. The same principle applies to code (next token prediction), music (next note), DNA sequences (next base pair), and time-series forecasting (next value).

6. **"You need sentence boundaries for CLM."** Modern training uses contiguous chunks of text with no sentence boundaries. The model learns to transition across boundaries, which improves long-form coherence.

7. **"CLM cannot learn reasoning because it only predicts one token."** This is a shallow objection. Reasoning emerges from the compounding of millions of single-token predictions. Each step is local, but the chain of steps can solve global problems.

---

### Where It Is Used in Our Code

`src/phase121/phase121_pretraining_concepts.py` — We implement a tiny causal language model in NumPy. We compute the shifted target sequence, apply softmax over the vocabulary, and calculate cross-entropy loss position-by-position to show exactly how CLM works under the hood.

`src/phase121/phase121_pretraining_colab.py` — We train a real GPT-2 model on WikiText-2 using the causal language modeling objective. Every training step optimizes next-token prediction, and we evaluate perplexity (the standard CLM metric) to measure learning progress.

(End of file - total 101 lines)
