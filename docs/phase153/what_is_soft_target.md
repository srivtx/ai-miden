## What Is a Soft Target?

**The Problem:**
A hard label says "this review is positive." That is one bit of information. But the teacher model might be 95% confident it is positive and 5% confident it is negative. That extra information — the teacher's confidence distribution — contains "dark knowledge" about how the teacher reasons. How do you extract and use this richer signal?

**Definition:**
A **soft target** is a probability distribution over all classes produced by a teacher model, typically with temperature scaling applied. Unlike a hard label (which is 100% for one class and 0% for others), a soft target reveals the teacher's confidence in every class and the relationships between them.

**Real-life analogy:**
A soft target is like a teacher's grading rubric, not just the final grade. A hard label is "B+." A soft target is "Thesis: A-, Evidence: B+, Analysis: A, Conclusion: B." The student learns not just that the essay was a B+, but which parts were strong and which were weak. They can focus their improvement on the specific areas that matter.

**Tiny numeric example:**
Hard label: [1, 0] (positive)
Teacher logits: [3.2, -1.5]
Teacher soft target (T=1): [0.990, 0.010]
Teacher soft target (T=4): [0.743, 0.257]
At T=4, the teacher reveals that the negative class is not impossible — it is just less likely. The student learns that "positive" and "negative" are related, not opposites.

**Common confusion:**
- **"Soft targets are just probabilities."** They are probabilities, but their value is relational. The ratio between class 0 and class 1 probability teaches the student more than the absolute value.
- **"Soft targets always improve training."** They help when the teacher is good and the task has structure. For random teachers or tasks with no class relationships, they add noise.
- **"You must match the teacher's temperature at inference."** No. Temperature scaling is only for training. At inference, the student uses T=1.
- **"Soft targets replace hard labels entirely."** In practice, a weighted combination works best: alpha * soft_loss + (1-alpha) * hard_loss. Pure soft targets can cause the student to copy the teacher's errors.
- **"Soft targets are only for the final layer."** Hidden-state distillation and attention distillation also transfer knowledge from intermediate layers, not just the output.

**Where it appears in our code:**
`src/phase153/phase153_knowledge_distillation.py` — The `generate_soft_labels()` function produces soft targets by dividing teacher logits by temperature=4 and applying softmax. The student loss combines KL divergence on soft targets with cross-entropy on hard labels.
