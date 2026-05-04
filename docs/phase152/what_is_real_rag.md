## What Is a Real RAG Application?

**The Problem:**
Language models hallucinate. They make up facts, cite non-existent papers, and confidently state falsehoods. You cannot trust a model to answer questions about your company's internal documents, medical records, or legal contracts. But you also cannot retrain the model every time a document changes. How do you ground the model's answers in real, verifiable documents without changing the model itself?

**Definition:**
A **Retrieval-Augmented Generation (RAG) application** is a system that answers user queries by first retrieving relevant documents from a knowledge base, then feeding those documents as context to a language model. The model generates an answer grounded in the retrieved text, not in its parametric memory.

**Real-life analogy:**
A RAG system is like a lawyer preparing for a case. The lawyer (language model) has general legal knowledge from law school. But for this specific case, they ask their paralegal (retriever) to fetch relevant case law, contracts, and precedents from the firm's library. The lawyer then writes their argument based on those specific documents. Without the paralegal, the lawyer might misremember a precedent or cite a case that does not exist. With the paralegal, every claim is traceable to a real document.

**Tiny numeric example:**
Query: "What is knowledge distillation and who invented it?"
- Without RAG: "Knowledge distillation is a technique where a smaller model learns from a larger one. It was developed by researchers at Google in 2014." (Wrong year, vague attribution)
- With RAG (retrieving Document 4): "Knowledge distillation is a compression technique where a small student model is trained to reproduce the behavior of a large teacher model. Geoffrey Hinton introduced the concept in 2015." (Correct, specific, traceable)

**Common confusion:**
- **"RAG is just adding documents to the prompt."** It is more than that. RAG requires embedding models, vector databases, relevance ranking, and context window management. Dumping 100 pages into the prompt exceeds the model's context limit.
- **"RAG eliminates hallucination."** It reduces hallucination but does not eliminate it. The model can still misinterpret a retrieved document or combine information incorrectly.
- **"Any embedding model works for RAG."** No. Embedding models are task-specific. A model trained on general web text works for general Q&A but fails on legal or medical documents. You must match the embedding model to your domain.
- **"RAG replaces fine-tuning."** They are complementary. RAG grounds answers in documents. Fine-tuning teaches the model a style, format, or task. Most production systems use both.
- **"RAG is only for text."** Multimodal RAG retrieves images, tables, audio, and video alongside text. A medical RAG system might retrieve CT scans and lab reports.
- **"The retriever is perfect."** Retrieval fails when the query is ambiguous, the documents are poorly written, or the embedding model does not understand the domain. Hybrid retrieval (dense + keyword) mitigates this.

**Where it appears in our code:**
`src/phase152/phase152_real_rag.py` — Loads MiniLM for embeddings, indexes 8 real documents, retrieves top-2 documents by cosine similarity for each query, and generates answers with GPT-2 using the retrieved context. Compares RAG vs. no-RAG output.
