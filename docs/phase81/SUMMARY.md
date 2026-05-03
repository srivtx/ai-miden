← [Previous: Phase 80: MLOps](docs/phase80/SUMMARY.md) | End →

---

# Phase 81: Continual Learning — Summary

## Overview

Phase 81 introduces **continual learning** (also called lifelong learning): the challenge of training a neural network on a sequence of tasks without forgetting previously learned skills. Standard neural networks suffer from **catastrophic forgetting**—when trained on Task B, they overwrite the weights that encoded Task A, causing Task A performance to collapse to random chance.

This phase covers three major approaches to solving catastrophic forgetting, plus the underlying problem itself.

---

## Documents

| Document | What It Covers |
|---|---|
| `what_is_catastrophic_forgetting.md` | The core problem: why neural networks forget old tasks when learning new ones, with numeric examples and common misconceptions. |
| `what_is_ewc.md` | **Elastic Weight Consolidation**: a regularization technique that computes how important each weight is for the old task (via Fisher information) and penalizes changes to important weights during new-task training. |
| `what_is_replay_buffer.md` | **Experience Replay**: storing a small subset of old examples and interleaving them with new training data, forcing the model to maintain performance on both tasks simultaneously. |
| `what_is_progressive_networks.md` | **Progressive Networks**: adding a new, separate column of layers for each new task while freezing old columns. Zero forgetting guaranteed, at the cost of linearly growing model size. |

---

## Code

| Script | Purpose |
|---|---|
| `src/phase81/phase81_continual_learning.py` | **NumPy concept demo**. Trains a 2-layer MLP on synthetic 2D data (Task A: circles vs squares, Task B: triangles vs stars). Demonstrates catastrophic forgetting, implements EWC and replay buffer from scratch, compares all three methods, and visualizes decision boundaries and accuracy curves. Saves plots to `continual_learning.png` and `continual_learning_comparison.png`. |
| `src/phase81/phase81_continual_learning_colab.py` | **Real-workflow PyTorch script** for Google Colab. Uses split MNIST (digits 0-4, then 5-9) and compares naive fine-tuning, replay buffer, EWC, and Progressive Networks. Includes heavy inline comments explaining the "why" behind every design choice. |

---

## Key Takeaways

1. **Catastrophic forgetting is sudden, not gradual.** One epoch of training on a new task can destroy performance on an old task.
2. **No single method is perfect for all scenarios.**
   - **Naive fine-tuning**: Simple, but destroys old knowledge. Only acceptable if you don't care about old tasks.
   - **Replay buffer**: Simplest effective method. Needs some old data storage. Works well for 2-5 tasks.
   - **EWC**: No old data needed after Fisher computation. Mathematically elegant. Struggles with 10+ tasks due to conflicting penalties.
   - **Progressive Networks**: Zero forgetting, but model grows linearly. Best when task count is small and memory is cheap.
3. **The choice of method depends on your constraints:**
   - Can you store any old data? → Replay buffer
   - Can you store old model parameters? → EWC
   - Can you afford model growth? → Progressive Networks
   - Do you only care about the latest task? → Naive (but admit you're doing it)

---

## Visual Outputs

- `continual_learning.png`: 3x3 grid showing decision boundaries for Task A and Task B under each method, plus training accuracy curves.
- `continual_learning_comparison.png`: Bar chart comparing final Task A vs Task B accuracy across naive, EWC, and replay.
- `continual_learning_mnist_comparison.png` (from Colab script): Bar chart comparing all four methods on split MNIST.

---

## Recommended Reading Order

1. Read `what_is_catastrophic_forgetting.md` — understand the enemy.
2. Read `what_is_replay_buffer.md` — the simplest weapon.
3. Read `what_is_ewc.md` — the mathematical weapon.
4. Read `what_is_progressive_networks.md` — the architectural weapon.
5. Run `phase81_continual_learning.py` — see it in 2D.
6. Run `phase81_continual_learning_colab.py` — see it on real images.

---

## Prerequisites

- Phase 1-10: Basic neural networks and backpropagation
- Phase 20-30: Regularization and optimization
- Phase 50+: Deep learning frameworks (PyTorch)

## Next Steps

Continue to Phase 83 for GPU kernel optimization and systems-level training infrastructure.

---

← [Previous: Phase 80: MLOps](docs/phase80/SUMMARY.md) | [Next: Phase 83: GPU Kernel Optimization](docs/phase83/SUMMARY.md) →
