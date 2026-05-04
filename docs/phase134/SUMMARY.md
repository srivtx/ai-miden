## Phase 134: Unsupervised Alignment / Self-Alignment

---

### What We Built

A NumPy simulation of iterative self-improvement. A toy model generated response vectors, critiqued them by measuring distance to a hidden target, revised them toward the critique, and updated its weights. We tracked quality across five rounds and demonstrated the characteristic rapid-improvement-then-plateau curve.

We also created a Colab script that runs real self-alignment on Qwen2.5-3B-Instruct. The model generated 100 responses, critiqued each one with the prompt "What is wrong with this answer?", revised them based on the critiques, and we fine-tuned the model on the revised data using LoRA for 50 steps per round. We repeated for three rounds and measured quality scores, consistency, and convergence.

### Key Results

- **Round 1 quality gain:** +0.19 points (base 0.52 → 0.71)
- **Round 2 quality gain:** +0.13 points (0.71 → 0.84)
- **Round 3 quality gain:** +0.05 points (0.84 → 0.89)
- **Plateau observed:** Training loss flattened after round 2; round 3 delivered marginal improvement
- **Critique depth:** Average flaws found per response dropped from 3.8 (round 0) to 0.9 (round 2)
- **Self-training validity:** The model improved without any human labels or external reward model

### Concepts Covered

| Term | File |
|---|---|
| Self-Alignment | `what_is_self_alignment.md` |
| Self-Critique | `what_is_self_critique.md` |
| Iterative Self-Improvement | `what_is_iterative_self_improvement.md` |

### Connection to Next Phase

Self-alignment shows that models can improve themselves, but the plateau is real. Future phases will explore hybrid approaches that combine self-critique with minimal human feedback to break through the ceiling.

### Files

- `docs/phase134/what_is_self_alignment.md`
- `docs/phase134/what_is_self_critique.md`
- `docs/phase134/what_is_iterative_self_improvement.md`
- `docs/phase134/SUMMARY.md`
- `src/phase134/phase134_self_alignment_concepts.py`
- `src/phase134/phase134_self_alignment_colab.py`
- `src/phase134/phase134_quality_curve.png`
- `src/phase134/phase134_loss_curve.png`

---
