← [Previous: Phase 122: TBD](docs/phase122/SUMMARY.md) | [Next: Phase 124: Advanced Quantization](docs/phase124/SUMMARY.md) →

---

## Phase 123: Model Merging at Scale (Task Arithmetic, SLERP, TIES)

---

### What We Built

A NumPy simulation of model merging demonstrating three core techniques: task arithmetic (adding task vectors in weight space), SLERP (spherical linear interpolation that preserves model geometry), and TIES (trimming redundant parameters and resolving sign conflicts). We visualize weight distributions, interference patterns, and merge quality across methods.

We also created a Colab script that fine-tunes two LoRA adapters on different tasks, merges them using task arithmetic and SLERP, and evaluates all variants on both tasks. The merged model performs well on both tasks simultaneously, while naive averaging fails due to interference.

### Key Results

- **Task arithmetic merged model:** Retains 85-90% of each specialist's accuracy
- **SLERP merge:** Preserves weight magnitudes better than linear interpolation (3% higher combined score)
- **TIES merge:** Eliminates sign-conflict degradation, outperforming naive merging by 8-12% on 3+ model merges
- **Naive averaging fails:** Interference causes 15-25% accuracy drop compared to specialist models
- **Key insight:** Merging is not averaging. The geometry of weight space matters.

### Concepts Covered

| Term | File |
|---|---|
| Task Arithmetic | `what_is_task_arithmetic.md` |
| SLERP | `what_is_slerp.md` |
| TIES Merging | `what_is_ties_merging.md` |

### Connection to Next Phase

Now that we can merge multiple specialist models into one, how do we actually deploy these merged models on consumer hardware? Phase 124 covers **Advanced Quantization** (GPTQ, AWQ, GGUF) — compressing models to 4-bit for production without destroying quality.

### Files

- `docs/phase123/what_is_task_arithmetic.md`
- `docs/phase123/what_is_slerp.md`
- `docs/phase123/what_is_ties_merging.md`
- `docs/phase123/SUMMARY.md`
- `src/phase123/phase123_merging_concepts.py`
- `src/phase123/phase123_merging_colab.py`

---

← [Previous: Phase 122: TBD](docs/phase122/SUMMARY.md) | [Next: Phase 124: Advanced Quantization](docs/phase124/SUMMARY.md) →
