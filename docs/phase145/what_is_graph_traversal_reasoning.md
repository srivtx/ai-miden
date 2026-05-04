## What Is Graph Traversal Reasoning?

---

### The Problem

A language model has read billions of documents and stored patterns in its weights. It can write poetry, debug code, and summarize meetings. But ask it "What is the relationship between the inventor of the transistor and the founder of the venture capital firm that funded the company where the inventor worked?" and it will guess. It has no explicit map of who worked where, who funded whom, or who invented what. The knowledge is compressed into statistical correlations, not navigable structure. A knowledge graph has the map, but no language understanding. It knows the edges but cannot read the question. How do you combine the explicit structure of a graph with the flexible reasoning of a language model?

---

### Definition

**Graph Traversal Reasoning** is the process of walking through a knowledge graph's nodes and edges to gather evidence, then using a language model to synthesize that evidence into a natural-language answer. It is the engine that makes GraphRAG powerful: the graph finds the facts, and the LLM explains them.

**How it works:**
```
Question: "Who is the CEO of the company that acquired WidgetCo?"

Step 1: Entity recognition
  Extract entities from question: "WidgetCo"

Step 2: Graph lookup
  Find "WidgetCo" node in the graph

Step 3: Traversal
  Follow "acquired by" edge backward -> "AcmeCorp"
  Follow "has CEO" edge forward -> "Carol"

Step 4: Subgraph extraction
  Collect path: WidgetCo --acquired by--> AcmeCorp --has CEO--> Carol

Step 5: LLM reasoning
  Feed subgraph to LLM: "Based on the following facts: AcmeCorp acquired WidgetCo. Carol is the CEO of AcmeCorp. Who is the CEO of the company that acquired WidgetCo?"
  LLM answers: "Carol"
```

**Key techniques:**
- **Breadth-first search (BFS):** explore all neighbors within K hops to find relevant subgraphs
- **Pathfinding:** find the shortest or highest-confidence path between two entities
- **Subgraph retrieval:** extract a small connected graph around query entities to limit LLM context
- **Iterative traversal:** use the LLM to decide which edge to follow next, treating the graph as an external memory the LLM can query

**Why this matters:**
- LLMs alone hallucinate on multi-hop questions because they lack explicit relational memory
- Graphs alone cannot interpret natural language or synthesize answers
- Together, the graph grounds the reasoning and the LLM articulates it

---

### Real-Life Analogy

A detective with a city map and a witness.
- **LLM alone (witness with no map):** The witness has read every newspaper in the city and remembers many stories. Ask them to trace a drug shipment from the port to the kingpin, and they will invent a plausible route based on patterns they have seen in movies. They might name the wrong warehouse, the wrong lieutenant, and the wrong motive. They sound confident because they are generalizing, not navigating.
- **Graph alone (map with no witness):** You have a perfect map with pins for every location and strings for every known connection. But the map cannot read your question. You ask "Where did the shipment go?" and the map says nothing. It has structure but no semantics.
- **Graph traversal reasoning (detective with map):** The detective reads the question, finds "port" on the map, follows the string to "Warehouse 7," then follows the string to "Lieutenant Varga," then to "Kingpin Morales." The detective uses the map to find the path and their own judgment to decide which strings are relevant. The map grounds the answer; the detective explains it.

---

### Tiny Numeric Example

**A 6-node graph:**
```
Nodes:  Bardeen, Shockley, Bell Labs, Fairchild, Kleiner, KPCB
Edges:  (Bardeen, invented, Transistor)      [not shown, implicit]
        (Bardeen, worked at, Bell Labs)
        (Shockley, worked at, Bell Labs)
        (Shockley, founded, Fairchild)
        (Kleiner, founder of, Fairchild)
        (Kleiner, founded, KPCB)
```

**Question: "Which venture firm was founded by someone who co-founded Fairchild?"**

**LLM-only reasoning (no graph):**
```
The model knows Kleiner is associated with KPCB and Fairchild.
It answers "KPCB" with 70% confidence because it has seen both names
in training data but has no explicit chain of evidence.
```

**Graph traversal reasoning:**
```
Step 1: Extract "Fairchild" and "venture firm" from question
Step 2: Find "Fairchild" node
Step 3: Traverse incoming "founder of" edges -> Kleiner
Step 4: Traverse outgoing "founded" edges from Kleiner -> KPCB
Step 5: Verify "KPCB" is a venture firm (node type check)
Retrieved path: Fairchild <-founder of- Kleiner -founded-> KPCB
LLM answers: "KPCB" with 98% confidence, citing the exact path
```

**Confidence on 50 multi-hop questions:**
```
LLM alone:            58% average confidence, 34% factually correct
Graph traversal + LLM: 94% average confidence, 91% factually correct
```

**The shift:** Explicit traversal replaces statistical guessing with traceable evidence. The answer is only as good as the graph, but the reasoning is inspectable.

---

### Common Confusion

1. **"Graph traversal reasoning is the same as a graph neural network (GNN)."** A GNN learns embeddings by propagating messages through the graph. Traversal reasoning explicitly walks edges to retrieve facts. GNNs compress structure into vectors; traversal keeps it explicit.

2. **"The LLM does not matter once you have the graph."** The graph finds the raw path, but the LLM interprets it. A path like "A -> B -> C" is meaningless without language understanding to map it to the question's intent.

3. **"Deeper traversal is always better."** Every extra hop introduces noise. A path of length 5 often includes irrelevant detours. Most effective GraphRAG systems limit traversal to 2-3 hops and use the LLM to score path relevance.

4. **"Graph traversal guarantees a correct answer."** Only if the graph is complete and accurate. Missing edges (the graph does not know about a recent acquisition) or wrong edges (a false relationship was extracted) produce wrong answers with high confidence.

5. **"This is the same as RDF reasoning or SPARQL."** SPARQL queries a structured database with explicit logic. Graph traversal reasoning uses an LLM to interpret a natural-language question, decide what to traverse, and synthesize an answer. The query layer is fuzzy, not formal.

6. **"You need a massive graph for this to be useful."** A graph of 500 well-curated nodes can answer questions that a vector database of 500,000 chunks cannot. Density and accuracy matter more than scale.

7. **"Traversal is deterministic."** It is not, unless you force it. The LLM may choose different edges based on prompt phrasing. Beam search, scoring functions, and structured constraints are needed to make traversal reproducible.

---

### Where It Is Used in Our Code

`src/phase145/phase145_graphrag_concepts.py` — We implement a simple breadth-first traversal over an adjacency-matrix graph and show how retrieving a connected subgraph improves multi-hop answer accuracy compared to retrieving isolated text chunks.

`src/phase145/phase145_graphrag_colab.py` — We build a `networkx` graph from LLM-extracted entities, traverse it to answer multi-hop questions, and compare the subgraph-retrieval path against a pure vector-similarity baseline.

(End of file)
