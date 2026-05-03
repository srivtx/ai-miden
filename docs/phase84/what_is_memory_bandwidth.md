## What Is Memory Bandwidth?

---

### The Problem

GPUs advertise massive compute power (100+ TFLOPS), but that compute is useless if the data cannot arrive fast enough. Reading and writing data to memory takes time. If a kernel does very little math per byte loaded, the cores will finish their calculation and then sit idle waiting for the next byte. Memory bandwidth is the invisible ceiling that determines whether a kernel is fast or slow, yet it is often ignored when people focus only on FLOPS.

---

### Definition

**Memory bandwidth** is the rate at which data can be read from or written to memory, measured in bytes per second (e.g., GB/s or TB/s). It is the width of the pipe between memory and compute units.

**How it works:**
```
GPU spec: 100 TFLOPS compute, 1 TB/s memory bandwidth
Kernel: vector add (read 2 floats, add, write 1 float)
Bytes per operation: 12 bytes
Max ops bandwidth allows: 1 TB/s / 12 bytes = 83 billion ops/sec
Theoretical compute peak: 100 TFLOPS
Actual peak: 83 GFLOPS
Result: kernel is memory bound, not compute bound
```

**Key distinctions:**
- **Bandwidth:** how much data moves per second (width of the pipe).
- **Latency:** how long one byte takes to arrive (length of the pipe).
- A wide pipe with a long path has high bandwidth but high latency.

**Why this matters:**
- Element-wise operations are almost always memory-bound.
- Matrix multiplication is usually compute-bound because it reuses each loaded byte millions of times.
- Reducing memory traffic (via fusion, checkpointing, or better access patterns) is often more impactful than buying a GPU with more FLOPS.

---

### Real-Life Analogy

Imagine a factory with 1,000 incredibly fast assembly workers. The workers can assemble a part in one second, but there is only one narrow conveyor belt bringing them raw materials. No matter how skilled the workers are, the factory's output is limited by the belt. Memory bandwidth is the conveyor belt; compute is the workers. You can hire more workers or make them faster, but if the belt does not widen, total throughput barely changes.

The trade-off is that widening the belt is expensive and physically constrained. Some factories solve this by redesigning the workflow so each raw material is used to make many parts before a new material is needed. In computing, this is exactly what matrix multiplication does: each loaded element participates in thousands of multiply-add operations. A vector add, by contrast, uses each element exactly once. This is why convolution and matmul kernels can approach theoretical FLOPS, while simple ReLU or addition layers cannot.

---

### Tiny Numeric Example

A GPU has 100 TFLOPS of compute and 1 TB/s of memory bandwidth.

**Vector-add kernel:** reads two floats (8 bytes), adds them (1 FLOP), writes one float (4 bytes).
- Bytes per operation: 12 bytes.
- Maximum operations bandwidth allows: 1 TB/s / 12 bytes = ~83 billion ops/sec.
- Theoretical compute peak: 100 TFLOPS.
- **Actual peak: 83 GFLOPS. The kernel is memory bound.**

**Matrix-multiply kernel:** reads two large matrices once and performs millions of multiply-adds per byte loaded.
- Bytes per operation: ~0.001 bytes (due to heavy reuse in registers/shared memory).
- Maximum operations bandwidth allows: far above 100 TFLOPS.
- Theoretical compute peak: 100 TFLOPS.
- **Actual peak: ~95 TFLOPS. The kernel is compute bound.**

| Kernel Type | FLOPs per Byte | Bottleneck | % of Peak FLOPS |
|---|---|---|---|
| Vector add | 0.083 | Memory bandwidth | 0.08% |
| Matrix multiply (1024x1024) | ~1000 | Compute | 95% |

This explains why reducing memory traffic through fusion or checkpointing can be more valuable than raw FLOPS for many deep learning operations.

---

### Common Confusion

1. **"Bandwidth is the same as latency."** No. Bandwidth is how much data moves per second (width of the pipe). Latency is how long one byte takes to arrive (length of the pipe). A wide pipe with a long path has high bandwidth but high latency.

2. **"Higher bandwidth fixes any slow kernel."** No. If access patterns are random or strided, you waste bandwidth on unused bytes within each cache line, so effective bandwidth remains low even if theoretical bandwidth is high.

3. **"Memory bandwidth is a software setting."** No. It is a hardware limit determined by the memory type (GDDR6X, HBM) and bus width. Software can only optimize how efficiently it uses the available bandwidth.

4. **"Caching eliminates bandwidth concerns."** No. Caching helps, but if the working set is larger than cache, you still hit memory bandwidth. Large transformers often have activation footprints far exceeding cache size.

5. **"Memory bandwidth only matters for GPUs."** No. CPUs also have bandwidth limits, but they are less severe because CPUs have fewer cores and larger caches relative to compute.

6. **"Compute-bound kernels don't need coalesced access."** They still benefit from coalesced access, but the bottleneck shifts from memory to arithmetic units, so the performance gain is smaller.

---

### Where It Is Used in Our Code

`src/phase84/phase84_memory_engineering.py` -- We discuss how activation checkpointing and gradient accumulation are both responses to memory pressure. We explain that training is often memory-bandwidth bound, which is why reducing memory traffic (via checkpointing or fusion) can be more impactful than increasing raw FLOPS. The activation memory bar chart visualizes how checkpointing halves peak memory usage.
