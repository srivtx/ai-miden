## What Is Neural Architecture Search?

---

## The Problem

Designing neural networks has historically been a manual, expert-driven craft. A researcher proposes a residual block, tests it on ImageNet, publishes the result, and the community adopts it. But this process does not scale to the combinatorial explosion of possible layer types, connectivity patterns, activation functions, and hyperparameters. For every new domain (molecules, satellite imagery, protein folding), the manual search for the right architecture starts over. How do you automate the discovery of effective architectures?

---

## Definition

**Neural Architecture Search (NAS)** is an automated process for discovering neural network architectures. A search algorithm explores a defined search space of operations and connections to find architectures that maximize performance on a validation set.

**How it works:**
```
Search space:    All possible DAGs where each node is a feature map
                 and each edge is one of {3x3 conv, 5x5 conv, max pool, skip}

Search strategy: Sample 100 architectures, train each for 10 epochs,
                 evaluate validation accuracy, keep the top 10,
                 mutate and recombine them (evolutionary search)

Result:          A discovered cell that outperforms hand-designed ResNet
```

**Key approaches:**
- **Reinforcement learning:** a controller network samples architectures; reward is validation accuracy
- **Evolutionary search:** populations of architectures compete; mutations and crossovers produce offspring
- **Gradient-based (DARTS):** relax the discrete search space to be continuous; optimize architecture weights jointly with model weights using gradients

**Why this matters:**
- NAS discovered EfficientNet and MobileNetV3, which set efficiency benchmarks
- It removes the bottleneck of human intuition in architecture design
- It can discover domain-specific biases that human researchers might miss

---

## Real-Life Analogy

Imagine an architect designing a skyscraper. Traditionally, the architect draws a single floor plan based on experience, builds a scale model, and hopes it works. NAS is like giving the architect a parametric design program that generates 10,000 floor plans overnight, simulates wind loads and energy efficiency for each one, and presents the top 10 designs for human review. The architect still defines the constraints (height limit, budget, materials), but the search for the optimal layout is automated.

But NAS is not magic. The parametric program is only as good as the building codes it knows. If the search space excludes cantilevered designs, the algorithm will never discover them, no matter how optimal they might be. Similarly, NAS requires careful definition of the search space. If you only allow 3x3 and 5x5 convolutions, you will never discover that a 7x7 dilated convolution was the right choice for your task. The search space is a meta-inductive bias: it encodes what you believe might work.

The trade-off is between search cost and discovery quality. Training each candidate architecture from scratch is prohibitively expensive (thousands of GPU-days). One-shot methods like DARTS reduce this by sharing weights across all candidates, but they introduce approximation error. The discovered architecture is good, but it may not be the true global optimum. NAS is a practical compromise between exhaustive search and human design, not a replacement for engineering judgment.

---

## Tiny Numeric Example

**Search space: a single cell with 4 nodes and 6 possible operations per edge.**

**Number of possible architectures:**
```
Edges per cell:     6 (in a 4-node DAG)
Operations per edge: 7 (3x3 conv, 5x5 conv, 3x3 dilated, 5x5 dilated, 3x3 avg pool, skip, none)
Total architectures: 7^6 = 117,649
```

**Random search baseline:**
```
Sampled:            100 architectures
Trained each:       10 epochs
Best found:         89.2% CIFAR-10 accuracy
Average:            84.5%
```

**Evolutionary NAS:**
```
Initial population: 50 random architectures
Generations:        10
Evaluations:        ~300 architectures total
Best found:         93.1% CIFAR-10 accuracy
```

**DARTS (gradient-based):**
```
Search cost:        ~4 GPU-days (vs 2,000+ for random search with full training)
Discovered cell:    7 operations selected by softmax over architecture weights
Final accuracy:     94.0% CIFAR-10 accuracy
```

**The shift:** Gradient-based NAS achieved the best accuracy at 0.2% of the search cost of random search, by relaxing the discrete search problem into a continuous optimization.

---

## Common Confusion

1. **"NAS discovers radically new architectures humans never imagined."** Most NAS-discovered architectures resemble known motifs (residual connections, inverted bottlenecks). The value is in optimizing the combination, not in inventing new primitives.

2. **"NAS removes the need for human expertise."** Humans still define the search space, the training protocol, and the objective. A poorly defined search space yields poor architectures regardless of the search algorithm.

3. **"DARTS is always better than evolutionary NAS."** DARTS is faster but suffers from collapse modes where it over-weights skip connections. Evolutionary search is slower but more robust to these pathologies.

4. **"NAS is only for image classification."** NAS has been applied to NLP (transformer search), object detection, semantic segmentation, and even molecular property prediction.

5. **"The best architecture found by NAS will generalize to any dataset."** NAS optimizes on a specific validation set. The discovered architecture may overfit to that dataset's idiosyncrasies and perform poorly on others.

6. **"NAS replaces architecture engineering entirely."** NAS complements human design. Hand-designed modules (attention, convolutions) are often used as building blocks within the NAS search space.

7. **"One-shot NAS finds the exact same architecture as training each candidate separately."** Weight sharing introduces coupling between architectures. The optimal architecture under shared weights is an approximation of the true optimum under independent weights.

---

## Where It Is Used in Our Code

`src/phase104/phase104_architecture_search.py` — We simulate the effect of architecture choice by comparing a fully connected network against a locally connected preprocessor on a structured grid task. While we do not implement a full NAS loop, we demonstrate how the right architectural prior (spatial locality) dramatically improves sample efficiency, which is the motivation behind automated architecture search.
