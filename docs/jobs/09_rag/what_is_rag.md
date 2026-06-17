## Why it exists (THE PROBLEM)

A 10M-param model trained on rich can complete `text = Text("Hello")` but can't complete `my_obscure_function(arg1, arg2)` because it never saw that function name. The model's knowledge is frozen in its weights — adding a new function requires retraining.

**RAG (Retrieval-Augmented Generation)** solves this. Instead of requiring the model to MEMORIZE everything in weights, store the code in an external database. At inference time, search the database for similar code, feed it as context to the model, and let the model CONTINUE from the retrieved patterns. The model doesn't need to know your codebase. It knows how to use retrieved context.

**Vector database** is how you search. Every code snippet is converted into a vector (embedding). Similar code = nearby vectors. The search is: embed the user's prompt → find the 5 nearest vectors → return those snippets as context.

## Definition (very simple)

**RAG** = retriever + generator. The retriever finds relevant documents. The generator uses those documents as extra context to produce better output. Neither is "intelligent" alone. Together they're a system that can answer questions about data it wasn't trained on.

**Vector database** = store vectors + search by similarity. Each document gets one vector (embedding). Searching means: compute cosine similarity between the query vector and all stored vectors → return top-K. The database handles this with approximate nearest neighbor (ANN) search — fast even for millions of vectors.

**The RAG workflow:**
```
1. User prompt: "def process_config(config):"
2. Embed prompt → vector V_q
3. Search vector DB for top-5 nearest vectors
4. Return the corresponding code snippets:
   Snippet 1: "def process_config(cfg): return {'port': cfg.get('port', 8080)}"
   Snippet 2: "def load_config(path): with open(path) as f: return yaml.safe_load(f)"
   ...
5. Feed to model: [RETRIEVED: snippets 1-5] + [PROMPT: def process_config(config):]
6. Model generates: "if isinstance(config, str): config = load_config(config)\n    return {'host': config.get('host', '0.0.0.0'), 'port': config.get('port', 8080)}"
```

The model didn't MEMORIZE `process_config`. It RETRIEVED similar functions from the codebase and ADAPTED them.

## Practice: Minimal vector DB for cortexcode

```python
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class CodeVectorStore:
    """A minimal vector database for code retrieval."""

    def __init__(self, embed_dim=384):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None  # FAISS index (built on first search)
        self.snippets = []  # Stores the actual code text
        self.vectors = []   # Temporary storage before building index

    def add(self, code_snippet):
        """Add a code snippet. Embedding computed and stored."""
        vec = self.embedder.encode([code_snippet])[0]  # (384,)
        self.vectors.append(vec)
        self.snippets.append(code_snippet)

    def build_index(self):
        """Build the FAISS index (call after adding all snippets)."""
        vectors = np.array(self.vectors).astype('float32')
        # Normalize for cosine similarity
        faiss.normalize_L2(vectors)
        self.index = faiss.IndexFlatIP(vectors.shape[1])  # Inner product = cosine
        self.index.add(vectors)
        self.vectors = []  # Free memory

    def search(self, query, k=5):
        """Search for top-K similar code snippets."""
        q_vec = self.embedder.encode([query])[0].reshape(1, -1).astype('float32')
        faiss.normalize_L2(q_vec)
        distances, indices = self.index.search(q_vec, k)
        results = []
        for i, d in zip(indices[0], distances[0]):
            if i < len(self.snippets):
                results.append((self.snippets[i], float(d)))
        return results


# ====== Usage ======
store = CodeVectorStore()

# Index your entire codebase (one-time, at startup)
for path in Path("/content/codebase").rglob("*.py"):
    code = path.read_text()
    # Split file into function-level chunks
    for fn in extract_functions(code):  # simple AST-based extraction
        store.add(fn)

store.build_index()  # Build FAISS index (FAST after this)

# At inference:
query = "def process_config(config):"
results = store.search(query, k=5)

# Feed to model:
context = "\n\n---\n\n".join(r[0] for r in results)
prompt = f"// Similar code:\n{context}\n\n// Complete:\n{query}"
completion = model.generate(prompt)
```

## Key properties

| Property | No retrieval | With RAG + vector DB |
|---|---|---|
| New code without retraining | Can't complete | Can complete (retrieved) |
| Knowledge updates | Retrain model | Just add vectors |
| Context window | Fixed (model's max_seq_len) | Dynamic (retrieved context fits) |
| Personalization | Train on your data | Index your data once |
| Forgetting | Yes (overwritten) | No (appended, never removed) |

## Vector DB comparison

| DB | Best for | Notes |
|---|---|---|
| **FAISS** | Embedded, fastest | Meta, C++/Python, runs in-process |
| **Chroma** | Simple, local | Python-native, tiny |
| **Pinecone** | Managed, serverless | No infra, pay per request |
| **Weaviate** | Full-featured | GraphQL API, hybrid search |
| **Milvus** | Scale (billions of vectors) | Distributed, K8s |
| **Qdrant** | Rust, fast filtering | Payload filtering alongside similarity |

**For cortexcode:** FAISS. In-process, no server, no network calls, 1ms search on 10K vectors. `pip install faiss-cpu`. 10 lines.

## Common confusion

1. **"RAG makes the model smarter."** No. The model is the same. RAG gives the model MORE INPUT. If the model was bad at using context, RAG doesn't help. You need to train the model on RAG-style examples (retrieved context + continuation) for it to learn HOW to use the context. A model trained on next-token prediction sees RAG context as "weird text that appeared in my prompt" — it doesn't inherently know to COPY from it.

2. **"FAISS is a database."** FAISS is an in-memory index, not a database. No persistence, no replication, no queries. For production, layer FAISS behind a proper DB (Chroma, Pinecone). For prototyping (10K vectors), FAISS in-process is fine.

3. **"Vector search is expensive."** For 10K vectors × 384 dimensions: O(384 × 10K) = 3.8M float operations per query. On CPU: ~0.1ms. For 1M vectors: ~10ms. FAISS' ANN indices (IVF, HNSW) reduce this to O(log N) with ~95% recall. Production search at 1M vectors: <2ms.

## Connection to cortexcode

Add the vector store to the API. Index the codebase at startup (one-time). On each `/complete` request, retrieve top-5 snippets, prepend as context. No retraining. Model sees your codebase without ever training on it.
