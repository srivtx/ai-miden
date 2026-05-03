# What is Variance Reduction?

## Problem it Solves
Machine learning estimates (accuracy, AUC, training loss) are noisy. High variance makes it hard to tell whether a small improvement is real or just luck.

## Definition
Variance reduction is the use of statistical techniques to decrease the variability of an estimator without introducing bias. Common methods include cross-validation, control variates, and averaging multiple runs.

## Analogy
Variance reduction is like measuring a table's length multiple times and averaging the measurements. The average is less jittery than any single measurement, so you trust it more.

## Example
Instead of evaluating a model on one random train-test split, 5-fold cross-validation averages performance across five splits. The resulting score has lower variance and gives a more stable ranking of models.

## Common Confusion
Variance reduction is not bias reduction. Bias reduction corrects systematic errors (e.g., an unfair coin); variance reduction smooths out random fluctuations without changing the expected value.

## Code Location
See `src/phase94/phase94_statistical_rigor.py` for a demonstration of how repeated evaluation and cross-validation reduce variance in accuracy estimates.
