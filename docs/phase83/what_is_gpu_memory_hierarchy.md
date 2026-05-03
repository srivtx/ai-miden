## What Is GPU Memory Hierarchy?

---

### The Problem

A GPU has thousands of cores, but they are useless without data. If every core had to read from slow main memory (global memory), most cores would sit idle waiting. To feed all those cores simultaneously, GPUs need a pyramid of memory types: tiny but instant registers, small but fast shared memory, and large but slower global memory. Without this hierarchy, the compute power of a GPU would be completely wasted.

---

### Definition

**GPU Memory Hierarchy** is the layered storage system inside a GPU: registers (fastest, per-thread), shared memory/L1 cache (fast, shared by a block of threads), L2 cache (medium, shared by the whole chip), and global memory (slowest, large, accessible by all threads).

**How it works:**
```
Thread starts: data is in global memory (slow)
Step 1: load a tile into shared memory (fast, shared by block)
Step 2: each thread copies its element into a register (instant)
Step 3: compute happens in registers
Step 4: write results back to shared memory, then to global memory
Result: most arithmetic happens at register speed, not global memory speed
```

**Key properties:**
- **Registers:** ~1 TB/s effective bandwidth, but only a few KB per thread.
- **Shared memory:** ~10 TB/s, but typically only 48-164 KB per block.
- **L2 cache:** ~2-5 TB/s, tens of megabytes, shared across the whole chip.
- **Global memory:** ~1-2 TB/s, gigabytes in size, but 100-200 ns latency.

**Why this matters:**
- A kernel that reads from global memory, does one addition, and writes back spends 99% of its time on memory, not math.
- Keeping data in registers or shared memory can speed up kernels by 10x or more.

---

### Real-Life Analogy

Think of cooking a meal in a professional kitchen. Registers are your hands and immediate attention: tiny capacity, instant access, but you can only hold so much at once. Shared memory is the countertop next to you: it holds a few ingredients, is very fast to reach, and everyone at your station can share it. L2 cache is the kitchen pantry just down the hall: still quick, but you have to walk there. Global memory is the grocery store warehouse across town: huge and comprehensive, but slow to access.

A good chef keeps ingredients on the countertop and works with their hands; a bad chef runs to the warehouse for every single ingredient. The trade-off is that the countertop is small. If you are preparing a feast for five hundred people, you cannot fit everything on the counter at once. You must carefully plan which ingredients to stage next, just as a GPU programmer must tile data into shared memory strategically. Running out of register space is like trying to juggle too many items in your hands; you start dropping things, and performance collapses.

---

### Tiny Numeric Example

Reading 1,024 floats from different levels of the GPU memory hierarchy:

| Memory Level | Latency per Access | Total Time for 1,024 Reads |
|---|---|---|
| Registers | ~0 ns (already held) | ~0 ns |
| Shared memory | ~1 ns | ~1,024 ns (1 microsecond) |
| L2 cache | ~10 ns | ~10,240 ns (10 microseconds) |
| Global memory | ~150 ns | ~153,600 ns (154 microseconds) |

If a kernel reads data from global memory, performs one addition, and writes back, the arithmetic takes roughly 1 ns while the memory operations take 300 ns. That means 99% of the time is spent waiting for data, not calculating. This is why coalesced access patterns and shared memory tiling matter so much: they reduce the number of trips to global memory.

---

### Common Confusion

1. **"GPU global memory is the same as CPU RAM."** No. They are physically separate memory chips on the GPU card. Data must be copied from CPU RAM to GPU global memory over PCIe, which is another bottleneck.

2. **"Shared memory is visible to all threads on the GPU."** No. Shared memory is only visible to threads within the same block, typically 256-1024 threads. Blocks cannot read each other's shared memory.

3. **"Registers can be shared between threads."** No. Registers are strictly private to each thread. You cannot read another thread's registers directly; you must write to shared memory or global memory to communicate.

4. **"L2 cache is bigger than global memory."** No. Global memory is gigabytes (e.g., 24-80 GB). L2 cache is tens of megabytes (e.g., 40-96 MB).

5. **"Memory coalescing helps shared memory too."** No. Coalescing is specifically about global memory access patterns where threads in a warp read consecutive addresses. Shared memory is banked differently and has its own conflict rules.

6. **"Unified memory is as fast as registers."** No. Unified memory still lives in global memory space. It is convenient because the OS manages migration between CPU and GPU, but it is not magically faster than explicit global memory.

---

### Where It Is Used in Our Code

`src/phase83/phase83_gpu_kernels.py` -- We simulate coalesced versus strided global memory access patterns using NumPy. The simulation shows why sequential (coalesced) access is faster: it mimics the behavior of fetching contiguous cache lines from global memory, while strided access forces the memory controller to jump around, wasting bandwidth.
