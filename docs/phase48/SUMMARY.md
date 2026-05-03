← [Previous: Phase 47: Synthetic Data & Self-Improvement](docs/phase47/SUMMARY.md) | [Next: Phase 49: Advanced Optimizers](docs/phase49/SUMMARY.md) →

---

## Phase 48: Test-Time Training

---

### What We Built

A demonstration of how models can adapt at inference time without any labeled test data. We showed meta-learning for fast few-shot adaptation, test-time training on a single input using auxiliary tasks, and online learning adapting to distribution shifts.

### Key Results

- **Meta-learning:** Meta-learned initialization achieves 91% accuracy vs. 90% for random init (5 examples)
- **Test-time training:** Adapting on shifted data improves from 60% to 70% without any labels
- **Online learning:** Model adapts to a distribution shift at step 50 in real-time

### Concepts Covered

| Term | File |
|---|---|
| Test-Time Training | `what_is_test_time_training.md` |
| Unsupervised Adaptation | `what_is_unsupervised_adaptation.md` |
| Meta-Learning | `what_is_meta_learning.md` |
| Online Learning | `what_is_online_learning.md` |

### How It Works

1. **Meta-learning:** Train across many related tasks to find an initialization that adapts in few steps
2. **Test-time training:** At inference, run auxiliary self-supervised tasks on the test input to shift representations
3. **Online learning:** Update the model continuously as new data arrives, adapting to distribution shifts

### Connection to Previous Phases

- **Phase 47 (Synthetic Data):** Models can generate training data; TTT adapts without any data collection
- **Phase 3 (Gradient Descent):** TTT is just a few gradient steps at inference time
- **Phase 8 (L2 Regularization):** Meta-learning finds good initializations that generalize across tasks

### Connection to Next Phase

This completes the extended phase series (45-48). The course now covers:
- Consumer deployment (quantization)
- Internal understanding (interpretability)
- Data scaling (synthetic data)
- Real-time adaptation (test-time training)

### Files

- `docs/phase48/what_is_test_time_training.md`
- `docs/phase48/what_is_unsupervised_adaptation.md`
- `docs/phase48/what_is_meta_learning.md`
- `docs/phase48/what_is_online_learning.md`
- `docs/phase48/SUMMARY.md`
- `src/phase48/phase48_test_time_training.py`
- `src/phase48/phase48_test_time_training_colab.py`
- `src/phase48/test_time_training.png`

---

← [Previous: Phase 47: Synthetic Data & Self-Improvement](docs/phase47/SUMMARY.md) | [Next: Phase 49: Advanced Optimizers](docs/phase49/SUMMARY.md) →