## Why it exists (THE PROBLEM)

Your model trains at 400 tokens/second on T4. You don't know if that's good or bad. You don't know which operation is slow. Is it attention? The tokenizer? Data loading? GPU memory transfers? You're optimizing blind.

**GPU profiling** tells you exactly where time goes: matrix multiply A takes 45% of step time, attention softmax takes 12%, data loading blocks for 20% (GPU idle waiting for CPU). Now you can optimize the right thing instead of guessing.

**GPU architecture knowledge** tells you WHY certain operations are slow: tensor cores only accelerate certain matrix shapes, shared memory is 100× faster than global memory, bank conflicts kill bandwidth. Without this knowledge, you can't interpret the profiler output.

## Definition (very simple)

**Profiling = measuring WHERE time and memory go during a training or inference step.**

The PyTorch Profiler instruments your code: every kernel launch, every data transfer, every CUDA operation is timestamped. The output is a timeline (Chrome Trace Viewer) showing exactly which GPU operations ran when.

**What you learn from a single profile:**
- GPU utilization: 60% → GPU is idle 40% of the time (probably waiting for CPU to load data)
- Kernel breakdown: matmul = 45%, softmax = 12%, add = 8%, memcpy = 20%, etc.
- Memory: 12GB of 16GB used → you have 4GB headroom (can increase batch size)
- Bottleneck: data loading takes 0.3ms per step → you're I/O bound, not compute bound

**GPU architecture (Nvidia, simplified):**
- **SM (Streaming Multiprocessor):** The compute unit. T4 has 40 SMs. Each SM has: tensor cores (matrix multiply), CUDA cores (general compute), shared memory (fast, 100KB per SM), registers.
- **Global memory (VRAM / HBM):** 16GB GDDR6 on T4. Bandwidth: 320 GB/s. Latency: ~400 cycles. SLOW but LARGE.
- **Shared memory (SRAM):** 100KB per SM. Bandwidth: 8 TB/s (25× faster than global). SMALL but FAST.
- **Tensor Cores:** Hardware matrix multiply units. 8× faster than CUDA cores for fp16 matmul. Only works for certain shapes (multiples of 16 bytes).
- **Memory hierarchy:** Global (slow, large) → L2 cache → shared memory (fast, small) → registers (fastest, tiny). Moving data up this hierarchy = the key to speed.

## Practice: Profiling a training step

```python
import torch
import torch.profiler as profiler

# Profile a single training step
with profiler.profile(
    activities=[profiler.ProfilerActivity.CPU, profiler.ProfilerActivity.CUDA],
    record_shapes=True,      # log tensor shapes
    profile_memory=True,      # track memory usage
    with_stack=True,          # Python call stack
) as prof:
    with profiler.record_function("forward"):
        logits, loss = model(x, y)
    with profiler.record_function("backward"):
        loss.backward()
    with profiler.record_function("optimizer"):
        optimizer.step()

# Export
print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=10))
prof.export_chrome_trace("trace.json")

# Output example:
# Name                    Self CPU %  Self CPU  CUDA total  CUDA self
# aten::mm                   0.01%    1.200ms   45.200ms    45.200ms
# aten::softmax              0.00%    0.050ms   12.100ms    12.100ms
# aten::add                  0.00%    0.030ms    8.300ms     8.300ms
# ...
# -------------------------------------------------------
# Self CPU time total: 3.400ms
# Self CUDA time total: 85.000ms
```

## What to look for in a profile

| Metric | Good sign | Bad sign | Fix |
|---|---|---|---|
| GPU utilization | 80-95% | <50% | Increase batch, fix data loading |
| Data loading time | <5% of step | >20% | More workers, prefetching, memmap |
| CPU/GPU sync points | <1ms | >10ms | Remove `.cpu()`, `.item()`, `.numpy()` calls in training loop |
| Kernel launch overhead | <1% of CUDA time | >10% | Fuse operations (torch.jit.script) |
| Memory alloc/free | Stable | Frequent alloc/free | Pre-allocate tensors, use memory pool |
| MatMul time | Matches expected | 3× slower than expected | Check tensor shapes (must be multiple of 8 for fp16, 16 for TF32) |

## Key architecture facts for T4

| Property | T4 | A100 | H100 |
|---|---|---|---|
| VRAM | 16GB | 40/80GB | 80GB |
| Bandwidth | 320 GB/s | 1.5 TB/s | 3.3 TB/s |
| Tensor Cores | 320 (Turing) | 432 (Ampere) | 528 (Hopper) |
| FP16 TFLOPS | 65 | 312 | 990 |
| Max batch @ dim=256, layers=6 | ~32 | ~256 | ~512 |

**On T4:** You're VRAM-limited (16GB) before you're compute-limited. Batch size matters more than kernel optimization. Fix the data pipeline first (avoid GPU idle), then tune attention (FlashAttention gives the biggest win), then look at matmul shapes.

## Common confusion

1. **"Profiling slows down my code."** Yes, profiling adds overhead (2-10%). That's fine — you profile ONCE, find the bottleneck, fix it, run at full speed. Don't profile in production.

2. **"I can just guess what's slow."** Programmers are terrible at guessing bottlenecks. Profile first. Always. The thing you think is slow (attention) is probably NOT the bottleneck (data loading usually is).

3. **"T4 is slow."** T4 is the SWEET SPOT for small models. 10M model on T4: 400 tokens/sec. 10M model on A100: 800 tokens/sec (2×). 10M model on CPU: 20 tokens/sec. T4 is 20× faster than CPU, 2× slower than A100. For $0 vs $2/hour, that's excellent.

4. **"More CUDA cores = faster."** Tensor cores are 8× faster than CUDA cores for matmul. On T4: 65 TFLOPS fp16 via tensor cores. Optimize for tensor cores: use fp16, keep shapes aligned to 16.

## Connection to cortexcode

Add `torch.profiler.profile` around a training step. Look at the table. Fix the top bottleneck. Re-profile. Repeat. The training loop should spend 80%+ of CUDA time in `aten::mm` (matrix multiply) — that's the core computation. If it's spending time in `aten::copy_` or `aten::to`, you're moving data unnecessarily between CPU and GPU.
