## What Is a Mobile LLM?

---

## The Problem

Large language models with billions of parameters require powerful GPUs, substantial RAM, and constant cloud connectivity. A 70B-parameter model needs 140GB of memory at FP16 precision, far exceeding the 4-8GB available on a smartphone. Mobile apps need millisecond-level response times, offline capability for privacy, and battery efficiency for all-day use. How do you deliver useful language intelligence on a device that fits in a pocket?

---

## Definition

A **Mobile LLM** is a language model optimized to run inference on resource-constrained devices such as phones, tablets, and IoT hardware. Techniques include model compression (quantization, pruning, distillation), efficient architectures (grouped-query attention, sliding window attention), and specialized inference engines.

**How it works:**
```
Standard LLM:        70B parameters, FP16, 140 GB RAM, server GPU required

Mobile LLM pipeline:
  1. Distill to smaller architecture (1B-3B parameters)
  2. Replace full attention with grouped-query attention (reduces KV cache)
  3. Apply quantization-aware training → INT4 weights
  4. Optimize inference engine for mobile CPU/GPU/NPU

Result:              1B parameters, INT4, 0.5 GB RAM, runs on phone NPU
```

**Key techniques:**
- **Grouped-query attention (GQA):** multiple query heads share the same key/value heads, reducing memory bandwidth
- **Sliding window attention:** limits context to recent tokens, reducing quadratic growth
- **Aggressive quantization:** INT4 or mixed-precision weights with calibration-aware scaling
- **On-device inference engines:** executables optimized for ARM cores, mobile GPUs, or neural processing units

**Why this matters:**
- On-device LLMs enable private, offline assistance (e.g., translation, summarization)
- They reduce cloud API costs and latency for high-volume applications
- Examples: Microsoft Phi, Google Gemma, Meta Llama-3.2

---

## Real-Life Analogy

A desktop LLM is like a full-sized university library with every book ever written, staffed by research librarians who can answer any question given enough time. A mobile LLM is like a pocket field guide: it cannot answer every question, but it covers the most important topics, fits in your pocket, and works without an internet connection. The field guide is not a shrunken library; it is a fundamentally different product designed for a different context.

But the analogy understates the engineering challenge. A field guide is simply a smaller book. A mobile LLM is not simply a smaller model. It uses architectural modifications — grouped-query attention, shallower layers, and customized activation functions — that would be suboptimal at large scale but efficient on mobile hardware. It is trained with quantization in mind, so its weights naturally cluster into the 16 levels representable by INT4. It is compiled into a format that the phone's neural processing unit can execute with minimal overhead. The mobile LLM is a co-designed system of model, algorithm, and hardware.

The trade-off is between capability and accessibility. A mobile LLM will not write a doctoral thesis or debug a complex distributed system. But it can summarize an email, translate a menu, or draft a quick reply while preserving user privacy. For many real-world tasks, a 1B-parameter model running locally is more valuable than a 70B-parameter model running in the cloud, because latency is lower, connectivity is optional, and data never leaves the device.

---

## Tiny Numeric Example

**A 1B-parameter model deployed on a smartphone:**

**Memory footprint:**
```
Format    Bits/weight    Size (MB)    Relative
FP32          32          3,814        8.0x
FP16          16          1,907        4.0x
INT8           8            954        2.0x
INT4           4            477        1.0x
```

**Inference latency (token generation speed):**
```
Model              Device        Latency/token    Tokens/sec
70B FP16           A100 GPU      35 ms            28.6
7B FP16            RTX 4090      12 ms            83.3
3B INT4            Phone NPU      8 ms           125.0
1B INT4            Phone CPU     15 ms            66.7
```

**Accuracy on commonsense reasoning (normalized to 70B = 100%):**
```
70B FP16:    100%
7B FP16:      82%
3B INT4:      68%
1B INT4:      54%
```

**The shift:** A 1B-parameter INT4 model uses 0.5GB of memory and generates 67 tokens per second on a phone CPU, achieving 54% of the large model's reasoning score. For on-device tasks, this is often sufficient.

---

## Common Confusion

1. **"A mobile LLM is just a smaller version of a big model with no changes."** Mobile LLMs often use architectural modifications (GQA, sliding window attention, SwiGLU activations) that require careful design and calibration to avoid catastrophic accuracy loss.

2. **"Quantization to INT4 is always safe for mobile deployment."** INT4 reduces precision to 16 levels per weight. For some tasks, especially math reasoning and long-context retrieval, INT4 can cause significant degradation even with QAT.

3. **"Mobile LLMs cannot run on CPUs."** Modern ARM CPUs with NEON instructions can run INT4 LLMs at usable speeds for short contexts. NPUs and GPUs are faster, but CPU-only deployment is possible.

4. **"A 1B model is useless compared to a 70B model."** For summarization, translation, and classification, a 1B model can be surprisingly capable. The gap is largest for reasoning, coding, and long-context tasks.

5. **"Mobile LLMs do not need context length."** Even mobile use cases benefit from longer context: summarizing a long email thread or referencing earlier parts of a conversation. Sliding window and ring attention extend effective context on device.

6. **"On-device inference is always more private than cloud inference."** It is more private for the user query, but model weights and updates still raise supply-chain security questions. Privacy is improved, not guaranteed.

7. **"Mobile LLMs will replace cloud LLMs."** They complement cloud models. Complex tasks are offloaded to the cloud; simple, latency-sensitive, or privacy-critical tasks run locally. The future is hybrid.

---

## Where It Is Used in Our Code

`src/phase107/phase107_on_device.py` — We simulate model size versus memory footprint and quantization trade-offs for a toy linear layer. We compare FP32, INT8, and INT4 precision, plot size reduction, and show how quantization error accumulates across layers, illustrating why mobile LLMs require careful quantization-aware training and architectural design.
