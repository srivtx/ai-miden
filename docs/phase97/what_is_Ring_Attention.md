# What Is Ring Attention?

## Problem
Standard self-attention computes an n x n attention score matrix. For sequence lengths of 100K tokens, this matrix requires terabytes of memory, making it impossible to fit on a single device.

## Definition
Ring Attention is a blockwise attention algorithm that splits the sequence into chunks and computes attention in a distributed ring pattern. Each device holds a query block and streams key/value blocks around a ring, accumulating partial attention statistics. This reduces peak memory from O(n^2) to O(n) per device.

## Analogy
Imagine a stadium with many sections. Instead of one person trying to watch every seat at once (impossible), each section leader only compares their section to one other section at a time, passing notes around a circle. Eventually everyone knows the full picture without anyone holding all the notes.

## Example
With 8 GPUs and a 128K sequence, each GPU might hold a 16K query block. It receives 16K key/value blocks from its neighbor, computes partial attention, and passes the block along. After 8 steps, every query block has seen every key/value block.

## Common Confusion
Ring Attention does not change the mathematical result of attention; it is purely a systems optimization for memory and parallelism. It is sometimes conflated with sparse attention patterns, which actually drop some computations.

## Code Location
See `src/phase97/phase97_long_context.py` for a memory comparison between full and blockwise attention.
