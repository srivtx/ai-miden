# Phase 107 Summary: On-Device LLMs

## What We Learned

This phase covered how large language models are adapted to run on mobile and edge devices. The core challenges are memory bandwidth, storage size, and compute constraints.

## Key Takeaways

1. **Mobile LLMs** use smaller architectures and aggressive compression to fit on phones (e.g., Phi, Gemma, Llama-3.2).
2. **Speculative Decoding** accelerates inference by drafting tokens with a small model and verifying with the large model, preserving exact outputs.
3. **Flash Attention** reduces memory bandwidth pressure by computing attention in tiles without materializing the full N x N matrix.

## Why It Matters

As AI moves to the edge, understanding quantization, efficient attention, and inference acceleration is essential for deploying LLMs in production on real consumer hardware.

## Navigation

- **Previous:** [Phase 106: AI for Science](../phase106/SUMMARY.md)
- **Next:** [Phase 108: Multimodal Reasoning](../phase108/SUMMARY.md)
