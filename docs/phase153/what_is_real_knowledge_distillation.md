## What Is Real Knowledge Distillation?

**The Problem:**
You have a 110M-parameter BERT model that achieves 92% accuracy on sentiment classification. Your product team wants to run it on a mobile app where inference must take under 50ms. A 110M model is too slow and uses too much memory. You could train a tiny 14M-parameter model from scratch on the same data, but it only gets 78% accuracy. How do you get the accuracy of the large model with the speed of the small one?

**Definition:**
**Knowledge distillation** is a training technique where a small "student" model is trained to mimic the behavior of a large "teacher" model. The student learns from the teacher's soft probability distributions (not just hard labels), which contain rich information about the relationships between classes. This transfers the teacher's reasoning into the student's smaller architecture.

**Real-life analogy:**
Knowledge distillation is like an apprentice chef learning from a master. The apprentice does not just copy the final plated dish (hard labels). They watch the master cook and learn that "this sauce is 70% French technique, 20% Asian fusion, 10% improvisation." The apprentice internalizes the relationships between techniques, not just the recipe. When the apprentice later cooks alone, they can adapt because they understand why the master made each choice, not just what the master did.

**Tiny numeric example:**
SST-2 sentiment classification:
- Teacher (BERT-base, 110M params): 92.3% accuracy
- Baseline student (4-layer, 14M params, trained on hard labels): 78.1% accuracy
- Distilled student (same 14M params, trained on teacher's soft labels T=4): 85.7% accuracy
- Distillation closed 58% of the accuracy gap between baseline and teacher.

**Common confusion:**
- **"Distillation is just training a smaller model on the same data."** No. The critical ingredient is the teacher's soft targets. Without them, it is just regular training and typically yields worse results.
- **"The student can never outperform the teacher."** While rare, a student with a better architecture or trained longer can exceed the teacher. The soft targets provide a strong prior that accelerates learning.
- **"Higher temperature always helps."** Temperature controls how soft the labels are. T=1 gives hard labels. T=4-8 is typical. Too high (T>20) makes all classes equal, destroying the signal.
- **"Distillation replaces quantization or pruning."** They are complementary. Distillation trains a small model. Quantization and pruning compress the existing model. Production pipelines often use all three.
- **"You need a perfect teacher."** Even a mediocre teacher provides useful relational information. The student benefits from knowing which wrong answers are closer to right.
- **"Distillation is only for classification."** It works for any task with probability outputs: language modeling (distilling GPT-4 into Llama), object detection, speech recognition, and even diffusion models.

**Where it appears in our code:**
`src/phase153/phase153_knowledge_distillation.py` — Loads BERT-base as teacher, builds a 4-layer tiny BERT as student, generates soft labels with T=4, trains the student with KL divergence on soft labels + cross-entropy on hard labels, and compares against a baseline trained on hard labels only.
