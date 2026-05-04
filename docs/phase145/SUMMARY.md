## Phase 145 Summary: Knowledge Graphs with LLMs (GraphRAG)

This phase introduces **GraphRAG** — retrieval-augmented generation powered by knowledge graphs. We covered three core concepts:

---

### Terms Introduced

1. **GraphRAG** — Using structured knowledge graphs (entities + relationships) as a retrieval layer instead of flat text chunks. Excels at multi-hop reasoning where answers live in connections, not isolated paragraphs.

2. **Entity Resolution** — Mapping ambiguous textual mentions ("Apple," "Apple Inc.," "the Cupertino giant") to canonical entities. Includes coreference resolution for pronouns and nominals. The hardest and most error-prone step in graph construction.

3. **Graph Traversal Reasoning** — Walking graph edges to retrieve subgraph evidence, then using an LLM to synthesize a natural-language answer. Combines the explicit structure of graphs with the flexible reasoning of language models.

---

### Key Takeaways

- Vector RAG retrieves chunks by semantic similarity. It fails when the answer requires connecting facts across multiple chunks.
- GraphRAG extracts entities and relations, builds a graph, and traverses it to answer multi-hop questions with explicit, inspectable paths.
- Entity resolution is the bottleneck: unresolved aliases fragment the graph and break traversal.
- Graph traversal alone is not enough. The LLM interprets the retrieved subgraph and maps it to the user's question.
- These three concepts form a pipeline: extract -> resolve -> traverse -> reason.

---

### Curriculum Connections

- **Phase 47 (Vector Databases):** GraphRAG complements vector retrieval; hybrid systems use both.
- **Phase 50 (RAG):** Standard RAG is the baseline that GraphRAG improves upon for structured reasoning.
- **Phase 146 (Continual Pretraining):** A stale model produces stale entity extractions; continual updates keep the knowledge graph current.

(End of file)
