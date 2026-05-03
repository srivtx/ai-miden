## What Is Mixture of Experts (MoE)?

---

## The Problem

A standard dense transformer with 1 billion parameters uses all 1 billion parameters on every single forward pass. When you scale to 100 billion parameters, inference becomes prohibitively expensive: a single token generation might require hundreds of gigabytes of memory and tens of thousands of floating-point operations. You want the capacity of a massive model — the ability to memorize rare facts, understand subtle patterns, and generate coherent long-form text — but you cannot afford to pay the full compute price on every token. The industry needs a way to increase model capacity without proportionally increasing per-token computation.

---

## Definition

**Mixture of Experts (MoE)** replaces a single dense feed-forward layer with multiple smaller "expert" networks and a gating network. For each input token, the gate selects a subset of experts (typically top-k), and only those selected experts are activated. The outputs are combined by a weighted sum. The model has many parameters in total, but only a fraction participate in any given forward pass.

**How it works:**
```
Dense layer:          1B parameters, all active per token
MoE layer:            64 experts × 16M parameters = 1.024B total parameters
                      Gate selects top-2 experts per token
                      Active parameters per token: 2 × 16M = 32M
                      Sparsity: 32M / 1.024B ≈ 3% active
```

**Key components:**
- **Experts:** small feed-forward networks that specialize in different input patterns.
- **Gating network:** a lightweight classifier that outputs a probability distribution over experts for each token.
- **Top-k selection:** choosing the k highest-scoring experts and masking the rest to zero.
- **Weighted aggregation:** combining the selected experts' outputs using the gate scores as weights.

**Why this matters:**
- A 1-trillion-parameter MoE model can run inference on hardware sized for a 10-billion-parameter dense model.
- Different experts can specialize in different domains: one for code, one for biology, one for conversation.
- MoE is the primary technique used to train models like GPT-4, Mixtral, and Switch Transformer at scale.

---

## Real-Life Analogy

Think of a large hospital with 100 medical specialists: cardiologists, neurologists, dermatologists, oncologists, and so on. A patient arrives with chest pain. In a "dense" hospital, every patient sees every single doctor: the cardiologist, the dermatologist, the podiatrist, and the psychiatrist. The podiatrist finds nothing wrong with the feet, but the appointment still consumes time and money. The patient receives comprehensive care at an absurd cost.

**The MoE approach:** A triage nurse (the gate) evaluates the patient in five minutes and routes them to the two most relevant specialists: the cardiologist and the internal medicine physician. The dermatologist and psychiatrist are not consulted. The hospital can employ 100 world-class doctors, but each patient only sees the few who matter. The hospital's capacity is massive, but the per-patient cost is low.

**The trade-off:** The hospital building is still huge. You pay rent for all 100 offices, maintain equipment for every specialty, and keep every doctor on salary. The memory footprint is large even though the compute per patient is small. If the triage nurse makes a mistake and sends a neurological patient to a dermatologist, the diagnosis fails. Similarly, if the MoE gate is poorly trained, tokens are routed to the wrong experts and the model hallucinates or underperforms.

---

## Tiny Numeric Example

**Comparing a dense 1B model to an MoE 8B model:**

| Property | Dense 1B | MoE 8B (64 experts, top-2) |
|---|---|---|
| Total parameters | 1,000M | 8,192M |
| Active parameters per token | 1,000M | 256M |
| FLOPs per token (forward) | 4.0 GFLOPs | 1.2 GFLOPs |
| Memory for weights | 4 GB | 32 GB |
| Inference throughput (A100) | 12 tokens/sec | 45 tokens/sec |
| Training time per step | 2.5 sec | 1.8 sec |

**Specialization check after training:**
```
Expert 0:  42% of code tokens,  3% of medical tokens  → code specialist
Expert 12: 38% of medical tokens, 5% of code tokens   → medical specialist
Expert 33: 25% of legal tokens,   4% of news tokens    → legal specialist
Expert 55:  no clear dominance   → undertrained or generalist
```

**Accuracy on domain benchmarks:**
```
Dense 1B:      code 32.1%, medical 28.4%, legal 25.7%
MoE 8B:        code 41.3%, medical 37.8%, legal 34.2%
Improvement:   +9.2, +9.4, +8.5 percentage points
```

**The shift:** MoE trades total memory for per-token compute efficiency. The model is 8x larger in parameter count but 3x faster in inference because only 3% of parameters are active per token. The remaining challenge is training the gate well enough to route each token to the right experts.

---

## Common Confusion

1. **"MoE makes the model smaller on disk."** The total parameter count is larger, not smaller. The weights are still stored in memory; only the compute is sparse.

2. **"MoE is the same as model pruning."** Pruning permanently deletes weights to reduce size; MoE keeps all weights but activates only a subset per token. Pruning is compression; MoE is conditional computation.

3. **"Any model can be converted to MoE by adding experts."** Naive conversion usually hurts performance. MoE requires careful gate initialization, load balancing, and communication-aware training to outperform dense baselines.

4. **"MoE always beats dense models."** At small scales, the overhead of routing and communication often outweighs the benefits. MoE shines at multi-billion-parameter scales.

5. **"MoE experts learn human-interpretable specializations."** Sometimes experts specialize by domain or syntax, but often they specialize by low-level statistical patterns that are not human-interpretable.

6. **"MoE eliminates the need for large batch sizes."** MoE still benefits from large batches, but for a different reason: large batches improve routing diversity and load balance across experts.

7. **"MoE is only for language models."** MoE has been applied to vision transformers, speech recognition, recommendation systems, and multi-modal models. The principle of conditional computation is domain-agnostic.

---

## Where It Is Used in Our Code

`src/phase96/phase96_moe.py` — We simulate a tiny MoE layer with 8 experts and a learned gating network. We forward a batch of synthetic token embeddings, compute top-2 routing, activate only the selected experts, and aggregate their outputs. We compare the active parameter count and FLOPs to a dense baseline of equivalent total capacity, and we plot the per-expert activation frequency to show how routing creates sparse compute.
