# Part 7: LoRA (Low-Rank Adaptation)

> Parameter-efficient fine-tuning. Update 0.1% of weights, keep 95% of the improvement.

## Files

- [what_is_lora.md](what_is_lora.md) — Full treatment

## Key insight

The weight update ΔW during fine-tuning is low-rank. Decompose ΔW = A×B where A is (d×r), B is (r×k), and r=4-16. Train only A and B (0.1% of params). Merge back for zero inference overhead.

## Connection to the curriculum

- Builds on [Part 1 (VAE)](../01_vae/) and [Part 2 (Diffusion)](../02_diffusion/) — LoRA works on any trained model
- Enables the multi-project deployment: one base model, N lightweight adapters
- Complements [Part 8 (MoE)](../08_moe/) — LoRA for task specialization, MoE for capacity scaling

## Code impact

cortexcode: Train ONE base model on jc+rich+cpython (30 min). Then 30s LoRA fine-tune per new codebase. Each adapter ~80KB.
