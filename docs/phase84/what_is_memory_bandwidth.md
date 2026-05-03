# What Is Memory Bandwidth?

## 1. Why it exists (THE PROBLEM first)

GPUs advertise massive compute power (100+ TFLOPS), but that compute is useless if the data cannot arrive fast enough. Reading and writing data to memory takes time. If a kernel does very little math per byte loaded, the cores will finish their calculation and then sit idle waiting for the next byte. Memory bandwidth is the invisible ceiling that determines whether a kernel is fast or slow.

## 2. Definition

**Memory bandwidth** is the rate at which data can be read from or written to memory, measured in bytes per second (e.g., GB/s or TB/s). It is the width of the pipe between memory and compute units.

## 3. Real-life analogy

Imagine a factory with 1,000 assembly workers. The workers are incredibly fast, but there is only one narrow conveyor belt bringing them parts. No matter how skilled the workers are, the factory's output is limited by the belt. Memory bandwidth is the conveyor belt; compute is the workers.

## 4. Tiny numeric example

A GPU has:
- Compute: 100 TFLOPS (100 trillion float operations per second)
- Memory bandwidth: 1 TB/s (1 trillion bytes per second)

A vector-add kernel reads two floats (8 bytes), adds them (1 FLOP), and writes one float (4 bytes).
Bytes per operation: 12 bytes.
Maximum operations bandwidth allows: 1 TB/s / 12 bytes = ~83 billion ops/sec.
Theoretical compute peak: 100 TFLOPS.
Actual peak: 83 GFLOPS. The kernel is **memory bound**.

A matrix-multiply kernel reads two large matrices once and performs millions of multiply-adds per byte loaded. It is **compute bound** and can approach the 100 TFLOPS ceiling.

## 5. Common confusion

- **"Bandwidth is the same as latency."** No. Bandwidth is how much data moves per second (width of the pipe). Latency is how long one byte takes to arrive (length of the pipe). A wide pipe with a long path has high bandwidth but high latency.
- **"Higher bandwidth fixes any slow kernel."** No. If access patterns are random or strided, you waste bandwidth on unused bytes within each cache line.
- **"Memory bandwidth is a software setting."** No. It is a hardware limit determined by the memory type (GDDR6X, HBM) and bus width.
- **"Caching eliminates bandwidth concerns."** No. Caching helps, but if the working set is larger than cache, you still hit memory bandwidth.
- **"Memory bandwidth only matters for GPUs."** No. CPUs also have bandwidth limits, but they are less severe because CPUs have fewer cores and larger caches relative to compute.
- **"Compute-bound kernels don't need coalesced access."** They still benefit, but the bottleneck shifts from memory to arithmetic units.

## 6. Where it is used in our code

In `src/phase84/phase84_memory_engineering.py`, we discuss how activation checkpointing and gradient accumulation are both responses to memory pressure. We explain that training is often memory-bandwidth bound, which is why reducing memory traffic (via checkpointing or fusion) can be more impactful than raw FLOPS.
