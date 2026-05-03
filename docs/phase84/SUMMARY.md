# Phase 84: Memory Engineering & Activation Checkpointing

## What We Learned

Training deep networks is not just about compute; it is about fitting data in limited GPU memory. This phase covered:

- **Activation Dominance:** In training, activations often consume more memory than model weights, especially for large batches and long sequences.
- **Activation Checkpointing:** Trading compute for memory by recomputing forward passes during backward. This allows deeper models or larger batches on the same hardware.
- **Gradient Accumulation:** Simulating large batch sizes by accumulating gradients across multiple micro-batches before updating weights.
- **Memory Bandwidth:** The true bottleneck for many kernels. Reducing memory traffic is often more valuable than increasing FLOPS.

## Key Terms

- Activation Checkpointing
- Gradient Accumulation
- Memory Bandwidth

## Code Files

- `src/phase84/phase84_memory_engineering.py` — NumPy demo showing memory usage with and without checkpointing and explaining gradient accumulation.

## Connections to Previous Phases

- Phase 83 introduced GPU kernels and memory hierarchy. This phase applies those concepts to training-specific memory problems.
- Phase 82 discussed CPU optimization; GPU memory engineering is the natural next step for scaling up.

## Navigation

← Previous: Phase 83 | Next: Phase 85 →
