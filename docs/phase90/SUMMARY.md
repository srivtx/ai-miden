# Phase 90: vLLM, TensorRT-LLM & Inference Serving

## What we covered

- **PagedAttention:** Block-based KV cache allocation that eliminates memory fragmentation.
- **Continuous Batching:** Dynamically adding and removing requests from the GPU batch to maximize utilization.
- **KV Cache Management:** Storing and reusing key/value tensors efficiently during generation.

## Why this matters

Inference serving is where models meet users. Slow or memory-inefficient serving means higher latency, lower throughput, and bigger GPU bills. PagedAttention and continuous batching are the core innovations that let modern serving engines handle far more concurrent users than naive implementations.

## Key takeaways

1. Memory fragmentation in the KV cache is the bottleneck, not compute.
2. PagedAttention treats GPU memory like virtual memory, allocating fixed-size blocks on demand.
3. Continuous batching plus paging unlocks high throughput without wasting GPU cycles.

## Navigation

- [Previous Phase](../phase89/SUMMARY.md)
- [Next Phase](../phase91/SUMMARY.md)
