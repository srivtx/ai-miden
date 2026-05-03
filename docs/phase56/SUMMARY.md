← [Previous: Phase 55: Distributed Training](docs/phase55/SUMMARY.md) | [Next: Phase 57: Adversarial Robustness](docs/phase57/SUMMARY.md) →

---

## Phase 56: Gradient Boosting

---

### What We Built

A from-scratch gradient boosting implementation on a 1D nonlinear regression task, plus AdaBoost on a classification task, demonstrating how ensembles of weak decision stumps outperform single complex models.

### Key Results

- **Single stump MSE:** 0.2090 (underfits)
- **Gradient boosting (20 rounds):** 0.0625 (3× better)
- **Regularized boosting:** 0.2106 (prevents overfitting to noise)
- **AdaBoost accuracy:** 92.5% (from weak stumps on binary task)

### Concepts Covered

| Term | File |
|---|---|
| Gradient Boosting | `what_is_gradient_boosting.md` |
| XGBoost | `what_is_xgboost.md` |
| AdaBoost | `what_is_adaboost.md` |
| Ensemble Learning | `what_is_ensemble_learning.md` |

### Connection to Next Phase

Now that we can combine many weak models, how do we make a single model robust against adversarial attacks? Phase 57 covers **adversarial robustness**.

### Files

- `docs/phase56/what_is_gradient_boosting.md`
- `docs/phase56/what_is_xgboost.md`
- `docs/phase56/what_is_adaboost.md`
- `docs/phase56/what_is_ensemble_learning.md`
- `docs/phase56/SUMMARY.md`
- `src/phase56/phase56_gradient_boosting.py`
- `src/phase56/gradient_boosting.png`

---

← [Previous: Phase 55: Distributed Training](docs/phase55/SUMMARY.md) | [Next: Phase 57: Adversarial Robustness](docs/phase57/SUMMARY.md) →