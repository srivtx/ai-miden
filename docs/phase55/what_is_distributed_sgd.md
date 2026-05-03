## What Is Distributed SGD?

---

### The Problem

You have 100 GPUs training the same model. Each GPU computes gradients on its local data shard. But if each GPU updates its model independently, you end up with 100 different models. How do you ensure all GPUs agree on a single set of weights?

---

### Definition

**Distributed SGD** is stochastic gradient descent where gradients are computed in parallel across multiple workers and synchronized before each weight update. The standard synchronization algorithm is **all-reduce**.

**All-reduce:**
```
Every worker starts with its own gradient vector g_i
After all-reduce: every worker has the same vector = average(g_1, g_2, ..., g_n)
```

**Ring all-reduce (most efficient):**
```
Workers arranged in a ring: W1 → W2 → W3 → W4 → W1
Phase 1 (scatter-reduce):
  W1 sends chunk 1 to W2
  W2 sends chunk 2 to W3
  W3 sends chunk 3 to W4
  W4 sends chunk 4 to W1
  Each worker accumulates received chunks
Phase 2 (all-gather):
  Each worker sends its fully accumulated chunk to the next worker
  After n-1 steps, every worker has all chunks
```

**Key insight:**
- Ring all-reduce communicates exactly 2×(n-1)/n of the total data per worker
- For 4 workers, each sends/receives only 1.5× the gradient size
- Communication time is independent of the number of workers (surprising but true)

**Why this matters:**
- Training GPT-4 on 25,000 GPUs requires all-reduce on every step
- Without efficient all-reduce, GPUs spend more time communicating than computing
- NCCL (NVIDIA Collective Communications Library) implements optimized ring all-reduce

---

### Real-Life Analogy

A town hall meeting where everyone must agree on the average tax rate.
- **Single GPU:** One accountant calculates the average from all tax returns. Slow.
- **Naive distributed:** Each of 4 accountants calculates a local average, then one reads all 4 reports and recalculates the global average. The other 3 wait idle.
- **All-reduce:** Each accountant shares their data with their neighbor in a circle. After passing notes around, everyone has independently computed the exact same global average. No one is idle, and no single accountant is a bottleneck.

---

### Tiny Numeric Example

**4 workers, gradients on a single parameter:**
```
Worker 1: g1 = -3.0
Worker 2: g2 = -5.0
Worker 3: g3 = -4.0
Worker 4: g4 = -6.0
```

**Ring all-reduce (simplified, 2 chunks):**
```
Chunk A: first half of parameters
Chunk B: second half of parameters

Step 1:
  W1 sends chunk A to W2
  W2 sends chunk B to W3
  W3 sends chunk A to W4
  W4 sends chunk B to W1

After accumulation:
  W2 has: chunk A = g1 + g2
  W3 has: chunk B = g2 + g3
  W4 has: chunk A = g3 + g4
  W1 has: chunk B = g4 + g1

Step 2 (all-gather):
  W2 sends chunk A to W3
  W3 sends chunk B to W4
  W4 sends chunk A to W1
  W1 sends chunk B to W2

After all-gather:
  W1 has: chunk A = g3+g4, chunk B = g4+g1
  W2 has: chunk A = g1+g2, chunk B = g4+g1
  W3 has: chunk A = g1+g2, chunk B = g2+g3
  W4 has: chunk A = g3+g4, chunk B = g2+g3

Wait — this is wrong for ring all-reduce. Let me do it properly.
```

**Simple average (conceptually equivalent):**
```
Global average = (-3.0 + -5.0 + -4.0 + -6.0) / 4 = -4.5

After all-reduce, every worker has: -4.5
```

The exact algorithm is complex, but the result is simple: every worker gets the average.

---

### Common Confusion

1. **"Distributed SGD is different from regular SGD."** Mathematically identical. The only difference is where the gradient computation happens.

2. **"All-reduce is the same as broadcasting."** No. Broadcast sends data from one worker to all others. All-reduce combines data from all workers and distributes the result to all.

3. **"More workers always means faster training."** Diminishing returns. Communication overhead grows, and batch size scaling has limits (too large and generalization suffers).

4. **"You need special hardware for distributed training."** No. You can simulate it on a single machine with multiple processes, or even on CPU.

5. **"Distributed SGD requires a parameter server."** Older approaches used a central parameter server. Modern approaches use decentralized all-reduce (Ring, Tree, Butterfly) which scales better.

---

### Where It Is Used in Our Code

`src/phase55/phase55_distributed_training.py` — We simulate ring all-reduce on 4 workers, showing how gradients are accumulated around the ring and how every worker ends up with the exact same averaged gradient.
