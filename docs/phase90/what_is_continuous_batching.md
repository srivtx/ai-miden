# What is Continuous Batching?

## Why it exists (THE PROBLEM first)

Traditional static batching waits for every sequence in a batch to finish generating before accepting new requests. If one sequence generates 500 tokens and another generates 50, the short sequence's GPU sits idle for 450 steps while the long one finishes. This wastes massive amounts of compute.

## Definition (very simple)

Continuous batching (also called in-flight batching) dynamically adds new requests to the GPU batch as soon as older requests finish, without waiting for the entire original batch to complete.

## Real-life analogy

A restaurant with static seating waits for an entire table of four to finish eating before seating a new party, even if three guests left an hour ago. Continuous batching is like a buffet: individual guests arrive, eat, and leave independently, and the restaurant fills seats continuously.

## Tiny numeric example

A batch of 4 requests starts. After 10 generation steps, 2 requests finish (they reached their stop token). With static batching, the GPU continues with only 2 active sequences for the next 100 steps. With continuous batching, 2 brand-new requests join the batch immediately, keeping the GPU at full utilization.

## Common confusion

- **Continuous batching is not larger batch sizes.** It is about when requests enter and leave the batch, not about how many fit at peak.
- **It does not remove the need for padding.** Requests still need alignment, but new requests can be padded to the current batch length rather than a fixed maximum.
- **It is not only for inference.** The same concept applies in data-loading pipelines.
- **Continuous batching does not guarantee full GPU utilization.** If traffic is sparse, the batch may still shrink.
- **It is harder to implement than static batching.** The scheduler must manage KV cache block allocation and attention mask updates every step.

## Where it is used in our code

In `src/phase90/phase90_inference_serving.py`, our time-step simulation shows active requests arriving and departing. While we focus on memory fragmentation, the higher utilization enabled by PagedAttention directly supports continuous batching: freed blocks can be reassigned to new requests immediately.
