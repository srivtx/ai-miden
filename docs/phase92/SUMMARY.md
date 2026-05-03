# Phase 92: Benchmark Design & Evaluation Science

## What We Learned

1. **Benchmarks are standardized contracts for comparison.** A dataset alone is not a benchmark. Only when combined with a task definition, evaluation metric, and protocol do results become comparable across models and research groups.
2. **Contamination invalidates generalization claims.** Even small amounts of test-set leakage into training data can inflate scores by double-digit percentages, making models appear capable when they have merely memorized answers.
3. **Validity ensures the benchmark measures what it claims.** A test with high reliability but low validity gives consistent wrong answers. Domain coverage, construct alignment, and predictive power matter more than headline numbers.
4. **Clean splits and isolation are non-negotiable.** Date-based partitioning, strict deduplication, and held-out test sets are foundational practices that separate honest evaluation from vanity metrics.
5. **Evaluation is a systems discipline, not an afterthought.** Good benchmarks are updated to prevent saturation, audited for bias, and validated against human performance and real-world utility.
6. **Headline numbers can mislead.** A model that tops a narrow benchmark by a fraction of a percent may fail on the actual task distribution. Skepticism and multi-benchmark evaluation are essential.

## Prerequisites

- Understanding of train/validation/test splits and cross-validation
- Familiarity with classification metrics: accuracy, precision, recall, F1
- Basic knowledge of statistical concepts: mean, standard deviation, confidence intervals
- Experience with NumPy for synthetic data generation and model training

## Recommended Reading Order

1. `what_is_benchmark.md` — Understand what makes a benchmark valid and comparable
2. `what_is_contamination.md` — Learn how train-test leakage destroys trust in benchmark scores
3. `what_is_validity.md` — Finish with the deeper question of whether the benchmark measures the right construct at all

## Visual Outputs

- `phase92_comparison.png` — Grouped bar chart comparing accuracy and F1 score between clean and contaminated evaluation scenarios.

## Navigation

- [Previous Phase](../phase91/SUMMARY.md)
- [Next Phase](../phase93/SUMMARY.md)
