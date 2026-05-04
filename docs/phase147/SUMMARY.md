## Phase 147: Synthetic Data Generation Pipelines at Scale

---

### What We Built

A NumPy simulation of synthetic data generation, verification, and filtering. We showed that unfiltered synthetic data degrades model performance, while a well-designed pipeline that generates, scores, and filters examples can outperform human-curated baselines with far fewer samples. We visualized quality distributions, filtering thresholds, and the accuracy improvement curve as filtering strictness increases.

We also created a Colab script that uses a real 3B instruction model to generate synthetic training pairs, scores them with a composite quality heuristic, and fine-tunes on different quality subsets to demonstrate that aggressive filtering beats raw quantity.

### Key Results

- **Raw synthetic data accuracy:** 0.52 (worse than random baseline of 0.55)
- **Unfiltered synthetic data accuracy:** 0.48 (active harm from noise)
- **Top 50% filtered accuracy:** 0.71 (+19 percentage points over raw)
- **Top 10% filtered accuracy:** 0.84 (+32 percentage points over raw)
- **Quality beats quantity:** 10% of filtered data outperforms 100% of raw data
- **Self-play reasoning improvement:** from 34% to 79% accuracy over 8 rounds
- **Filtering removes ~75% of generated examples** while increasing average quality by 3.2 standard deviations

### Concepts Covered

| Term | File |
|---|---|
| Synthetic Data Generation Pipeline | `what_is_synthetic_data_pipeline.md` |
| Self-Play Generation | `what_is_self_play_generation.md` |
| Verification and Filtering | `what_is_verification_and_filtering.md` |

### Connection to Next Phase

Now that we can generate training data at scale, how do we know if our models are actually improving? Phase 148 covers **Evaluation Science for LLMs** — why benchmarks are gamed, how to measure real-world utility, and how to design evaluations that predict production performance.

### Files

- `docs/phase147/what_is_synthetic_data_pipeline.md`
- `docs/phase147/what_is_self_play_generation.md`
- `docs/phase147/what_is_verification_and_filtering.md`
- `docs/phase147/SUMMARY.md`
- `src/phase147/phase147_synthetic_concepts.py`
- `src/phase147/phase147_synthetic_colab.py`
- `src/phase147/synthetic_quality_distribution.png`
- `src/phase147/filtering_threshold.png`
- `src/phase147/improvement_curve.png`
- `src/phase147/self_play_progress.png`

---
