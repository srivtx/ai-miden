← [Previous: Phase 75: Explainable AI (XAI)](docs/phase75/SUMMARY.md) | [Next: Phase 77: Unsupervised Learning](docs/phase77/SUMMARY.md) →

---

# Phase 76: Fairness & Bias — Summary

## Overview

Phase 76 introduces algorithmic fairness: how models encode societal biases, how to measure those biases with formal definitions, and how to mitigate them. Fairness is not a single number; it is a set of competing constraints that force us to confront what "fair" actually means in a given context.

## Documents

| Document | Topic |
|----------|-------|
| `what_is_algorithmic_bias.md` | How models replicate historical discrimination from training data |
| `what_is_demographic_parity.md` | Equal positive prediction rates across groups |
| `what_is_equalized_odds.md` | Equal true positive and false positive rates across groups |
| `what_is_bias_mitigation.md` | Pre-processing, in-processing, and post-processing techniques |

## Code

| Script | Purpose |
|--------|---------|
| `src/phase76/phase76_fairness_bias.py` | NumPy concept demo: synthetic biased loan data, logistic classifier, fairness metrics, re-weighting mitigation, before/after visualization |
| `src/phase76/phase76_fairness_bias_colab.py` | Real-workflow script: Adult Census dataset, fairlearn metrics, demographic parity constraint, unconstrained vs. constrained comparison |

## Key Takeaways

1. **Models are mirrors.** They reflect the patterns in training data, including historical prejudice.
2. **Fairness has multiple definitions.** Demographic parity and equalized odds are mathematically incompatible when base rates differ. You must choose which ethical intuition matters for your use case.
3. **Measurement comes first.** You cannot mitigate what you cannot quantify. Always compute group-specific TPR, FPR, and positive rates before attempting fixes.
4. **Mitigation is a trade-off.** Reducing bias often costs some overall accuracy, but sometimes it improves generalization by breaking spurious correlations.
5. **Start simple.** A pre-processing re-weighting scheme is easy to implement and debug. Move to in-processing constraints only when simple fixes are insufficient.

## Outputs

- `src/phase76/fairness_bias.png` — Bar charts of acceptance rates, confusion matrices, and fairness metrics before/after mitigation

---

← [Previous: Phase 75: Explainable AI (XAI)](docs/phase75/SUMMARY.md) | [Next: Phase 77: Unsupervised Learning](docs/phase77/SUMMARY.md) →
