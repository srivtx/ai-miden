## What Is AdaBoost?

---

### The Problem

You have many weak classifiers — each slightly better than random guessing. Individually, they are useless. But what if you could combine them so that each new classifier focuses on the examples the previous ones got wrong? Could many weak learners become one strong learner?

---

### Definition

**AdaBoost (Adaptive Boosting)** is an ensemble method that trains weak classifiers sequentially, adjusting the weight of each training example so that misclassified examples get higher weight. The final prediction is a weighted vote of all classifiers.

**How it works:**
```
1. Start with equal weights for all training examples
2. Train a weak classifier on the weighted data
3. Compute the classifier's error rate: ε = Σ weight_i × [predicted ≠ actual]
4. Compute classifier weight: α = 0.5 × ln((1-ε)/ε)
   (good classifiers get high weight, bad classifiers get low/negative weight)
5. Update example weights:
   - Increase weight for misclassified examples
   - Decrease weight for correctly classified examples
   - Normalize so weights sum to 1
6. Repeat steps 2-5 for N rounds
7. Final prediction = weighted majority vote of all classifiers
```

**Key insight:**
- AdaBoost is a special case of gradient boosting where the loss function is exponential loss
- It adaptively focuses on hard examples, making it robust to noise if stopped early
- The weighted voting ensures good classifiers matter more than bad ones

**Why this matters:**
- AdaBoost was the first successful boosting algorithm (Freund & Schapire, 1997)
- It proved that weak learners can be combined into strong learners
- It is the conceptual ancestor of gradient boosting and XGBoost

---

### Real-Life Analogy

A jury deliberating a complex case.
- **Round 1:** All jurors vote equally. 6 say guilty, 6 say not guilty. The case is tied.
- **The judge (AdaBoost):** "Juror 3, you were correct on 90% of past cases. Your vote counts 3×. Juror 7, you were only correct on 40%. Your vote counts 0.4×."
- **Round 2:** The judge focuses on the evidence that confused the most jurors in Round 1. The jury revisits those points.
- **Round 3:** The judge focuses on the evidence still causing disagreement.
- **Final verdict:** Weighted vote where accurate jurors have more say.

AdaBoost is the judge who learns which jurors to trust and which evidence to revisit.

---

### Tiny Numeric Example

**Dataset (binary classification):**
```
x = [1, 2, 3, 4]
y = [-1, -1, 1, 1]  (stumps classify x > threshold as +1)
```

**Round 1:**
```
Initial weights: [0.25, 0.25, 0.25, 0.25]

Stump: predict +1 if x > 2.5, else -1
Predictions: [-1, -1, 1, 1] — all correct!
Error ε = 0
Classifier weight α = 0.5 × ln((1-0)/0) = infinity
```

This stump is perfect, so AdaBoost stops. Let us use a worse stump:

**Round 1 (worse stump: x > 1.5):**
```
Predictions: [-1, 1, 1, 1]
Mistake on x=2 (should be -1)
Error ε = 0.25 (weight of x=2)

Classifier weight:
α = 0.5 × ln((1-0.25)/0.25) = 0.5 × ln(3) = 0.549

Update weights:
Correct examples (x=1,3,4): weight × exp(-α) = 0.25 × 0.578 = 0.145
Incorrect example (x=2): weight × exp(α) = 0.25 × 1.732 = 0.433

Normalize: sum = 0.145×3 + 0.433 = 0.868
New weights: [0.167, 0.499, 0.167, 0.167]
```

**Round 2:**
```
x=2 now has 50% of the total weight.
The next stump will focus on classifying x=2 correctly.
Stump: x > 2.5 (classifies x=2 as -1, correct)
Predictions: [-1, -1, 1, 1] — all correct on weighted data!
```

**Final prediction:**
```
Stump 1 weight: 0.549, predicts [ -1, 1, 1, 1]
Stump 2 weight: large, predicts [ -1, -1, 1, 1]

For x=2:
  Stump 1 says +1 with weight 0.549
  Stump 2 says -1 with large weight
  Weighted vote: -1 wins (Stump 2 has more weight)
```

---

### Common Confusion

1. **"AdaBoost and gradient boosting are the same."** Related but different. AdaBoost uses exponential loss and reweights examples. Gradient boosting uses any differentiable loss and fits residuals.

2. **"AdaBoost requires weak learners to be better than random."** Yes. If a learner is worse than random (error > 0.5), AdaBoost flips its predictions and uses it.

3. **"AdaBoost is outdated."** Conceptually yes — gradient boosting/XGBoost perform better. But AdaBoost introduced the key insight that boosting works, which changed machine learning.

4. **"AdaBoost cannot handle noise."** It is actually sensitive to noise because it focuses on hard examples (which may be mislabeled). Gradient boosting with regularization is more robust.

5. **"More rounds always help."** No. AdaBoost can overfit if run too long. Early stopping is essential.

---

### Where It Is Used in Our Code

`src/phase56/phase56_gradient_boosting.py` — We implement a simplified AdaBoost-style reweighting on a classification task, showing how example weights adapt and how the weighted vote combines weak stumps into a strong classifier.
