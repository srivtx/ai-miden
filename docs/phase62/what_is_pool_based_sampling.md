## What Is Pool-Based Sampling?

---

### The Problem

In active learning, you need a source of unlabeled examples to query from. You cannot just generate random examples — they must be realistic inputs that the model will actually encounter in deployment. How do you maintain and sample from a large collection of unlabeled data?

---

### Definition

**Pool-based sampling** is the most common active learning scenario where the model selects examples to label from a large, fixed pool of unlabeled data.

**Alternative scenarios:**

**Stream-based sampling:**
```
Data arrives one example at a time (e.g., from a sensor).
For each example, the model decides: label it or discard it?
```

**Membership query synthesis:**
```
The model generates synthetic examples and asks the oracle to label them.
"What label should this AI-generated image have?"
```

**Pool-based (most common):**
```
You have a fixed pool of 100,000 unlabeled images.
The model evaluates all 100,000 and picks the top 100 to label.
```

**Why pool-based is dominant:**
- Most organizations already have large unlabeled datasets
- Evaluating the entire pool is feasible with modern compute
- It gives the model a global view of all available data

---

### Real-Life Analogy

A hiring manager with a stack of 1,000 resumes.
- **Pool-based sampling:** The manager reads all 1,000 resumes (or uses software to score them), then selects the top 20 for interviews. They have a complete view of the candidate pool.
- **Stream-based:** Resumes arrive by email one at a time. The manager must decide to interview or reject each immediately, without seeing future resumes.
- **Membership query:** The manager asks an AI to generate "ideal candidate" profiles and asks HR to find real people matching those profiles.

Pool-based sampling is the gold standard when you have all the data upfront.

---

### Tiny Numeric Example

**Pool:** 20 unlabeled 2D points
**Budget:** Label 5 points
**Model:** Trained on 3 initial labeled points

**Step 1: Evaluate all 20 points**
```
Point 1:  uncertainty = 0.95
Point 2:  uncertainty = 0.92
Point 3:  uncertainty = 0.88
...
Point 20: uncertainty = 0.10
```

**Step 2: Select top 5 by uncertainty**
```
Selected: Points 1, 2, 3, 4, 5
```

**Step 3: Label selected points**
```
Oracle (human) provides labels for Points 1-5.
```

**Step 4: Retrain model**
```
Model now trained on 3 + 5 = 8 labeled points.
```

**Step 5: Repeat**
```
Evaluate remaining 15 unlabeled points.
Select next 5 most uncertain.
```

After 3 rounds (15 labeled points), the model often matches the performance of random sampling with 30 labeled points.

---

### Common Confusion

1. **"Pool-based sampling requires evaluating the entire pool every round."** Yes, that is the main cost. But for many models (neural networks), forward passes on unlabeled data are fast.

2. **"The pool must be representative of deployment data."** Yes. If the pool does not match real-world inputs, active learning will not help.

3. **"Pool-based is always better than stream-based."** Not if data arrives in real-time and you cannot store it all (e.g., sensor streams).

4. **"You must start with a large pool."** The pool can be as small as 100 examples. Active learning helps at any scale where labeling is expensive.

5. **"Pool-based sampling is only for classification."** No. It works for any task: regression, segmentation, object detection, NLP.

---

### Where It Is Used in Our Code

`src/phase62/phase62_active_learning.py` — We maintain a pool of 200 unlabeled 2D points and iteratively select the most informative ones for labeling, showing how the model's decision boundary improves with each round of pool-based active learning.
