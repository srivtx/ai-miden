## What Is Multi-Token Prediction?

---

### The Problem

Standard language models are trained with next-token prediction: given tokens t_1 through t_n, predict t_{n+1}. Every forward pass produces exactly one label, so the model sees one gradient signal per sequence position. At billion-parameter scale, this is computationally wasteful. The forward pass computes a full contextual representation that could predict t_{n+2}, t_{n+3}, and t_{n+4} just as well, but that information is thrown away. Training times stretch to months because the gradient signal is sparse. How do you extract more supervision from the same computation?

---

### Definition

**Multi-Token Prediction (MTP)** is a training objective where the model predicts N future tokens simultaneously using N independent classification heads attached to the same hidden representation. Each head is a linear projection from the base model's output to the vocabulary, trained with cross-entropy against its respective future token. The total loss is the average cross-entropy over the N predictions.

**How it works:**
```
Standard next-token prediction:
  hidden = Transformer(tokens[0:T])
  logits = LM_head(hidden[0:T-1])
  loss = CrossEntropy(logits, tokens[1:T])

Multi-token prediction (N=4):
  hidden = Transformer(tokens[0:T])
  logits_1 = head_1(hidden[0:T-1])  → target tokens[1:T]
  logits_2 = head_2(hidden[0:T-2])  → target tokens[2:T]
  logits_3 = head_3(hidden[0:T-3])  → target tokens[3:T]
  logits_4 = head_4(hidden[0:T-4])  → target tokens[4:T]
  loss = (CE_1 + CE_2 + CE_3 + CE_4) / 4
```

**Information theory argument:**
Natural language is highly autocorrelated. If the model knows "The cat sat on the", predicting "mat" is easy, and predicting "and" after "mat" is also easy because the context is rich. Predicting four tokens at once is not four times harder; the heads share the same contextual backbone, and the conditional entropy of future tokens given the past is lower than the marginal entropy of each token alone.

**Difference from speculative decoding:**
- **MTP** is a training-time objective. It changes what the model learns.
- **Speculative decoding** is an inference-time technique. It uses a small draft model to propose tokens that the large model verifies. MTP-trained models can serve as their own draft models, but the concepts are orthogonal.

---

### Real-Life Analogy

Imagine a chess grandmaster analyzing a position.

**Standard next-token prediction** is like asking the grandmaster to name only the next move. They study the board deeply, formulate a plan, announce "Knight to f3," and then the position is reset. All the strategic insight they developed about move two, three, and four is discarded. They must re-analyze the position from scratch for every single move.

**Multi-token prediction** is like asking the grandmaster to announce their next four moves at once. They still perform one deep analysis, but now they output "1. Nf3 2. c4 3. Nc3 4. d4." The analysis cost is roughly the same because understanding the position deeply is what takes time; listing the continuation is cheap. Moreover, forcing the grandmaster to think about move four while analyzing move one sharpens their strategic planning. They catch long-term weaknesses they might have missed if they only thought one move ahead.

**The trade-off:** the grandmaster might occasionally misjudge move four because the position could change unpredictably. But the extra training makes their overall intuition stronger, and in practice their endgame accuracy improves because they have practiced long-range planning.

---

### Tiny Numeric Example

**A tiny vocabulary {A, B, C, D} and sequence "A B C D A B C D":**

**Standard loss at position 0 (predicting token 1 = B):**
```
Context: [A]
Logits:  [0.1, 2.0, 0.3, 0.1]  → probabilities [0.11, 0.67, 0.15, 0.07]
Target: B (index 1)
Cross-entropy: -log(0.67) = 0.40
```

**MTP loss at position 0 (predicting tokens 1, 2, 3, 4 = B, C, D, A):**
```
Context: [A]
Head 1 logits: [0.1, 2.0, 0.3, 0.1]  → CE = 0.40
Head 2 logits: [0.2, 0.4, 1.8, 0.2]  → target C, prob 0.60, CE = 0.51
Head 3 logits: [0.3, 0.1, 0.2, 1.5]  → target D, prob 0.65, CE = 0.43
Head 4 logits: [1.6, 0.2, 0.1, 0.3]  → target A, prob 0.70, CE = 0.36
MTP loss = (0.40 + 0.51 + 0.43 + 0.36) / 4 = 0.425
```

**Gradient comparison:**
```
Standard backprop at position 0:
  Gradient flows back through 1 head only.
  Gradient norm = 1.2

MTP backprop at position 0:
  Gradients from 4 heads sum into the shared trunk.
  Gradient norm = 3.8
  The signal is richer but requires careful scaling to avoid exploding gradients.
```

**The shift:** one forward pass produces four independent supervisory signals. The model learns four times as much about how context predicts the future, while the backbone computation — the expensive transformer layers — is shared.

---

### Common Confusion

1. **"MTP hurts quality because the later heads have less information."** The later heads do have less direct context, but they benefit from the same deep representation. Empirical results from DeepSeek-V3 and Meta show no quality degradation; in fact, some tasks improve because the model learns longer-range dependencies.

2. **"MTP is the same as speculative decoding."** Speculative decoding happens at inference time and does not change the training loss. MTP is a training objective. A model trained with MTP can be used for standard autoregressive inference, or its extra heads can be used for speculative decoding, but the training objective itself is independent.

3. **"Predicting four tokens is four times harder, so the model needs four times the capacity."** The heads are tiny (vocab-sized linear layers) compared to the backbone. The extra parameters are negligible. The difficulty is sublinear because tokens are correlated.

4. **"MTP requires four times the memory for activations."** Only the logits and loss for the extra heads are stored. The shared transformer activations are computed once. Memory overhead is roughly 10-15%, not 4x.

5. **"MTP only works for small models."** DeepSeek-V3, a 671B parameter model, uses MTP. The technique scales to the largest models because the overhead is additive (small heads) while the gain is multiplicative (more labels per pass).

6. **"MTP changes the inference API."** At inference time, you can drop the extra heads and use only head_1. The model behaves exactly like a standard next-token model. The extra heads are optional accelerators, not requirements.

7. **"MTP requires a special dataset."** No. Any standard text corpus works. You simply slice the targets differently: instead of shifting by one, you create four shifted target sequences.

---

### Where It Is Used in Our Code

`src/phase112/phase112_mtp_concepts.py` — We simulate a tiny language model with four MTP heads in NumPy, showing how one forward pass produces four next-token predictions and how the averaged cross-entropy loss compares to standard next-token loss. We visualize gradient norms and token probability distributions to demonstrate that MTP provides richer gradients without changing the backbone architecture.

`src/phase112/phase112_mtp_training_colab.py` — We load GPT-2 124M, add three additional LM heads, and train on WikiText-2 with MTP loss. We compare loss curves, perplexity, and training throughput against standard next-token training to show that MTP processes 4x more tokens per forward pass.
