## What Is GraphRAG?

---

### The Problem

Standard retrieval-augmented generation (RAG) chops documents into chunks, embeds them into vectors, and retrieves the closest chunks to a user's question. This works brilliantly for single-fact questions like "What is the capital of France?" But it collapses on multi-hop questions like "Who is the CEO of the company that acquired the startup founded by the inventor of the technology used in this product?" The answer is scattered across three separate chunks, none of which mention the CEO directly. Vector similarity sees each chunk in isolation and misses the chain of relationships. How do you retrieve structured connections, not just similar text?

---

### Definition

**GraphRAG** is retrieval-augmented generation that uses a **knowledge graph** as its retrieval structure instead of (or alongside) raw text chunks. It extracts entities and relationships from source documents, stores them in a graph, and answers questions by traversing the graph to find connected facts.

**How it works:**
```
Documents:
  "Alice founded AcmeCorp in 2010."
  "Bob invented the Widget in 2008."
  "AcmeCorp acquired WidgetCo in 2015."
  "Carol became CEO of AcmeCorp in 2020."

Extraction:
  Entities: Alice, AcmeCorp, Widget, Bob, WidgetCo, Carol
  Relations: (Alice, founded, AcmeCorp), (Bob, invented, Widget),
             (AcmeCorp, acquired, WidgetCo), (Carol, CEO of, AcmeCorp)

Graph storage:
  Nodes = entities, Edges = relationships

Question: "Who is the CEO of the company that acquired WidgetCo?"
  Vector RAG: retrieves chunk about acquisition, misses CEO
  Graph RAG: traverses WidgetCo -> acquired by -> AcmeCorp -> CEO -> Carol
```

**Key techniques:**
- **Entity extraction:** identifying named entities (people, companies, locations) in text
- **Relationship extraction:** determining how entities connect (founded, acquired, CEO of)
- **Graph traversal:** walking edges between nodes to answer multi-hop questions
- **Subgraph retrieval:** extracting a small connected subgraph relevant to the query

**Why this matters:**
- Multi-hop reasoning requires following chains of relationships across documents
- Graphs preserve structure that flat chunking destroys
- A graph of 10,000 nodes can answer questions that 100,000 text chunks cannot

---

### Real-Life Analogy

A police investigation board vs. a filing cabinet.
- **Vector RAG (filing cabinet):** You have thousands of witness statements sorted by topic. To find who ordered the hit, you search for "hit" and get statements about the crime scene, the weapon, and the victim. Each document is relevant but isolated. You never see the string connecting the crime boss to the hitman.
- **GraphRAG (investigation board):** You have a wall with photos of people, places, and events connected by colored strings. The crime boss photo has a string to the lieutenant, who has a string to the hitman, who has a string to the crime scene. One glance at the board reveals the chain of command. You traverse the wall, not read every file.
- **The difference:** The filing cabinet gives you proximity; the board gives you causality.

---

### Tiny Numeric Example

**A 5-node knowledge graph:**
```
Nodes:  Alice, Bob, AcmeCorp, WidgetCo, Carol
Edges:  (Alice, founded, AcmeCorp)
        (AcmeCorp, acquired, WidgetCo)
        (Carol, CEO of, AcmeCorp)
        (Bob, founded, WidgetCo)
```

**Question: "Who is the CEO of the company that acquired WidgetCo?"**

**Vector RAG retrieval (cosine similarity on sentence embeddings):**
```
Chunk 1: "AcmeCorp acquired WidgetCo in 2015."          -> similarity 0.82
Chunk 2: "Carol became CEO of AcmeCorp in 2020."       -> similarity 0.61
Chunk 3: "Alice founded AcmeCorp in 2010."             -> similarity 0.45
```
Vector RAG returns chunk 1 and chunk 2. The LLM must infer the connection from separate chunks. Success rate: 45%.

**Graph RAG traversal:**
```
Step 1: Find "WidgetCo" in graph
Step 2: Follow incoming "acquired" edge to "AcmeCorp"
Step 3: Follow incoming "CEO of" edge to "Carol"
Answer: Carol
```
Graph RAG retrieves the exact path. Success rate: 95%.

**Accuracy on 100 multi-hop questions:**
```
Vector RAG alone:     34/100 correct (34%)
Graph RAG:            89/100 correct (89%)
```

**The shift:** GraphRAG trades the ambiguity of semantic similarity for the precision of structured traversal. It wins when the answer lives in the connections, not the chunks.

---

### Common Confusion

1. **"GraphRAG replaces vector search entirely."** No. Most production systems use hybrid retrieval: vector search for surface-level similarity, graph traversal for multi-hop reasoning. They complement each other.

2. **"Building the graph is automatic and perfect."** Far from it. Entity extraction misses 10-30% of mentions. Relationship extraction confuses "CEO of" with "board member of." The graph is noisy and requires human curation or iterative refinement.

3. **"Any graph database makes this work."** A graph database stores the data. GraphRAG is the pipeline that extracts entities, populates the graph, and traverses it at query time. Storage is only one piece.

4. **"GraphRAG eliminates hallucination."** No. It reduces hallucination on multi-hop questions because the traversal grounds the answer in explicit edges. But if the extracted relationship is wrong, the answer will be wrong. Garbage in, garbage out.

5. **"This is the same as a knowledge graph from 2010."** Traditional knowledge graphs are manually curated and static. GraphRAG uses LLMs to extract and update the graph automatically from unstructured text. The extraction layer is the new ingredient.

6. **"GraphRAG is only for question answering."** It also excels at anomaly detection (finding unexpected edges), summarization (condensing a subgraph into narrative), and recommendation (suggesting unvisited but connected nodes).

7. **"One graph works for every domain."** A general-purpose graph mixes medical, legal, and casual relationships. Domain-specific graphs use domain ontologies and relationship types. A "treats" edge in medicine is very different from a "acquired" edge in finance.

---

### Where It Is Used in Our Code

`src/phase145/phase145_graphrag_concepts.py` — We simulate a knowledge graph as an adjacency matrix, build a simple vector-retrieval baseline, and show how graph traversal succeeds on multi-hop questions where vector retrieval fails. We visualize the graph structure and highlight the retrieval path.

`src/phase145/phase145_graphrag_colab.py` — We use `Qwen/Qwen2.5-3B-Instruct` to extract entities and relations from a Wikipedia-style document, build a `networkx` graph, and compare multi-hop question accuracy between vector RAG and GraphRAG.

(End of file)
