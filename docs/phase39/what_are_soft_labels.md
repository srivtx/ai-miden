## What Are Soft Labels?

---

### The Problem

In standard classification, the target is a one-hot vector: [1, 0, 0] for class 0. This is a **hard label** — it says class 0 is 100% correct and the others are 0% correct. But in reality, class 1 might be quite similar to class 0, while class 2 is completely different. How do you encode this nuance in the training target?

---

### Definition

**Soft labels** are probability distributions over all classes that encode the relative likelihood of each class. Instead of [1, 0, 0], a soft label might be [0.70, 0.25, 0.05].

**Sources of soft labels:**
1. **Teacher model:** A large model's predicted probabilities
2. **Label smoothing:** Artificially soften hard labels (e.g., [0.9, 0.05, 0.05] instead of [1, 0, 0])
3. **Human annotators:** Multiple humans label the same example and aggregate their votes

**Why soft labels help:**
- They encode similarity structure between classes
- They provide richer gradients (all classes contribute, not just the correct one)
- They act as regularization, preventing overconfidence

---

### Real-Life Analogy

A biology exam.
- **Hard label grading:** Question: "What is this animal?" Answer: "Cat." Grade: 100% if correct, 0% if wrong. A student who answered "lynx" gets the same 0% as a student who answered "table."
- **Soft label grading:** The teacher's answer key says: "Cat: 70%, Lynx: 20%, Tiger: 10%." The student who answered "lynx" gets partial credit because lynx is biologically similar to cat. The student who answered "table" gets 0%.

Soft labels reward understanding of relationships, not just memorization of categories.

---

### Tiny Numeric Example

**3-class problem:** {apple, pear, stone}

**Hard label for an apple:**
```
[1.0, 0.0, 0.0]
```

**Soft label (from teacher, T=2):**
```
Teacher logits: [2.0, 1.0, -3.0]
Teacher logits / T: [1.0, 0.5, -1.5]
exp: [2.718, 1.649, 0.223]
sum: 4.590
Soft label: [0.592, 0.359, 0.049]
```

**What the soft label encodes:**
- Apple is most likely (59%)
- Pear is somewhat likely (36%) — because pears look and taste similar to apples
- Stone is very unlikely (5%) — completely different category

**Training with soft labels:**
The student's loss is:
```
L = -Σ soft_label(i) × log(P_student(i))
  = -(0.592 × log(0.55) + 0.359 × log(0.30) + 0.049 × log(0.15))
```

All three classes contribute to the gradient. The student learns to distinguish apples from pears AND learns that pears are more similar to apples than stones are.

---

### Common Confusion

1. **"Soft labels are just label smoothing."** Label smoothing is a simple way to create soft labels artificially. Teacher-generated soft labels are much richer because they capture real class similarities.

2. **"Soft labels make the model less confident."** Yes, and that is often good. A model trained on soft labels is less overconfident and generalizes better. But at inference, you can still use temperature=1 for standard predictions.

3. **"Soft labels are only for classification."** No. They are used in object detection (soft bounding box targets), semantic segmentation (soft pixel labels), and even language modeling (next-token probability distributions).

4. **"Higher temperature always produces better soft labels."** Not always. Very high temperature (T>10) makes all probabilities nearly uniform, destroying useful information. T=2–5 is the sweet spot.

5. **"Soft labels are less precise than hard labels."** They are less sharp, but they contain more information. Information theory shows that soft labels have higher entropy and convey more bits per example.

---

### Where It Is Used in Our Code

`src/phase39/phase39_knowledge_distillation.py` — The `softmax_with_temperature()` function generates soft labels from teacher logits. The visualization `distillation_comparison.png` shows how soft labels differ from hard labels and how the student learns from them.
