## What Is Neural Architecture Search?

---

### The Problem

Designing a neural network architecture is an art. ResNet, Transformer, U-Net — each was designed by experts over months or years. But what if the best architecture for your specific dataset has not been invented yet? How do you automatically discover network structures that maximize performance?

---

### Definition

**Neural Architecture Search (NAS)** is the process of automatically designing neural network architectures by searching through a space of possible structures and evaluating their performance.

**Search space:**
```
What can vary:
  - Number of layers
  - Layer types (conv, attention, pooling)
  - Connections (sequential, skip, dense)
  - Filter sizes, kernel sizes, expansion ratios
  - Activation functions
```

**Search strategies:**

**1. Random/Grid search:**
```
Try random architectures, keep the best.
```

**2. Reinforcement learning:**
```
A controller network generates architectures.
Reward = validation accuracy.
Controller learns to generate better architectures over time.
```

**3. Evolutionary algorithms:**
```
Start with a population of architectures.
Mutate and crossover the best performers.
Survival of the fittest over generations.
```

**4. Differentiable NAS (DARTS):**
```
Instead of discrete choices, make them continuous and differentiable.
Train architecture weights jointly with model weights.
Prune to get the final discrete architecture.
```

**Why this matters:**
- NAS discovered EfficientNet, which outperformed hand-designed models
- AutoML-Zero evolved algorithms from scratch using only basic operations
- NAS is how Google scales model design beyond human capacity

---

### Real-Life Analogy

Evolutionary breeding of racehorses.
- **Hand-designed architecture:** A human breeder picks two fast horses and hopes their offspring is faster. This works but is limited by the breeder's intuition.
- **NAS (evolutionary):** Start with 100 random horses. Race them. Breed the top 20. Mutate some offspring (randomly change leg length, muscle ratio). Race again. After 50 generations, you have a horse faster than anything a human designed.
- **NAS (differentiable):** Instead of discrete horses, imagine a continuous "horse space" where you can blend features. You find the optimal blend mathematically, then build the closest real horse.

---

### Tiny Numeric Example

**Search space:** 2-layer MLPs with varying hidden sizes.
```
Architecture A: [4, 4]   → val_acc = 72%
Architecture B: [8, 4]   → val_acc = 78%
Architecture C: [8, 8]   → val_acc = 81%  ← best
Architecture D: [16, 8]  → val_acc = 80%  (overfits)
Architecture E: [4, 8]   → val_acc = 75%
```

**NAS finds:** Wider first layer helps. But too wide overfits. [8, 8] is optimal for this dataset.

**Differentiable NAS (simplified):**
```
Instead of choosing between A, B, C, D, E:
  architecture = α*A + β*B + γ*C + δ*D + ε*E
  where α+β+γ+δ+ε = 1

Train α, β, γ, δ, ε jointly with weights.
After training: γ=0.6, others < 0.1
Final architecture: C ([8, 8]) with minor blending.
```

---

### Common Confusion

1. **"NAS always finds better architectures than humans."** Often yes, but it requires enormous compute. EfficientNet took thousands of GPU-hours to discover.

2. **"NAS is only for computer vision."** No. NAS has discovered architectures for NLP (Evolved Transformer), speech, and even RL.

3. **"NAS replaces the need for domain knowledge."** No. You still define the search space. NAS explores within your constraints.

4. **"Differentiable NAS is always best."** It is efficient but can bias toward wide, shallow networks. Evolutionary methods explore more diversely.

5. **"NAS is too expensive for small teams."** Modern techniques (weight sharing, proxy tasks) make NAS accessible. Platforms like AutoKeras run on a single GPU.

---

### Where It Is Used in Our Code

`src/phase61/phase61_automl.py` — We implement a tiny neural architecture search over layer widths and depths, using random search with early stopping to find the best-performing architecture on a synthetic task.
