## What Is Hyperband?

---

### The Problem

Hyperparameter search is expensive because you must fully train each configuration to know if it is good. But bad configurations reveal themselves early — their validation loss plateaus or diverges within a few epochs. How do you stop wasting time on bad configurations and allocate more budget to promising ones?

---

### Definition

**Hyperband** is a hyperparameter optimization algorithm that uses **successive halving** to eliminate poor configurations early and allocate more resources to promising ones.

**The core idea:**
```
Instead of training all configurations for the full budget:
  1. Train M configurations for a small budget (e.g., 1 epoch each)
  2. Keep the top half (M/2 best configurations)
  3. Double their budget (2 epochs each)
  4. Keep the top half again
  5. Repeat until one configuration remains with the full budget
```

**Example with budget = 81 epochs:**
```
Bracket 1:
  Round 1: 81 configs × 1 epoch = 81 epochs
  Round 2: 27 configs × 3 epochs = 81 epochs (keep top 1/3)
  Round 3: 9 configs × 9 epochs = 81 epochs
  Round 4: 3 configs × 27 epochs = 81 epochs
  Round 5: 1 config × 81 epochs = 81 epochs
  Total: 405 epochs
```

**Why this is efficient:**
- Bad configurations are killed after 1 epoch
- Good configurations get progressively more training
- Total budget is linear in the max budget, not exponential

**Comparison to random search:**
```
Random search with 81 configurations × 81 epochs = 6561 epochs
Hyperband with same max budget: ~2000 epochs (3× faster)
```

---

### Real-Life Analogy

A singing competition with elimination rounds.
- **Standard search:** Every contestant sings a full 5-minute song. Judges score them. It takes all day.
- **Hyperband:** Round 1: 100 contestants sing 10 seconds each. Top 50 advance. Round 2: 50 sing 30 seconds. Top 25 advance. Round 3: 25 sing 1 minute. Top 10 advance. Round 4: 10 sing the full song. Winner chosen.
- **Result:** Bad singers are eliminated quickly. Good singers get more stage time. The total competition time is much shorter, and the winner is still the best.

Hyperband is American Idol for hyperparameters.

---

### Tiny Numeric Example

**Search space:** 8 configurations of learning rate.
**Budget:** 8 epochs max per configuration.

**Standard random search:**
```
8 configs × 8 epochs = 64 epochs total
```

**Hyperband:**
```
Round 1: 8 configs × 1 epoch = 8 epochs
  Losses: [0.8, 0.9, 0.5, 0.7, 0.4, 0.85, 0.6, 0.75]
  Keep top 4: configs 3, 5, 7, 1 (losses 0.5, 0.4, 0.6, 0.8)

Round 2: 4 configs × 2 epochs = 8 epochs
  Losses after 2 epochs: [0.45, 0.35, 0.55, 0.75]
  Keep top 2: configs 5, 3

Round 3: 2 configs × 4 epochs = 8 epochs
  Losses: [0.30, 0.40]
  Keep top 1: config 5

Round 4: 1 config × 8 epochs = 8 epochs
  Final loss: 0.25

Total: 8 + 8 + 8 + 8 = 32 epochs (vs. 64 for standard)
```

Hyperband used half the compute while still fully training the best configuration.

---

### Common Confusion

1. **"Hyperband is the same as early stopping."** Related but different. Early stopping stops one training run. Hyperband systematically allocates budget across many configurations.

2. **"Hyperband only works for epoch-based training.**" It works for any iterative training with intermediate evaluations: iterations, data subsets, model sizes.

3. **"Hyperband always finds the global optimum."** No. It is a heuristic. But it finds good configurations much faster than exhaustive search.

4. **"You cannot combine Hyperband with Bayesian optimization."** You can. BOHB combines Bayesian optimization (smart sampling) with Hyperband (smart allocation).

5. **"Hyperband wastes budget on poor configurations in early rounds."** Yes, but only a tiny budget. The elimination is the whole point.

---

### Where It Is Used in Our Code

`src/phase61/phase61_automl.py` — We implement successive halving on a hyperparameter search task, showing how configurations are eliminated early and how the total compute budget is reduced compared to full training of all candidates.
