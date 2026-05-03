# What is Flash Attention?

## 1. Problem Statement

Standard attention implementations materialize the full N x N attention matrix in high-bandwidth memory (HBM), which is slow and memory-intensive. For long sequences, this quadratic memory footprint becomes the bottleneck, especially on bandwidth-constrained mobile hardware.

## 2. Definition

**Flash Attention** is an exact attention algorithm that computes the output in tiles, using careful reordering of operations to avoid materializing the full attention matrix. It fuses the softmax and matrix multiplication into a single kernel, reducing HBM reads/writes from O(N^2) to O(N). FlashAttention-2 and FlashAttention-3 further optimize parallelism and hardware utilization.

## 3. Analogy

Imagine summing a huge spreadsheet. Instead of writing every intermediate cell to a notebook (HBM), you keep a running total in your head (SRAM) and only write the final answer. Flash Attention does the same: it keeps intermediate values in fast on-chip SRAM rather than slow GPU memory.

## 4. Example

In a 4K context length LLM, standard attention might require 64MB just for the attention matrix. Flash Attention reduces this to a small constant by computing attention block-by-block, enabling longer contexts on the same hardware and significantly faster training/inference.

## 5. Common Confusion

Flash Attention is NOT an approximation or sparse attention variant. It computes the exact same result as standard attention, just faster and with less memory. The speedup comes from memory efficiency (IO-awareness), not from skipping computations.

## 6. Code Location

See `src/phase107/phase107_on_device.py` for a NumPy simulation of model size vs memory and quantization trade-offs.
