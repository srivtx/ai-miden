# What is an Ablation?

## Problem it Solves
Complex models contain many components (attention, residual connections, data augmentation). It is unclear which components actually drive performance and which are unnecessary baggage.

## Definition
An ablation study is a controlled experiment in which one component of a system is removed to measure its marginal contribution to overall performance.

## Analogy
An ablation is like removing one ingredient at a time from a soup recipe. If the soup still tastes great without saffron, then saffron was not the secret to its success.

## Example
A vision transformer paper reports 87% accuracy. An ablation removes the positional encoding and sees accuracy drop to 62%, proving that positional encoding is essential. Another ablation removes dropout and sees no change, suggesting dropout can be omitted for speed.

## Common Confusion
Ablation is not the same as a hyperparameter search. A search varies a setting to find the best value; an ablation removes the component entirely to test necessity.

## Code Location
See `src/phase93/phase93_paper_reading.py` for an ablation that removes a custom regularization term and measures the impact on a toy task.
