## What Is Knowledge Distillation?

---

## The Problem

State-of-the-art models have hundreds of billions of parameters. They achieve remarkable accuracy but cannot run on phones, microcontrollers, or browser tabs. A mobile app cannot ship a 175B-parameter model. We need smaller models that approximate the behavior of large ones without requiring the same memory, compute, or energy. How do you transfer the capabilities of a massive teacher into a tiny student?

---

## Definition

**Knowledge Distillation** is a training technique where a small "student" model is trained to mimic a large "teacher" model. Instead of training the student on ground-truth hard labels, it is trained on the teacher's soft probability distribution (logits with temperature scaling), which contains richer information about the relationships between classes.

**How it works:**
```
Teacher logits for an image:    [8.0, 2.0, 1.0, 0.5, 0.2]
Hard label:                     [1,   0,   0,   0,   0]
Soft targets (T=4):             [0.52, 0.22, 0.14, 0.08, 0.04]

Student loss:   alpha * CE(student_soft, teacher_soft)
              + (1 - alpha) * CE(student_logits, hard_label)
```

**Key components:**
- **Temperature scaling:** a temperature T > 1 softens the teacher's distribution, revealing relationships between incorrect classes
- **Soft-target loss:** the student learns why the teacher prefers one class over another, not just which class is correct
- **Distillation weight (alpha):** balances imitation of the teacher against fidelity to ground truth

**Why this matters:**
- DistilBERT retains 97% of BERT's performance with 40% of the parameters
- Mobile vision models use distillation to preserve accuracy after aggressive compression
- The soft targets act as a form of regularization, improving generalization

---

## Real-Life Analogy

Imagine a master chess player teaching a student. The naive approach is to show the student only the best move in each position and ask them to memorize it. This works for common openings but fails in unfamiliar middlegames where memorization runs out. The master instead explains: "Knight to f3 is best, but bishop to c4 is also strong, and pawn to e5 is playable but slightly worse." The student learns the landscape of move quality, not just the peak. When faced with a new position, they can generalize because they understand relative strengths, not just absolute answers.

But the analogy has a catch. If the master is wrong, the student inherits the error. A teacher that systematically confuses two breeds of dog will pass that confusion to the student through the soft targets. The student also learns the teacher's confidence calibration. If the teacher is overconfident in its wrong answers, the student becomes overconfident too. Knowledge distillation is not just compression; it is cultural transmission. The student absorbs the teacher's heuristics, biases, and blind spots along with its knowledge.

The trade-off is between fidelity to the teacher and fidelity to the ground truth. If alpha is too high, the student copies the teacher's errors. If alpha is too low, the student ignores the rich relational information in the soft targets. The optimal alpha depends on the teacher's quality: a near-perfect teacher deserves high alpha, while a mediocre teacher should be distrusted in favor of hard labels.

---

## Tiny Numeric Example

**A 5-class classification task with 800 training samples:**

**Teacher model (large MLP, 128 hidden units):**
```
Training accuracy:   94.5%
Validation accuracy: 87.2%
Logits for one sample:  [8.2, 2.1, 1.3, 0.4, 0.1]
```

**Student model (small MLP, 8 hidden units) trained on hard labels:**
```
Validation accuracy:  72.3%
Loss curve:           converges quickly but plateaus early
```

**Student model trained on soft labels (distillation, T=4, alpha=0.7):**
```
Validation accuracy:  79.8%
Loss curve:           converges more smoothly, generalizes better
```

**Comparison:**
```
Method                  Validation accuracy    Parameters
Teacher (large)              87.2%               26,000
Student (hard labels)        72.3%                216
Student (soft labels)        79.8%                216
```

**The shift:** Distillation closed 55% of the accuracy gap between the large teacher and the small student, using the same student architecture but a richer training signal.

---

## Common Confusion

1. **"Knowledge distillation is just training a smaller model on the same data."** The critical ingredient is the teacher's soft targets. Training a small model on hard labels from the same dataset is regular training, not distillation, and typically yields worse results.

2. **"The student can never outperform the teacher."** While rare, a student with better architecture or more data can exceed the teacher. The soft targets provide a strong prior that accelerates learning, but they do not cap performance.

3. **"Higher temperature always helps."** A very high temperature makes all classes equally likely, destroying the signal. A very low temperature recovers hard labels. The optimal temperature is usually between 2 and 10 and is task-dependent.

4. **"Distillation only works for classification."** It has been applied to object detection, semantic segmentation, machine translation, and even generative models. Any task where a teacher produces structured outputs can be distilled.

5. **"You need a perfect teacher to distill effectively."** Even a mediocre teacher provides useful relational information. The student benefits from knowing which wrong answers are closer to right.

6. **"Distillation and quantization are interchangeable."** Distillation reduces model size by using a smaller architecture. Quantization reduces precision. They are complementary: a distilled student can also be quantized.

7. **"Distillation fixes all the problems of model compression."** It preserves accuracy better than pruning alone, but a student with 1% of the teacher's parameters will still struggle on hard examples. There is a floor below which compression destroys capability.

---

## Where It Is Used in Our Code

`src/phase105/phase105_tiny_ml.py` — We train a large teacher MLP on synthetic classification data, then train a small student MLP in two ways: once on hard labels and once on the teacher's soft targets with temperature scaling. We compare training loss curves and validation accuracy, showing that soft-label distillation closes a significant fraction of the teacher-student accuracy gap.
