## Why it exists (THE PROBLEM)

A 10M-param model trains on a single T4 in 15 minutes. A 1B-param model needs days on a single GPU. A 70B-param model can't fit on one GPU at all. The only way to train large models is to split the work across multiple GPUs — sometimes hundreds or thousands. This requires careful orchestration: how do you split the model? How do you split the data? How do GPUs communicate?

**Distributed training** is the answer. Three strategies cover 95% of cases:

1. **Data Parallel (DDP):** Every GPU has the FULL model. Each GPU gets a different batch of data. After each forward/backward pass, gradients are averaged across GPUs. Works for models that fit in a single GPU's VRAM.

2. **Model Parallel (FSDP):** Split the MODEL across GPUs. Each GPU holds a fraction of the layers. Communication happens at layer boundaries. Works for models too large for one GPU.

3. **Pipeline Parallel:** Split the model into stages (GPU1: layers 1-8, GPU2: layers 9-16, etc.). Process pipeline batches (micro-batches) to keep all GPUs busy simultaneously.

In practice, production training combines all three (3D parallelism). LLaMA 3 405B was trained on 16,000 H100 GPUs using FSDP + tensor parallel + pipeline parallel.

## Definition (very simple)

**Distributed Data Parallel (DDP):** The entry point. Every GPU loads the full model. Each forward pass processes different data. Backward computes local gradients. An `all_reduce` operation averages gradients across all GPUs. Each GPU updates its own copy. After N steps, all GPUs have identical weights.

**Fully Sharded Data Parallel (FSDP):** Like DDP, but the model is SHARDED across GPUs instead of replicated. Each GPU holds only 1/N of the model parameters. Before each layer's forward pass, the GPU fetches the needed parameters from other GPUs (all-gather). After the backward pass, parameters are re-sharded. This lets you train models N× larger than what fits on one GPU.

**Zero Redundancy Optimizer (ZeRO, part of DeepSpeed):** Extends the sharding idea to optimizer states and gradients. ZeRO-1 shards optimizer states. ZeRO-2 adds gradient sharding. ZeRO-3 shards everything (params + grads + optimizer). Each stage saves memory: ZeRO-1 saves 4×, ZeRO-2 saves 8×, ZeRO-3 saves N× (for N GPUs).

## Real-life analogy

**DDP = 4 students each solving the same problem set, then comparing answers.** Everyone has the full textbook (model). But each works on different questions (different data batch). At the end, they average their answers. All 4 end up with the same improved understanding.

**FSDP = 4 students each holding a different chapter of the textbook, passing them around.** Student 1 has chapters 1-2, Student 2 has 3-4, etc. When Student 1 needs chapter 3, they ask Student 2. Nobody has the full book, but they can solve any problem by fetching chapters as needed.

**Pipeline parallel = an assembly line.** GPU1 processes layers 1-8, passes its output to GPU2 for layers 9-16, which passes to GPU3. While GPU2 works on batch 1, GPU1 starts batch 2. The pipeline stays full.

## Tiny numeric example

Training a 10B model on 4 GPUs (24GB each):

**DDP:** Model = 40GB (10B × 4 bytes fp32). Doesn't fit on one 24GB GPU. ❌
**FSDP:** Model sharded across 4 GPUs. 40GB / 4 = 10GB per GPU. Plus optimizer (20GB) / 4 = 5GB. Activations: ~2GB. Total: 17GB per GPU. Fits! ✅
**FSDP + mixed precision (fp16):** Model = 20GB / 4 = 5GB. Optimizer = 10GB / 4 = 2.5GB. Total: ~9GB. Lots of room.

Training time comparison (same batch, 4 GPUs):
- Single GPU: 40 hours
- DDP (model fits): 10 hours (4× speedup, near-linear)
- FSDP: 12 hours (4× speedup minus communication overhead ~20%)

## Key properties

| Strategy | Model per GPU | Memory saved | Communication | Scaling limit |
|---|---|---|---|---|
| Single GPU | 100% | 0% | None | VRAM |
| DDP | 100% (replicated) | 0% | Gradients (small) | Models that fit in VRAM |
| FSDP | 1/N (sharded) | N× | Params + grads (large) | Very large N (thousands) |
| ZeRO-1 | 100% | 4× (optimizer sharded) | Small | ~100 GPUs |
| ZeRO-2 | 100% | 8× (+ gradients) | Medium | ~100 GPUs |
| ZeRO-3 | 1/N | N× (+ params) | High | Thousands of GPUs |

## Common confusion

1. **"FSDP is just DDP with sharding."** Close but the implementation differs. DDP does one `all_reduce` after backward. FSDP does `all_gather` before EACH layer and `reduce_scatter` after each layer. More communication events but smaller messages. Net result: same wall time but much less memory.

2. **"More GPUs = faster training."** Only up to a point. Each GPU adds communication overhead. At 1000 GPUs, communication can consume 40% of step time. You hit diminishing returns. The sweet spot depends on model size, batch size, and interconnect speed (NCCL, InfiniBand).

3. **"I can just use a bigger GPU."** The H100 has 80GB. A 70B model in fp16 needs 140GB. Even the biggest single GPU can't fit it. You MUST use model parallelism.

4. **"PyTorch DDP wraps my training loop."** Yes: `model = DDP(model, device_ids=[local_rank])`. That's one line. But you need: `torchrun --nproc_per_node=N train.py` to launch, data must be partitioned per GPU, random seeds must differ, logging must only happen on rank 0, and checkpointing must handle partial saves.

## Connection to our projects

**cortexcode:** For 10M models on T4, DDP is trivial. For 100M models on multi-GPU, use FSDP. The transition: `python train.py` → `torchrun --nproc_per_node=4 train.py`. Same code, add `model = FSDP(model)`.

**What to learn:** Start with PyTorch DDP (one line). Graduate to FSDP when models don't fit. DeepSpeed if you need ZeRO-3. NCCL is the communication backend — learn to debug it.
