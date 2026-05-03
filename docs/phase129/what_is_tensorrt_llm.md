## What Is TensorRT-LLM?

---

### The Problem

You have an NVIDIA A100 and you are running vLLM. Throughput is good, but your latency-sensitive application still stutters. Profiling reveals that 40% of the GPU time is spent in Python overhead, CUDA kernel launch gaps, and redundant memory copies. The model is spending milliseconds not computing, just waiting. You need the math to run as close to the hardware limit as possible, with fused kernels, static graphs, and quantized weights that the tensor cores can chew through at maximum throughput.

---

### Definition

**TensorRT-LLM** is NVIDIA's production inference engine that compiles transformer models into highly optimized execution graphs for NVIDIA GPUs. It fuses layers into single CUDA kernels, converts weights to INT8 or FP8, and builds a static engine that eliminates Python dispatch overhead. The result is the highest possible throughput and lowest possible latency on NVIDIA hardware, at the cost of a longer compile step and less scheduling flexibility than vLLM.

**How it works:**
```
Standard PyTorch inference:
  Python loop → dispatch matmul → dispatch softmax → dispatch add
  → dispatch LayerNorm → dispatch next matmul ...
  Overhead: hundreds of kernel launches per layer

TensorRT-LLM:
  Compile entire layer graph into one fused kernel
  Weights quantized to FP8/INT8 offline
  At runtime: single kernel launch per layer
  Overhead: near zero
```

**Key techniques:**
- **Kernel fusion:** multiple operations (matmul, bias, activation, norm) are fused into a single CUDA kernel, eliminating intermediate memory writes and kernel launch latency
- **Graph optimization:** the entire model is compiled into a static execution plan; no Python interpreter touches the forward pass
- **FP8/INT8 inference:** weights and activations are quantized to 8-bit formats that NVIDIA tensor cores process at 2× the throughput of FP16
- **Multi-GPU tensor parallelism:** the engine can shard layers across GPUs at compile time with no runtime communication overhead

**Why this matters:**
- TensorRT-LLM can be 1.5-3× faster than vLLM on pure throughput benchmarks for identical models on identical NVIDIA GPUs
- Latency for the first token (TTFT) drops significantly because the prompt is processed by fused attention kernels
- FP8 inference nearly doubles effective batch capacity without buying more GPUs

---

### Real-Life Analogy

A hand-built race car vs. a factory sports car.
- **Standard inference (PyTorch/vLLM):** A factory sports car with a good engine but standard suspension, road-legal tires, and a comfortable interior. It is fast, versatile, and easy to drive every day. But every gear shift has a tiny delay, and the air conditioning steals horsepower.
- **TensorRT-LLM:** A hand-built race car with the interior stripped out, tires glued to the track, and the engine tuned to a single octane of fuel. It is not comfortable, it takes a week to build, and you cannot easily swap the engine. But on race day, nothing else comes close.
- **The trade-off:** You choose the race car when you know the track (model, batch size, sequence length) in advance and need the absolute best lap time. You choose the sports car when you need to carry passengers, drive in the rain, or switch tracks mid-season.

---

### Tiny Numeric Example

**Llama-3-8B, batch_size=8, sequence_length=1024 on an A100:**

**Standard PyTorch (FP16):**
```
Prompt processing:  32 layers × 8 requests × 1024 tokens
  Each layer: ~2.3 ms (kernel launch + compute)
  Total prompt time: 294 ms
Token generation:   ~14 ms per token (single token per request)
Throughput:         571 tokens/sec (8 × 1 / 0.014)
Memory:             18.2 GB (FP16 weights + KV cache)
```

**TensorRT-LLM (FP8):**
```
Compile time:       8 minutes (one-time cost)
Prompt processing:  fused kernel, 89 ms total
Token generation:   ~5.2 ms per token
Throughput:         1,538 tokens/sec
Memory:             10.1 GB (FP8 weights + compressed KV cache)
```

**Comparison:**
```
Metric                PyTorch    TensorRT-LLM    Improvement
----------------------------------------------------------------
TTFT (prompt)         294 ms     89 ms           3.3× faster
TPOT (per token)      14 ms      5.2 ms          2.7× faster
Throughput            571 tok/s  1,538 tok/s     2.7× higher
Memory                18.2 GB    10.1 GB         45% less
```

**The shift:** TensorRT-LLM trades compile-time flexibility for runtime performance. Every millisecond of latency is squeezed out by fusing operations and quantizing weights.

---

### Common Confusion

1. **"TensorRT-LLM trains models."** No. It is inference-only. You train in PyTorch, export weights, and compile them into a TensorRT engine.

2. **"TensorRT-LLM works on AMD or Apple GPUs."** No. It is NVIDIA-only because it relies on CUDA, cuBLAS, and tensor-core-specific kernels.

3. **"FP8 inference loses too much quality."** For most chat and completion tasks, FP8 models score within 0.5% of FP16 on benchmarks. The degradation is measurable on tiny numeric tasks but invisible to end users.

4. **"TensorRT-LLM is always faster than vLLM."** Not always. vLLM's continuous batching and prefix caching can outperform TensorRT-LLM on workloads with highly variable request lengths or heavy prefix sharing. TensorRT-LLM wins when the workload is predictable.

5. **"You need to rewrite your model in C++ to use TensorRT-LLM."** No. You use Python APIs to build the engine from a HuggingFace checkpoint. The runtime is C++, but the setup is Python.

6. **"Compile time is a runtime cost."** The compile ("build") step happens once when you deploy or update the model. It is not paid per request. However, it does mean you cannot dynamically change model architecture without rebuilding.

7. **"TensorRT-LLM and ONNX are the same thing."** ONNX is a model exchange format. TensorRT-LLM is a compiler and runtime. You can convert ONNX to TensorRT, but TensorRT-LLM has specialized transformer layers that ONNX does not express natively.

---

### Where It Is Used in Our Code

`src/phase129/phase129_inference_concepts.py` — We simulate the effect of kernel fusion and quantization by showing how reduced per-layer overhead and smaller weight footprints translate to higher throughput. We compare "fused" vs. "unfused" latency curves.

`src/phase129/phase129_inference_colab.py` — We benchmark real inference on Llama-3.2-3B-Instruct using HuggingFace baseline and vLLM. We discuss where TensorRT-LLM would fit in the comparison and note the compile-time trade-off.

(End of file)
