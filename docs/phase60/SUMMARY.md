← [Previous: Phase 59: Federated Learning](docs/phase59/SUMMARY.md) | [Next: Phase 61: AutoML & Hyperparameter Search](docs/phase61/SUMMARY.md) →

---

## Phase 60: Bayesian Neural Networks

---

### What We Built

A Bayesian linear regression with exact posterior computation, plus a Monte Carlo Dropout approximation using a neural network. We compared uncertainty on in-distribution vs. out-of-distribution data.

### Key Results

- **Bayesian LR in-dist uncertainty:** 0.213
- **Bayesian LR OOD uncertainty:** 0.970 (4.6× higher)
- **MC Dropout in-dist uncertainty:** 0.214
- **MC Dropout OOD uncertainty:** 0.759 (3.5× higher)
- Both methods correctly identify regions with no training data as uncertain.

### Concepts Covered

| Term | File |
|---|---|
| Bayesian Neural Network | `what_is_bayesian_neural_network.md` |
| Monte Carlo Dropout | `what_is_monte_carlo_dropout.md` |
| Variational Inference | `what_is_variational_inference.md` |
| Epistemic Uncertainty | `what_is_epistemic_uncertainty.md` |

### Connection to Next Phase

Now that we can quantify uncertainty, how do we automate the process of finding the best model architecture and hyperparameters? Phase 61 covers **AutoML and hyperparameter search**.

### Files

- `docs/phase60/what_is_bayesian_neural_network.md`
- `docs/phase60/what_is_monte_carlo_dropout.md`
- `docs/phase60/what_is_variational_inference.md`
- `docs/phase60/what_is_epistemic_uncertainty.md`
- `docs/phase60/SUMMARY.md`
- `src/phase60/phase60_bayesian_neural_networks.py`
- `src/phase60/bayesian_neural_networks.png`

---

← [Previous: Phase 59: Federated Learning](docs/phase59/SUMMARY.md) | [Next: Phase 61: AutoML & Hyperparameter Search](docs/phase61/SUMMARY.md) →