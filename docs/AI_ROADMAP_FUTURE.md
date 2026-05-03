# AI Course: Future Expansion Roadmap

> **Status:** Paused. The core 82-phase curriculum (0-81) is complete and pushed.
> **When to resume:** After the DSA (docs_dsa/) module is complete.
>
> This document captures everything the current repo teaches well, everything it lacks for real-world frontier ML roles, and the planned phases/topics to fill those gaps.

---

## What We Teach Well (Strong Coverage)

| Area | Phases | Strength |
|---|---|---|
| Neural network fundamentals | 0-21 | Excellent — from linear regression to training a tiny GPT from scratch in NumPy |
| Transformer architecture | 17-20 | Excellent — attention, multi-head, positional encoding, BERT vs GPT |
| Fine-tuning & alignment | 22-24, 35, 64-66 | Strong — SFT, RLHF, DPO, LoRA, QLoRA |
| Inference optimization | 25, 36, 45 | Good — KV cache, quantization, speculative decoding, GGUF |
| Agentic & multimodal | 27-28, 41 | Good — ReAct, tool use, vision-language |
| Generative models | 29-31, 40 | Good — VAE, GAN, diffusion, flow matching |
| Safety & evaluation | 67-69 | Good — jailbreaking, red-teaming, safety eval |
| Specialized applied topics | 53-56, 57-62 | Good — RL, GNNs, distributed training, boosting, adversarial robustness, time series, federated learning, Bayesian NNs, AutoML, active learning |
| Domain applications | 73-81 | Good — speech/audio, recsys, XAI, fairness, unsupervised learning, object detection, causal inference, MLOps, continual learning |

---

## What We Lack (The Gaps for Real-World Roles)

### 1. Large-Scale Systems & Infrastructure

| Topic | Why It Matters | What We Would Build |
|---|---|---|
| **Custom CUDA Kernel Writing** | PyTorch ops are generic; fused kernels (e.g., FlashAttention) are 2-10x faster | Phase: "GPU Kernel Optimization" — write a simple vector-add CUDA kernel, profile memory bandwidth vs compute bound, understand occupancy |
| **NCCL & Multi-Node Communication** | Training 70B+ models requires GPUs across multiple nodes talking via InfiniBand | Phase: "Collective Communication" — simulate all-reduce, broadcast, reduce-scatter with MPI-like primitives, measure bandwidth vs latency |
| **Memory Profiling & Optimization** | OOM errors are the #1 debugging time sink in training | Phase: "Memory Engineering" — trace activation checkpointing, gradient accumulation, ZeRO-1/2/3 partitioning, memory-mapped datasets |
| **Checkpointing & Fault Tolerance** | A 1000-GPU job will crash; you must resume without losing days | Phase: "Resilient Training" — async checkpointing to object storage, checkpoint sharding, deterministic reseeding |
| **JAX / XLA / TPU Stack** | Anthropic, Google DeepMind, and many research labs use JAX, not PyTorch | Phase: "JAX & XLA" — JIT compilation, pmap for data parallelism, pjit for model parallelism, understanding XLA HLO |
| **Containerization & Orchestration** | Production training runs in Kubernetes with custom images | Phase: "ML Infrastructure" — Docker for ML, Kubernetes basics, Kubeflow/Polyaxon/Metaflow overview |

### 2. Research-Grade Rigor & Novel Contributions

| Topic | Why It Matters | What We Would Build |
|---|---|---|
| **Paper Reading & Reproduction** | You cannot do research if you cannot read papers fast | Phase: "How to Read an AI Paper" — abstract triage, method archaeology, reproduction checklist, common statistical fallacies |
| **Experiment Design & Ablations** | Knowing *what* to vary is as important as *how* to train | Phase: "Rigorous Experimentation" — controlled ablations, significance testing, variance reduction, reporting standards |
| **Novel Architecture Design** | Eventually you invent things, not just use them | Phase: "Architecture Search & Design" — inductive bias, module substitution, scaling laws for depth vs width, compute-optimal shapes |
| **Mechanistic Interpretability at Scale** | Understanding what circuits do inside a 70B model | Phase: "Automated Circuit Discovery" — attribution patching at scale, SAE (Sparse Autoencoder) training, feature visualization |

### 3. Data Engineering at Scale

| Topic | Why It Matters | What We Would Build |
|---|---|---|
| **Web-Scale Data Pipelines** | Common Crawl is terabytes; filtering is the secret sauce | Phase: "Data Engineering for LLMs" — deduplication (MinHash), quality scoring (perplexity, classifier-based), language ID, PII removal |
| **Synthetic Data Generation** | Self-improvement requires generating training data | Phase: "Synthetic Data Bootstrapping" — rejection sampling, constitutional AI pipelines, verifier-augmented generation |
| **Multimodal Data Curation** | Aligning image-text, video-audio pairs at billion scale | Phase: "Multimodal Datasets" — contrastive filtering, CLIP-style scoring, temporal alignment for video |

