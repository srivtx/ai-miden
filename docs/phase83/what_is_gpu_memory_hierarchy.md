# What Is GPU Memory Hierarchy?

## 1. Why it exists (THE PROBLEM first)

A GPU has thousands of cores, but they are useless without data. If every core had to read from slow main memory (global memory), most cores would sit idle waiting. To feed all those cores simultaneously, GPUs need a pyramid of memory types: tiny but instant registers, small but fast shared memory, and large but slower global memory. Without this hierarchy, the compute power of a GPU would be completely wasted.

## 2. Definition

**GPU Memory Hierarchy** is the layered storage system inside a GPU: registers (fastest, per-thread), shared memory/L1 cache (fast, shared by a block of threads), L2 cache (medium, shared by the whole chip), and global memory (slowest, large, accessible by all threads).

## 3. Real-life analogy

Think of cooking a meal. Registers are your hands and immediate attention (tiny capacity, instant). Shared memory is the countertop next to you (holds a few ingredients, very fast to reach). L2 cache is the kitchen pantry (a bit farther, still quick). Global memory is the grocery store warehouse across town (huge, but slow to access). A good chef keeps ingredients on the countertop; a bad chef runs to the warehouse for every single ingredient.

## 4. Tiny numeric example

Reading 1,024 floats:

- From registers: effectively 0 nanoseconds (already in the thread).
- From shared memory: ~1 nanosecond.
- From L2 cache: ~10 nanoseconds.
- From global memory: ~100-200 nanoseconds.

If a kernel reads data from global memory, does one addition, and writes back, 99% of the time is spent on memory, not math. That is why coalesced access and shared memory tiling matter so much.

## 5. Common confusion

- **"GPU global memory is the same as CPU RAM."** No. They are physically separate. Data must be copied from CPU RAM to GPU global memory over PCIe, which is another bottleneck.
- **"Shared memory is visible to all threads on the GPU."** No. Shared memory is only visible to threads within the same block (typically 256-1024 threads).
- **"Registers can be shared between threads."** No. Registers are private to each thread. You cannot read another thread's registers directly.
- **"L2 cache is bigger than global memory."** No. Global memory is gigabytes. L2 cache is tens of megabytes.
- **"Memory coalescing helps shared memory too."** No. Coalescing is specifically about global memory access patterns. Shared memory is banked differently.
- **"Unified memory is as fast as registers."** No. Unified memory still lives in global memory space. It is convenient but not magically faster.

## 6. Where it is used in our code

In `src/phase83/phase83_gpu_kernels.py`, we simulate coalesced versus strided global memory access patterns using NumPy. The simulation shows why sequential (coalesced) access is faster: it mimics the behavior of fetching contiguous cache lines from global memory, while strided access forces the memory controller to jump around, wasting bandwidth.
