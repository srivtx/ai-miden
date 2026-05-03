### 1. Why it exists (THE PROBLEM first)
Standard attention computes the full N x N score matrix and stores it in high-bandwidth memory (HBM, the GPU's main RAM). For long sequences, this matrix is enormous. Worse, the algorithm reads and writes this matrix repeatedly from slow HBM instead of keeping it in fast on-chip SRAM. Most of the time is spent moving data, not doing math.

### 2. Definition (very simple)
Flash Attention is an algorithm that computes attention in small tiles that fit entirely in fast GPU SRAM. It never materializes the full N x N attention matrix in HBM. By fusing the softmax, masking, and dropout operations into a single kernel, it reduces memory reads/writes and achieves both speedup and memory savings.

### 3. Real-life analogy
A chef is making a 100-ingredient salad. Standard attention: the chef walks to the pantry, brings ALL 100 ingredients to the counter at once (no counter is big enough, so they spill onto the floor = HBM), prepares the salad, then cleans up. Flash Attention: the chef brings only 10 ingredients at a time (fits on the counter = SRAM), chops them, then fetches the next 10. The counter is small but fast; the pantry is big but slow.

### 4. Tiny numeric example
Sequence length N = 4096, head dimension d = 64.

Standard attention:
- Compute QK^T: 4096 x 4096 matrix = 16.7 million values
- At FP32: 67 MB just for the score matrix
- Plus reads/writes for softmax, masking, dropout, and the final multiply with V

Flash Attention:
- Tile size B = 256 (fits in SRAM)
- Process 256 x 256 blocks
- Never stores the full 4096 x 4096 matrix
- Memory usage drops from O(N^2) to O(N), and wall-clock time drops 2-7x

### 5. Common confusion
- **Flash Attention does not change the math.** The output is numerically identical (up to floating-point rounding) to standard attention. It is purely an implementation optimization.
- **It is not just about memory.** It is also about speed, because reducing HBM transfers is often the bottleneck, not FLOPs.
- **It requires specific hardware support.** Flash Attention is written as a custom CUDA kernel for NVIDIA GPUs. It does not run on CPUs or all GPUs out of the box.
- **It does not help with KV Cache memory.** The K and V matrices still grow linearly with sequence length. Flash Attention speeds up the attention computation itself.
- **Flash Attention 2 and 3 exist.** Flash Attention 2 improves parallelism over the sequence dimension. Flash Attention 3 further optimizes for Hopper-class GPUs with asynchronous memory access.

### 6. Where it is used in our code
`src/phase25/phase25_inference_optimization.py` visualizes the memory access pattern difference between standard attention (repeated HBM reads) and Flash Attention (SRAM tiling).
