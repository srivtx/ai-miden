← [Previous: Phase 78: Object Detection & Segmentation](docs/phase78/SUMMARY.md) | [Next: Phase 80: MLOps](docs/phase80/SUMMARY.md) →

---

# Phase 79: Causal Inference — Summary

## Overview

Phase 79 introduces **causal inference**: the science of moving beyond correlation to answer "what happens if I intervene?" Modern AI systems often make decisions—recommending treatments, setting prices, adjusting feeds—that require causal reasoning, not just prediction.

## Topics Covered

| Document | Core Idea |
|----------|-----------|
| `what_is_causal_inference.md` | Correlation vs. causation, potential outcomes framework, confounders |
| `what_is_ab_testing.md` | Randomized controlled trials, hypothesis testing, p-values, peeking |
| `what_is_propensity_scoring.md` | Matching treated and control units by estimated treatment probability |
| `what_is_instrumental_variable.md` | Using external instruments to isolate causal effects when confounders are unobserved |

## Key Concepts

- **Confounder**: A variable that influences both treatment and outcome, creating spurious associations.
- **Randomization**: Breaks confounding by making treatment independent of all covariates, on average.
- **ATE (Average Treatment Effect)**: The expected difference in outcomes if everyone were treated vs. if no one were treated.
- **Propensity Score**: The probability of receiving treatment given observed covariates; used to balance groups retrospectively.
- **Instrumental Variable**: An external variable that affects treatment but not outcome directly, isolating exogenous variation.

## Files in This Phase

```
docs/phase79/
  what_is_causal_inference.md
  what_is_ab_testing.md
  what_is_propensity_scoring.md
  what_is_instrumental_variable.md
  SUMMARY.md

src/phase79/
  phase79_causal_inference.py        # NumPy concept demo + visualizations
  phase79_causal_inference_colab.py  # Colab workflow with sklearn + econml/dowhy
  causal_inference.png               # Output plot from local script
```

## How to Run

```bash
# Local NumPy demo
python src/phase79/phase79_causal_inference.py

# Colab workflow (requires optional libraries)
# In a notebook or Colab:
#   !pip install econml dowhy scikit-learn matplotlib
#   %run src/phase79/phase79_causal_inference_colab.py
```

## Takeaway

Prediction asks: "What will happen?" Causal inference asks: "What will happen if I act?" Without causal reasoning, AI systems risk optimizing the wrong lever, perpetuating biases hidden in observational data, and failing when deployed in new environments. Mastering causality is essential for trustworthy, actionable machine learning.

---

← [Previous: Phase 78: Object Detection & Segmentation](docs/phase78/SUMMARY.md) | [Next: Phase 80: MLOps](docs/phase80/SUMMARY.md) →
