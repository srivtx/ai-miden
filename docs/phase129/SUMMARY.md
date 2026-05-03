← [Previous: Phase 128: TBD](docs/phase128/SUMMARY.md) | [Next: Phase 130: Production Monitoring and MLOps](docs/phase130/SUMMARY.md) →

---

## Phase 129: Production Inference Engines (vLLM / TensorRT-LLM)

---

### What We Built

A NumPy simulation of production LLM inference optimization demonstrating why naive single-request generation fails at scale and how modern inference engines solve the problem. We simulated PagedAttention memory savings, continuous batching throughput gains, and the latency vs. batch size trade-off. We plotted throughput curves, latency percentiles, and memory fragmentation comparisons.

We also created a Colab script that benchmarks Llama-3.2-3B-Instruct with three inference methods: naive HuggingFace generation, HuggingFace with KV cache, and vLLM-style batched generation. We measured time to first token (TTFT), time per output token (TPOT), total throughput, and peak memory on 50 requests with varying prompt lengths. The results show that batched generation with KV caching is 5-10× faster than naive single-request inference.

### Key Results

- **PagedAttention memory savings:** 35-50% reduction in KV cache waste vs. contiguous allocation
- **Continuous batching throughput:** 10-16× higher than static single-request generation
- **Batch size sweet spot:** 4-8 for Llama-3.2-3B on T4; beyond 16 latency degrades faster than throughput grows
- **TTFT vs TPOT trade-off:** prompt processing dominates TTFT; token generation dominates TPOT
- **KV cache impact:** enabling cache reduces peak memory by ~20% and speeds generation by 2-3×
- **Cost per 1M tokens:** drops from $19.85 (single) to $0.49 (optimized continuous batching)

### Concepts Covered

| Term | File |
|---|---|
| vLLM | `what_is_vllm.md` |
| TensorRT-LLM | `what_is_tensorrt_llm.md` |
| Inference Optimization | `what_is_inference_optimization.md` |

### Connection to Next Phase

With the model now served efficiently, the next frontier is keeping it healthy in production. Phase 130 covers **Production Monitoring and MLOps**: tracking latency distributions, detecting input and output drift, setting up alerts, and running A/B tests between model versions so that deployment does not become a blind flight.

### Files

- `docs/phase129/what_is_vllm.md`
- `docs/phase129/what_is_tensorrt_llm.md`
- `docs/phase129/what_is_inference_optimization.md`
- `docs/phase129/SUMMARY.md`
- `src/phase129/phase129_inference_concepts.py`
- `src/phase129/phase129_inference_colab.py`

---

← [Previous: Phase 128: TBD](docs/phase128/SUMMARY.md) | [Next: Phase 130: Production Monitoring and MLOps](docs/phase130/SUMMARY.md) →
