← [Previous: Phase 65: QLoRA & Memory-Efficient Training](docs/phase65/SUMMARY.md) | [Next: Phase 67: Jailbreaking — Basic Attacks](docs/phase67/SUMMARY.md) →

---

# Phase 66 Summary: Preference Alignment (DPO & ORPO)

## What You Learned

This phase covered the final step of building a helpful assistant: **alignment**.
You learned how to steer a language model's behavior using preference data
instead of absolute scores.

### Key Terms

| Term | One-Sentence Meaning |
|---|---|
| **Alignment** | Shaping model behavior to be helpful, harmless, and honest. |
| **Preference Data** | Pairs of responses where one is labeled better than the other. |
| **DPO** | Directly optimizing a policy from preferences without a reward model. |
| **ORPO** | Combining SFT and preference optimization into a single training stage. |

## How It Connects

- **Phase 64 (SFT with LoRA)** gave us an instruction-following model.
- **Phase 65 (QLoRA)** let us fine-tune on limited GPU memory.
- **Phase 66** aligns that model with human values using preference pairs.
- **Phase 67 (Jailbreaking)** will test how robust our alignment is.

## The Math in Plain English

**DPO:** Compare the policy's preference for "chosen vs rejected" against the
reference model's preference. If the policy likes chosen more than the reference
does, the loss goes down.

**ORPO:** Train the model to generate the chosen answer (SFT loss) while
simultaneously increasing the odds ratio of chosen over rejected (preference
loss). One stage, no reference model.

## Code You Built

| File | What It Does |
|---|---|
| `src/phase66/phase66_dpo_orpo.py` | NumPy simulation of DPO and ORPO losses, with probability-shift plots. |
| `src/phase66/phase66_dpo_orpo_colab.py` | Real DPO and ORPO training on GPT-2 using TRL. |

## The Big Idea

Pre-training teaches knowledge. SFT teaches format. **Alignment teaches values.**
DPO and ORPO are the simplest, most popular ways to align models today — no
reward model, no PPO, just preference pairs and gradient descent.

---

← [Previous: Phase 65: QLoRA & Memory-Efficient Training](docs/phase65/SUMMARY.md) | [Next: Phase 67: Jailbreaking — Basic Attacks](docs/phase67/SUMMARY.md) →