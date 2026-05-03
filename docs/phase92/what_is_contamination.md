# What is Contamination?

## Problem it Solves
When test examples leak into training data, models appear stronger than they are. This undermines claims of generalization and wastes research effort on inflated results.

## Definition
Contamination is the presence of test-set information in the training pipeline. It includes exact duplicates, near-duplicates, or indirect exposure (e.g., pre-training on a corpus that contains the test set).

## Analogy
Contamination is like a student who sees the exam questions while studying. The resulting score no longer reflects true understanding, only memorization.

## Example
A language model is pre-trained on a massive web corpus. Unbeknownst to the authors, the corpus contains the exact paragraphs of a reading-comprehension benchmark. When the model is later evaluated on that benchmark, it scores artificially high.

## Common Confusion
Contamination is different from overfitting. Overfitting occurs when a model learns training-specific noise; contamination occurs when the model has already seen the test data during training.

## Code Location
See `src/phase92/phase92_benchmark_design.py` for a simulation showing how contaminated training data inflates accuracy and F1.
