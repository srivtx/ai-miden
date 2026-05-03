# Phase 83: GPU Kernel Optimization (CUDA)

## What We Learned

Modern deep learning runs on GPUs, not CPUs. This phase explained why:

- **SIMT Execution:** GPUs use Single Instruction, Multiple Thread execution. Thousands of threads run the same instruction on different data simultaneously, turning massive parallelism into practical speedups.
- **Warps and Divergence:** Threads are grouped into warps of 32. All threads in a warp execute the same instruction at the same time. Branch divergence within a warp serializes execution, wasting cycles.
- **GPU Memory Hierarchy:** Registers, shared memory, L2 cache, and global memory form a pyramid where speed decreases as capacity increases. Understanding this hierarchy is essential for writing fast kernels.
- **Coalesced Access:** When threads in a warp read consecutive memory addresses, the GPU fetches a single cache line for all of them. Strided or random access forces separate fetches, destroying bandwidth.
- **Kernel Fusion:** Combining multiple element-wise operations into one kernel cuts memory traffic in half by keeping intermediate values in registers instead of writing them to global memory.

## Prerequisites

- Phase 82: CPU Optimization and Vectorization
- Phase 81: Continual Learning

## Recommended Reading Order

1. `what_is_cuda.md` -- Understand the CUDA programming model and thread hierarchy.
2. `what_is_gpu_memory_hierarchy.md` -- Learn why memory layers matter and how to use them.
3. `what_is_kernel_fusion.md` -- See how fusion reduces bandwidth and why it is critical for element-wise ops.

## Visual Outputs

- `src/phase83/memory_access_patterns.png` -- Line plot comparing coalesced vs strided memory access timing across different array sizes.

## Key Terms

- CUDA
- GPU Memory Hierarchy
- Kernel Fusion

## Code Files

- `src/phase83/phase83_gpu_kernels.py` -- NumPy simulation of coalesced vs strided memory access timing and a conceptual vector-add kernel.

## Connections to Previous Phases

- Phase 82 covered CPU optimization and vectorization. GPUs take that idea to an extreme: instead of 8-wide SIMD, GPUs use 32-wide warps and thousands of threads.
- Phase 81 discussed continual learning; training larger continual learning models efficiently requires the GPU concepts from this phase.

## Navigation

[Previous: Phase 81: Continual Learning](docs/phase81/SUMMARY.md) | [Next: Phase 84: Memory Engineering](docs/phase84/SUMMARY.md)
