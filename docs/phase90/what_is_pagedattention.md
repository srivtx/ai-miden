## What Is PagedAttention?

---

## The Problem

During autoregressive LLM inference, each sequence stores key and value tensors in a KV cache. Because requests have variable prompt lengths and generate variable numbers of new tokens, allocating one large contiguous block per sequence leaves huge holes of unused memory. This fragmentation kills throughput and limits how many concurrent requests a GPU can serve.

---

## Definition

**PagedAttention** divides the KV cache into fixed-size blocks (like operating-system pages). A sequence receives blocks on demand, and blocks can be non-contiguous. This virtualizes the KV cache and eliminates most external fragmentation.

**How it works:**
```
Memory pool setup:
  1. Total KV cache: 4096 tokens
  2. Block size: 16 tokens
  3. Total blocks: 4096 / 16 = 256 blocks

Allocation per sequence:
  1. Sequence needs 200 tokens → ceil(200 / 16) = 13 blocks
  2. Scheduler assigns any 13 free blocks (non-contiguous is fine)
  3. Block table maps logical token positions to physical block IDs

During generation:
  1. New token appended → if current block full, allocate one more block
  2. Sequence finishes → all its blocks returned to free pool
  3. Freed blocks immediately available for new requests
```

**Why this matters:**
- Without paging, 20 requests with average length 200 tokens waste 82% of a 1024-token contiguous allocation.
- With paging, those same sequences use only 13 blocks each, and the remaining blocks serve new requests.
- Higher memory utilization directly translates to higher throughput and lower serving costs.

---

## Real-Life Analogy

A library assigns books to fixed-size shelves rather than giving each patron one giant private bookcase. A patron who needs 35 books gets 2 full shelves and 1 partially used shelf. The empty spots on other shelves can be used by other patrons. No single patron monopolizes a huge contiguous space.

Imagine a coworking space with hot desks instead of private offices. If the space assigned each freelancer a permanent 20-desk office, most offices would sit half-empty most of the time. Instead, the space divides the floor into identical 4-person desk clusters. A freelancer checks in, gets as many clusters as needed, and returns them at the end of the day. A writer who only needs one desk gets one cluster (with three empty spots), and a team of six gets two clusters. The empty spots inside a partially used cluster are internal fragmentation, but the remaining clusters are free for others. PagedAttention works identically: fixed-size blocks are the desk clusters, and the block table is the check-in log.

**The trade-off:** PagedAttention adds complexity to the attention kernel. The GPU must now gather non-contiguous blocks using a block table instead of reading a single contiguous tensor. The overhead is small compared to the memory savings, but it requires a custom CUDA kernel rather than a standard matrix multiplication.

---

## Tiny Numeric Example

**Naive contiguous allocation (before PagedAttention):**

| Parameter | Value |
|-----------|-------|
| Cache capacity | 4,096 tokens |
| Requests | 20 |
| Slot per request | 1,024 tokens (worst-case) |
| Average sequence length | 200 tokens |

| Metric | Calculation | Result |
|--------|-------------|--------|
| Total allocated | 20 × 1,024 | 20,480 tokens |
| Actual used | 20 × 200 | 4,000 tokens |
| Wasted | 20,480 - 4,000 | 16,480 tokens |
| Utilization | 4,000 / 20,480 | 19.5% |

**PagedAttention allocation (16-token blocks):**

| Parameter | Value |
|-----------|-------|
| Total blocks | 256 (4,096 / 16) |
| Blocks per request | ceil(200 / 16) = 13 |
| Total blocks used | 20 × 13 | 260 blocks |

Wait, 260 blocks needed but only 256 available. Let's adjust to 8 requests fitting in cache.

**Revised for 8 requests:**

| Metric | Naive | Paged |
|--------|-------|-------|
| Allocated tokens | 8 × 1,024 = 8,192 | 8 × 13 × 16 = 1,664 |
| Actual used | 8 × 200 = 1,600 | 1,600 |
| Wasted | 6,592 | 64 |
| Utilization | 19.5% | 96.2% |

- Memory saved: 6,528 tokens (80% reduction)
- Additional requests that fit: Paged can serve ~24 requests in the same space naive serves 8
- Internal fragmentation: 64 tokens (4% overhead) from partially filled final blocks

---

## Common Confusion

1. **"PagedAttention reduces the total number of tokens cached."** It does not. It only improves how those tokens are packed into memory. The same tokens are stored; they are just arranged more tightly.

2. **"It is the same as swapping to disk."** It is not. Operating-system paging moves memory to disk; PagedAttention keeps everything in GPU memory but manages allocation in fixed-size blocks.

3. **"Blocks are attention heads."** They are not. A block contains tokens across all heads and layers for a slice of the sequence. It is a memory-management unit, not an attention-computation unit.

4. **"It eliminates all fragmentation."** It does not. Internal fragmentation still exists within the last partially filled block of each sequence. External fragmentation is eliminated.

5. **"PagedAttention is only for batching."** It is not. It also enables memory sharing during parallel sampling and beam search, where multiple candidates share prompt prefix blocks.

6. **"Any attention implementation can use PagedAttention."** Not without modification. The attention kernel must be rewritten to index into non-contiguous blocks via a block table rather than a flat tensor.

7. **"Paging adds no latency overhead."** The overhead is small but nonzero. The block-table indirection requires extra GPU operations per attention step, though the benefit of higher batch size usually outweighs this cost.

---

## Where It Is Used in Our Code

`src/phase90/phase90_inference_serving.py` — We simulate a fixed-size KV cache and compare naive contiguous allocation against block-based paging. We generate random sequence lengths, compute utilization under both schemes, and simulate dynamic arrivals and departures across 50 timesteps. The script plots fragmentation ratio over time and saves the comparison to `kv_cache_fragmentation.png`, showing that paging achieves significantly higher memory utilization when sequence lengths vary.
