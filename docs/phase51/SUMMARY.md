← [Previous: Phase 50: Self-Supervised Learning](docs/phase50/SUMMARY.md) | [Next: Phase 52: Data Augmentation & Tokenization](docs/phase52/SUMMARY.md) →

---

## Phase 51: Evaluation Metrics

---

### What We Built

A demonstration of how to evaluate models using multiple metrics: accuracy, precision, recall, F1, perplexity, BLEU, and Expected Calibration Error (ECE).

### Key Results

- **Classification:** Accuracy 70%, Precision 75%, Recall 60%, F1 66.7%
- **Perplexity:** 21.1 (model uncertainty equivalent to 21 choices)
- **BLEU:** 0.500 on a 4-word sentence against 5-word reference
- **ECE:** 25.5% (model is overconfident, especially in 50-70% bin)

### Concepts Covered

| Term | File |
|---|---|
| Evaluation Metrics | `what_are_evaluation_metrics.md` |
| Perplexity | `what_is_perplexity.md` |
| BLEU | `what_is_bleu.md` |
| Calibration | `what_is_calibration.md` |

### Connection to Next Phase

Now that we can measure models, how do we build better training data? Phase 52 covers **data augmentation and tokenization**.

### Files

- `docs/phase51/what_are_evaluation_metrics.md`
- `docs/phase51/what_is_perplexity.md`
- `docs/phase51/what_is_bleu.md`
- `docs/phase51/what_is_calibration.md`
- `docs/phase51/SUMMARY.md`
- `src/phase51/phase51_evaluation_metrics.py`
- `src/phase51/evaluation_metrics.png`

---

← [Previous: Phase 50: Self-Supervised Learning](docs/phase50/SUMMARY.md) | [Next: Phase 52: Data Augmentation & Tokenization](docs/phase52/SUMMARY.md) →