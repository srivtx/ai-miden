## What Is Inference Optimization?

---

### The Problem

You benchmarked your model in a notebook and it looks fast. Then you deploy it. Real traffic arrives in bursts. Some users send novels as prompts; others send single words. Some need answers in 200 milliseconds; others will wait ten seconds. Your fixed batch size of 4 turns out to be too small at peak and too large at trough. Your GPU sits idle 30% of the time. Your cloud bill is $12,000 per month for a model that serves 50 requests per minute. You are optimizing the wrong thing: you tuned for single-request latency when production cares about throughput, cost per token, and tail latency.

---

### Definition

**Inference optimization** is the engineering discipline of tuning how a language model is served to minimize cost, latency, and resource usage while maintaining quality. It spans batch size selection, request scheduling, memory layout, quantization, speculative decoding, and hardware-specific kernel tuning. The goal is not to make one request fast; it is to make the entire serving system efficient under real traffic patterns.

**How it works:**
```
Production inference stack:
  ┌─────────────────────────────────────────┐
  │  Request router (load balancing)        │
  ├─────────────────────────────────────────┤
  │  Scheduler (continuous batching)        │
  ├─────────────────────────────────────────┤
  │  KV cache manager (PagedAttention)      │
  ├─────────────────────────────────────────┤
  │  Model engine (fused kernels, FP8)      │
  ├─────────────────────────────────────────┤
  │  Hardware (GPU, tensor cores, HBM)      │
  └─────────────────────────────────────────┘
```

**Key techniques:**
- **Batch size tuning:** larger batches increase throughput but also increase per-request latency (queuing delay). The optimal batch size is where marginal throughput gain equals acceptable latency.
- **Request scheduling:** shortest-job-first for latency-sensitive requests, longest-prompt-first for throughput-heavy workloads. Preemption lets high-priority requests interrupt low-priority ones.
- **Speculative decoding:** a small draft model generates candidate tokens; the large model verifies them in parallel. Accepted tokens cost one forward pass each, rejected tokens are cheap.
- **Cost per 1M tokens:** the dollar cost of processing one million input and output tokens. This combines GPU rental price, utilization rate, and throughput.

**Why this matters:**
- A poorly optimized deployment costs 5-10× more per token than an optimized one
- Tail latency (p99) determines user experience; mean latency is a vanity metric
- The same hardware can serve 10× more users if batching and caching are tuned

---

### Real-Life Analogy

An airport security checkpoint.
- **Naive inference:** One security lane, one passenger at a time. Each passenger empties their entire bag onto the belt, walks through the scanner, and repacks before the next person starts. Fifty people take an hour. The scanner is idle while people repack.
- **Batching (static):** Five lanes, each with five people. But everyone in a lane must wait for the slowest repacker. Four people stand idle while one fumbles with a laptop. Throughput improves, but latency is unpredictable.
- **Optimized inference:** Five lanes with a shared pool of trays. People put items in trays as they arrive; trays go through the scanner continuously. Fast passengers finish and free trays instantly. Slow passengers do not block others. A priority lane lets first-class passengers skip ahead. This is continuous batching + preemption + memory pooling.

---

### Tiny Numeric Example

**Serving Llama-3-8B on an A100 ($2.50/hour):**

**Scenario A: Single-request, no batching**
```
Requests/sec:    1
Tokens/sec:      35
Cost per 1M tokens:
  1M / 35 = 28,571 seconds = 7.94 hours
  7.94 × $2.50 = $19.85 per million tokens
```

**Scenario B: Static batch_size=8**
```
Throughput:      220 tokens/sec (batch overhead)
Latency per request:  8 × 0.045 = 360 ms per token (queue + compute)
Cost per 1M tokens:
  1M / 220 = 4,545 seconds = 1.26 hours
  1.26 × $2.50 = $3.15 per million tokens
```

**Scenario C: Continuous batching + PagedAttention + FP8**
```
Throughput:      1,400 tokens/sec
Latency (p50):   55 ms per token
Latency (p99):   180 ms per token
Cost per 1M tokens:
  1M / 1,400 = 714 seconds = 0.20 hours
  0.20 × $2.50 = $0.49 per million tokens
```

**Latency vs throughput trade-off:**
```
Batch Size   Throughput   p50 Latency   p99 Latency   Cost/1M tok
-------------------------------------------------------------
1            35 tok/s     28 ms         45 ms         $19.85
4            140 tok/s    42 ms         95 ms         $4.96
8            220 tok/s    58 ms         180 ms        $3.15
16           280 tok/s    95 ms         420 ms        $2.48
32           310 tok/s    170 ms        890 ms        $2.24
64           320 tok/s    310 ms        2,100 ms      $2.17
```

**The shift:** Batch size 8 is the sweet spot for this model and GPU. Beyond 16, throughput barely grows but latency explodes. Inference optimization is finding that knee in the curve.

---

### Common Confusion

1. **"Higher batch size is always better."** No. Throughput plateaus while latency grows linearly. The optimal batch size depends on your latency budget, not on maximizing throughput.

2. **"Mean latency is the metric to watch."** Production systems care about p99 or p99.9 latency. A mean of 50 ms with occasional 5-second outliers will lose users faster than a steady 80 ms.

3. **"Speculative decoding is free speed."** It adds memory and compute overhead for the draft model. It only helps when the acceptance rate is high (usually >70%). On code or reasoning tasks where the large model disagrees with the draft, it can slow things down.

4. **"Optimization is only about software."** Hardware matters enormously. H100 with FP8 tensor cores is 3× faster than A100 for the same model. Memory bandwidth, not FLOPS, is usually the bottleneck for token generation.

5. **"You optimize once and you are done."** Traffic patterns change. A chatbot at 9 AM gets short queries; at 5 PM users paste entire documents. The scheduler must adapt, which is why production systems expose dynamic batching limits.

6. **"Quantization always hurts quality."** FP8 on large models (8B+) is virtually indistinguishable from FP16 for most tasks. INT8 with proper scaling can match FP16 within 1% on benchmarks. Only extreme quantization (INT4) causes visible degradation.

7. **"One inference engine is best for everything."** vLLM for diverse, bursty traffic. TensorRT-LLM for predictable, latency-critical workloads. TGI for HuggingFace ecosystem compatibility. The best system often uses multiple engines behind a router.

---

### Where It Is Used in Our Code

`src/phase129/phase129_inference_concepts.py` — We simulate the batch size vs. latency trade-off, showing the throughput knee and the p50/p95/p99 latency curves. We simulate memory fragmentation and how PagedAttention fixes it. We compute a mock cost-per-million-tokens table.

`src/phase129/phase129_inference_colab.py` — We benchmark real inference on Llama-3.2-3B-Instruct across three configurations, measuring TTFT, TPOT, throughput, and peak memory. We show how batched generation and KV caching translate to real speedups and cost savings.

(End of file)
