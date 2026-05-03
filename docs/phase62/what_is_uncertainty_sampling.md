## What Is Uncertainty Sampling?

---

### The Problem

In active learning, you need a rule for selecting which unlabeled examples to label. The simplest idea: pick the examples the model is least confident about. But "uncertainty" can mean different things. What is the best way to measure it?

---

### Definition

**Uncertainty sampling** is a query strategy for active learning that selects unlabeled examples where the model's prediction is most uncertain.

**Types of uncertainty:**

**1. Least confident:**
```
Uncertainty = 1 - max(p(y|x))
```
- Pick examples where the highest predicted probability is lowest
- Simple but ignores information about other classes

**2. Margin sampling:**
```
Uncertainty = p(y_1|x) - p(y_2|x)
```
- Difference between top two predicted probabilities
- Small margin = model is torn between two classes
- Better than least confident because it considers the runner-up

**3. Entropy:**
```
Uncertainty = -Σ p(y_i|x) * log(p(y_i|x))
```
- Measures overall uncertainty across all classes
- High entropy = model is confused across many classes
- Most informative measure for multi-class problems

**Why this matters:**
- Different uncertainty measures work better for different problems
- Entropy is theoretically optimal but computationally heavier
- Margin sampling is a good balance of effectiveness and simplicity

---

### Real-Life Analogy

A student deciding which homework problem to ask the teacher about.
- **Least confident:** "I have no idea how to solve problem 7." (But maybe it is just one hard problem and the rest are fine.)
- **Margin sampling:** "I am torn between answer A and answer B on problem 12." (The student has narrowed it down to two options. One clarification will resolve it.)
- **Entropy:** "I am completely confused about problem 15. It could be A, B, C, or D." (The student needs fundamental help on this topic.)

The teacher should prioritize problems where the student is almost right but needs a small push (margin sampling) and problems where the student is fundamentally lost (high entropy).

---

### Tiny Numeric Example

**Three-class classification:**

**Example A:**
```
Probabilities: [0.9, 0.05, 0.05]
Least confident: 1 - 0.9 = 0.1
Margin: 0.9 - 0.05 = 0.85
Entropy: -(0.9*log(0.9) + 0.05*log(0.05)*2) = 0.39
```

**Example B:**
```
Probabilities: [0.4, 0.35, 0.25]
Least confident: 1 - 0.4 = 0.6
Margin: 0.4 - 0.35 = 0.05
Entropy: -(0.4*log(0.4) + 0.35*log(0.35) + 0.25*log(0.25)) = 1.08
```

**Example C:**
```
Probabilities: [0.5, 0.5, 0.0]
Least confident: 1 - 0.5 = 0.5
Margin: 0.5 - 0.5 = 0.0
Entropy: -(0.5*log(0.5)*2) = 0.69
```

**Selection:**
```
Least confident: B (0.6) > C (0.5) > A (0.1)
Margin: B (0.05) > C (0.0) > A (0.85)
Entropy: B (1.08) > C (0.69) > A (0.39)
```

All three methods agree: **Example B** is the most uncertain and should be labeled first.

---

### Common Confusion

1. **"Uncertainty sampling only works for probabilistic models."** Mostly true. You need a confidence score. For SVMs, you can use distance to decision boundary. For neural networks, use softmax probabilities.

2. **"High uncertainty means the example is noisy or mislabeled."** Sometimes, but not always. High uncertainty often means the example is near the decision boundary — exactly where labels are most valuable.

3. **"You should always pick the most uncertain example."** Usually yes, but diversity-aware sampling also considers covering different regions of the input space.

4. **"Uncertainty sampling is the only query strategy."** No. Other strategies include query-by-committee, expected model change, and density-weighted methods.

5. **"Uncertainty sampling works for regression."** Yes, but uncertainty is measured differently: prediction variance, confidence interval width, or epistemic uncertainty from Bayesian models.

---

### Where It Is Used in Our Code

`src/phase62/phase62_active_learning.py` — We implement least-confident, margin, and entropy sampling on a classification task, comparing which strategy finds the most informative examples fastest.
