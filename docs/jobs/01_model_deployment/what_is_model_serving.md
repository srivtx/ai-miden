## Why it exists (THE PROBLEM)

You trained a model. Loss is 0.5. Samples look great. Now what? You have a 38MB `.pt` file and no way to serve it. A production model needs to handle concurrent requests, batch inference, GPU memory management, health checks, and scale from 1 to 10,000 requests/second — all while staying within GPU VRAM.

A FastAPI endpoint with `model.generate()` is not production. One request at a time. Blocking the event loop. No batching. No GPU memory optimization. If two users hit `/complete` simultaneously, the second waits for the first to finish. At 100 concurrent users, latency spikes to 50 seconds.

**Model serving** solves this. Triton, TorchServe, vLLM, TGI are all production-grade serving frameworks. They handle batching, scheduling, KV-cache management, multi-GPU, and zero-copy tensor transfer. The difference: FastAPI = 1 request/second, vLLM = 100 requests/second on the same GPU.

## Definition (very simple)

**Model serving** is the layer between your trained weights and the users. It takes incoming requests, batches them together (tokens from multiple users are processed in one forward pass), manages GPU memory (allocates KV cache per sequence, evicts when full), and returns responses. The serving framework handles all the infrastructure so you just write the model definition.

The key innovations:
- **Continuous batching:** When a new request arrives mid-generation, add it to the current batch immediately (not at the next `batch()` boundary)
- **Paged attention:** KV cache is stored in fixed-size blocks (pages). When a sequence needs more memory, allocate a new page. Old pages can be evicted (LRU). No pre-allocation.
- **Prefix caching:** If two requests share a prefix (e.g., the same system prompt), compute the KV cache for that prefix once and reuse it.

## Real-life analogy

**FastAPI = a single cashier at a grocery store.** One customer at a time. If someone can't find their wallet, the line stops. 10 customers = 10 minutes.

**vLLM = self-checkout with a conveyor belt.** Items from multiple customers can be on the belt simultaneously. The scanner processes them as fast as they come. If one customer is slow, the belt keeps moving. 10 customers = 3 minutes.

**Continuous batching = never stopping the conveyor belt.** When a new item appears, it goes on immediately. You don't wait for the current batch to finish before starting the next.

**Paged attention = a parking lot.** When a car arrives, assign it a spot. When it leaves, free the spot for the next car. Fixed-size spots (pages) mean you never waste space. The lot can hold N cars at any time. If full, the newest car waits.

## Tiny numeric example

Without continuous batching:
```
Time 0ms:  Request A arrives (need 100 tokens). Start generation.
Time 50ms: Request B arrives. Must wait. GPU idle during A's generation.
Time 200ms: A completes (100 tokens × 2ms). 
Time 200ms: B starts. GPU was idle for 150ms.
Time 400ms: B completes.
Throughput: 2 requests in 400ms = 5 req/s. GPU utilization: 50%.
```

With continuous batching:
```
Time 0ms:   Request A enters batch. Batch size = 1.
Time 50ms:  Request B arrives. Joined to batch immediately. Batch = 2.
Time 55ms:  Request C arrives. Batch = 3.
Time 0-200ms: GPU processes batch=1→2→3→2→1. No idle time.
Time 220ms: All complete.
Throughput: 3 requests in 220ms = 13.6 req/s. GPU utilization: 91%.
```

## Key properties

| Property | FastAPI naive | vLLM / Triton |
|---|---|---|
| Concurrent requests | 1 (blocking) | 100+ (continuous batching) |
| GPU utilization | 20-50% | 80-95% |
| KV cache | O(n) per request, pre-allocated | Paged, O(active_pages), allocated on demand |
| Latency at 100 req/s | 50+ seconds | 2-3 seconds |
| Memory overhead | 2× (model + cache) | 1.2× (paged + sharing) |
| Prefix sharing | No (redundant compute) | Yes (cache once, reuse) |

## Tech comparison: serving frameworks

| Framework | Best for | Key feature |
|---|---|---|
| **vLLM** | LLM serving | Paged attention, fastest open-source |
| **Triton** | General-purpose | Multi-framework (TF, PT, ONNX), ensemble |
| **TorchServe** | PyTorch models | Native PyTorch, easy to set up |
| **TGI** (Text Gen Inf) | HuggingFace models | Watermarking, safety, streaming |
| **Ray Serve** | Complex pipelines | GPU scheduling, auto-scaling |
| **FastAPI** | Prototypes / demos | Simple, no dependencies |

## Connection to our projects

**cortexcode:** Replace `cortexcode_api.py` with a vLLM-compatible serving layer. Wrap the model in vLLM's `LLM` interface. Gain: 10× throughput, continuous batching, KV cache paging. cortexcode goes from 1 request/second to 10-50. Paged attention lets it handle 100 concurrent users on T4.

**The transition:** `python cortexcode_api.py --model cortexcode.pt` becomes:
```
python -m vllm.entrypoints.api_server --model /path/to/cortexcode --max-num-seqs 100
```
Same model, same weights, 10× the throughput, zero code changes in the model itself.
