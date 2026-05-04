## Phase 146 Summary: Continual Pretraining for LLMs

This phase covers how to update pretrained models over time without retraining from scratch, and why models inevitably decay if left frozen.

---

### Terms Introduced

1. **Continual Pretraining** — Updating a pretrained model on new, unlabeled data while minimizing catastrophic forgetting. Techniques include replay buffers, elastic weight consolidation, and adapters.

2. **Knowledge Editing** — Surgically modifying specific factual associations (e.g., "CEO of Twitter") without retraining. Methods like ROME and MEMIT locate and edit weights storing a single fact. Powerful but unreliable at scale due to side effects.

3. **Model Staleness** — The degradation of model accuracy as the real world diverges from training data. Driven by temporal drift in events, concepts, relationships, and language. Invisible until it causes harm.

---

### Key Takeaways

- Frozen models decay on time-sensitive tasks at roughly 4-6 percentage points per quarter.
- Naive fine-tuning on new data learns the new domain but catastrophically forgets the old.
- Replay buffers (mixing old and new data) are the most reliable production technique for reducing forgetting.
- Knowledge editing offers surgical precision for isolated facts but suffers from side effects and limited capacity.
- There is no free lunch: freshness and retention are always in tension. The goal is managed trade-offs, not perfection.

---

### Curriculum Connections

- **Phase 145 (GraphRAG):** A stale model extracts stale entities and relations; continual pretraining keeps the extraction layer current.
- **Phase 70 (Domain Adaptation):** Continual pretraining is domain adaptation over time, with the added challenge of preserving prior domains.
- **Phase 50 (RAG):** Retrieval mitigates staleness by fetching current documents, but the base model's internalized reasoning still degrades.

(End of file)
