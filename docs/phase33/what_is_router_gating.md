## What Is Router Gating?

---

### The Problem

You have 8 experts in your MoE layer. For each input token, you need to decide which 1 or 2 experts should process it. How do you make this decision? And how do you make it learnable so the model figures out which experts should specialize in which types of inputs?

---

### Definition

**Router gating** is the mechanism that assigns each input token to a subset of experts. It is a small neural network (usually just a linear projection) that takes the token's hidden state and outputs a score for each expert. The highest-scoring experts are selected, and their outputs are combined using a weighted sum.

The most common form is **Noisy Top-K Gating:**
```
logits = (x · W_g) + noise
selected_experts = top_k(logits, k)
gate_values = softmax(selected_logits)
output = sum(gate_i × expert_i(x))
```

---

### Real-Life Analogy

A restaurant host stand. When a party arrives, the host quickly assesses them (party size, dietary restrictions, preferred ambiance) and routes them to 1 or 2 specific chefs. The host's judgment is learned over time — they notice that vegetarian parties love Chef Maria's dishes, while steak lovers prefer Chef Antonio. The host is the "router," and their routing decision is the "gate."

---

### Tiny Numeric Example

**Input:** `x = [1.0, 0.5]` (a token's hidden state, 2D for simplicity)

**Router weights:** `W_g = [[0.1, 0.3, 0.5, 0.2], [-0.2, 0.4, 0.1, 0.6]]`

**Step 1 — Compute raw logits:**
```
logits = x · W_g
       = [1.0, 0.5] · W_g
       = [1.0×0.1 + 0.5×(-0.2), 1.0×0.3 + 0.5×0.4,
          1.0×0.5 + 0.5×0.1, 1.0×0.2 + 0.5×0.6]
       = [0.1 - 0.1, 0.3 + 0.2, 0.5 + 0.05, 0.2 + 0.3]
       = [0.0, 0.5, 0.55, 0.5]
```

**Step 2 — Add noise (prevents collapse early in training):**
```
noise = [0.02, -0.01, 0.03, -0.02]  (random Gaussian)
noisy_logits = [0.02, 0.49, 0.58, 0.48]
```

**Step 3 — Select top-2:**
```
Top 2: Expert 2 (0.58) and Expert 1 (0.49)
```

**Step 4 — Compute gate values (softmax over selected):**
```
gate_values = softmax([0.58, 0.49])
            = [exp(0.58)/(exp(0.58)+exp(0.49)), exp(0.49)/(exp(0.58)+exp(0.49))]
            = [1.786/(1.786+1.632), 1.632/(1.786+1.632)]
            = [0.523, 0.477]
```

So this token goes to Expert 2 with weight 0.523 and Expert 1 with weight 0.477.

**Why noise matters:**
Without noise, if Expert 2 happens to start with a slightly higher weight, it might get selected for everything. The noise forces exploration early in training so all experts get a chance to learn.

---

### Common Confusion

1. **"The router is a complex neural network."** Usually it is just a single linear layer. Its job is to produce a score per expert, not to deeply process the input. In some architectures (like Switch Transformers), the router is literally one matrix multiplication.

2. **"Top-k means k separate forward passes."** Yes, but they can be parallelized. In practice, tokens routed to the same expert are batched together. The router's decision happens once per token, then tokens are "dispatched" to their assigned experts.

3. **"The router is trained separately."** No. The router is trained end-to-end with the rest of the model via backpropagation. The gradients flow through the expert outputs back to the gate values, then to the router weights.

4. **"Softmax over all experts vs. softmax over top-k."** You can do either. Softmax over all experts (sparse gating) creates a weighted combination of all experts, but you still only compute the top-k. Softmax over top-k (switch-style) is simpler and works well in practice.

5. **"The router always converges to a good solution."** Not automatically. Without load balancing (see next doc), the router often collapses: 1-2 experts handle 90% of tokens and the rest are unused. Training becomes unstable.

---

### Where It Is Used in Our Code

`src/phase33/phase33_moe.py` — The `router_forward()` function computes logits, adds noise, selects top-k experts, and returns gate values. You can see the routing decisions visualized in the generated plots.
