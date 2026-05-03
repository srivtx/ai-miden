# Phase 87: Checkpointing, Fault Tolerance & Determinism

## What We Learned

Training large models is expensive and time-consuming. This phase covered how to make training robust and reproducible:

- **Checkpointing:** Saving model weights, optimizer state, and RNG state to durable storage at regular intervals. A checkpoint every 10 epochs on a 100-epoch job limits maximum loss to 10 epochs of work.
- **Deterministic Training:** Fixing random seeds, data order, and algorithm flags so that experiments are reproducible bit-for-bit. This is essential for debugging and scientific validity.
- **Fault Tolerance:** Designing systems to detect failures and restart automatically from the latest checkpoint. In large clusters, failures are statistically inevitable, not exceptional.
- **Trade-offs:** Frequent checkpoints cost disk I/O and can stall GPUs. Deterministic algorithms can be 10-20% slower than nondeterministic ones. Fault tolerance infrastructure adds overhead but pays for itself after a single crash.

## Prerequisites

- Phase 86: JAX, XLA & TPU Programming
- Phase 85: NCCL, InfiniBand & Multi-Node Training
- Phase 84: Memory Engineering & Activation Checkpointing

## Recommended Reading Order

1. `what_is_checkpointing.md` -- Learn what to save and why it enables recovery.
2. `what_is_deterministic_training.md` -- Understand how to make experiments reproducible.
3. `what_is_fault_tolerance.md` -- See how checkpointing and monitoring combine into resilient systems.

## Visual Outputs

- `src/phase87/checkpoint_determinism.png` -- Line plot showing original weights and two deterministic update runs, verifying that checkpoint recovery produces identical trajectories.

## Key Terms

- Checkpointing
- Deterministic Training
- Fault Tolerance

## Code Files

- `src/phase87/phase87_checkpointing.py` -- Demonstrates checkpoint creation, simulated crash, deterministic recovery, and trajectory verification.

## Connections to Previous Phases

- Phase 86 introduced JIT compilation and XLA. Long compiled training runs benefit enormously from checkpointing because recompilation on restart is expensive.
- Phase 85 covered multi-node training. When one node in a large cluster fails, fault tolerance and checkpointing prevent the entire job from collapsing.

## Navigation

[Previous: Phase 86: JAX & TPU Programming](docs/phase86/SUMMARY.md) | [Next: Phase 88](docs/phase88/SUMMARY.md)
