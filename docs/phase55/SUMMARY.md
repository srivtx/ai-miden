## Phase 55: Distributed Training

---

### What We Built

A conceptual demonstration of distributed training techniques using simulated workers on a simple linear regression dataset.

### Key Results

- **Data parallelism:** 4 workers compute local gradients; all-reduce average matches full-batch gradient exactly
- **Model parallelism:** A 2-layer MLP split across 2 workers; neither holds the full model
- **Gradient accumulation:** 4 mini-batches of 4 accumulate to match full batch of 16 exactly
- **All-reduce:** 4 workers with unique gradient chunks all converge to the true average [7, 8, 9, 10]

### Concepts Covered

| Term | File |
|---|---|
| Data Parallelism | `what_is_data_parallelism.md` |
| Model Parallelism | `what_is_model_parallelism.md` |
| Gradient Accumulation | `what_is_gradient_accumulation.md` |
| Distributed SGD / All-Reduce | `what_is_distributed_sgd.md` |

### Connection to Next Phase

Now that we can train across many machines, what if we want models that combine many weak learners into a strong one? Phase 56 covers **gradient boosting**.

### Files

- `docs/phase55/what_is_data_parallelism.md`
- `docs/phase55/what_is_model_parallelism.md`
- `docs/phase55/what_is_gradient_accumulation.md`
- `docs/phase55/what_is_distributed_sgd.md`
- `docs/phase55/SUMMARY.md`
- `src/phase55/phase55_distributed_training.py`
- `src/phase55/distributed_training.png`
