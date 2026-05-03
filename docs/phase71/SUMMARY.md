← [Previous: Phase 70: Domain Adaptation — Custom Assistants](docs/phase70/SUMMARY.md) | [Next: Phase 72: Real Agents with Tool Use](docs/phase72/SUMMARY.md) →

---

## Phase 71: Inference & Deployment

---

### What We Built

A NumPy simulation of GPU inference dynamics, plus a Colab script for real transformer benchmarking, ONNX export, and FastAPI serving. We explored the tension between latency and throughput, demonstrated why vLLM's continuous batching matters, and showed how to optimize batches and deploy models cross-platform.

### Key Results

- **Optimal batch size:** ~16 for this synthetic workload
- **Max throughput:** ~1,500 tokens/sec (synthetic GPU model)
- **Batching speedup:** ~4.5x vs. single-request inference
- **Dynamic batching padding reduction:** ~45% less wasted compute
- **ONNX export:** Verified portable graph export from PyTorch
- **FastAPI mockup:** Production-ready server architecture with comments

### Concepts Covered

| Term | File |
|---|---|
| Model Serving | `what_is_model_serving.md` |
| vLLM | `what_is_vllm.md` |
| Batch Optimization | `what_is_batch_optimization.md` |
| ONNX Export | `what_is_onnx_export.md` |

### Connection to Next Phase

Serving is only half the battle. Once a model is deployed, how do you monitor it, detect drift, and update it without downtime? Phase 72 covers **MLOps & Model Monitoring** — observability, A/B testing, and automated retraining pipelines.

### Files

- `docs/phase71/what_is_model_serving.md`
- `docs/phase71/what_is_vllm.md`
- `docs/phase71/what_is_batch_optimization.md`
- `docs/phase71/what_is_onnx_export.md`
- `docs/phase71/SUMMARY.md`
- `src/phase71/phase71_inference_deployment.py`
- `src/phase71/phase71_inference_deployment_colab.py`
- `src/phase71/inference_deployment.png`

---

← [Previous: Phase 70: Domain Adaptation — Custom Assistants](docs/phase70/SUMMARY.md) | [Next: Phase 72: Real Agents with Tool Use](docs/phase72/SUMMARY.md) →