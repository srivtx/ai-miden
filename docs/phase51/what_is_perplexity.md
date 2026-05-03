## What Is Perplexity?

---

### The Problem

You have a language model. It assigns probabilities to words. How do you summarize its overall quality in a single number? You could report the average log-probability, but that is hard to interpret. Is -2.3 good or bad?

---

### Definition

**Perplexity** is the exponential of the average negative log-likelihood. It measures how "surprised" the model is by the test data. Lower is better.

**Formula:**
```
Perplexity = exp(-(1/N) × Σ log P(word_i | context_i))
```

**Intuition:**
- Perplexity = 100 means the model is as confused as if it had to choose uniformly from 100 options at each step
- Perplexity = 2 means the model is nearly certain (like a coin flip)
- A well-trained GPT-3 has perplexity ~10-20 on web text
- A random model has perplexity = vocab_size (e.g., 50,000)

**Why perplexity matters:**
- It is the standard metric for language models
- It correlates with downstream performance (lower perplexity -> better generation)
- It is differentiable (the model can optimize it directly)

**Perplexity vs. Cross-Entropy:**
```
Cross-Entropy = -(1/N) × Σ log P(word_i | context_i)
Perplexity = exp(Cross-Entropy)
```
They contain the same information. Perplexity is just cross-entropy in "number of equivalent choices" units.

---

### Real-Life Analogy

A weather forecaster.
- **Perplexity = 2:** The forecaster says "70% chance of rain." They are pretty sure. You need an umbrella.
- **Perplexity = 10:** The forecaster says "it might rain, or be sunny, or snow." They are genuinely uncertain.
- **Perplexity = 100:** The forecaster has no idea. They might as well pick a random weather pattern.

Perplexity measures the forecaster's uncertainty. A good model should not be surprised by real text.

---

### Tiny Numeric Example

**Sequence: "the cat sat"**

**Model probabilities:**
```
P("the") = 0.05
P("cat" | "the") = 0.02
P("sat" | "the cat") = 0.03
```

**Cross-entropy:**
```
CE = -(log(0.05) + log(0.02) + log(0.03)) / 3
   = -(-2.996 - 3.912 - 3.507) / 3
   = 10.415 / 3 = 3.47
```

**Perplexity:**
```
PP = exp(3.47) = 32.1
```

**Interpretation:** The model is as uncertain as if choosing among 32 equally likely options at each step.

**Better model:**
```
P("the") = 0.08
P("cat" | "the") = 0.05
P("sat" | "the cat") = 0.10
CE = 2.55, PP = 12.8
```

The better model has lower perplexity (12.8 vs. 32.1).

---

### Common Confusion

1. **"Perplexity measures human-like text."** Not directly. It measures statistical fit. A model with low perplexity on news text might generate boring, repetitive text.

2. **"Perplexity can be compared across different vocabularies."** No. A model with a smaller vocabulary has an unfair advantage because there are fewer choices.

3. **"Perplexity is only for language models."** It can be used for any probabilistic model: speech recognition, machine translation, music generation.

4. **"Lower perplexity is always better."** Usually yes, but extremely low perplexity can mean the model is memorizing the training data (overfitting).

5. **"Perplexity is the same as bits per character."** Related but different. Bits per character = log₂(perplexity). Perplexity uses natural log.

---

### Where It Is Used in Our Code

`src/phase51/phase51_evaluation_metrics.py` — We compute perplexity for a tiny language model on a test corpus, showing how it measures model uncertainty.
