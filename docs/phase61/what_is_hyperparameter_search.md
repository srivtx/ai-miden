## What Is Hyperparameter Search?

---

### The Problem

Your model has knobs: learning rate, batch size, number of layers, dropout rate, weight decay. Each combination produces a different result. With 5 hyperparameters and 10 options each, there are 100,000 combinations. Training each takes an hour. You cannot try them all. How do you find the best combination without exhaustive search?

---

### Definition

**Hyperparameter search** is the process of systematically exploring the space of hyperparameter configurations to find the ones that yield the best model performance on a validation set.

**Search methods:**

**Grid search:**
```
Try every combination:
  LR: [0.1, 0.01, 0.001]
  Dropout: [0.2, 0.5]
  Total: 3 × 2 = 6 trials
```
- Exhaustive but scales terribly
- Wastes time on obviously bad regions

**Random search:**
```
Sample configurations randomly:
  Trial 1: LR=0.034, Dropout=0.37
  Trial 2: LR=0.008, Dropout=0.12
```
- Often better than grid search in high dimensions
- Some hyperparameters matter more than others; random search explores all dimensions equally

**Bayesian optimization:**
```
1. Train a few random configurations
2. Build a surrogate model (e.g., Gaussian Process) that predicts validation loss from hyperparameters
3. Use the surrogate to pick the next most promising configuration
4. Repeat
```
- Learns from past trials
- Focuses search on promising regions
- Most efficient for expensive evaluations

**Why this matters:**
- The difference between default and optimal hyperparameters can be 10-30% accuracy
- Proper tuning is the difference between a failed project and state-of-the-art results

---

### Real-Life Analogy

Finding the best recipe for chocolate chip cookies.
- **Grid search:** You try every combination of 3 flours × 2 sugars × 3 chocolates × 2 baking times = 36 batches. You find the best one, but you baked 35 mediocre batches along the way.
- **Random search:** You randomly pick 12 combinations. You might get lucky and find a great one early, or you might miss the best entirely.
- **Bayesian optimization:** You bake 5 random batches, taste them, and build a mental model: "More butter seems good, less sugar is bad." Your next batch uses more butter and moderate sugar. After 12 batches, you have a better cookie than grid search with 36.

---

### Tiny Numeric Example

**Hyperparameter space:**
```
Learning rate: log-uniform [1e-4, 1e-1]
Dropout: uniform [0.1, 0.5]
```

**Grid search (3×3):**
```
(1e-4, 0.1): val_loss=0.85
(1e-4, 0.3): val_loss=0.82
(1e-4, 0.5): val_loss=0.88
(1e-2, 0.1): val_loss=0.25  ← best found
(1e-2, 0.3): val_loss=0.28
(1e-2, 0.5): val_loss=0.35
(1e-1, 0.1): val_loss=0.55
(1e-1, 0.3): val_loss=0.60
(1e-1, 0.5): val_loss=0.72
```

**Random search (6 trials):**
```
(0.003, 0.15): val_loss=0.22
(0.008, 0.42): val_loss=0.30
(0.015, 0.22): val_loss=0.18  ← better than grid search!
(0.06, 0.38): val_loss=0.45
(0.002, 0.48): val_loss=0.35
(0.04, 0.12): val_loss=0.28
```

Random search found a better configuration because it explored the continuous space, not just grid points.

---

### Common Confusion

1. **"Hyperparameters are the same as parameters."** No. Parameters are learned during training (weights). Hyperparameters are set before training (learning rate, architecture).

2. **"Grid search is always best."** No. Random search often beats grid search, especially when some hyperparameters matter more than others.

3. **"You only need to tune the learning rate."** No. Batch size, regularization, and architecture all interact. Tuning only one leaves performance on the table.

4. **"Hyperparameter search is a one-time task."** No. As data changes or models evolve, optimal hyperparameters change too.

5. **"Bayesian optimization is always fastest."** For very cheap evaluations, random search is fine. Bayesian optimization shines when each trial is expensive (hours of training).

---

### Where It Is Used in Our Code

`src/phase61/phase61_automl.py` — We compare grid search, random search, and successive halving on a toy hyperparameter space, showing how intelligent search strategies find better configurations with fewer evaluations.
