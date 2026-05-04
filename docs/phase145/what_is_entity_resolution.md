## What Is Entity Resolution?

---

### The Problem

You are building a knowledge graph from one million news articles. "Apple Inc." appears in a tech story. "Apple" appears in a headline. "the Cupertino giant" appears in an op-ed. "AAPL" appears in a financial report. A human knows these all refer to the same company. But an extraction pipeline sees four distinct strings and creates four separate nodes. The graph becomes fragmented, sparse, and useless for traversal. How do you teach a machine that different surface forms can point to the same underlying entity?

---

### Definition

**Entity Resolution** (also called entity linking, coreference resolution, or canonicalization) is the process of mapping ambiguous textual mentions to a single canonical entity. It ensures that "Apple," "Apple Inc.," and "the Cupertino giant" all resolve to one node in the knowledge graph.

**How it works:**
```
Raw mentions extracted from text:
  Mention 1: "Apple Inc."        -> candidate: Apple (company), Apple (fruit)
  Mention 2: "Apple"             -> candidate: Apple (company), Apple (fruit)
  Mention 3: "the Cupertino giant" -> candidate: Apple (company), Nvidia, Intel
  Mention 4: "Tim Cook"          -> candidate: Tim Cook (CEO), Tim Cook (actor)

Resolution steps:
  1. Generate candidate entities for each mention using a knowledge base
  2. Score candidates using context similarity, prior probability, and coherence
  3. Link each mention to the highest-scoring candidate
  4. Coreference: "it" and "the company" in later sentences link back to Apple

Result: All four mentions point to a single canonical node: Apple (company)
```

**Key techniques:**
- **Candidate generation:** retrieve possible entities from a knowledge base (Wikipedia, Wikidata) using string similarity
- **Context encoding:** embed the mention and its surrounding sentence to compare with entity descriptions
- **Coherence scoring:** prefer entity assignments that make the overall document coherent (a tech article mentioning Apple and Tim Cook is more coherent if both link to the company)
- **Coreference resolution:** link pronouns and nominals ("it," "the firm," "her") back to previously resolved entities

**Why this matters:**
- A graph with 1M nodes for 200K real entities is 80% noise
- Traversal fails when edges connect to duplicate nodes instead of the true target
- Downstream reasoning assumes each entity is unique; duplicates break that assumption

---

### Real-Life Analogy

A police intelligence desk sorting aliases.
- **Extraction without resolution:** The desk receives reports mentioning "Scarface," "Al Capone," "Alphonse Capone," and "the Chicago boss." They file four separate case folders. Detectives working each case never realize they are hunting the same man. Tips about one alias do not inform investigations into the others.
- **Entity resolution:** A senior analyst reads the reports, recognizes the aliases, and creates one master folder labeled "Al Capone (canonical)" with all aliases listed. Every new mention of any alias is routed to the master folder. The graph of associates, crimes, and locations becomes dense and useful.
- **Coreference resolution:** A witness report says "He was wearing a gray suit." The analyst knows "he" refers to Al Capone because of the preceding sentence, so the clothing description is added to the master folder. Without coreference, the detail is orphaned.

---

### Tiny Numeric Example

**Five mentions from a short article:**
```
M1: "Apple Inc. reported earnings."
M2: "The company beat expectations."
M3: "Apple's stock rose."
M4: "Tim Cook praised the team."
M5: "He has led the firm since 2011."
```

**Without resolution:**
```
Nodes created: Apple Inc., The company, Apple, Tim Cook, He, the firm
Graph edges:   (Apple Inc., reported, earnings)
               (The company, beat, expectations)   <- orphan node
               (Apple, stock, rose)                <- duplicate node
               (Tim Cook, praised, team)
               (He, led, the firm)                 <- two orphan nodes
```
Effective entities: 6 (4 of them wrong). Traversal from "Apple" misses "Tim Cook" because "He" is disconnected.

**With resolution:**
```
Canonical entities: Apple (company), Tim Cook (person)
Resolved mentions:
  M1 -> Apple,  M2 -> Apple (coreference),  M3 -> Apple
  M4 -> Tim Cook,  M5 -> Tim Cook (coreference)
Graph edges: (Apple, reported, earnings)
             (Apple, beat, expectations)
             (Apple, stock, rose)
             (Tim Cook, praised, team)
             (Tim Cook, led, Apple)
```
Effective entities: 2. Traversal from "Apple" now reaches "Tim Cook" in one hop.

**Accuracy on a 100-mention test set:**
```
Raw extraction (no resolution):   62/100 mentions linked correctly (62%)
With entity resolution:           91/100 mentions linked correctly (91%)
With coreference resolution:      96/100 mentions linked correctly (96%)
```

**The shift:** Resolution compresses noisy surface forms into clean canonical entities. It is the difference between a fragmented phone book and a unified database.

---

### Common Confusion

1. **"Entity resolution is the same as named entity recognition (NER)."** NER spots that "Apple" is an organization. Entity resolution decides which organization it is. They are sequential steps, not substitutes.

2. **"String matching is enough."** Exact string matching fails on "Apple" vs. "Apple Inc." vs. "AAPL." Fuzzy matching helps but still misses aliases like "the Cupertino giant." Context is essential.

3. **"Entity resolution is 100% accurate."** State-of-the-art systems score 85-95% on standard benchmarks. In noisy real-world text (social media, OCR errors), accuracy drops to 60-70%. Errors propagate into the graph forever.

4. **"Coreference resolution is a solved problem."** It is not. Pronouns like "it" and "they" are ambiguous. Systems struggle with nested references and distant antecedents. A single coreference error can reroute an entire chain of facts to the wrong entity.

5. **"You only need entity resolution for people and companies."** False. Products ("iPhone 15" vs. "the latest iPhone"), locations ("NYC" vs. "the Big Apple"), and scientific concepts ("SARS-CoV-2" vs. "the novel coronavirus") all require resolution.

6. **"A static knowledge base is sufficient for resolution."** New entities emerge daily (startups, products, trends). A knowledge base from 2023 cannot resolve a startup founded in 2025. Continuous updates or in-graph canonicalization are required.

7. **"Entity resolution is only for text."** The same problem exists in tables ("N.Y." vs. "New York"), images (matching faces across photos), and sensor data (resolving device IDs to physical locations).

---

### Where It Is Used in Our Code

`src/phase145/phase145_graphrag_concepts.py` — We simulate raw entity extraction with duplicate and alias nodes, then show how a resolution step collapses aliases into canonical entities and improves graph connectivity for traversal.

`src/phase145/phase145_graphrag_colab.py` — We extract entities using an LLM and apply a simple string-similarity clustering step to resolve near-duplicate mentions before building the final `networkx` graph.

(End of file)
