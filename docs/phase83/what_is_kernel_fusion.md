# What Is Kernel Fusion?

## 1. Why it exists (THE PROBLEM first)

Every time a GPU kernel launches, there is overhead. Worse, if you run operation A, then operation B, then operation C, the intermediate results of A and B must be written to global memory and then read back. That wastes enormous memory bandwidth. For element-wise operations (add, multiply, ReLU), the math is trivial but the memory traffic dominates. Kernel fusion exists to combine multiple operations into one kernel, keeping data in registers or shared memory instead of round-tripping through global memory.

## 2. Definition

**Kernel fusion** is the technique of combining multiple GPU operations into a single kernel so that intermediate values never leave fast on-chip memory (registers or shared memory).

## 3. Real-life analogy

Imagine you need to go to the grocery store, the post office, and the pharmacy. Without fusion, you drive home after each errand, unload the car, then drive out again. With fusion, you plan one efficient loop and do all three stops in a single trip. The "home" in this analogy is global memory; the "car" is registers.

## 4. Tiny numeric example

Three operations on a vector of 1 million floats:

Unfused:
- y = x + 1     (read x, compute, write y)
- z = y * 2     (read y, compute, write z)
- w = z - 3     (read z, compute, write w)
Total memory traffic: 8 MB read + 8 MB written = 16 MB.

Fused into one kernel:
- w = (x + 1) * 2 - 3
Total memory traffic: 4 MB read (x) + 4 MB written (w) = 8 MB.

Same math, half the memory bandwidth. On a memory-bound GPU, this can double speed.

## 5. Common confusion

- **"Fusion reduces the number of arithmetic operations."** No. Fusion reduces memory traffic, not math. The same additions and multiplications still happen.
- **"Any two operations can be fused."** No. If operation B needs a global reduction or matrix transpose that changes memory layout, fusion may be impossible.
- **"Developers write fused kernels by hand."** Rarely. Frameworks like XLA (JAX/TensorFlow) and torch.compile automatically fuse kernels for you.
- **"Fused kernels are easier to debug."** No. When five ops become one kernel, you cannot inspect intermediate values easily.
- **"Fusion always improves performance."** Usually, but not always. A very complex fused kernel may use too many registers, reducing occupancy and hurting performance.
- **"Kernel fusion is the same as loop fusion in CPU compilers."** Conceptually similar, but GPU kernel fusion is more critical because global memory bandwidth is the main bottleneck.

## 6. Where it is used in our code

In `src/phase83/phase83_gpu_kernels.py`, we conceptually demonstrate fused operations by comparing separate NumPy calls versus a single combined expression. While NumPy does not have kernels in the CUDA sense, the principle is identical: one pass over memory is faster than three.
