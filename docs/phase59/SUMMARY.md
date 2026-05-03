← [Previous: Phase 58: Time Series Forecasting](docs/phase58/SUMMARY.md) | [Next: Phase 60: Bayesian Neural Networks](docs/phase60/SUMMARY.md) →

---

## Phase 59: Federated Learning

---

### What We Built

A simulated federated learning system with 5 clients holding non-IID data slices. We trained a global model via FedAvg and compared it to a centralized baseline and a differentially private version.

### Key Results

- **Centralized baseline:** MSE = 0.0048
- **FedAvg (30 rounds):** MSE = 0.0016 (matches centralized)
- **FedAvg + Differential Privacy:** MSE = 0.3419 (privacy-utility trade-off)
- **Final FedAvg slope:** 2.026 (true = 2.0)
- **Final DP slope:** 1.648 (noise degrades accuracy)

### Concepts Covered

| Term | File |
|---|---|
| Federated Learning | `what_is_federated_learning.md` |
| Differential Privacy | `what_is_differential_privacy.md` |
| Federated Averaging | `what_is_federated_averaging.md` |
| Non-IID Data | `what_is_non_iid_data.md` |

### Connection to Next Phase

Now that we can train without centralizing data, how do we handle uncertainty in model predictions? Phase 60 covers **Bayesian neural networks**.

### Files

- `docs/phase59/what_is_federated_learning.md`
- `docs/phase59/what_is_differential_privacy.md`
- `docs/phase59/what_is_federated_averaging.md`
- `docs/phase59/what_is_non_iid_data.md`
- `docs/phase59/SUMMARY.md`
- `src/phase59/phase59_federated_learning.py`
- `src/phase59/federated_learning.png`

---

← [Previous: Phase 58: Time Series Forecasting](docs/phase58/SUMMARY.md) | [Next: Phase 60: Bayesian Neural Networks](docs/phase60/SUMMARY.md) →