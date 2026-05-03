← [Previous: Phase 61: AutoML & Hyperparameter Search](docs/phase61/SUMMARY.md) | [Next: Phase 63: Dataset Curation for Fine-Tuning](docs/phase63/SUMMARY.md) →

---

## Phase 62: Active Learning

---

### What We Built

A pool-based active learning simulation on a 2D classification task. We compared uncertainty sampling, margin sampling, and random sampling, showing how intelligent selection reaches perfect accuracy faster.

### Key Results

- **Uncertainty sampling (110 labels):** 100.0% accuracy
- **Margin sampling (110 labels):** 100.0% accuracy
- **Random sampling (110 labels):** 98.3% accuracy
- **Gain over random:** 1.7 percentage points
- Both active strategies reached 100% accuracy by focusing on the decision boundary.

### Concepts Covered

| Term | File |
|---|---|
| Active Learning | `what_is_active_learning.md` |
| Uncertainty Sampling | `what_is_uncertainty_sampling.md` |
| Query Strategy | `what_is_query_strategy.md` |
| Pool-Based Sampling | `what_is_pool_based_sampling.md` |

### Connection to Next Phase

Now that we have completed the core and advanced conceptual phases, we move to the **applied AI extension**. Phase 63 covers **dataset curation for fine-tuning** — the first step in building real-world AI systems.

### Files

- `docs/phase62/what_is_active_learning.md`
- `docs/phase62/what_is_uncertainty_sampling.md`
- `docs/phase62/what_is_query_strategy.md`
- `docs/phase62/what_is_pool_based_sampling.md`
- `docs/phase62/SUMMARY.md`
- `src/phase62/phase62_active_learning.py`
- `src/phase62/active_learning.png`

---

← [Previous: Phase 61: AutoML & Hyperparameter Search](docs/phase61/SUMMARY.md) | [Next: Phase 63: Dataset Curation for Fine-Tuning](docs/phase63/SUMMARY.md) →