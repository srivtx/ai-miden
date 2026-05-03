# Phase 85: NCCL, InfiniBand & Multi-Node Training

## What We Learned

Training at scale requires more than one GPU. This phase covered how multiple GPUs cooperate:

- **Data Parallelism:** Replicating the model across GPUs and splitting the batch. It is the simplest way to scale training throughput, though it requires careful gradient synchronization.
- **All-Reduce:** The critical collective operation that averages gradients across all GPUs so model copies stay synchronized. Without it, replicas would diverge after one step.
- **Ring-Allreduce:** An algorithm that avoids a central bottleneck by passing chunks around a ring. It is bandwidth-optimal because every link is fully utilized and no single rank becomes a hotspot.
- **Collective Communication:** Standardized patterns (broadcast, all-gather, reduce-scatter) that replace chaotic point-to-point messaging with efficient, structured algorithms.
- **Bandwidth vs Latency:** For large tensors like deep learning gradients, bandwidth dominates communication time. For small messages, latency dominates, which affects scaling efficiency.

## Prerequisites

- Phase 84: Memory Engineering & Activation Checkpointing
- Phase 83: GPU Kernel Optimization (CUDA)

## Recommended Reading Order

1. `what_is_data_parallelism.md` -- Understand how to replicate models and split data across GPUs.
2. `what_is_all_reduce.md` -- Learn the specific collective that synchronizes gradients.
3. `what_is_collective_communication.md` -- Explore the broader family of communication patterns used in distributed systems.

## Visual Outputs

- `src/phase85/ring_chunks.png` -- Bar charts showing how a gradient tensor is split into chunks for ring-allreduce.
- `src/phase85/ring_topology.png` -- Diagram of the ring communication topology across ranks.

## Key Terms

- All-Reduce
- Data Parallelism
- Collective Communication

## Code Files

- `src/phase85/phase85_multi_node.py` -- NumPy simulation of ring-allreduce on a small tensor across 4 ranks.

## Connections to Previous Phases

- Phase 84 covered memory engineering for a single GPU. This phase scales to multiple GPUs.
- Phase 83 explained GPU kernel execution. Multi-node training is simply many GPUs running kernels and then synchronizing via collectives.

## Navigation

[Previous: Phase 84: Memory Engineering](docs/phase84/SUMMARY.md) | [Next: Phase 86: JAX & TPU Programming](docs/phase86/SUMMARY.md)
