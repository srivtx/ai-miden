← [Previous: Phase 49: Advanced Optimizers](docs/phase49/SUMMARY.md) | [Next: Phase 51: Evaluation Metrics](docs/phase51/SUMMARY.md) →

---

## Phase 50: Self-Supervised Learning

---

### What We Built

Demonstrations of self-supervised learning: contrastive learning on 2D points, masked autoencoding on tiny images, and rotation prediction as a pretext task.

### Key Results

- **Contrastive learning:** Loss decreases from 1.29, embeddings cluster by group
- **Masked autoencoding:** Reconstruction MSE = 0.047 on masked pixels (learned structure)
- **Rotation prediction:** 41% accuracy on 4-way rotation classification from stripe patterns

### Concepts Covered

| Term | File |
|---|---|
| Self-Supervised Learning | `what_is_self_supervised_learning.md` |
| Contrastive Learning | `what_is_contrastive_learning.md` |
| Masked Autoencoding | `what_is_masked_autoencoding.md` |
| Pretext Task | `what_is_pretext_task.md` |

### Connection to Next Phase

Now that models can learn without labels, how do we measure if they learned anything useful? Phase 51 covers **evaluation metrics**.

### Files

- `docs/phase50/what_is_self_supervised_learning.md`
- `docs/phase50/what_is_contrastive_learning.md`
- `docs/phase50/what_is_masked_autoencoding.md`
- `docs/phase50/what_is_pretext_task.md`
- `docs/phase50/SUMMARY.md`
- `src/phase50/phase50_self_supervised_learning.py`
- `src/phase50/self_supervised_learning.png`

---

← [Previous: Phase 49: Advanced Optimizers](docs/phase49/SUMMARY.md) | [Next: Phase 51: Evaluation Metrics](docs/phase51/SUMMARY.md) →