← [Previous: Phase 63: Dataset Curation for Fine-Tuning](docs/phase63/SUMMARY.md) | [Next: Phase 65: QLoRA & Memory-Efficient Training](docs/phase65/SUMMARY.md) →

---

## Phase 64: Practical SFT with LoRA

---

### What We Built

A NumPy simulation of LoRA fine-tuning on a toy regression task, plus a Colab script for real LoRA fine-tuning of GPT-2. We trained separate adapters for two tasks, merged them, and compared parameter counts.

### Key Results

- **LoRA parameters:** 32 (2× reduction vs. 64 full fine-tuning)
- **LoRA Task A loss:** 0.3782
- **Full fine-tune loss:** 0.2321 (better with more params, as expected)
- **LoRA Task B loss:** 0.4747
- **Merged model:** Preserves both tasks without retraining

### Concepts Covered

| Term | File |
|---|---|
| LoRA | `what_is_lora.md` |
| SFT (Supervised Fine-Tuning) | `what_is_sft.md` |
| Target Module | `what_is_target_module.md` |
| Adapter Merging | `what_is_adapter_merging.md` |

### Connection to Next Phase

LoRA is efficient, but what if the model is so large it does not even fit in GPU memory? Phase 65 covers **QLoRA** — quantizing the base model to 4 bits while keeping LoRA adapters in full precision.

### Files

- `docs/phase64/what_is_lora.md`
- `docs/phase64/what_is_sft.md`
- `docs/phase64/what_is_target_module.md`
- `docs/phase64/what_is_adapter_merging.md`
- `docs/phase64/SUMMARY.md`
- `src/phase64/phase64_sft_lora.py`
- `src/phase64/phase64_sft_lora_colab.py`
- `src/phase64/sft_lora.png`

---

← [Previous: Phase 63: Dataset Curation for Fine-Tuning](docs/phase63/SUMMARY.md) | [Next: Phase 65: QLoRA & Memory-Efficient Training](docs/phase65/SUMMARY.md) →