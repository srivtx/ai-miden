# Phase 94 Summary: Experiment Design & Statistical Rigor

## What We Learned

- A point estimate without a measure of variance is a claim without evidence; always report uncertainty alongside headline metrics.
- The p-value measures how surprising the observed data would be if the null hypothesis were true, not the probability that your hypothesis is correct.
- Confidence intervals bound the true population parameter, not future individual observations, and they widen as you demand higher confidence.
- Cross-validation and repeated runs are cheap insurance against false discoveries caused by random initialization or data splits.
- Statistical rigor does not guarantee truth, but it separates noise from signal well enough to make trustworthy decisions.
- Bias reduction and variance reduction are distinct goals; fixing one does not fix the other.

## Prerequisites

- Completion of Phases 0 through 93
- Basic probability and statistics (mean, standard deviation, sampling distributions)
- Familiarity with model evaluation metrics such as accuracy, loss, and F1 score

## Recommended Reading Order

1. `what_is_variance_reduction.md` — Learn to stabilize noisy estimates before interpreting them.
2. `what_is_confidence_interval.md` — Quantify the uncertainty around your stabilized estimates.
3. `what_is_p_value.md` — Test whether observed differences between models are real or plausibly due to chance.

## Visual Outputs

- `src/phase94/phase94_statistical_rigor.py` generates bootstrap distribution histograms showing the sampling variability of accuracy, confidence interval bounds plotted over sample size, and p-value simulation charts that visualize the null distribution against observed test statistics.

## Navigation

- Previous: [Phase 93](../phase93/SUMMARY.md)
- Next: [Phase 95](../phase95/SUMMARY.md)
