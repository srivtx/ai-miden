# What is a Confidence Interval?

## Problem it Solves
A single accuracy number (e.g., 92.3%) is just a point estimate. It does not tell us how much that number might fluctuate if we collected a different test set or ran a different random seed.

## Definition
A confidence interval is a range of values, derived from sample data, that is likely to contain the true population parameter with a specified probability (e.g., 95%).

## Analogy
A confidence interval is like casting a net into a lake. If you cast it many times, 95% of the nets will catch the true fish (parameter). The net's width reflects how uncertain you are about the fish's exact location.

## Example
A model scores 90% accuracy on 1000 examples. Bootstrapping yields a 95% confidence interval of [88.1%, 91.7%]. We can be reasonably sure the true accuracy lies in that range.

## Common Confusion
A confidence interval is not a prediction interval. A confidence interval bounds an unknown population parameter; a prediction interval bounds where a future individual observation might fall.

## Code Location
See `src/phase94/phase94_statistical_rigor.py` for a NumPy demo that bootstraps confidence intervals around accuracy.
