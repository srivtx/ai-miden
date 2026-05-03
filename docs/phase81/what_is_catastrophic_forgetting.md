# What Is Catastrophic Forgetting?

## 1. Why it exists (THE PROBLEM first)

When a neural network learns Task A, it adjusts millions of weights to encode patterns specific to that task. Later, when you train the **same** network on Task B (without Task A data), backpropagation optimizes the same weights for Task B. The result? The network "forgets" Task A almost entirely. Its accuracy on Task A collapses from, say, 98% down to random chance (50% for binary classification). This is catastrophic forgetting, and it makes standard neural networks terrible at lifelong learning. In production, this means every time you deploy a model to a new region, product line, or data distribution, you risk destroying the capabilities it already had.

## 2. Definition

**Catastrophic forgetting** is the sudden and severe loss of previously learned knowledge when a neural network is trained on new tasks, caused by new gradients overwriting old weight configurations.

## 3. Real-life analogy

Imagine you only have one notebook. You fill it with detailed notes for a biology exam. The next week, you need to study for a history exam, so you start erasing and rewriting pages. By the time the history exam comes, your biology notes are gone. You didn't get a second notebook—you overwrote the first one. That notebook is your neural network's weights.

## 4. Tiny numeric example

Imagine a single weight $w$ that needs to be:
- $w = +2.0$ for Task A (circles vs squares)
- $w = -2.0$ for Task B (triangles vs stars)

You train on Task A and converge to $w = +2.0$. Then you train on Task B. Gradient descent pushes $w$ toward $-2.0$. After Task B training, $w \approx -2.0$. Now you test on Task A: the model behaves as if it never saw Task A. One weight, one overwrite. Multiply by millions.

## 5. Common confusion

- **"It forgets slowly, like humans do."** No—it forgets catastrophically. One epoch of Task B training can destroy Task A performance.
- **"More data for Task B will help remember Task A."** No. More Task B data only makes the overwriting worse because gradients keep pushing weights away from Task A's optimum.
- **"Regularization (L2) prevents it."** Not really. L2 keeps weights near zero, not near Task A's solution. It slows forgetting slightly but doesn't solve it.
- **"Just save the old model and ensemble them."** That works but scales linearly with tasks—you need N models for N tasks. Catastrophic forgetting is about doing it with **one** model.
- **"It only happens in deep networks."** It happens in any parametric model trained by gradient descent on shared parameters—even a single linear layer.
- **"Fine-tuning is the standard way to adapt models, so it's fine."** Fine-tuning is standard for **transfer** learning when you don't care about the old task. For continual learning, it's the problem.

## 6. Where it is used in our code

In `src/phase81/phase81_continual_learning.py`, the "naive fine-tuning" experiment explicitly demonstrates catastrophic forgetting: we train a 2-layer MLP on Task A until it reaches ~95% accuracy, then train the same model on Task B without Task A data. Task A accuracy drops to ~50% (random chance) within a few epochs. This is the baseline we compare EWC and replay against.