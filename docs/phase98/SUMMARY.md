# Phase 98: System-2 Reasoning & o1-Style Training — Summary

This phase explored methods for making models "think longer" and more reliably at inference time.

## Key Concepts

- **Process Reward Model (PRM):** Provides step-by-step rewards during reasoning, enabling early detection of errors and more efficient search.
- **Chain-of-Thought (CoT):** Explicit intermediate reasoning steps that decompose complex problems and improve model reliability.
- **Self-Consistency:** Sampling multiple reasoning chains and voting on the final answer to reduce noise and boost accuracy.

## Takeaway
Longer reasoning and search at inference time (System-2) can outperform simply scaling model size. The key is providing the right training signals (PRM) and aggregation strategies (self-consistency) to make that search effective.

## Navigation

- **Previous:** Phase 97 — Extreme Context Windows (100K+)
- **Next:** Phase 99 — Video & 3D Generation
