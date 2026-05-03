## What Is Model Serving?

---

### The Problem

You spent months training a state-of-the-art language model. It scores perfectly on your benchmark. Then you deploy it. One user sends a request and gets an answer in 50 milliseconds. Ten users send requests at the same time and the tenth user waits 5 seconds. One hundred users hit your API and the server crashes with an out-of-memory error. The model is brilliant, but the infrastructure around it is broken. How do you turn a research checkpoint into a production system that is fast, reliable, and cost-efficient at scale?

---

### Definition

**Model serving** is the infrastructure layer that exposes trained machine learning models as network APIs (typically REST or gRPC), queues incoming user requests, batches them intelligently, and continuously balances two opposing goals: **latency** (how long one user waits) and **throughput** (how many total users the system can help per second).

**Key mechanisms:**
- **API endpoint:** A URL that accepts input data and returns model predictions
- **Request queue:** A buffer that holds incoming requests so the GPU never sits idle
- **Batching:** Grouping multiple requests into one forward pass to amortize fixed overhead
- **Load balancing:** Distributing traffic across multiple replicas so no single GPU is overwhelmed

**Why this matters:**
- A GPU running one sample at a time is often 80% idle
- Batching 8 requests can raise throughput 3-5x with only a small latency increase
- But batching 64 requests may double latency, hurting real-time user experience
- Model serving is the art of finding the sweet spot

---

### Real-Life Analogy

A busy restaurant kitchen.
- **No serving layer:** One chef cooks one dish from start to finish, then starts the next. The kitchen is empty 70% of the time while the chef plates. Customers with simple salads wait behind customers ordering a 7-course tasting menu.
- **Static batching:** The chef waits until 10 orders are queued, then cooks them all. If one order is a 7-course meal, the other 9 customers wait 45 minutes for their salads.
- **Model serving (dynamic):** A smart expediter groups orders by complexity, starts new dishes the moment a burner frees up, and caps any party at 8 orders so no table waits more than 15 minutes. Throughput is high, but no single customer suffers.

---

### Tiny Numeric Example

**Setup:** One GPU, one model, fixed overhead per forward pass = 20ms, per-token cost = 2ms.

**Single request (10 tokens):**
```
Latency = 20ms + (10 × 2ms) = 40ms
Throughput = 1 request / 0.040s = 25 requests/sec
```

**Static batch of 4 (each 10 tokens):**
```
Latency = 20ms + (4 × 10 × 2ms) = 100ms
Throughput = 4 requests / 0.100s = 40 requests/sec
Efficiency gain: 60% more throughput
```

**Batch of 16:**
```
Latency = 20ms + (16 × 10 × 2ms) = 340ms
Throughput = 16 / 0.340 = 47 requests/sec
```

**Result:** Throughput barely improved from batch 4 to batch 16, but latency exploded from 100ms to 340ms. Model serving must reject batch sizes that hurt latency without meaningful throughput gains.

---

### Common Confusion

1. **"Higher throughput always means lower latency."** No. Throughput is a system-level metric (total jobs per second). Latency is a user-level metric (time for my job). Aggressive batching raises throughput but often raises latency for every individual user.

2. **"Batching is just processing requests in parallel."** No. True GPU batching fuses requests into a single matrix multiplication. Simply running 4 Python threads still launches 4 separate kernels with 4x overhead.

3. **"Model serving is the same as model training."** No. Training optimizes for gradient throughput and convergence. Serving optimizes for request latency, queue stability, and memory fragmentation. The code paths are different.

4. **"REST API is the only way to serve models."** No. gRPC is common for internal microservices because it is lower-latency and binary. Triton, TorchServe, and vLLM all support both.

5. **"You should always maximize batch size to fill the GPU."** No. Real users abandon requests after 1-2 seconds. A batch size of 128 may give 5% more throughput but 10x latency, causing timeouts and retries that tank actual system capacity.

6. **"Model serving is only for cloud GPUs."** No. Edge devices, mobile phones, and browsers all need serving infrastructure, often using ONNX, CoreML, or TensorFlow Lite instead of cloud APIs.

7. **"One big server is cheaper than many small ones."** No. Large batches create head-of-line blocking. A fleet of smaller instances with load balancing often delivers lower p99 latency than one monolithic GPU.

---

### Where It Is Used in Our Code

`src/phase71/phase71_inference_deployment.py` — We simulate inference latency across batch sizes, compute throughput curves, and show the exact batch size where latency starts to dominate.

`src/phase71/phase71_inference_deployment_colab.py` — We build a FastAPI server mockup that accepts requests, batches them dynamically, and returns predictions, demonstrating why model serving is not just `model.generate()` in a loop.
