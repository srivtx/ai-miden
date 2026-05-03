# Frontier Gap Analysis: What a Lead ML Engineer at Moonshot AI / Anthropic Needs That We Do Not Yet Teach

> Based on recent arxiv trends (May 2026), Anthropic's published research priorities, and DeepSeek/Moonshot AI's public technical work.

---

## The Short Version

Our 110 phases cover the fundamentals, mainstream architectures, and established training pipelines well. But a lead engineer at a frontier lab works on things that are **one research cycle ahead** of what is in textbooks. Here are the 10 categories where our coverage is thin or missing entirely.

---

## Category 1: FP8 / Low-Precision Training and Inference

**Why it matters:** NVIDIA H100/B200 and AMD MI300 have native FP8 support. Training in FP8 is not "quantization after training" — it is training IN FP8 from step 1. This requires different optimizer states, different gradient scaling, and different numerical stability techniques. Anthropic and Moonshot both train in mixed precision (BF16/FP8) at scale.

**What we cover:** Phase 45 (quantization for inference), Phase 83 (GPU kernels conceptually).

**What is missing:**
- How FP8 tensor cores work (E4M3 vs E5M2 formats)
- Per-tensor vs per-block scaling
- Delayed scaling (NVIDIA's recipe)
- Gradient scaling in FP8 (not just loss scaling)
- When FP8 training fails and why
- MXFP (AMD's competing format)

**Recent research:** NVIDIA's Transformer Engine, AMD's MI300 FP8 whitepapers.

**Recommended phase:** **Phase 111: FP8 and Low-Precision Training**

---

## Category 2: Multi-Token Prediction (MTP)

**Why it matters:** DeepSeek-V3 showed that predicting 4 tokens at once (instead of 1) speeds up training by ~2× with no quality loss. Meta has confirmed this independently. This is becoming standard for pre-training at frontier labs.

**What we cover:** Standard next-token prediction (Phase 21).

**What is missing:**
- The MTP loss function (multiple independent heads)
- Why MTP does not hurt quality (information theory argument)
- MTP for inference (acceptance of multiple tokens)
- The relationship between MTP and speculative decoding

**Recent research:** DeepSeek-V3 technical report, "Better & Faster Large Language Models via Multi-token Prediction" (Meta).

**Recommended phase:** **Phase 112: Multi-Token Prediction**

---

## Category 3: KV Cache Compression and Dynamic Memory

**Why it matters:** PagedAttention (Phase 90) solves allocation fragmentation. But it does not solve the fundamental problem: KV cache memory grows linearly with sequence length. Frontier models serve 1M+ token contexts. H2O, SnapKV, and PyramidKV drop "unimportant" tokens to compress the cache 2-10×.

**What we cover:** KV cache basics (Phase 25), PagedAttention (Phase 90).

**What is missing:**
- H2O: keep heavy-hitters, evict the rest
- SnapKV: observe which tokens matter during prefill, compress before generation
- PyramidKV: different compression ratios per layer
- StreamingLLM: keep sink tokens + recent window
- Dynamic memory compression during inference

**Recent research:** H2O (2023), SnapKV (2024), PyramidKV (2024), StreamingLLM (2023).

**Recommended phase:** **Phase 113: KV Cache Compression**

---

## Category 4: DeepSeek-R1 Full Pipeline (Cold Start → Pure RL → Distillation)

**Why it matters:** DeepSeek-R1 proved you can train reasoning models with ZERO human-annotated reasoning traces. Just SFT on a small curated set, then pure RL with verifiable rewards. The model invents chain-of-thought, self-reflection, and verification on its own. This changes how frontier labs think about alignment and training.

**What we cover:** GRPO (Phase 24, 98), reasoning (Phase 26, 42, 98).

**What is missing:**
- The cold-start problem: how to bootstrap reasoning without human CoT
- Rule-based reward models (not learned RM)
- The "aha moment" — emergent self-reflection during RL
- Distilling reasoning into small models (reasoning traces as training data)
- The rejection sampling step: filter bad reasoning, keep good
- Comparison: DeepSeek-R1 vs OpenAI o1 vs Anthropic's approach

**Recent research:** DeepSeek-R1 (Nature, Jan 2026), o1 system card.

**Recommended phase:** **Phase 114: DeepSeek-R1 and Emergent Reasoning**

---

## Category 5: Constrained Decoding and Structured Generation

**Why it matters:** Production LLMs must output valid JSON, SQL, or function calls. You cannot just prompt "output JSON" and hope. Constrained decoding forces the model to only emit valid tokens at each step. This is critical for agents, APIs, and reliable tool use.

**What we cover:** Tool use (Phase 27, 72), agents.

**What is missing:**
- Grammar-based decoding (Outlines, llama.cpp)
- Finite-state machine constraints
- JSON schema enforcement at the token level
- Performance overhead of constrained decoding
- Batch constrained decoding

**Recent research:** Outlines, XGrammar, llama.cpp grammar mode.

**Recommended phase:** **Phase 115: Structured Generation and Constrained Decoding**

---

## Category 6: Automated Red-Teaming and Scalable Oversight

**Why it matters:** Anthropic's Frontier Red Team and safety work (Apr 2026) focuses on automating the discovery of dangerous capabilities. Manual red-teaming does not scale to 100B+ parameter models. Automated red-teaming uses the model itself to find its own failure modes.

**What we cover:** Manual red-teaming (Phase 69), jailbreaking (Phase 67-68), Constitutional AI (Phase 101).

**What is missing:**
- Automated adversarial suffix generation (beyond GCG)
- Model-based red-teaming (using one model to attack another)
- Capability evaluation at scale (automated eval harnesses)
- Biosecurity and cybersecurity threat modeling
- Anthropic's Constitutional Classifiers
- Automated alignment researchers (Anthropic's April 2026 paper)

**Recent research:** Anthropic "Automated Alignment Researchers" (Apr 2026), "Constitutional Classifiers" (Feb 2025), "Exploration Hacking" (May 2026 arxiv).

**Recommended phase:** **Phase 116: Automated Red-Teaming and Scalable Oversight**

---

## Category 7: Data Mixing Laws and Curriculum Learning

**Why it matters:** Chinchilla (Phase 38) told us how to balance model size and data volume. But it said nothing about HOW TO MIX different data sources. What ratio of code vs math vs dialogue? Doremi and similar work answer this. Frontier labs treat data mixing as a hyperparameter optimization problem.

**What we cover:** Scaling laws (Phase 38), data engineering (Phase 89).

**What is missing:**
- Doremi: learn optimal data mixing weights
- DoReMi: domain reweighting with minimal compute
- Curriculum learning for pretraining (easy → hard)
- Capability gap diagnosis in training data
- Data source ablation at billion-token scale

**Recent research:** Doremi (2023), DoReMi (2023), "Diagnosing Capability Gaps in Fine-Tuning Data" (May 2026 arxiv).

**Recommended phase:** **Phase 117: Data Mixing Laws and Curriculum Learning**

---

## Category 8: Native Multimodal Architectures (Early Fusion)

**Why it matters:** LLaVA-style models (Phase 41) bolt a vision encoder onto a language model. This is "late fusion." Native multimodal models (Chameleon, Show-o) process images and text in the SAME embedding space from layer 1. This enables true interleaved reasoning and is where the field is heading.

**What we cover:** Vision-language (Phase 28, 41), multimodal data (Phase 103), cross-modal attention (Phase 108).

**What is missing:**
- Early fusion vs late fusion trade-offs
- Tokenizing images into discrete tokens (VQ-VAE for images)
- Interleaved pretraining (text and images mixed in one sequence)
- Unified architectures that handle text, image, and audio natively
- Training stability challenges of multimodal pretraining

**Recent research:** Chameleon (Meta), Show-o, Gemini native multimodal.

**Recommended phase:** **Phase 118: Native Multimodal Architectures**

---

## Category 9: Advanced Speculative Decoding and Draft Models

**Why it matters:** Speculative decoding (Phase 36) uses a small draft model to predict tokens, then the large model verifies. But draft models are hard to train. EAGLE uses the large model's own hidden states as draft inputs. Medusa adds multiple prediction heads. Tree attention verifies multiple draft paths at once. These are production techniques at frontier labs.

**What we cover:** Basic speculative decoding (Phase 36).

**What is missing:**
- EAGLE: exact speculative decoding with hidden-state input
- Medusa: multiple decoding heads on the base model
- Lookahead decoding: n-gram based, no draft model needed
- Tree attention: verify multiple draft sequences in parallel
- Speculative decoding for coding (where acceptance rates are high)

**Recent research:** EAGLE (2024), Medusa (2024), Lookahead (2024), Speculative Streaming.

**Recommended phase:** **Phase 119: Advanced Speculative Decoding**

---

## Category 10: Disaggregated Serving and Prefill/Decode Separation

**Why it matters:** LLM inference has two phases: prefill (process the prompt, compute-heavy) and decode (generate tokens, memory-bandwidth-bound). These have opposite hardware needs. Prefill wants compute. Decode wants memory bandwidth. Frontier serving systems (vLLM, TensorRT-LLM) now separate them onto different GPU pools.

**What we cover:** vLLM, continuous batching (Phase 90), inference serving.

**What is missing:**
- Why prefill and decode have different compute/memory profiles
- Disaggregated serving architecture
- Chunked prefill (interleave prefill and decode on the same GPU)
- Load balancing between prefill and decode workers
- Cost modeling for disaggregated serving

**Recent research:** DistServe (2024), SplitWise, vLLM disaggregated serving.

**Recommended phase:** **Phase 120: Disaggregated Serving and Prefill/Decode Separation**

---

## Bonus: Emerging Areas from Recent Papers

| Paper / Trend | Why It Matters | Gap in Our Course |
|---|---|---|
| **Exploration Hacking** (May 2026) | LLMs can learn to resist RL training. Critical for alignment safety. | No coverage of adversarial training dynamics |
| **Dynamic Model Merging** (May 2026) | Merging models at inference time based on input. | Phase 43 covers static merging, not dynamic |
| **Cost-Aware Learning** (May 2026) | Optimizing training for dollar cost, not just loss. | No coverage of cost-aware optimization |
| **Physical Foundation Models** (May 2026) | Fixed hardware implementations of LLMs. | No hardware/ML crossover content |
| **Latent-GRPO** (May 2026) | Reasoning in latent space, not token space. | GRPO is covered, but not latent reasoning |
| **Sparse Autoencoders for Concept Manifolds** (May 2026) | SAEs capture continuous concepts, not just discrete features. | Phase 100 covers SAEs but not manifolds |

---

## Recommended Priority Order

If you want to build these as new phases, here is the order that maximizes value for a frontier ML engineer:

**Immediate (highest impact, well-defined):**
1. **Phase 111: FP8 and Low-Precision Training** — Every frontier lab trains in FP8 now.
2. **Phase 112: Multi-Token Prediction** — Becoming standard for pretraining.
3. **Phase 113: KV Cache Compression** — Required for long-context serving.
4. **Phase 114: DeepSeek-R1 Full Pipeline** — The biggest training paradigm shift in 2025-2026.

**High (important for production):**
5. **Phase 115: Structured Generation and Constrained Decoding** — Required for reliable agents.
6. **Phase 116: Automated Red-Teaming and Scalable Oversight** — Anthropic's core research focus.
7. **Phase 119: Advanced Speculative Decoding** — 2-3× inference speedup with no quality loss.
8. **Phase 120: Disaggregated Serving** — Standard for production inference at scale.

**Medium (research frontier):**
9. **Phase 117: Data Mixing Laws and Curriculum Learning** — Optimizes the most expensive part (data).
10. **Phase 118: Native Multimodal Architectures** — Where multimodal is heading.

---

## What This Means for the Course

We have two options:

**Option A: Add 10 new phases (111-120)** as a "Frontier Track" that sits on top of the existing 110.

**Option B: Create deep-dive supplements** for existing phases rather than new phases. For example, expand Phase 36 (speculative decoding) with EAGLE/Medusa, expand Phase 90 with KV cache compression, etc.

**My recommendation:** Option A. The 10 topics above are substantial enough to each warrant a full phase. They also represent a natural "second pass" through the curriculum — the student has completed 110 phases and now wants to work at a frontier lab.

Which approach do you prefer? And which topics from the list above resonate most with what you see at Moonshot AI / Anthropic?
