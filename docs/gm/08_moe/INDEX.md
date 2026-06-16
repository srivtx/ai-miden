# Part 8: Mixture of Experts (MoE)

> 8× capacity at 2× compute. Only the relevant part of the model activates.

## Files

- [what_is_moe.md](what_is_moe.md) — Full treatment

## Key insight

Replace one dense FFN with N independent FFN experts + a learned router. Only top-K experts activate per token. Total params explode (8×), active compute barely moves (2×). The brain does this — 86B neurons, 1-5% active.

## Connection to the curriculum

- Builds on understanding of transformer architecture
- Complements [Part 7 (LoRA)](../07_lora/) — LoRA for task specialization, MoE for capacity scaling
- Direct neuroscience connection to sparse cortical activation and thalamic routing

## Code impact

cortexcode: Replace dense FFN in MSPCHBlock with MoE (8 experts, top-2). 10M→40M params. Active per token: 20M. Route class definitions, imports, args to different experts.
