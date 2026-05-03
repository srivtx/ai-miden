## What Is Kernel Fusion?

---

### The Problem

Every time a GPU kernel launches, there is overhead: the GPU must schedule the kernel, set up registers, and dispatch warps. Worse, if you run operation A, then operation B, then operation C, the intermediate results of A and B must be written to global memory and then read back. That wastes enormous memory bandwidth. For element-wise operations like add, multiply, and ReLU, the math is trivial but the memory traffic dominates. Kernel fusion exists to combine multiple operations into one kernel, keeping data in fast on-chip memory instead of round-tripping through slow global memory.

---

### Definition

**Kernel fusion** is the technique of combining multiple GPU operations into a single kernel so that intermediate values never leave fast on-chip memory (registers or shared memory). The fused kernel reads input once, performs all computations in registers, and writes the final result once.

**How it works:**
```
Unfused:
  Kernel 1: read x from global memory, compute y = x + 1, write y to global memory
  Kernel 2: read y from global memory, compute z = y * 2, write z to global memory
  Kernel 3: read z from global memory, compute w = z - 3, write w to global memory

Fused:
  Single kernel: read x from global memory, compute w = ((x + 1) * 2) - 3 in registers, write w to global memory
```

**Key benefits:**
- **Half the memory bandwidth:** one read and one write instead of three reads and three writes.
- **Less kernel launch overhead:** one launch instead of three.
- **Better cache utilization:** intermediate data stays in registers, never polluting caches.

**Why this matters:**
- On a memory-bound GPU, fusion can double the speed of element-wise pipelines.
- Frameworks like XLA (JAX/TensorFlow) and `torch.compile` automatically fuse kernels without hand-written CUDA.

---

### Real-Life Analogy

Imagine you need to go to the grocery store, the post office, and the pharmacy. Without fusion, you drive home after each errand, unload the car, then drive out again. You make six trips total and waste most of your day in traffic. With fusion, you plan one efficient loop and do all three stops in a single trip. The "home" in this analogy is global memory; the "car" is registers, where your groceries stay while you move between stops.

The trade-off is that fusion requires careful planning. If the pharmacy turns out to be closed, you cannot simply abort that one errand and go home with your other items; you are committed to the full loop. Similarly, a fused kernel is harder to debug because you cannot inspect intermediate values easily. If one operation in the fused chain produces incorrect results, you must dissect the entire kernel. Additionally, a very complex fused kernel may use too many registers, reducing occupancy and actually hurting performance. Fusion is powerful, but it is not free.

---

### Tiny Numeric Example

Three element-wise operations on a vector of 1 million 32-bit floats (4 MB):

**Unfused (three separate kernels):**
| Step | Operation | Memory Read | Memory Write | Traffic |
|---|---|---|---|---|
| 1 | y = x + 1 | 4 MB | 4 MB | 8 MB |
| 2 | z = y * 2 | 4 MB | 4 MB | 8 MB |
| 3 | w = z - 3 | 4 MB | 4 MB | 8 MB |
| **Total** | | **12 MB** | **12 MB** | **24 MB** |

**Fused (single kernel):**
| Step | Operation | Memory Read | Memory Write | Traffic |
|---|---|---|---|---|
| 1 | w = (x + 1) * 2 - 3 | 4 MB | 4 MB | **8 MB** |

Same math, half the total memory bandwidth. On a GPU with 1 TB/s global memory bandwidth, the unfused version takes 24 microseconds just for memory traffic, while the fused version takes 8 microseconds. If the GPU is memory-bound, this can yield a 2-3x speedup.

---

### Common Confusion

1. **"Fusion reduces the number of arithmetic operations."** No. Fusion reduces memory traffic, not math. The same additions and multiplications still happen; they just occur inside registers instead of across separate kernel launches.

2. **"Any two operations can be fused."** No. If the second operation needs a global reduction, a matrix transpose that changes memory layout, or data-dependent shapes, fusion may be impossible or unprofitable.

3. **"Developers write fused kernels by hand."** Rarely. Modern frameworks like XLA (JAX/TensorFlow) and `torch.compile` automatically fuse kernels for you by analyzing the computation graph.

4. **"Fused kernels are easier to debug."** No. When five operations become one kernel, you cannot easily inspect intermediate values. Debugging requires specialized tools or temporarily splitting the fused kernel back apart.

5. **"Fusion always improves performance."** Usually, but not always. A very complex fused kernel may use too many registers, reducing occupancy and hurting performance, or it may exceed shared memory limits.

6. **"Kernel fusion is the same as loop fusion in CPU compilers."** Conceptually similar, but GPU kernel fusion is far more critical because global memory bandwidth is the main bottleneck, whereas CPU caches are larger and more forgiving.

---

### Where It Is Used in Our Code

`src/phase83/phase83_gpu_kernels.py` -- While the script focuses on coalesced versus strided memory access and a conceptual vector-add kernel, the principle of fusion underlies the entire demonstration. The coalesced access benchmark shows why minimizing global memory round-trips matters, and kernel fusion is the ultimate technique for achieving that: it keeps data on-chip across multiple operations, just as coalesced access keeps memory fetches efficient.
