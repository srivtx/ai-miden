## What Is a Teacher Model?

---

### The Problem

In knowledge distillation, you need something to teach the student. But what makes a good teacher? Does it need to be the absolute best model possible? Can multiple teachers work together? How does the teacher generate the soft labels that train the student?

---

### Definition

A **teacher model** is a large, well-trained neural network that generates soft probability distributions used to train a smaller student model. The teacher is typically:
- Pre-trained on a large dataset
- Fine-tuned on the target task
- Frozen during distillation (its weights do not update)

**The teacher's role:**
1. Receive the same input as the student
2. Produce logits (unnormalized scores) for each class
3. Convert logits to soft probabilities using temperature scaling
4. These soft probabilities become the "target" for the student

**Multi-teacher distillation:**
Instead of one teacher, multiple teachers can ensemble their predictions:
```
P_ensemble = (P_teacher1 + P_teacher2 + P_teacher3) / 3
```
This often produces richer soft labels than any single teacher.

---

### Real-Life Analogy

A university professor (teacher) and a high school student (student model).

The professor has spent decades studying a field. When asked a question, they do not just give the answer — they explain the reasoning, mention alternative interpretations, and discuss edge cases. The high school student takes notes on this rich explanation, not just the final answer.

If the student had only read the textbook (hard labels), they would know the facts but miss the nuance. By attending the professor's lectures (soft labels), they learn how the facts connect.

Multiple professors (multi-teacher) with different specialties give an even richer education.

---

### Tiny Numeric Example

**Teacher model:** 3-layer neural network, 50 hidden units per layer

**Input:** x = [0.8, -0.3]

**Teacher forward pass:**
```
Layer 1: h1 = ReLU(x @ W1 + b1)     → [0.5, 0.2, 0.8, ...] (50 dims)
Layer 2: h2 = ReLU(h1 @ W2 + b2)    → [0.3, 0.9, 0.1, ...] (50 dims)
Output:  z = h2 @ W3 + b3           → [2.1, 0.4, -0.8] (3 classes)
```

**Soft probabilities (T=2):**
```
z/T = [1.05, 0.2, -0.4]
softmax = [0.62, 0.26, 0.12]
```

**Student model:** 1-layer network, 10 hidden units

**Student sees:**
- Input: x = [0.8, -0.3]
- Target: [0.62, 0.26, 0.12] (not [1, 0, 0])

The student learns that class 2 (probability 0.12) is not just "wrong" but "somewhat related to the input."

---

### Common Confusion

1. **"The teacher must be state-of-the-art."** Not necessarily. A good teacher just needs to generalize well. Sometimes a medium-sized model that is well-regularized makes a better teacher than a huge overfitted model.

2. **"The teacher is trained during distillation."** No. The teacher is frozen. Only the student learns. Training the teacher would change its soft labels mid-distillation, confusing the student.

3. **"Teacher and student must have the same architecture."** No. They can be completely different. A Transformer can teach an RNN. A CNN can teach an MLP.

4. **"Logit matching is the only form of teaching."** No. Some methods use hidden-state matching (student mimics teacher's intermediate layers) or attention matching (student mimics teacher's attention maps).

5. **"A bigger teacher is always better."** Diminishing returns apply. A 70B teacher might be only slightly better than a 7B teacher for distilling a 1B model. The 7B teacher might actually be better if it generalizes more cleanly.

---

### Where It Is Used in Our Code

`src/phase39/phase39_knowledge_distillation.py` — The `TeacherModel` class is a 3-layer MLP with 50 hidden units. It is pre-trained on the task and frozen during student training.
