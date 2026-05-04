## What Is Dense Retrieval?

**The Problem:**
Keyword search (Ctrl+F) only finds exact word matches. If a document says "convolutional neural networks process visual imagery" and the user searches "how do CNNs analyze pictures," keyword search fails. How do you find documents that are semantically related even when they use different words?

**Definition:**
**Dense retrieval** is the process of encoding text into high-dimensional vectors (embeddings) and finding documents whose vectors are close to the query vector. Unlike keyword search, it captures meaning and synonyms.

**Real-life analogy:**
Dense retrieval is like finding a song by humming the melody. You do not know the title or lyrics (keywords), but you know how it sounds. A music recognition app converts your hum into a vector and finds the closest match in its database. Dense retrieval does the same for text: it converts meaning into vectors and finds close matches.

**Tiny numeric example:**
Query embedding: [0.12, -0.05, 0.33, ...] (384 dimensions)
Document 1 embedding: [0.10, -0.08, 0.30, ...] → cosine similarity = 0.97
Document 2 embedding: [-0.40, 0.90, -0.10, ...] → cosine similarity = 0.12
Document 1 is retrieved; Document 2 is irrelevant.

**Common confusion:**
- **"Dense retrieval understands language."** No. The embedding model understands language (to a degree). The retrieval step is pure math: dot products and sorting.
- **"Dense retrieval replaces keyword search."** In production, hybrid systems use both. Keyword search excels on product IDs, names, and dates. Dense retrieval excels on conceptual queries.
- **"Bigger embeddings are always better."** Larger models produce richer embeddings but are slower. A 384-dim MiniLM model is often sufficient and 100x faster than a 4096-dim model.
- **"Cosine similarity is the only metric."** Euclidean distance, dot product, and learned similarity functions are also used. Cosine similarity ignores vector magnitude, which is often desirable for text.
- **"Dense retrieval is deterministic."** Embedding models are deterministic, but approximate nearest neighbor search (ANN) introduces randomness for speed. FAISS and HNSW trade exactness for 1000x speedup.
- **"You need a GPU for dense retrieval."** Embedding 1000 documents takes seconds on a CPU. GPUs matter when indexing millions of documents or embedding in real-time.

**Where it appears in our code:**
`src/phase152/phase152_real_rag.py` — Uses sentence-transformers/all-MiniLM-L6-v2 to embed documents and queries, then computes cosine similarity with numpy dot products to rank documents.
