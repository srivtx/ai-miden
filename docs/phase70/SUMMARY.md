← [Previous: Phase 69: Red-Teaming & Safety Evaluation](docs/phase69/SUMMARY.md) | [Next: Phase 71: Inference & Deployment](docs/phase71/SUMMARY.md) →

---

## Phase 70: Domain Adaptation — Building Custom Assistants

---

### What We Built

A NumPy simulation of domain adaptation showing how fine-tuning shifts a model's distribution toward a specialized domain at a measurable cost to general performance. We plotted the accuracy trade-off curve and demonstrated the full pipeline from base model to domain expert.

We also created a Colab script that builds a custom coding assistant: curating instruction data, applying chat templates, fine-tuning with LoRA, and evaluating on HumanEval-style prompts with before/after quality comparison.

### Key Results

- **Base model general accuracy:** 0.875
- **Base model domain accuracy:** 0.580
- **Domain-adapted general accuracy:** 0.715 (-16 percentage points)
- **Domain-adapted accuracy:** 0.905 (+32.5 percentage points)
- **Trade-off confirmed:** specialization improves in-domain performance while reducing generalization
- **LoRA parameter efficiency:** <1% trainable parameters achieve full adaptation in the Colab workflow

### Concepts Covered

| Term | File |
|---|---|
| Domain Adaptation | `what_is_domain_adaptation.md` |
| Continual Pre-training | `what_is_continual_pretraining.md` |
| Task-Specific Fine-Tuning | `what_is_task_specific_fine_tuning.md` |
| Custom Assistant | `what_is_custom_assistant.md` |

### Connection to Next Phase

Now that we can build domain-specific assistants, how do we serve them to real users at scale? Phase 71 covers **Inference & Deployment** with vLLM, batch optimization, and production monitoring.

### Files

- `docs/phase70/what_is_domain_adaptation.md`
- `docs/phase70/what_is_continual_pretraining.md`
- `docs/phase70/what_is_task_specific_fine_tuning.md`
- `docs/phase70/what_is_custom_assistant.md`
- `docs/phase70/SUMMARY.md`
- `src/phase70/phase70_domain_adaptation.py`
- `src/phase70/phase70_domain_adaptation_colab.py`
- `src/phase70/domain_adaptation.png`

---

← [Previous: Phase 69: Red-Teaming & Safety Evaluation](docs/phase69/SUMMARY.md) | [Next: Phase 71: Inference & Deployment](docs/phase71/SUMMARY.md) →