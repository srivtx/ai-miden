## What Is Expert Capacity?

---

### The Problem

Your router sends 90% of tokens to Expert 3. Even with load balancing loss, some imbalance persists. Expert 3 gets swamped with work while Experts 0, 1, and 2 sit idle. On a GPU, this means one compute unit is maxed out while others are wasted. How do you prevent any single expert from becoming a bottleneck?

---

### Definition

**Expert capacity** is a hard limit on how many tokens each expert can process in a single batch. It is calculated as:
```
Expert Capacity = (tokens_per_batch / num_experts) × capacity_factor
```

The **capacity factor** (CF) is a hyperparameter:
- **CF = 1.0:** Perfectly even distribution, no buffer
- **CF = 1.25:** 25% buffer for natural imbalance (common default)
- **CF = 2.0:** Lots of buffer, but more memory and compute

Tokens that exceed an expert's capacity are "dropped." They skip the expert layer and pass through via a residual connection.

---

### Real-Life Analogy

A highway with toll booths. There are 8 booths, and cars are routed to specific booths based on their license plate (the router). Without capacity limits, all cars might pile up at Booth 3. With capacity limits, each booth can only process 50 cars per hour. Car 51 at Booth 3 is redirected to the express lane (residual connection) and skips the booth entirely. The express lane ensures no one is completely stuck, but they also miss the specialized service the booth provides.

---

### Tiny Numeric Example

**Batch size:** 8 tokens
**Number of experts:** 4
**Capacity factor:** 1.25

**Step 1 — Calculate capacity per expert:**
```
Capacity = (8 / 4) × 1.25 = 2 × 1.25 = 2.5
```

Since we cannot process half a token, we round up or down. In practice, capacities are often left as floats and compared against counts. Let us use `capacity = 2.5`.

**Step 2 — Router assigns tokens:**
```
Token 0 → Expert 2
Token 1 → Expert 2
Token 2 → Expert 2
Token 3 → Expert 1
Token 4 → Expert 2
Token 5 → Expert 3
Token 6 → Expert 0
Token 7 → Expert 2
```

**Step 3 — Count tokens per expert:**
```
Expert 0: 1 token (Token 6) → within capacity ✓
Expert 1: 1 token (Token 3) → within capacity ✓
Expert 2: 5 tokens (Tokens 0,1,2,4,7) → over capacity! ⚠️
Expert 3: 1 token (Token 5) → within capacity ✓
```

**Step 4 — Drop excess tokens at Expert 2:**
Expert 2 can only process 2.5 tokens. Tokens 0 and 1 are processed. Token 2 is dropped (goes through residual). Token 4 is dropped. Token 7 is dropped.

**Result:** 3 tokens skipped the expert layer. They still get the input added back via the residual connection, so the network does not crash. But they miss the expert's transformation.

---

### Common Confusion

1. **"Dropped tokens destroy model quality."** A few dropped tokens are fine. With CF = 1.25 and a well-trained router, the drop rate is usually under 1%. Even with some drops, MoE outperforms dense models of equivalent compute.

2. **"Higher capacity factor is always better."** Not quite. Higher CF means more memory (you need buffer space for all those tokens) and more compute (experts process more tokens). CF = 2.0 uses twice the memory of CF = 1.0. The sweet spot is typically 1.0–1.5.

3. **"Capacity factor is the same as load balancing loss."** No. Load balancing loss is a soft incentive (the optimizer tries to minimize it). Capacity factor is a hard limit (tokens are literally dropped). You typically use both.

4. **"Expert capacity only matters for training."** It matters more for training, but it also affects inference. At inference, you want CF just high enough that you never drop tokens. Some systems use dynamic capacity: monitor drop rate and adjust CF.

5. **"All experts must have the same capacity."** In standard MoE, yes. But some variants (like Expert Choice Routing) flip the problem: each expert picks its top-C favorite tokens. This naturally balances load without explicit capacity limits.

---

### Where It Is Used in Our Code

`src/phase33/phase33_moe.py` — The `moe_forward()` function implements expert capacity. When tokens are dispatched to experts, it counts how many each expert receives and drops excess tokens. The drop count is printed so you can see when imbalance occurs.
