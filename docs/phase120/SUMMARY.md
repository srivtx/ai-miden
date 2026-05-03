← [Previous: Phase 119: Advanced Speculative Decoding](docs/phase119/SUMMARY.md) | [Next: Phase 121: TBD](docs/phase121/SUMMARY.md) →

---

## Phase 120: Disaggregated Serving and Prefill/Decode Separation

---

### What We Built

A NumPy simulation of LLM inference serving architectures. We modeled the prefill phase (compute-bound prompt processing) and decode phase (memory-bandwidth-bound token generation), showing how their hardware needs conflict when colocated. We simulated disaggregated serving with separate prefill and decode GPU pools, demonstrating 2-3x throughput improvements. We also simulated chunked prefill, showing how interleaving prefill chunks with decode steps eliminates starvation without extra hardware.

We also created a Colab script that profiles real LLaMA-3.2-3B inference on a T4 GPU, measuring prefill time vs. prompt length and decode tokens/sec. We calculate theoretical throughput gains from disaggregated serving and discuss why H100-class hardware is required for real-world deployment.

### Key Results

- **Prefill scaling:** time grows linearly with prompt length (compute-bound)
- **Decode scaling:** time grows linearly with output length (memory-bandwidth-bound)
- **Compute asymmetry:** decode achieves <10% compute utilization on the same GPU that achieves >70% during prefill
- **Disaggregated throughput gain:** 2-4x for batch size 8+ (simulated)
- **Chunked prefill benefit:** decode latency drops from 100ms to 12ms when interleaved with 256-token chunks
- **T4 limitation:** real disaggregation requires NVLink/InfiniBand for KV cache transfer; T4 is demonstration-only

### Concepts Covered

| Term | File |
|---|---|
| Prefill/Decode Separation | `what_is_prefill_decode_separation.md` |
| Disaggregated Serving | `what_is_disaggregated_serving.md` |
| Chunked Prefill | `what_is_chunked_prefill.md` |

### Connection to Next Phase

With efficient serving architectures in place, the next frontier is optimizing the model itself for inference. Phase 121 will cover **Model Compression and Distillation for Serving**, exploring how to shrink models without losing quality for production deployment.

### Files

- `docs/phase120/what_is_prefill_decode_separation.md`
- `docs/phase120/what_is_disaggregated_serving.md`
- `docs/phase120/what_is_chunked_prefill.md`
- `docs/phase120/SUMMARY.md`
- `src/phase120/phase120_serving_concepts.py`
- `src/phase120/phase120_serving_colab.py`

---

← [Previous: Phase 119: Advanced Speculative Decoding](docs/phase119/SUMMARY.md) | [Next: Phase 121: TBD](docs/phase121/SUMMARY.md) →
