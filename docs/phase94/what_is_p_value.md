# What is a p-value?

## Problem it Solves
When comparing two models, the observed difference might be due to random chance rather than a true improvement. We need a principled way to decide whether a result is surprising under the null hypothesis.

## Definition
The p-value is the probability of obtaining test results at least as extreme as the observed results, assuming that the null hypothesis (no effect) is true.

## Analogy
Imagine flipping a coin 100 times and getting 65 heads. The p-value asks: if the coin were fair, how likely is it to see 65 or more heads? A very low probability suggests the coin may not be fair.

## Example
Model A scores 85.0% and Model B scores 85.4% on the same test set. A paired permutation test yields p=0.12. Because 0.12 is above the conventional 0.05 threshold, we do not have enough evidence to claim B is truly better.

## Common Confusion
A p-value is not the probability that the null hypothesis is true. It is the probability of the data given the null hypothesis, not the probability of the hypothesis given the data.

## Code Location
See `src/phase94/phase94_statistical_rigor.py` for a simulation comparing two models with a paired t-test and interpreting the resulting p-value.