### 4. Specialized Frontier Topics

| Topic | Why It Matters | What We Would Build |
|---|---|---|
| **Mixture of Experts (MoE) at Scale** | GPT-4, Mixtral, and DeepSeek use sparse MoE | Phase: "Sparse MoE Training" — load balancing loss, expert choice routing, capacity factor tuning |
| **Long Context (100K+ tokens)** | Processing books, codebases, conversations | Phase: "Extreme Context Windows" — Ring Attention, striped attention, Hierarchial KV cache, context compression |
| **Reasoning & Math** | o1, DeepSeek-R1 style reasoning chains | Phase: "System-2 Reasoning" — process reward models, tree search (MCTS), self-consistency at scale |
| **Multimodal Generation** | Sora, Stable Diffusion 3, video generation | Phase: "Video & 3D Generation" — latent video diffusion, 3D Gaussian splinting, DiT for spatiotemporal data |
| **Efficient Inference Serving** | vLLM, TensorRT-LLM, continuous batching | Phase: "Inference at Scale" — PagedAttention, prefix caching, speculative decoding with tree attention, request scheduling |
| **Alignment Beyond RLHF** | Constitutional AI, debate, scalable oversight | Phase: "Advanced Alignment" — iterated amplification, debate protocols, reward hacking detection |
| **Evaluation at Scale** | LMSYS arena, MMLU, HumanEval are just the start | Phase: "Benchmark Design" — constructing evaluations that actually measure capability, not memorization |
| **On-Device / Edge ML** | Running models on phones, AR glasses, robots | Phase: "Tiny ML & Edge Deployment" — Neural Architecture Search for latency, CoreML/TensorFlow Lite, quantization-aware training |
| **Biology & Science Applications** | AlphaFold, protein design, drug discovery | Phase: "AI for Science" — geometric deep learning, equivariant networks, diffusion for molecular design |

### 5. Soft Skills & Research Culture

| Topic | Why It Matters |
|---|---|
| **Open Source Contribution** | Building reputation through PRs to transformers, vLLM, axolotl |
| **Research Communication** | Writing blog posts, Twitter threads, conference talks |
| **Collaboration Tools** | Git workflows, code review, experiment tracking (Weights & Biases, MLflow) |
| **Reading Math** | Understanding proofs, convergence rates, information theory bounds |

---

## Proposed Future Phases (83-120 Rough Sketch)

**Systems Track (83-95)**
- 83: GPU Kernel Optimization (CUDA)
- 84: Memory Engineering & Activation Checkpointing
- 85: NCCL, InfiniBand & Multi-Node Training
- 86: JAX, XLA & TPU Programming
- 87: Checkpointing, Fault Tolerance & Determinism
- 88: Docker, Kubernetes & ML Orchestration
- 89: Data Engineering at Scale (Web pipelines)
- 90: vLLM, TensorRT-LLM & Inference Serving
- 91: Experiment Tracking & MLOps Maturity
- 92: Benchmark Design & Evaluation Science
- 93: Paper Reading & Reproduction
- 94: Experiment Design & Statistical Rigor
- 95: Open Source & Research Communication

**Frontier Research Track (96-110)**
- 96: Sparse MoE Training at Scale
- 97: Extreme Context Windows (100K+)
- 98: System-2 Reasoning & o1-Style Training
- 99: Video & 3D Generation
- 100: Automated Circuit Discovery (MechInterp)
- 101: Advanced Alignment (Constitutional AI, Debate)
- 102: Synthetic Data Bootstrapping
- 103: Multimodal Data Curation
- 104: Architecture Search & Inductive Bias Design
- 105: Tiny ML & Edge Deployment
- 106: AI for Science (Protein, Molecules)
- 107: On-Device LLMs
- 108: Multimodal Reasoning
- 109: World Models & Model-Based RL
- 110: Test-Time Compute Scaling (Search, Refinement)

**Capstone Track (111-120)**
- 111-115: Reproduce a major paper from scratch (e.g., Chinchilla, LLaMA, DeepSeek-R1)
- 116-120: Original research project — train a model, evaluate it, write it up

---

## When to Resume

Resume this roadmap after:
1. `docs_dsa/` module is complete (all 18 NeetCode patterns with deep intuition)
2. DSA problem-solving speed is comfortable (can solve medium in 20-30 min)
3. Interview loop for target roles is approaching

The DSA module builds the algorithmic thinking muscle that underlies ALL of the above — especially systems design, efficient implementations, and understanding why certain architectures are faster than others.

---

*Document created: 2026-05-03*
*Last AI commit: bde7b00 (Phases 0-81 complete)*
