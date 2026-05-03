## What Is Expert Choice?

---

## The Problem

In a standard Mixture of Experts model, each token selects its top-k favorite experts. This seems democratic, but it creates a tragedy of the commons: a few "star" experts become wildly popular while the majority sit idle. To prevent overflow, engineers add a capacity factor and pad underloaded experts with dummy tokens. The result is wasted compute, fragmented memory, and a routing mechanism that optimizes token preference instead of global efficiency. A batch of 512 tokens might send 340 to Expert 0, 280 to Expert 1, and only 20 to Expert 7, leaving Expert 7's specialized knowledge permanently untapped.

---

## Definition

**Expert Choice** is an alternative routing strategy where each expert selects its top-k tokens, rather than each token selecting its top-k experts. This inverts the decision logic: instead of tokens voting for experts, experts compete for tokens. It guarantees a fixed number of tokens per expert, eliminates the need for capacity padding, and naturally balances the computational load.

**How it works:**
```
Standard top-2 routing:
  Token 0 → Expert 3 (score 0.8), Expert 1 (score 0.6)
  Token 1 → Expert 3 (score 0.9), Expert 0 (score 0.5)
  ...
  Result: Expert 3 receives 340 tokens, Expert 7 receives 20 tokens.

Expert Choice (top-8 per expert):
  Expert 0 → picks tokens {12, 45, 67, ...} (8 tokens)
  Expert 1 → picks tokens {3, 89, 102, ...} (8 tokens)
  ...
  Expert 7 → picks tokens {5, 34, 201, ...} (8 tokens)
  Result: Every expert processes exactly 8 tokens. No padding.
```

**Key properties:**
- **Fixed load:** each expert receives exactly k tokens, so throughput is predictable.
- **No capacity factor:** there is no overflow, so no dummy tokens and no wasted FLOPs.
- **Token redundancy:** a single token can be chosen by multiple experts or by none, which must be handled in the aggregation step.

**Why this matters:**
- Hardware utilization becomes uniform; no GPU is overwhelmed while others wait.
- Memory fragmentation disappears because every expert block has the same shape.
- The model can safely use more experts because load imbalance is no longer a bottleneck.

---

## Real-Life Analogy

Imagine a university with 100 professors and 500 students. In the standard system, every student ranks their top-2 favorite professors and enrolls in their classes. The result is predictable: the charismatic lecturer in Intro to Psychology has 400 students in a 50-seat auditorium, while the niche expert in Sumerian grammar has two students and a half-empty seminar room. The university hires teaching assistants and builds overflow classrooms to handle the crowds, which costs money and dilutes quality.

**The Expert Choice approach:** Instead of students choosing professors, each professor hand-picks the 8 students whose research interests best match their expertise. Every seminar has exactly 8 students. No overflow rooms. No half-empty rooms. The Sumerian grammarian gets 8 highly motivated students who actually need her knowledge. The psychology lecturer gets 8 students who are genuinely interested in her specific subfield.

**The trade-off:** A brilliant student with broad interests might fall through the cracks if no professor's narrow filter selects them. Conversely, a mediocre student who happens to match a professor's keyword might get in. And if every professor wants the same 8 "star" students, the system degenerates into a different kind of competition. Expert Choice is not magic; it is a design decision that trades token autonomy for load uniformity.

---

## Tiny Numeric Example

**Routing a batch of 128 tokens across 8 experts with top-2 vs. Expert Choice:**

| Expert | Standard Top-2 Load | Expert Choice Load | Standard Padding Waste |
|---|---|---|---|
| 0 | 42 tokens | 16 tokens | 18% |
| 1 | 38 tokens | 16 tokens | 16% |
| 2 | 22 tokens | 16 tokens | 5% |
| 3 | 18 tokens | 16 tokens | 2% |
| 4 | 5 tokens | 16 tokens | 35% (underflow) |
| 5 | 3 tokens | 16 tokens | 39% (underflow) |
| 6 | 1 token | 16 tokens | 47% (underflow) |
| 7 | 1 token | 16 tokens | 47% (underflow) |

**Token fate in Expert Choice:**
```
Chosen by 2 experts:    45 tokens (gain diverse processing)
Chosen by 1 expert:     68 tokens (standard path)
Chosen by 0 experts:    15 tokens (must be handled by residual or baseline)
```

**Compute efficiency:**
```
Standard top-2:   capacity factor 1.25, effective utilization 72%
Expert Choice:    no capacity factor, effective utilization 100%
Speedup on 8-GPU system: 1.18x
```

**The shift:** Standard routing optimizes for token preference and pays in load imbalance. Expert Choice optimizes for hardware efficiency and pays in token coverage. The choice depends on whether your bottleneck is memory fragmentation or model quality.

---

## Common Confusion

1. **"Expert Choice eliminates the need for load balancing entirely."** It eliminates load imbalance caused by token routing, but if the same tokens are always chosen by all experts, the model may still fail to specialize. Diversity of selection matters.

2. **"Expert Choice is always better than token-choice routing."** It is better for hardware efficiency but can hurt model quality if important tokens are not selected by any expert. The optimal strategy depends on the task.

3. **"Expert Choice changes the attention formula."** It changes only the routing assignment. The expert computation and the aggregation logic remain identical to standard MoE.

4. **"Every token is guaranteed to be selected by at least one expert."** No. A token can be chosen by zero experts if no expert ranks it in their top-k. The system needs a fallback path for orphan tokens.

5. **"Expert Choice requires fewer experts."** Actually, it shines with many experts because standard routing would collapse into extreme imbalance. With only 4 experts, the advantage is marginal.

6. **"Expert Choice is harder to implement than token-choice routing."** It requires a different sorting operation (per-expert instead of per-token) but removes the capacity padding logic, which often simplifies the overall pipeline.

7. **"Expert Choice is only for transformer MoE layers."** The principle applies to any modular system where items must be assigned to workers: recommendation systems, distributed databases, and task scheduling queues can all use inverted assignment.

---

## Where It Is Used in Our Code

`src/phase96/phase96_moe.py` — We implement a tiny MoE layer with both standard token-choice routing and Expert Choice routing. We simulate a batch of tokens, compute the routing matrices for both strategies, and compare expert load distributions. We print the load per expert and plot the histograms so you can see how Expert Choice eliminates the hot-expert problem.
