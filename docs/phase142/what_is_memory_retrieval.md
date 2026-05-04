## What Is Memory Retrieval?

---

### The Problem

Storing millions of memories is easy; finding the right one at the right time is hard. A naive retrieval system returns the most textually similar past message, but that is often not the most useful one. The user might need a memory because it is recent, because it is highly relevant, or because it was emotionally important — and these three criteria can conflict. A fact from five years ago might be more relevant than yesterday's weather. How do you rank memories so that the truly useful ones surface first?

---

### Definition

**Memory retrieval** is the process of selecting which stored memories to inject into an agent's current context. It balances multiple signals — relevance (semantic similarity to the query), recency (how long ago the memory was formed), and importance (how significant the memory was judged to be) — to surface the most useful information without overloading the context window.

**How it works:**
```
Memory score = w_relevance * similarity(query, memory)
             + w_recency * exp(-age / decay_rate)
             + w_importance * importance_score

Retrieve top-k memories with highest composite score.
```

**Key techniques:**
- **Recency bias:** Recent memories get a boost because the current conversation is usually contiguous with the immediate past.
- **Relevance ranking:** Cosine similarity between query and memory embeddings finds thematically related entries even with different wording.
- **Importance scoring:** A separate model or heuristic tags critical memories (e.g., "user changed password," "user is frustrated") so they are not buried.
- **Summarization of long histories:** When episodic memory is too long, a summarizer compresses it into a short narrative before retrieval.

**Why this matters:**
- Context windows are finite. Even 1M tokens is too small for a lifetime of memories.
- Retrieval quality is the bottleneck for long-term agent usefulness. A perfect memory store with bad retrieval is as useless as no memory at all.
- Human memory is not purely similarity-based; it is contextual, emotional, and temporal. Good agent retrieval mimics these properties.

---

### Real-Life Analogy

Searching your email inbox.
- **Relevance-only retrieval:** You search for "budget" and get every email that mentions the word, including a 2013 newsletter about household budgets, a spam email, and the critical Q4 budget approval you need right now. The signal is buried in noise.
- **Recency-only retrieval:** You sort by date and see this morning's cafeteria menu, a Slack notification, and then — eventually — the budget email from two days ago. You missed it because you were looking at the top of the list.
- **Composite retrieval:** The search engine knows "budget" is relevant, knows the finance thread has high importance because you starred it, and knows the Q4 thread is more recent than the 2013 newsletter. It surfaces the Q4 approval first. That is memory retrieval done well.

---

### Tiny Numeric Example

**Memory store:** 5 candidate memories for the query "What is my login?"

**Memory attributes:**
```
ID  Text                                    Similarity  Age(days)  Importance
1   "Your login is admin_2023"              0.95        730        0.6
2   "You reset your password to Xk9#qL"     0.72         14        0.9
3   "Login page is at /portal"              0.88          2        0.3
4   "You forgot your login again"           0.65          1        0.5
5   "System uses OAuth, not passwords"      0.50        180        0.4
```

**Scores with weights (relevance=1.0, recency=0.5, importance=0.3):**
```
ID  Score = 1.0*sim + 0.5*exp(-age/30) + 0.3*imp
1   0.95 + 0.5*0.0   + 0.18 = 1.13
2   0.72 + 0.5*0.627 + 0.27 = 1.30
3   0.88 + 0.5*0.935 + 0.09 = 1.44  ← Top
4   0.65 + 0.5*0.967 + 0.15 = 1.28
5   0.50 + 0.5*0.002 + 0.12 = 0.62
```

**Retrieved top-2:** Memories 3 and 2.
- Memory 3 wins because it is extremely recent and highly similar, even though it is low importance.
- Memory 2 beats memory 1 because recency and importance outweigh the similarity gap.

**Comparison of retrieval strategies on 50 queries:**
```
Strategy                User satisfaction (proxy metric)
Random:                 22%
Similarity only:        61%
Recency only:           48%
Importance only:        55%
Composite (all three):  79%
```

**The shift:** No single signal is sufficient. Combining relevance, recency, and importance models the way human memory prioritizes: you remember what matters, what happened recently, and what relates to your current focus.

---

### Common Confusion

1. **"Retrieval is just nearest-neighbor search."** Nearest-neighbor is the engine, but retrieval is the full system: scoring, filtering, ranking, and formatting memories for the context window.

2. **"Recency bias is a mistake."** In some domains it is (medical history should not be overridden by yesterday's gossip). But in conversation, recency bias is essential because discourse is locally coherent. The right answer is tunable weights, not zero recency.

3. **"Importance scores are hand-coded."** They can be, but modern systems learn them. A small model can be trained to predict which memories the user will ask about again, using click-through or re-query signals.

4. **"Summarization loses too much information."** Bad summarization does. Good summarization is lossy compression that preserves the semantic skeleton. You lose the exact wording but keep the meaning — which is usually what the agent needs.

5. **"More retrieved memories always help."** Each retrieved memory consumes context tokens. Retrieving 50 memories might leave no room for the actual response. The art is retrieving the minimal set that maximally improves the answer.

6. **"Retrieval happens once per query."** Sophisticated agents retrieve iteratively: an initial set of memories refines the query, which triggers a second, more targeted retrieval. This is analogous to human "searching your memory" in stages.

7. **"All memories should be treated equally."** Context determines value. A memory about Python is irrelevant during a cooking conversation, even if it is important and recent in absolute terms. Retrieval must be context-conditioned.

---

### Where It Is Used in Our Code

`src/phase142/phase142_memory_concepts.py` — We simulate a memory store with relevance, recency, and importance scores, then compare retrieval accuracy when using each signal alone versus a composite score. We also demonstrate how summarization of long episodic chains improves retrieval precision by compressing noise into signal.

(End of file - total 97 lines)
