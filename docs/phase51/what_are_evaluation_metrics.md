## What Are Evaluation Metrics?

---

### The Problem

Your model is trained. Loss is going down. But does it actually work? A spam classifier might get 99% accuracy by always predicting "not spam" — useless. A language model might generate fluent gibberish. How do you measure what matters?

---

### Definition

**Evaluation metrics** are quantitative measures of model performance on a specific task. Unlike loss (which the model optimizes), metrics tell humans whether the model is useful.

**Why metrics differ from loss:**
- Loss is differentiable (needed for gradient descent)
- Metrics are human-interpretable (needed for decisions)
- A model can have low loss but terrible metrics, or vice versa

**Key metrics by task:**

**Classification:**
- **Accuracy:** Fraction correct. Misleading with imbalanced data.
- **Precision:** Of predicted positives, how many are correct?
- **Recall:** Of actual positives, how many did we find?
- **F1:** Harmonic mean of precision and recall

**Generation (text):**
- **Perplexity:** How "surprised" the model is by real text
- **BLEU:** N-gram overlap with reference text
- **ROUGE:** Recall-oriented overlap for summaries

**Regression:**
- **MAE:** Mean absolute error
- **RMSE:** Root mean squared error
- **R²:** Variance explained

**Calibration:**
- **ECE:** Expected calibration error. Does 80% confidence mean 80% accuracy?

---

### Real-Life Analogy

A student taking an exam.
- **Loss:** How hard the student studied (input effort). Not directly observable.
- **Accuracy:** Percentage of questions answered correctly. But if the test is all easy questions, 100% means nothing.
- **Precision/Recall:** In a medical diagnosis test, precision = "of students flagged as sick, how many actually are?" Recall = "of actually sick students, how many did we flag?"
- **Perplexity:** How "confused" the student is by the exam. Lower is better.

Metrics tell you whether the student can actually DO the job, not just whether they tried hard.

---

### Tiny Numeric Example

**Spam classifier predictions vs. ground truth:**
```
Actual:    [Spam, Spam, Not, Spam, Not, Not, Not, Spam]
Predicted: [Spam, Not,  Not, Spam, Spam, Not, Not, Not]
```

**Confusion matrix:**
```
              Predicted
              Spam   Not
Actual Spam    2      2
       Not     1      3
```

**Accuracy:** (2 + 3) / 8 = 62.5%

**Precision:** 2 / (2 + 1) = 66.7% (of predicted spam, 2/3 correct)

**Recall:** 2 / (2 + 2) = 50% (found 2 of 4 actual spam)

**F1:** 2 × (0.667 × 0.5) / (0.667 + 0.5) = 57.1%

**The model looks mediocre on all metrics** — not the 99% accuracy trap, but genuinely weak. Metrics reveal this clearly.

---

### Common Confusion

1. **"High accuracy means a good model."** Only with balanced data. A fraud detector with 99.9% accuracy might never detect fraud (if fraud is 0.1% of data).

2. **"Perplexity measures human quality."** No. Perplexity measures statistical fit. A model with low perplexity can still generate nonsense.

3. **"BLEU score correlates with human judgment."** Roughly, but not perfectly. A translation with perfect BLEU can be unnatural, and a natural translation can have low BLEU.

4. **"You only need one metric."** Real evaluation uses multiple metrics. Accuracy + precision + recall + calibration gives a fuller picture.

5. **"Metrics are objective."** The choice of metric is a design decision that encodes values. Optimizing for recall vs. precision is a choice about false positives vs. false negatives.

---

### Where It Is Used in Our Code

`src/phase51/phase51_evaluation_metrics.py` — We compute accuracy, precision, recall, F1, perplexity, and calibration error on synthetic predictions, showing how different metrics reveal different failure modes.
