## What Is CUDA?

---

### The Problem

Training a neural network requires millions of identical arithmetic operations. A CPU has only 8-64 cores and is optimized for sequential, complex tasks; it would take weeks to train a modern model. GPUs have thousands of simple cores, but they need a specialized programming model to use them effectively. Writing GPU code in assembly or raw hardware instructions is nearly impossible for developers.

---

### Definition

**CUDA** (Compute Unified Device Architecture) is NVIDIA's parallel computing platform and programming model. It extends C/C++ with keywords like `__global__` so developers can write functions ("kernels") that run simultaneously on thousands of GPU threads.

**How it works:**
```
Base program: sequential C++ loop over 1M elements
CUDA version: write a __global__ kernel that handles one element per thread
Launch: 1024 blocks * 1024 threads = 1,048,576 threads run in parallel
Result: the loop completes in microseconds instead of milliseconds
```

**Key concepts:**
- **Threads:** the smallest unit of execution; one thread handles one data element.
- **Blocks:** groups of threads (typically 256-1024) that share fast shared memory.
- **Warps:** groups of 32 threads that execute the same instruction in lockstep.
- **Grids:** the collection of all blocks launched for a kernel.

**Why this matters:**
- A CPU might process 8 elements at a time; a GPU processes 1,048,576 simultaneously.
- Matrix multiplication, convolution, and element-wise ops all map naturally to the CUDA thread hierarchy.
- Without CUDA (or an equivalent), GPUs remain inaccessible black boxes.

---

### Real-Life Analogy

Imagine a single master craftsperson building a house alone versus a thousand interns each painting one fence picket at the same time. The master is better at complex decisions, custom cuts, and problem-solving; the interns win when there are millions of identical, simple tasks. CUDA is the instruction manual that tells each intern exactly which picket to paint and what color to use, all at once.

The trade-off is flexibility. If the fence suddenly needs curved pickets, the master adapts immediately while the interns panic because their instructions assumed straight lines. Similarly, CUDA cores struggle with branching code; if threads in the same warp take different paths, the GPU serializes execution. You gain massive throughput for uniform workloads but lose efficiency when the workload becomes irregular or deeply sequential.

---

### Tiny Numeric Example

Adding two vectors of 1,048,576 floats:

| Approach | Threads | Time |
|---|---|---|
| CPU (single core) | 1 | ~20 ms |
| CPU (8 cores) | 8 | ~2.5 ms |
| GPU (CUDA, 1024 blocks x 1024 threads) | 1,048,576 | ~0.02 ms |

The GPU is roughly 100x faster than the multi-core CPU for this task. Not because each CUDA thread is faster -- each is actually much simpler and slower than a CPU core -- but because all one million threads run in parallel. The arithmetic per thread is trivial (one addition), so the bottleneck is launching enough threads to hide memory latency.

---

### Common Confusion

1. **"CUDA is a programming language."** No. It is an extension to C/C++. You still write C++ code with a few extra keywords like `__global__` and `__shared__`.

2. **"CUDA works on any GPU."** No. CUDA is proprietary to NVIDIA GPUs. AMD uses ROCm; Apple uses Metal; Intel uses oneAPI.

3. **"More CUDA threads always means faster code."** No. Performance is limited by memory bandwidth, register count, and occupancy. Launching too many threads can slow things down if they stall waiting for global memory.

4. **"A CUDA kernel is an operating system kernel."** No. In CUDA, a kernel is simply a function that runs on the GPU. It has nothing to do with OS kernels that manage hardware resources.

5. **"CUDA cores are like CPU cores."** No. A CPU core is complex, handles branching well, and operates independently. A CUDA core is extremely simple and must run in lockstep with other cores in the same warp.

6. **"You need CUDA for all GPU programming."** No. OpenCL, Vulkan Compute, and WebGPU are alternatives, but CUDA is the most mature ecosystem for deep learning.

---

### Where It Is Used in Our Code

`src/phase83/phase83_gpu_kernels.py` -- We simulate the concept of a CUDA kernel with a Python `vector_add_kernel()` function that loops over elements exactly as a real CUDA kernel would, except a real kernel has no explicit loop because each thread handles one index automatically. We also benchmark coalesced versus strided memory access patterns to show why GPU memory behavior matters.
