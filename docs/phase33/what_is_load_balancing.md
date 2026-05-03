## What Is Load Balancing?

---

### The Problem

You have 8 experts in your MoE layer. During training, the router naturally discovers that Expert 3 is slightly better than the others early on. So it starts sending almost all tokens to Expert 3. The other 7 experts never get trained and remain useless. Expert 3 becomes overloaded. The model collapses into a de-facto dense network with one expert. How do you force the router to distribute work evenly?

---

### Definition

**Load balancing** in MoE is the set of techniques that prevent the router from collapsing to a small subset of experts. The two main approaches are:

1. **Auxiliary load balancing loss:** A penalty term added to the training loss that rewards evenly distributed expert usage.
2. **Expert capacity:** A hard cap on how many tokens each expert can process per batch. Excess tokens are dropped.

The most common auxiliary loss (from the original Shazeer et al. 2017 paper) is:
```
L_balance = num_experts × sum(f_i × P_i)
```
Where `f_i` is the fraction of tokens sent to expert `i`, and `P_i` is the average routing probability for expert `i`. When usage is balanced, `f_i ≈ 1/num_experts` and `P_i ≈ 1/num_experts`, so the loss is minimized.

---

### Real-Life Analogy

A school principal notices that all students are signing up for Mr. Smith's math class because he has a reputation for being easy. The other math teachers have empty classrooms. The principal introduces a rule: if a class exceeds 30 students, new sign-ups are redirected to other teachers. Additionally, teachers get a bonus when their class sizes are balanced. Soon, all teachers have reasonable class sizes and students get diverse instruction.

The "30 student cap" is expert capacity. The "balance bonus" is the auxiliary loss.

---

### Tiny Numeric Example

**Batch of 4 tokens routed to 4 experts:**

**Routing counts:**
- Expert 0: 0 tokens
- Expert 1: 1 token
- Expert 2: 3 tokens
- Expert 3: 0 tokens

**Fraction of tokens per expert (f):**
```
f = [0/4, 1/4, 3/4, 0/4] = [0.0, 0.25, 0.75, 0.0]
```

**Average routing probability per expert (P):**
Assume the router output these probabilities before top-k selection:
```
P = [0.05, 0.25, 0.60, 0.10]  (averaged across the 4 tokens)
```

**Load balancing loss:**
```
L_balance = num_experts × sum(f_i × P_i)
          = 4 × (0.0×0.05 + 0.25×0.25 + 0.75×0.60 + 0.0×0.10)
          = 4 × (0 + 0.0625 + 0.45 + 0)
          = 4 × 0.5125
          = 2.05
```

**Perfectly balanced case:**
```
f = [0.25, 0.25, 0.25, 0.25]
P = [0.25, 0.25, 0.25, 0.25]
L_balance = 4 × 4 × (0.25 × 0.25) = 4 × 0.25 = 1.0
```

Wait — the minimum is actually lower. Let us recalculate: `4 × (0.0625 + 0.0625 + 0.0625 + 0.0625) = 4 × 0.25 = 1.0`. The perfectly balanced loss is 1.0, and our imbalanced loss is 2.05. The optimizer will push toward 1.0.

**Total loss:**
```
L_total = L_task + α × L_balance
```
Where `α` is a small constant (typically 0.01). The task loss is what we actually care about (e.g., next-token prediction). The balance loss is just a regularizer.

---

### Common Confusion

1. **"Load balancing loss hurts model quality."** Not if `α` is small enough. The auxiliary loss is a tiny regularizer. Its purpose is to keep the system functional, not to maximize balance at all costs. Values like `α = 0.01` mean the balance term is 1% as important as the task.

2. **"Capacity factor means dropping data."** Yes, and that is intentional. If an expert is over capacity, excess tokens are skipped ("dropped"). This creates pressure on the router to distribute better. Dropped tokens are usually handled by passing them through a residual connection.

3. **"You only need load balancing at the start of training."** No, you need it throughout. Even well-trained routers can drift back to favoring a few experts as the data distribution shifts.

4. **"Load balancing ensures each expert learns a different specialty."** Not directly. It only ensures each expert gets *roughly equal usage*. What each expert actually learns depends on the data. In practice, experts do specialize (e.g., one expert for syntax, one for facts), but that emerges organically, not from the loss.

5. **"There is only one way to do load balancing."** Many variants exist: Switch Transformers use a simplified `f_i × P_i` loss; ST-MoE adds a "router z-loss" that penalizes large logits for stability; some approaches use expert choice routing (tokens choose experts, experts choose tokens).

---

### Where It Is Used in Our Code

`src/phase33/phase33_moe.py` — The `compute_load_balance_loss()` function calculates the auxiliary loss. You can see it in action in the training loop, where the total loss is `task_loss + 0.01 × balance_loss`. The plot `moe_load_balancing.png` shows how expert usage becomes more even over training iterations.
