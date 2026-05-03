# What is a Mobile LLM?

## 1. Problem Statement

Large language models with billions of parameters require powerful GPUs and substantial RAM, making them inaccessible on smartphones, tablets, and edge devices. Mobile apps need low latency, offline capability, and battery efficiency, which full-scale LLMs cannot provide.

## 2. Definition

A **Mobile LLM** is a language model optimized to run inference on resource-constrained devices such as phones and IoT hardware. Techniques include model compression (quantization, pruning, distillation), efficient architectures (smaller attention variants), and specialized inference engines. Examples include Microsoft Phi, Google Gemma, and Meta Llama-3.2.

## 3. Analogy

A desktop LLM is like a full-sized library reference desk with every book ever written. A mobile LLM is like a pocket guidebook: it cannot answer every question, but it covers the most important topics and fits in your pocket.

## 4. Example

Llama-3.2 1B and 3B variants are designed specifically for edge devices. They use grouped-query attention and training optimizations to maintain useful performance at a fraction of the size of 70B+ models, enabling on-device summarization and translation.

## 5. Common Confusion

Mobile LLMs are NOT just smaller versions of big models with no changes. They often use architectural modifications (e.g., GQA, sliding window attention) and aggressive quantization that require careful calibration to avoid catastrophic accuracy loss.

## 6. Code Location

See `src/phase107/phase107_on_device.py` for a NumPy simulation of model size vs memory and how INT4 quantization reduces footprint.
