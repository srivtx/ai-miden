# Research: Mixture of Experts (MoE)

**Status:** Missing from course. Should be Phase 33 or integrated into Phase 18/20.
**Last Updated:** May 2026
**Sources:** Hugging Face Blog (Dec 2023, updated Feb 2026), Switch Transformers paper (2022), Mixtral (2023), ST-MoE (2022), DeepSeek-V3 (2024)

---

## 1. The Problem

Transformers scale quadratically with sequence length and linearly with parameter count. To get better performance, we need bigger models — but training a 1T parameter dense model is prohibitively expensive. We need a way to increase model capacity without proportionally increasing compute.

## 2. What It Is

A Mixture of Experts (MoE) replaces every FFN layer in a Transformer with an MoE layer consisting of:
- **N "expert" networks** (each is a small FFN)
- **A router/gating network** that decides which tokens go to which experts

Only a subset of experts (typically 1–2) are activated per token. The rest are dormant. This means:
- **Total parameters** scale with N × expert_size
- **Active parameters per token** scale with k × expert_size (where k << N)
- **Compute** is much lower than a dense model with the same total parameter count

## 3. Real-World Analogy

A hospital with 100 specialists but only 2 are on call per patient. The triage nurse (router) sends the cardiac patient to the cardiologist, the broken bone to the orthopedist. The hospital has enormous collective knowledge (100 doctors) but each patient only needs a tiny fraction of it.

## 4. Key Technical Details

### Sparsity and Routing
```
G(x) = Softmax(TopK(H(x), k))
H(x)_i = (x · W_g)_i + StandardNormal() · Softplus((x · W_noise)_i)
```

**Noisy Top-K Gating:** Adds Gaussian noise before selecting top-k experts. The noise prevents the router from collapsing to always picking the same expert early in training.

### Load Balancing
Without intervention, the router converges to favoring a few "easy" experts. Solutions:
- **Auxiliary loss:** Penalizes imbalance in expert usage
- **Expert capacity:** Caps how many tokens each expert can process per batch
- **Router Z-loss:** Penalizes large logits entering the gating network (improves stability)

### Capacity Factor
```
Expert Capacity = (tokens_per_batch / num_experts) × capacity_factor
```
- CF = 1.0: Perfect balance, no buffer
- CF = 1.25: 25% buffer for imbalanced routing (common default)
- Higher CF = better quality but more memory and communication

### Switch Transformers (Google, 2022)
- Simplified to **top-1 routing** (one expert per token)
- Achieved 4× pre-training speedup over T5-XXL
- Released 1.6T parameter model with 2048 experts
- Introduced selective precision: bfloat16 for experts, fp32 for router

### Mixtral 8×7B (Mistral, 2023)
- 8 experts, each 7B parameters
- Total params: ~47B (not 56B because attention layers are shared)
- Top-2 routing
- Outperforms Llama 2 70B with faster inference
- Compute per token: ~12B equivalent (not 14B because of shared layers)

## 5. Common Confusion

- **MoE is not an ensemble.** Ensembles run all models and average. MoE runs only k experts per token.
- **Memory is the bottleneck.** All experts must be in RAM, even though only k are used. A 47B MoE needs 47B worth of VRAM, not 12B.
- **Fine-tuning is harder.** MoEs overfit more than dense models. Solutions: higher dropout in experts, smaller batch sizes, higher learning rates, freezing non-expert layers.
- **Communication costs matter.** In distributed training, tokens must be sent to the GPU hosting their assigned expert. All-to-all communication can dominate runtime.
- **Not all layers become MoE.** Typically only every other FFN layer is replaced. Attention layers are always shared.

## 6. What We Would Build

A tiny MoE where:
- Input tokens are routed to 1 of 4 small expert networks
- Router is learned jointly
- Load balancing loss prevents collapse
- Compare parameter count vs. active compute vs. dense baseline

## 7. Why It Matters Now

- **GPT-4** is widely believed to be an MoE (8×220B or similar)
- **DeepSeek-V3** (2024) uses MoE with 256B total / 37B active, trained for $5.6M
- **Mixtral** proved open-source MoEs can beat dense models
- MoE is the dominant architecture for frontier models because it decouples capacity from compute

## 8. Connection to Existing Phases

- **Phase 18 (Transformer):** MoE replaces FFN layers
- **Phase 25 (Inference Optimization):** MoE inference requires expert parallelism and careful capacity management
- **Phase 32 (Foundation Models):** GPT-4 and Mixtral are MoE-based foundation models

---

## References

- Shazeer et al. (2017): "Outrageously Large Neural Networks"
- Fedus et al. (2022): "Switch Transformers"
- Mistral AI (2023): "Mixtral of Experts"
- Zoph et al. (2022): "ST-MoE: Designing Stable and Transferable Sparse Expert Models"
