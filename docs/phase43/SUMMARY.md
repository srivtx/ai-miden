## Phase 43: Model Merging & Ensembles

---

### What We Built

A demonstration of **model merging** — combining multiple fine-tuned models into a single model without any additional training. We compare simple averaging, task arithmetic, SLERP, and TIES-Merging on a multi-task classification problem.

### Key Results

- **Base model (mixed training):** 62.5% / 70.5% / 58.0% on Tasks 0/1/2
- **Specialist models:** Each achieves ~90% on its own task but forgets others
- **Simple Average merge:** 64.5% / 68.0% / 57.0% — reasonable across all tasks
- **Task Arithmetic:** 65.5% / 67.5% / 56.0% — preserves base knowledge explicitly
- **SLERP:** 64.5% / 69.5% / 55.5% — respects weight space geometry
- **TIES-Merging:** 61.5% / 65.5% / 47.5% — removes noise but threshold-sensitive on tiny models

### Concepts Covered

| Term | File |
|---|---|
| Model Merging | `what_is_model_merging.md` |
| Task Arithmetic | `what_is_task_arithmetic.md` |
| SLERP | `what_is_slerp.md` |
| TIES-Merging | `what_is_ties_merging.md` |

### How It Works

1. Train a base model on mixed data
2. Fine-tune three copies on individual tasks
3. Merge the fine-tuned weights using various techniques
4. Evaluate the merged model on all tasks simultaneously

### Connection to Previous Phases

- **Phase 35 (LoRA):** LoRA creates small adapters; model merging combines full fine-tunes
- **Phase 22 (SFT):** Model merging is a post-SFT technique for multi-task combination
- **Phase 8 (L2 Regularization):** Merging works because fine-tuning deltas stay small

### Connection to Next Phase

Now that we can combine models, how do we handle inputs longer than the model was trained for? In Phase 44, we explore **long context and position interpolation** — techniques to extend a model's context window without retraining from scratch.

### Files

- `docs/phase43/what_is_model_merging.md`
- `docs/phase43/what_is_task_arithmetic.md`
- `docs/phase43/what_is_slerp.md`
- `docs/phase43/what_is_ties_merging.md`
- `docs/phase43/SUMMARY.md`
- `src/phase43/phase43_model_merging.py`
- `src/phase43/phase43_model_merging_colab.py`
- `src/phase43/model_merging.png`
