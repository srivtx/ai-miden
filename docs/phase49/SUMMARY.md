← [Previous: Phase 48: Test-Time Training](docs/phase48/SUMMARY.md) | [Next: Phase 50: Self-Supervised Learning](docs/phase50/SUMMARY.md) →

---

## Phase 49: Advanced Optimizers

---

### What We Built

A comparison of SGD, Momentum, RMSprop, Adam, and AdamW on the Rosenbrock function, plus learning rate schedules (step decay, cosine annealing, warmup).

### Key Results

- **SGD:** Final loss = 1.41 (struggles with narrow valley)
- **Momentum:** Final loss = 0.000129 (dramatic improvement)
- **RMSprop:** Final loss = 0.0058 (adaptive scaling helps)
- **Adam:** Final loss = 0.132 (momentum + adaptive scaling)
- **AdamW:** Final loss = 0.127 (decoupled weight decay)
- **SGD+Cosine:** Final loss = 0.235 (schedule helps convergence)

### Concepts Covered

| Term | File |
|---|---|
| Adam | `what_is_adam.md` |
| AdamW | `what_is_adamw.md` |
| Learning Rate Schedule | `what_is_learning_rate_schedule.md` |
| Warmup | `what_is_warmup.md` |

### Connection to Next Phase

Now that we understand how to optimize models, how do we know if they are actually good? In Phase 51, we cover **evaluation metrics** — the tools for measuring model quality.

### Files

- `docs/phase49/what_is_adam.md`
- `docs/phase49/what_is_adamw.md`
- `docs/phase49/what_is_learning_rate_schedule.md`
- `docs/phase49/what_is_warmup.md`
- `docs/phase49/SUMMARY.md`
- `src/phase49/phase49_advanced_optimizers.py`
- `src/phase49/advanced_optimizers.png`

---

← [Previous: Phase 48: Test-Time Training](docs/phase48/SUMMARY.md) | [Next: Phase 50: Self-Supervised Learning](docs/phase50/SUMMARY.md) →