# What is Knowledge Distillation?

## Problem

State-of-the-art models are too large to run on phones, microcontrollers, or browser tabs. A 175-billion-parameter model cannot be shipped in a mobile app. We need smaller models that approximate the behavior of large ones.

## Definition

Knowledge Distillation is a training technique where a small "student" model is trained to mimic a large "teacher" model. Instead of training the student on ground-truth hard labels, it is trained on the teacher's soft probability distribution (logits with temperature scaling), which contains richer information about the relationships between classes.

## Analogy

A master chess player explains not just the best move, but why other moves are worse. A student learning from this nuanced explanation improves faster than a student who is only told the correct move with no context. The soft targets are the nuanced explanations; the hard label is just "play knight to f3."

## Example

A large BERT model outputs probabilities [0.7, 0.2, 0.1] for three sentiment classes. A small DistilBERT student is trained with cross-entropy against these soft targets rather than the one-hot ground truth. The student learns that the second class is almost as plausible as the first, capturing the teacher's internal reasoning.

## Confusion

Knowledge distillation is not just "training a smaller model on the same data." The critical ingredient is the teacher's soft targets. Training a small model on hard labels from the same dataset is just regular training, not distillation, and typically yields worse results.

## Code Location

See `src/phase105/phase105_tiny_ml.py` for a NumPy simulation of knowledge distillation where a student is trained on hard labels vs soft teacher targets.
