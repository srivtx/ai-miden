## What Is vLLM?

---

### The Problem

You want to serve a 70-billion-parameter LLM. Standard inference frameworks process sequences one at a time or in static batches. The KV cache — the memory storing key/value vectors for every token so the model can attend to past context — is allocated as one contiguous block per sequence. When a sequence finishes early, its block is freed but leaves holes. When a new sequence arrives, it needs a new contiguous block, but none are large enough. The GPU memory becomes a Swiss cheese of fragments. Meanwhile, static batching forces the GPU to wait until every sequence in the batch finishes before starting new ones. For a 70B model on an A100, this means thousands of dollars per day of GPU time spent doing nothing.

---

### Definition

**vLLM** is an open-source inference and serving engine specifically designed for large language models. It solves the memory fragmentation and batching inefficiency problems through two core innovations:

1. **PagedAttention:** The KV cache is divided into fixed-size "pages" (blocks) that can be stored non-contiguously, just like virtual memory in an operating system. When a sequence finishes, its pages are returned to a free list and reused immediately by new sequences. No fragmentation, no wasted memory.

2. **Continuous batching (inflight batching):** New requests are added to the running batch immediately when another request finishes its generation step. The GPU never waits for the slowest sequence in a batch; it is always running at full capacity.

**Why this matters:**
- PagedAttention enables 2-4x more concurrent requests on the same GPU
- Continuous batching eliminates idle GPU cycles between batches
- Combined, vLLM routinely delivers 3-5x higher throughput than naive frameworks

---

### Real-Life Analogy

A highway toll plaza.
- **Naive inference:** Each car gets a dedicated lane from entry to exit. If a car breaks down, the lane is closed forever. New cars cannot use that lane even though it is empty. Cars also cannot enter until a full "convoy" of 10 cars has assembled.
- **PagedAttention:** The toll plaza has a pool of reusable booths. A car uses exactly as many booths as it needs (one per axle, say), and releases them immediately. The booths are reassigned to the next car in microseconds. No lane sits empty because it was "reserved" for a car that already left.
- **Continuous batching:** Cars do not wait for the entire convoy to clear the plaza. As soon as one car passes the last booth, a new car enters the first booth. The plaza is always processing the maximum number of cars it can handle.

---

### Tiny Numeric Example

**Setup:** GPU can hold 100 KV cache pages. 3 requests arrive:
- Request A: 10 tokens
- Request B: 30 tokens
- Request C: 20 tokens

**Naive contiguous allocation:**
```
A gets pages 0-9  (10 pages)
B gets pages 10-39 (30 pages)
C gets pages 40-59 (20 pages)
Total used: 60 pages, 40 free (pages 60-99)
```
Now Request A finishes. Pages 0-9 are freed, but they are a small block.
Request D arrives needing 25 pages. No contiguous block of 25 exists (0-9 is only 10, 60-99 is 40 but fragmented conceptually). D cannot start until B or C finishes.

**PagedAttention (vLLM):**
```
A gets pages [3, 7, 12, 45, 81, 90, 91, 92, 93, 94]  (scattered)
B gets pages [0, 1, 2, 4, 5, 6, ...]  (scattered)
C gets pages [...]  (scattered)
```
When A finishes, all 10 pages return to the free list.
Request D needs 25 pages. vLLM assigns any 25 free pages — they do not need to be contiguous.
D starts immediately. GPU utilization stays at 100%.

**Throughput result:**
- Naive: D waits 10 more steps for B or C to finish. Idle GPU time = 10 steps.
- vLLM: D starts immediately. Throughput improvement on this micro-batch: ~30%.
- At scale with hundreds of requests: 3-5x throughput improvement.

---

### Common Confusion

1. **"vLLM is just a faster version of Hugging Face Transformers."** No. vLLM reimplements the entire attention kernel and scheduling layer. It is not a wrapper; it replaces the inference engine.

2. **"PagedAttention means the KV cache is stored on disk."** No. "Paging" is a memory management analogy, not disk swapping. All KV cache pages live in GPU memory; they are just allocated non-contiguously.

3. **"Continuous batching means all requests finish at the same time."** No. Requests finish whenever they reach an EOS token or max length. New requests hop in to fill the gap immediately. The batch composition changes at every generation step.

4. **"vLLM only works with Llama models."** No. vLLM supports GPT-2, Llama, Mistral, Falcon, ChatGLM, and many others through a unified model architecture abstraction.

5. **"PagedAttention has no overhead."** Not quite. The page table lookup adds a small compute cost, but it is negligible compared to the massive memory savings and elimination of fragmentation.

6. **"You cannot use vLLM with LoRA adapters."** This was once true, but vLLM now supports LoRA serving via `--enable-lora`, allowing multiple adapters to be hot-swapped without reloading the base model.

7. **"vLLM is only for cloud deployments."** No. vLLM runs on single GPUs, multi-GPU nodes, and can be containerized for Kubernetes. It is used in startups and hyperscalers alike.

---

### Where It Is Used in Our Code

`src/phase71/phase71_inference_deployment.py` — We simulate the difference between static and continuous batching by modeling request arrival times and showing how continuous batching keeps GPU utilization flat while static batching creates sawtooth idle periods.

`src/phase71/phase71_inference_deployment_colab.py` — We load a small model with vLLM (or transformers as fallback), run a benchmark comparing single-request latency against batched throughput, and demonstrate how the scheduler keeps the GPU saturated.
