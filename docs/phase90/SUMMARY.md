# Phase 90: vLLM, TensorRT-LLM & Inference Serving

## What We Learned

1. **Memory fragmentation in the KV cache is the serving bottleneck, not compute.** GPUs often sit idle not because they lack FLOPs, but because poor memory allocation prevents larger batches or longer sequences from fitting.
2. **PagedAttention treats GPU memory like virtual memory.** By splitting the KV cache into fixed-size blocks allocated on demand, it eliminates external fragmentation and raises utilization from under 20% to over 95%.
3. **Continuous batching keeps the GPU fully utilized.** Dynamically backfilling finished requests with new ones avoids the idle slots that plague static batching when sequence lengths vary.
4. **KV cache management is a systems problem, not just an algorithmic one.** Techniques like quantization, CPU offloading, and prefix sharing all trade memory, latency, and quality to squeeze more throughput from limited hardware.
5. **These innovations compound.** PagedAttention enables the memory efficiency that continuous batching needs to backfill slots without running out of space. Together they transform naive serving into production-grade throughput.
6. **Serving cost scales directly with memory efficiency.** A 4x improvement in cache utilization translates to roughly 4x more concurrent users on the same GPU, which directly lowers per-request serving costs.

## Prerequisites

- Solid understanding of transformer attention mechanism and autoregressive generation
- Familiarity with GPU memory architecture and memory fragmentation
- Basic knowledge of operating-system virtual memory and paging
- Completion of Phase 89 (data pipelines) is helpful but not required

## Recommended Reading Order

1. `what_is_kv_cache_management.md` — Understand the memory problem and baseline management techniques
2. `what_is_pagedattention.md` — Learn the block-based allocation solution that solves fragmentation
3. `what_is_continuous_batching.md` — See how dynamic request scheduling maximizes GPU utilization on top of efficient memory management

## Visual Outputs

- `src/phase90/kv_cache_fragmentation.png` — Line plot comparing fragmentation ratio over 50 timesteps for naive contiguous allocation versus PagedAttention block-based allocation.

## Navigation

- [Previous Phase](../phase89/SUMMARY.md)
- [Next Phase](../phase91/SUMMARY.md)
