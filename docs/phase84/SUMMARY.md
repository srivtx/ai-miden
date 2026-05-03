# Phase 84: Memory Engineering & Activation Checkpointing

## What We Learned

Training deep networks is not just about compute; it is about fitting data in limited GPU memory. This phase covered:

- **Activation Dominance:** In training, activations often consume more memory than model weights, especially for large batches and long sequences. A 100-layer transformer can use 40 GB of activations on a 24 GB GPU.
- **Activation Checkpointing:** Trading compute for memory by recomputing forward passes during backward. This allows deeper models or larger batches on the same hardware, typically at a 30-50% compute overhead.
- **Gradient Accumulation:** Simulating large batch sizes by accumulating gradients across multiple micro-batches before updating weights. It preserves the statistical benefits of large batches without requiring the memory to hold them all at once.
- **Memory Bandwidth:** The true bottleneck for many kernels. Reducing memory traffic through fusion, checkpointing, or coalesced access is often more valuable than increasing FLOPS.

## Prerequisites

- Phase 83: GPU Kernel Optimization (CUDA)
- Phase 82: CPU Optimization and Vectorization

## Recommended Reading Order

1. `what_is_memory_bandwidth.md` -- Understand why memory bandwidth is the hidden ceiling on GPU performance.
2. `what_is_activation_checkpointing.md` -- Learn how to trade compute for memory by saving selective checkpoints.
3. `what_is_gradient_accumulation.md` -- See how to simulate large batches on limited hardware.

## Visual Outputs

- `src/phase84/memory_checkpointing.png` -- Bar chart comparing peak activation memory with and without checkpointing every 2 layers.

## Key Terms

- Activation Checkpointing
- Gradient Accumulation
- Memory Bandwidth

## Code Files

- `src/phase84/phase84_memory_engineering.py` -- NumPy demo showing memory usage with and without checkpointing and explaining gradient accumulation.

## Connections to Previous Phases

- Phase 83 introduced GPU kernels and memory hierarchy. This phase applies those concepts to training-specific memory problems.
- Phase 82 discussed CPU optimization; GPU memory engineering is the natural next step for scaling up.

## Navigation

[Previous: Phase 83: GPU Kernel Optimization](docs/phase83/SUMMARY.md) | [Next: Phase 85: Multi-Node Training](docs/phase85/SUMMARY.md)
