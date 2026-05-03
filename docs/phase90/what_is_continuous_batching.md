## What Is Continuous Batching?

---

## The Problem

Traditional static batching waits for every sequence in a batch to finish generating before accepting new requests. If one sequence generates 500 tokens and another generates 50, the short sequence's GPU sits idle for 450 steps while the long one finishes. This wastes massive amounts of compute and keeps users waiting for no reason.

---

## Definition

**Continuous batching** (also called in-flight batching) dynamically adds new requests to the GPU batch as soon as older requests finish, without waiting for the entire original batch to complete.

**How it works:**
```
Initialization:
  1. Batch starts with N active requests
  2. Each request has its own KV cache blocks and attention mask

Each generation step:
  1. Run forward pass on current batch
  2. Check which requests produced an end-of-sequence token
  3. Remove finished requests from the batch
  4. Immediately pull new requests from the waiting queue
  5. Pad new requests to current batch length or use prefix caching
  6. Update attention masks and block tables
  7. Repeat until queue is empty and all active requests finish
```

**Why this matters:**
- In static batching, a batch of 4 with 2 short and 2 long sequences wastes ~50% of GPU cycles on idle slots.
- Continuous batching keeps the GPU at full utilization by backfilling finished slots with new requests.
- Serving engines like vLLM and TensorRT-LLM rely on continuous batching to maximize throughput under real-world request distributions.

---

## Real-Life Analogy

A restaurant with static seating waits for an entire table of four to finish eating before seating a new party, even if three guests left an hour ago. Continuous batching is like a buffet: individual guests arrive, eat, and leave independently, and the restaurant fills seats continuously.

Imagine a taxi stand at an airport. In the static model, a dispatcher sends four taxis as a batch to a group of travelers. If three travelers are going to nearby hotels and one is going to a distant suburb, the three taxis return to the stand and wait for the fourth to come back before accepting new passengers. In the continuous model, each taxi leaves as soon as its passenger is seated. When a taxi returns, it immediately picks up the next traveler in line. The stand serves far more passengers per hour because no vehicle sits idle waiting for a slow trip to finish. Continuous batching in inference engines works the same way: GPU slots are taxis, and requests are passengers.

**The trade-off:** Continuous batching is harder to implement than static batching. The scheduler must manage KV cache block allocation and attention mask updates every step. The added complexity pays off only when request lengths vary significantly and traffic is bursty.

---

## Tiny Numeric Example

**Static batching over 100 generation steps:**

| Step | Active Requests | Notes |
|------|-----------------|-------|
| 1-10 | 4 | All generating |
| 11 | 2 | 2 finished (50 tokens each) |
| 12-100 | 2 | 2 remaining (500 tokens each); GPU 50% idle |
| 101 | 0 | Batch complete; new batch starts |

- Total tokens generated: 2 × 50 + 2 × 500 = 1,100
- GPU-active token steps: 4 × 10 + 2 × 90 = 580
- GPU-idle token steps: 2 × 90 = 180
- Utilization: 580 / (4 × 100) = 72.5%

**Continuous batching over 100 generation steps:**

| Step | Active Requests | Notes |
|------|-----------------|-------|
| 1-10 | 4 | All generating |
| 11 | 4 | 2 finished, 2 new requests join immediately |
| 12-100 | 4 | Backfilled slots keep GPU full |

- Total tokens generated: 2 × 50 + 2 × 500 + 2 × 50 + 2 × 500 = 2,200 (twice the throughput)
- GPU-active token steps: 4 × 100 = 400
- GPU-idle token steps: 0
- Utilization: 100%

---

## Common Confusion

1. **"Continuous batching is larger batch sizes."** It is not. It is about when requests enter and leave the batch, not about how many fit at peak. The peak size may be identical; the difference is that slots refill dynamically.

2. **"It removes the need for padding."** It does not. New requests still need alignment, but they can be padded to the current batch length rather than a fixed maximum.

3. **"It is only for inference."** The same concept applies in data-loading pipelines, where workers refill batches as samples are consumed.

4. **"Continuous batching guarantees full GPU utilization."** It does not. If traffic is sparse, the batch may still shrink because there are no waiting requests to backfill.

5. **"It is harder to implement than static batching."** It is. The scheduler must manage KV cache block allocation and attention mask updates every step, which adds significant engineering complexity.

6. **"Continuous batching improves latency for every request."** It improves system throughput and average latency, but a single long-running request still takes the same number of steps to complete.

7. **"Any inference engine can add continuous batching easily."** It requires deep changes to the serving stack, including dynamic memory management and attention kernel modifications.

---

## Where It Is Used in Our Code

`src/phase90/phase90_inference_serving.py` — Our time-step simulation shows active requests arriving and departing. While we focus on memory fragmentation, the higher utilization enabled by PagedAttention directly supports continuous batching: freed blocks can be reassigned to new requests immediately, which is exactly what a continuous batching scheduler needs to backfill the batch without waiting.
