# Phase 85: NCCL, InfiniBand & Multi-Node Training

## What We Learned

Training at scale requires more than one GPU. This phase covered how multiple GPUs cooperate:

- **Data Parallelism:** Replicating the model across GPUs and splitting the batch. The simplest way to scale training throughput.
- **All-Reduce:** The critical collective operation that averages gradients across all GPUs so model copies stay synchronized.
- **Ring-Allreduce:** An algorithm that avoids a central bottleneck by passing chunks around a ring. It is bandwidth-optimal because every link is fully utilized.
- **Collective Communication:** Standardized patterns (broadcast, all-gather, reduce-scatter) that replace chaotic point-to-point messaging with efficient, structured algorithms.
- **Bandwidth vs Latency:** For large tensors (deep learning gradients), bandwidth dominates. For small messages, latency dominates.

## Key Terms

- All-Reduce
- Data Parallelism
- Collective Communication

## Code Files

- `src/phase85/phase85_multi_node.py` — NumPy simulation of ring-allreduce on a small tensor across 4 ranks.

## Connections to Previous Phases

- Phase 84 covered memory engineering for a single GPU. This phase scales to multiple GPUs.
- Phase 83 explained GPU kernel execution. Multi-node training is simply many GPUs running kernels and then synchronizing via collectives.

## Navigation

← Previous: Phase 84 | Next: Phase 86 →
