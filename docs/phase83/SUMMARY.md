# Phase 83: GPU Kernel Optimization (CUDA)

## What We Learned

Modern deep learning runs on GPUs, not CPUs. This phase explained why:

- **SIMT Execution:** GPUs use Single Instruction, Multiple Thread execution. Thousands of threads run the same instruction on different data simultaneously.
- **Warps:** Threads are grouped into warps of 32. All threads in a warp execute the same instruction at the same time. Branch divergence within a warp serializes execution.
- **Occupancy:** The ratio of active warps to maximum possible warps. Low occupancy means cores sit idle.
- **Memory Bound vs Compute Bound:** If a kernel spends most of its time waiting for data, it is memory bound. If it spends most of its time calculating, it is compute bound. Element-wise ops are usually memory bound.
- **Coalesced Access:** When threads in a warp read consecutive memory addresses, the GPU fetches a single cache line for all of them. Strided or random access forces separate fetches.
- **Kernel Fusion:** Combining multiple operations into one kernel cuts memory traffic in half.

## Key Terms

- CUDA
- GPU Memory Hierarchy
- Kernel Fusion

## Code Files

- `src/phase83/phase83_gpu_kernels.py` — NumPy simulation of coalesced vs strided memory access timing and a conceptual vector-add kernel.

## Connections to Previous Phases

- Phase 82 covered CPU optimization and vectorization. GPUs take that idea to an extreme: instead of 8-wide SIMD, GPUs use 32-wide warps and thousands of threads.
- Phase 81 discussed continual learning; training larger continual learning models efficiently requires the GPU concepts from this phase.

## Navigation

← [Previous: Phase 81: Continual Learning](docs/phase81/SUMMARY.md) | [Next: Phase 84: Memory Engineering](docs/phase84/SUMMARY.md) →
