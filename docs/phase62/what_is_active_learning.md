## What Is Active Learning?

---

### The Problem

Labeling data is expensive. A medical expert charges $500/hour to label X-rays. A linguist takes hours to annotate a single document. You have 1 million unlabeled images but can only afford to label 1,000. How do you choose which 1,000 examples to label so that your model learns the most from them?

---

### Definition

**Active learning** is a training paradigm where the model actively selects which unlabeled examples it wants labeled next. Instead of random sampling, the model queries the most informative examples — the ones it is most uncertain about.

**The active learning loop:**
```
1. Start with a small labeled dataset
2. Train a model on the labeled data
3. Use the model to evaluate all unlabeled examples
4. Select the most informative examples (query strategy)
5. Ask a human (oracle) to label those examples
6. Add newly labeled examples to the training set
7. Repeat until budget is exhausted
```

**Why this matters:**
- Active learning can achieve the same accuracy with 10-50% fewer labels
- It focuses human effort on the most valuable examples
- Critical for domains where labeling is expensive: medicine, law, science

---

### Real-Life Analogy

A student preparing for an exam with a tutor.
- **Passive learning (random sampling):** The tutor randomly selects 100 problems from the textbook. Many are too easy. Many are too hard. The student wastes time.
- **Active learning:** The tutor gives the student a diagnostic quiz. The student struggles with calculus but aces algebra. The tutor focuses the next session on calculus. After 50 targeted problems, the student is ready for the exam.
- **The key:** The student (model) identifies their own weaknesses (uncertain predictions) and asks for help on those specifically.

---

### Tiny Numeric Example

**Dataset:** 100 points, binary classification
**Budget:** Label only 20 points

**Random sampling (label 20 random points):**
```
Labeled: mostly easy examples near the decision boundary
Model accuracy after training: 82%
```

**Active learning (uncertainty sampling, label 20 most uncertain):**
```
Round 1: Label 5 most uncertain → train → model improves
Round 2: Label next 5 most uncertain → train → model improves more
Round 3: Label next 5 most uncertain
Round 4: Label next 5 most uncertain

Model accuracy: 91% (same budget, better result)
```

The active learner strategically placed its labels near the decision boundary where they mattered most.

---

### Common Confusion

1. **"Active learning is just data augmentation."** No. Augmentation creates synthetic data. Active learning selects real data for labeling.

2. **"Active learning only works for classification."** No. It works for regression, segmentation, NLP, and any task with an uncertainty measure.

3. **"The model trains itself without labels."** No. The model selects which unlabeled examples to ask a human to label.

4. **"Active learning is always better than random sampling."** Usually yes, but if the initial model is terrible, its uncertainty estimates are unreliable.

5. **"Active learning requires retraining from scratch each round."** No. You can incrementally fine-tune. But retraining often works better.

---

### Where It Is Used in Our Code

`src/phase62/phase62_active_learning.py` — We simulate an active learning loop on a 2D classification task, comparing random sampling vs. uncertainty sampling, and showing how active learning reaches higher accuracy with fewer labeled examples.
