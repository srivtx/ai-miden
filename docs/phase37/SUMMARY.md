← [Previous: Phase 36: Speculative Decoding](docs/phase36/SUMMARY.md) | [Next: Phase 38: Scaling Laws & Compute-Optimal Training](docs/phase38/SUMMARY.md) →

---

## Phase 37 Summary: Retrieval-Augmented Generation (RAG)

**The Question:** "LLMs only know their training data. They cannot access your private documents, today's news, or real-time information. How do you ground their answers in external knowledge without retraining?"

---

### What We Learned

1. **Retrieval-Augmented Generation (RAG)**
   - Augments the LLM prompt with relevant documents retrieved from a knowledge base
   - Pipeline: embed documents → store in vector database → embed query → retrieve top-k → inject into prompt → generate
   - The LLM does not need to "know" the answer; it reads and synthesizes provided context

2. **Vector Database**
   - Stores documents as high-dimensional embeddings
   - Supports fast approximate nearest-neighbor search
   - Documents with similar meanings are close in embedding space, even with different words

3. **Embedding Retrieval**
   - Converts text to dense vectors using embedding models (BERT, E5, BGE)
   - Cosine similarity measures semantic relevance
   - Enables matching meaning instead of keywords

4. **Context Injection**
   - Formats retrieved documents into the prompt as "Context"
   - Standard format: context + question + answer prompt
   - Grounds generation in real text, dramatically reducing hallucination

---

### Results

- On a toy corpus of 10 documents about Acme Corp:
  - Retrieval successfully found relevant documents for all 5 queries
  - Without RAG, the model had no access to private data
  - With RAG, correct documents were retrieved by cosine similarity
  - The demo shows the full pipeline: embedding → retrieval → injection → generation

---

### Phase 37 Files

| File | Purpose |
|---|---|
| `docs/phase37/what_is_retrieval_augmented_generation.md` | Core RAG concept and pipeline |
| `docs/phase37/what_is_vector_database.md` | Storing and searching document embeddings |
| `docs/phase37/what_is_embedding_retrieval.md` | Semantic matching via dense vectors |
| `docs/phase37/what_is_context_injection.md` | Formatting retrieved documents into prompts |
| `src/phase37/phase37_rag.py` | Toy RAG with bag-of-words retrieval (NumPy) |
| `src/phase37/phase37_rag_colab.py` | Neural embedder + generator with RAG pipeline (PyTorch) |

---

### Connects To

- **Phase 27 (Agentic AI):** RAG is the primary tool for knowledge retrieval in agent systems
- **Phase 28 (Multimodal AI):** Multimodal RAG retrieves images, tables, and audio alongside text
- **Phase 32 (Foundation Models):** RAG is how most users interact with foundation models in production
- **Phase 35 (LoRA):** RAG + fine-tuning is the dominant production paradigm for LLM applications

---

### What You Should Remember

> **RAG is like a lawyer with a paralegal.** The lawyer (LLM) has general knowledge from law school. The paralegal (retriever) fetches relevant case law. The lawyer reads the cases and writes the argument. Without the paralegal, the lawyer might misremember or hallucinate a precedent. With the paralegal, the argument is grounded in real documents.

---

← [Previous: Phase 36: Speculative Decoding](docs/phase36/SUMMARY.md) | [Next: Phase 38: Scaling Laws & Compute-Optimal Training](docs/phase38/SUMMARY.md) →