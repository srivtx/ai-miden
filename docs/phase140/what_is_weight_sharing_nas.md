## What Is Weight-Sharing NAS?

---

### The Problem

Neural Architecture Search sounds magical until you look at the price tag. Training a single Transformer from scratch can cost thousands of dollars. Evaluating even 100 architectures would bankrupt a university lab. Early NAS methods did exactly this: they trained every candidate to convergence, which meant only tech giants could afford to play. How do you search through millions of architectures without training millions of models?

---

### Definition

**Weight-Sharing NAS** solves the cost problem by training one enormous "supernet" that contains every candidate architecture as a sub-network. All subnets share the same set of weights. Once the supernet is trained, evaluating a new architecture requires no training at all — you simply extract the corresponding subset of weights and measure validation accuracy.

**How it works:**
```
Supernet:        A model with maximum depth D_max and maximum width W_max
Candidate A:     depth=4, width=256   -> uses first 4 layers, first 256 channels
Candidate B:     depth=8, width=512   -> uses first 8 layers, first 512 channels
Training:        Each batch, sample a random subnet and update its weights
Evaluation:      For each candidate, run forward pass using shared weights
Result:          1 training run evaluates 10^6 architectures
```

**Key techniques:**
- **Single-path sampling:** During supernet training, each batch uses one random subnet. This prevents bias toward any single architecture.
- **Uniform sampling:** Every valid architecture must be sampled with equal probability, or the supernet overfits to the most frequently sampled size.
- **Progressive shrinking:** Start by training the full supernet, then gradually allow smaller subnets. This stabilizes training because large subnets provide good initialization for smaller ones.
- **Ranking correlation:** The supernet's validation accuracy is noisy, but the *ranking* of architectures is often preserved. You use the supernet to rank candidates, then fully train only the top-5.

**Why this matters:**
- Weight-sharing reduces NAS cost from thousands of GPU-hours to tens of GPU-hours.
- It enables architecture search on-device: a phone can search for the best model for its own hardware by evaluating subnets.
- It underpins efficient mobile models like MobileNetV3 and EfficientNet, which were discovered via supernet search.

---

### Real-Life Analogy

A shared kitchen in a food hall.
- **Naive NAS:** Every restaurant builds its own private kitchen, hires its own chefs, and runs for a month before the health inspector rates it. Only a billionaire could afford to test 100 restaurant concepts.
- **Weight-sharing NAS:** One giant communal kitchen has every possible appliance: 50 stoves, 100 ovens, 200 prep stations. Each restaurant concept simply reserves a subset of stations. The inspector can evaluate 100 concepts in a single day because they all share the same ingredients and equipment. A sushi bar uses 2 stoves and 10 prep stations; a bakery uses 5 ovens and 5 prep stations.
- **The catch:** If the communal kitchen is optimized for baking, the sushi bar's rating will be slightly off. But the *relative* ranking (bakery A vs. bakery B) is accurate enough to pick winners.

---

### Tiny Numeric Example

**Supernet:** 6 layers, width 128.
**Subnets evaluated:** 4 architectures.
```
Architecture    Layers    Width    Supernet accuracy    Fully-trained accuracy
A               2         64       0.72                 0.78
B               4         64       0.81                 0.85
C               4         128      0.85                 0.89
D               6         128      0.88                 0.91
```

**Ranking correlation:**
Supernet ranking: D > C > B > A
True ranking:     D > C > B > A
Kendall tau = 1.0 (perfect correlation)

**Cost comparison:**
Naive NAS (train all 4):     400 GPU-hours
Weight-sharing NAS:          120 GPU-hours (3x speedup for tiny space; 1000x for large spaces)

**The insight:** The supernet accuracy numbers are all 0.03-0.06 lower than the true accuracies because shared weights are a compromise. But the *order* is preserved, which is all you need for search.

---

### Common Confusion

1. **"Weight-sharing means all subnets have identical performance."** No. They share weights, but different depths and widths extract different features. The supernet weights are a compromise, so individual subnets underperform relative to standalone training, but their ranking is correlated.

2. **"Supernet training is the same as training the largest model."** It is similar, but the sampling strategy matters enormously. If you only train the full model and then extract subnets, the smaller subnets will perform poorly because their weights were never optimized.

3. **"Any architecture can be a subnet of any supernet."** The supernet defines a family. You cannot extract a ResNet from a Transformer supernet. The search space is constrained by the supernet's topology.

4. **"Weight-sharing eliminates the need for full retraining of top candidates."** It reduces it, but does not eliminate it. You still fully train the top 1-5 architectures found by the supernet to get final numbers.

5. **"Supernets are only for vision models."** False. Transformer supernets (e.g., SuperBERT, AutoTinyBERT) search over depth, width, and attention heads for language models using the exact same principles.

6. **"Sampling every subnet once is enough."** In practice, you need millions of sampled subnets to train the supernet well. The weights must be exposed to many different activation paths to generalize across architectures.

7. **"Weight-sharing NAS finds the globally optimal architecture."** It finds the best architecture *within the supernet's family*. If the true optimal model lies outside that family, the supernet will never discover it.

---

### Where It Is Used in Our Code

`src/phase140/phase140_nas_concepts.py` — We simulate a supernet by defining a single accuracy function that interpolates smoothly across depth and width. Evaluating a candidate requires only a lookup, mimicking the zero-cost evaluation of a trained supernet. We show how ranking correlation allows fast pruning of the search space.

`src/phase140/phase140_nas_colab.py` — Although we train each of the 9 models independently for ground-truth accuracy, we simulate a weight-sharing scenario by using the fully trained weights of the largest model to initialize smaller ones. This demonstrates the progressive-shrinking principle that makes supernet training stable.
