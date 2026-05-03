# What Is CUDA?

## 1. Why it exists (THE PROBLEM first)

Training a neural network requires millions of identical arithmetic operations (matrix multiplications, additions). A CPU has only 8-64 cores and is optimized for sequential, complex tasks. It would take weeks to train a modern model on a CPU. GPUs have thousands of simple cores, but they need a specialized programming model to use them effectively. Writing GPU code in assembly or raw hardware instructions is nearly impossible for developers. CUDA exists to make massively parallel GPU programming accessible.

## 2. Definition

**CUDA** (Compute Unified Device Architecture) is NVIDIA's parallel computing platform and programming model. It extends C/C++ with keywords like `__global__` so developers can write functions ("kernels") that run simultaneously on thousands of GPU threads.

## 3. Real-life analogy

Imagine a single master craftsperson (CPU) building a house alone versus a thousand interns (GPU) each painting one fence picket at the same time. CUDA is the instruction manual that tells each intern exactly which picket to paint and what color to use, all at once. The master is better at complex decisions; the interns win when there are millions of identical, simple tasks.

## 4. Tiny numeric example

Adding two vectors of 1,048,576 floats:

- CPU (8 cores): processes 8 elements at a time sequentially. ~2 milliseconds.
- GPU (CUDA, 1024 threads per block, 1024 blocks): launches 1,048,576 threads, each adding one pair. ~0.02 milliseconds.

The GPU is 100x faster not because each thread is faster, but because all one million threads run in parallel.

## 5. Common confusion

- **"CUDA is a programming language."** No. It is an extension to C/C++. You still write C++ code with a few extra keywords.
- **"CUDA works on any GPU."** No. CUDA is proprietary to NVIDIA GPUs. AMD uses ROCm; Apple uses Metal.
- **"More CUDA threads always means faster code."** No. Performance is limited by memory bandwidth, register count, and occupancy. Launching too many threads can slow things down if they stall waiting for memory.
- **"A CUDA kernel is an operating system kernel."** No. In CUDA, a kernel is simply a function that runs on the GPU. It has nothing to do with OS kernels.
- **"CUDA cores are like CPU cores."** No. A CPU core is complex and handles branching well. A CUDA core is extremely simple and must run in lockstep with other cores in the same warp.
- **"You need CUDA for all GPU programming."** No. OpenCL, Vulkan Compute, and WebGPU are alternatives, but CUDA is the most mature for deep learning.

## 6. Where it is used in our code

In `src/phase83/phase83_gpu_kernels.py`, we simulate the concept of a CUDA kernel with a Python `vector_add_kernel()` function. It loops over elements exactly as a real CUDA kernel would, except a real kernel has no explicit loop because each thread handles one index automatically. We also discuss how SIMT execution and warps make real CUDA kernels fundamentally different from a Python loop, even though the math is identical.
