← [Previous: Phase 60: Bayesian Neural Networks](docs/phase60/SUMMARY.md) | [Next: Phase 62: Active Learning](docs/phase62/SUMMARY.md) →

---

## Phase 61: AutoML & Hyperparameter Search

---

### What We Built

An AutoML simulation comparing grid search, random search, and successive halving on a toy regression task. We searched over hidden size and learning rate.

### Key Results

- **Grid search:** MSE = 0.1997, 900 epochs
- **Random search:** MSE = 0.2623, 600 epochs
- **Successive halving:** MSE = 0.2061, 400 epochs (best efficiency)
- Successive halving found a near-optimal config with less than half the compute of grid search.

### Concepts Covered

| Term | File |
|---|---|
| AutoML | `what_is_automl.md` |
| Hyperparameter Search | `what_is_hyperparameter_search.md` |
| Neural Architecture Search | `what_is_neural_architecture_search.md` |
| Hyperband / Successive Halving | `what_is_hyperband.md` |

### Connection to Next Phase

Now that we can find optimal configurations automatically, how do we decide which data points to label when labeling is expensive? Phase 62 covers **active learning**.

### Files

- `docs/phase61/what_is_automl.md`
- `docs/phase61/what_is_hyperparameter_search.md`
- `docs/phase61/what_is_neural_architecture_search.md`
- `docs/phase61/what_is_hyperband.md`
- `docs/phase61/SUMMARY.md`
- `src/phase61/phase61_automl.py`
- `src/phase61/automl.png`

---

← [Previous: Phase 60: Bayesian Neural Networks](docs/phase60/SUMMARY.md) | [Next: Phase 62: Active Learning](docs/phase62/SUMMARY.md) →