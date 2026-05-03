# Research: RAG — Retrieval-Augmented Generation

**Status:** Missing from course. Should be Phase 36 or extension of Phase 27 (Agentic AI).
**Last Updated:** May 2026
**Sources:** Lewis et al. (2020), various surveys and implementations

---

## 1. The Problem

LLMs have two fundamental limitations:
1. **Knowledge cutoff:** They only know what was in their training data. They don't know today's news, your company's private documents, or real-time information.
2. **Hallucination:** When they don't know something, they make up plausible-sounding but false answers.

We need a way to give LLMs access to external, up-to-date, and private knowledge without retraining them.

## 2. What It Is

**RAG (Retrieval-Augmented Generation)** augments the LLM prompt with relevant documents retrieved from an external knowledge base.

### The RAG Pipeline

```
1. User asks: "What was our Q3 revenue?"
2. Retriever searches a vector database of company documents
3. Finds relevant chunks: ["Q3 Report: Revenue was $5.2M...", "Financial Summary Q3..."]
4. Constructs prompt:
   "Context: [retrieved documents]
    Question: What was our Q3 revenue?
    Answer:"
5. LLM generates answer based on the provided context
```

### Two-Stage Architecture

**Stage 1: Retrieval**
- Documents are split into chunks
- Each chunk is embedded into a vector (using an embedding model like BGE, E5, or OpenAI's text-embedding-3)
- Chunks are stored in a vector database (FAISS, Chroma, Pinecone, Weaviate)
- Query is embedded with the same model
- Top-k most similar chunks are retrieved

**Stage 2: Generation**
- Retrieved chunks are inserted into the prompt as context
- LLM generates answer conditioned on the context
- The LLM does not need to "know" the answer — it only needs to read and synthesize the provided text

## 3. Real-World Analogy

A lawyer preparing for a case. The lawyer (LLM) has general legal knowledge from law school (pre-training). But for this specific case, they need to research case law, statutes, and precedents (retrieval). They send a paralegal (retriever) to the law library to find relevant documents. The paralegal returns 5 key cases. The lawyer reads these cases and then writes their argument, citing specific passages. Without the paralegal, the lawyer might misremember a precedent or cite a case that doesn't exist (hallucination). With the paralegal, the argument is grounded in real documents.

## 4. Key Technical Details

### Chunking Strategy
- **Too small (sentence-level):** Loses context and relationships
- **Too large (document-level):** Dilutes relevance, exceeds context window
- **Optimal:** 200–500 tokens with overlap (sliding window)

### Embedding Models
| Model | Dimensions | Strength |
|---|---|---|
| text-embedding-ada-002 | 1536 | General purpose, OpenAI API |
| BGE-large-en | 1024 | Open source, strong performance |
| E5-mistral-7b-instruct | 4096 | Instruction-tuned, state-of-the-art |
| GTE-large | 1024 | Google, efficient |

### Similarity Metrics
- **Cosine similarity:** Most common, good for semantic search
- **Dot product:** Faster, works if embeddings are normalized
- **Maximum Inner Product Search (MIPS):** Used by FAISS for approximate nearest neighbors

### Advanced RAG Techniques

**Query Expansion:**
- Generate multiple variants of the query
- Retrieve for each variant, combine results

**Re-ranking:**
- Retrieve 100 chunks quickly (bi-encoder)
- Re-rank top 100 with a slower but more accurate cross-encoder
- Use top 5 for generation

**Self-RAG (2023):**
- LLM decides whether to retrieve at all
- If confident, answers directly
- If uncertain, retrieves and then answers
- Cites sources explicitly

**Corrective RAG (2024):**
- Evaluate retrieved documents for relevance
- If documents are irrelevant, fall back to web search
- If documents are relevant but insufficient, expand query and retrieve more

## 5. Common Confusion

- **RAG is not fine-tuning.** Fine-tuning changes the model weights. RAG leaves the model frozen and changes the prompt.
- **RAG does not eliminate hallucination.** The LLM can still misinterpret retrieved documents or synthesize them incorrectly. But it grounds the answer in real text.
- **Retrieval quality is the bottleneck.** A bad retriever that returns irrelevant documents makes RAG worse than no RAG. Garbage in, garbage out.
- **Context window limits matter.** If you retrieve 10 documents × 500 tokens each = 5000 tokens, that leaves less room for the actual answer in models with 8K context windows.
- **RAG is not just for Q&A.** It powers code assistants (retrieve relevant code), medical diagnosis (retrieve case studies), legal analysis (retrieve precedents), and customer support (retrieve documentation).

## 6. What We Would Build

A toy RAG system where:
- 10 short documents are embedded into a simple vector store
- User query is embedded and matched against documents
- Top-3 documents are injected into the prompt
- A tiny LLM generates the answer from the context
- Show the difference between answering with and without retrieval

## 7. Why It Matters Now

- **ChatGPT with browsing** and **Claude with tools** are RAG systems
- **Enterprise AI** is almost entirely RAG: companies connect LLMs to their internal document stores
- **OpenAI Assistants API** has built-in retrieval
- **LangChain and LlamaIndex** are entire frameworks built around RAG
- RAG + fine-tuning is the dominant paradigm for production LLM applications

## 8. Connection to Existing Phases

- **Phase 27 (Agentic AI):** RAG is the primary tool for knowledge retrieval
- **Phase 28 (Multimodal AI):** Multimodal RAG retrieves images, videos, and audio alongside text
- **Phase 32 (Foundation Models):** RAG is how most users interact with foundation models in production

---

## References

- Lewis et al. (2020): "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
- Asai et al. (2023): "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection"
- Yan et al. (2024): "Corrective Retrieval Augmented Generation"
