# What is Validity?

## Problem it Solves
A high score on a benchmark is meaningless if the benchmark does not capture the real-world capability it claims to measure. Validity ensures that the ruler is measuring length, not temperature.

## Definition
Validity is the degree to which a test or benchmark actually measures the construct it is intended to measure. It encompasses content validity, construct validity, and predictive validity.

## Analogy
A bathroom scale has high validity if it measures weight accurately. If it instead reacts to humidity, it is unreliable for weight and therefore invalid for that purpose, even if it gives consistent readings.

## Example
A translation benchmark that only evaluates short, formal sentences may have low validity for measuring a model's ability to translate informal, conversational speech, even if the metric (BLEU) is computed correctly.

## Common Confusion
Validity is not the same as reliability. Reliability means the test gives consistent results; validity means it measures the right thing. A scale that always shows 5 kg extra is reliable but invalid.

## Code Location
See `src/phase92/phase92_benchmark_design.py` for a discussion of how a toy benchmark's validity depends on whether it reflects the true task distribution.
