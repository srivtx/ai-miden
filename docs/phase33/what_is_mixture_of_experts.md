## What Is Mixture of Experts (MoE)?

---

### The Problem

You want a 1 trillion parameter model because bigger models are smarter. But training and running a dense 1T model is impossibly expensive. Every single parameter is used for every single token. You are paying for 1T parameters worth of compute on every forward pass. How do you get the *capacity* of a huge model without the *cost* of using every parameter every time?

---

### Definition

A **Mixture of Experts (MoE)** is a neural network architecture where only a small subset of the network's parameters are activated for any given input. Instead of one giant feed-forward layer, an MoE layer contains many smaller "expert" networks (each is a normal FFN) plus a "router" that decides which experts to use for each input token.

**Key insight:**
- Total parameters = `num_experts × expert_size` (huge)
- Active parameters per token = `top_k × expert_size` (small)
- Compute per token scales with active parameters, not total parameters

---

### Real-Life Analogy

Imagine a hospital with 100 specialists: cardiologists, neurologists, dermatologists, etc. When a patient arrives, a triage nurse (the router) quickly assesses them and sends them to exactly 2 relevant specialists. The hospital has enormous collective knowledge (100 doctors), but each patient only sees 2 of them. The hospital is "sparsely activated."

A dense model is like forcing every patient to see all 100 doctors. An MoE is like the triage system.

---

### Tiny Numeric Example

**Input token:** `x = [0.5, -0.3]` (2-dimensional)

**4 experts, each is a tiny FFN:**
- Expert 0: `W0 = [[1.0, 0.5], [0.2, 0.8]]`
- Expert 1: `W1 = [[0.5, 1.0], [0.8, 0.2]]`
- Expert 2: `W2 = [[0.1, 0.9], [0.9, 0.1]]`
- Expert 3: `W3 = [[0.7, 0.3], [0.4, 0.6]]`

**Router weights:** `W_g = [[0.2, 0.8, -0.1, 0.5], [0.5, -0.3, 0.9, 0.1]]`

**Step 1 — Compute router logits:**
```
logits = x · W_g
       = [0.5, -0.3] · W_g
       = [0.5×0.2 + (-0.3)×0.5, 0.5×0.8 + (-0.3)×(-0.3),
          0.5×(-0.1) + (-0.3)×0.9, 0.5×0.5 + (-0.3)×0.1]
       = [0.10 - 0.15, 0.40 + 0.09, -0.05 - 0.27, 0.25 - 0.03]
       = [-0.05, 0.49, -0.32, 0.22]
```

**Step 2 — Select top-2 experts:**
```
Top 2 logits: Expert 1 (0.49) and Expert 3 (0.22)
```

**Step 3 — Compute expert outputs (only for selected experts):**
```
Expert 1 output: y1 = ReLU(x · W1) = ReLU([0.5×0.5 + (-0.3)×0.8, 0.5×0.8 + (-0.3)×0.2])
                  = ReLU([0.25 - 0.24, 0.40 - 0.06])
                  = ReLU([0.01, 0.34])
                  = [0.01, 0.34]

Expert 3 output: y3 = ReLU(x · W3) = ReLU([0.5×0.7 + (-0.3)×0.4, 0.5×0.3 + (-0.3)×0.6])
                  = ReLU([0.35 - 0.12, 0.15 - 0.18])
                  = ReLU([0.23, -0.03])
                  = [0.23, 0.0]
```

**Step 4 — Combine with router weights (softmax over top-k):**
```
gate_values = softmax([-0.05, 0.49, -0.32, 0.22]) over top-2
            = softmax([0.49, 0.22])
            = [exp(0.49)/(exp(0.49)+exp(0.22)), exp(0.22)/(exp(0.49)+exp(0.22))]
            = [1.632/(1.632+1.246), 1.246/(1.632+1.246)]
            = [0.567, 0.433]

final_output = 0.567 × y1 + 0.433 × y3
             = 0.567 × [0.01, 0.34] + 0.433 × [0.23, 0.0]
             = [0.0057 + 0.0996, 0.1928 + 0.0]
             = [0.1053, 0.1928]
```

**Parameter count:** 4 experts × 4 weights each = 16 total parameters. But only 2 experts were used, so only 8 parameters were active for this token.

---

### Common Confusion

1. **"MoE is an ensemble of models."** No. An ensemble runs ALL models and averages their outputs. An MoE runs only k experts per token. The other experts do zero computation.

2. **"MoE reduces memory usage."** No. All experts must live in memory (RAM/VRAM), even though only k are used. A 47B parameter Mixtral needs 47B worth of GPU memory, not 12B.

3. **"More experts always means better quality."** Not necessarily. With too many experts, the router becomes the bottleneck and load balancing becomes harder. DeepSeek-V3 uses 256 experts; Mixtral uses 8. The sweet spot depends on the task.

4. **"MoE is only for language models."** No. MoE has been applied to vision (Vision MoE), speech, and multimodal models. Anywhere you have a large FFN layer, you can replace it with an MoE layer.

5. **"MoE makes fine-tuning easier because there are fewer active parameters."** Actually the opposite. MoEs overfit more easily than dense models. The sparse activation creates noisy gradients during fine-tuning. You typically need higher dropout, smaller batch sizes, and sometimes you freeze the non-expert layers.

---

### Where It Is Used in Our Code

`src/phase33/phase33_moe.py` — Demonstrates a tiny MoE layer with 4 experts, top-2 routing, and load balancing. Compares parameter count vs. active compute against a dense baseline.
