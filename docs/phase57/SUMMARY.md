## Phase 57: Adversarial Robustness

---

### What We Built

A 2D binary classifier and attacked it with FGSM and PGD to demonstrate how tiny perturbations flip predictions. We also trained an adversarially robust model and compared its trade-offs.

### Key Results

- **Standard model clean accuracy:** 100%
- **Under FGSM ε=0.2:** 78% (22% drop from tiny perturbations)
- **Under PGD (20 steps):** 78%
- **Adversarial training clean accuracy:** 98% (small drop)
- **Adversarial training under FGSM ε=0.2:** 80% (slight improvement)

### Concepts Covered

| Term | File |
|---|---|
| Adversarial Example | `what_is_adversarial_example.md` |
| FGSM | `what_is_fgsm.md` |
| PGD | `what_is_pgd.md` |
| Adversarial Training | `what_is_adversarial_training.md` |

### Connection to Next Phase

Now that we understand how to break and defend models, how do we predict sequences over time? Phase 58 covers **time series forecasting**.

### Files

- `docs/phase57/what_is_adversarial_example.md`
- `docs/phase57/what_is_fgsm.md`
- `docs/phase57/what_is_pgd.md`
- `docs/phase57/what_is_adversarial_training.md`
- `docs/phase57/SUMMARY.md`
- `src/phase57/phase57_adversarial_robustness.py`
- `src/phase57/adversarial_robustness.png`
