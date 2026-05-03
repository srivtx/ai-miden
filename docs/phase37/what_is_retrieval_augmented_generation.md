## What Is Retrieval-Augmented Generation (RAG)?

---

### The Problem

You ask an LLM: "What was our company's revenue last quarter?" The model has no idea. It was not trained on your private financial documents. It might hallucinate a plausible-sounding number. You could fine-tune the model on your documents, but that is expensive and the data changes every quarter. How do you give the model access to external, private, and up-to-date knowledge without retraining it?

---

### Definition

**RAG (Retrieval-Augmented Generation)** is a technique that augments an LLM's prompt with relevant documents retrieved from an external knowledge base before generating an answer.

**The pipeline:**
```
1. User asks a question
2. Retriever searches a vector database of documents
3. Finds the top-k most relevant document chunks
4. Injects those chunks into the prompt as "context"
5. LLM generates an answer based on the provided context
```

**Key insight:** The LLM does not need to "know" the answer in its weights. It only needs to read and synthesize the text you put in front of it.

---

### Real-Life Analogy

A lawyer preparing for a case.
- The lawyer (LLM) has general legal knowledge from law school (pre-training).
- But for this specific case, they need to research case law, statutes, and precedents.
- They send a paralegal (retriever) to the law library with the question.
- The paralegal returns 5 key cases.
- The lawyer reads these cases and writes their argument, citing specific passages.

Without the paralegal, the lawyer might misremember a precedent or cite a case that does not exist (hallucination). With the paralegal, the argument is grounded in real documents.

---

### Tiny Numeric Example

**Documents (simplified to word counts):**
```
Doc 1: "The cat sat on the mat"       → [2, 1, 1, 1, 1, 0, 0, 0]  (cat, sat, mat, the, on, dog, park, runs)
Doc 2: "The dog runs in the park"     → [0, 0, 0, 2, 0, 1, 1, 1]
Doc 3: "A cat and a dog play"         → [1, 0, 0, 0, 0, 1, 0, 0]
```

**Query:** "Where does the dog run?"
```
Query vector: [0, 0, 0, 1, 0, 1, 0, 1]
```

**Step 1 — Compute cosine similarities:**
```
sim(Query, Doc 1) = (Query · Doc 1) / (|Query| × |Doc 1|)
                  = (0×2 + 0×1 + 0×1 + 1×1 + 0×1 + 1×0 + 0×0 + 1×0) / (sqrt(3) × sqrt(8))
                  = 1 / 4.90 = 0.20

sim(Query, Doc 2) = (0×0 + 0×0 + 0×0 + 1×2 + 0×0 + 1×1 + 0×1 + 1×1) / (sqrt(3) × sqrt(7))
                  = 4 / 4.58 = 0.87

sim(Query, Doc 3) = (0×1 + 0×0 + 0×0 + 1×0 + 0×0 + 1×1 + 0×0 + 1×0) / (sqrt(3) × sqrt(3))
                  = 1 / 3.0 = 0.33
```

**Step 2 — Retrieve top-1:** Doc 2 (similarity 0.87)

**Step 3 — Augmented prompt:**
```
Context: The dog runs in the park
Question: Where does the dog run?
Answer:
```

**Step 4 — Generation:** The LLM reads the context and answers: "in the park"

---

### Common Confusion

1. **"RAG is a type of fine-tuning."** No. Fine-tuning changes the model's weights. RAG leaves the model completely frozen and changes only the prompt. It is prompt engineering at scale.

2. **"RAG eliminates hallucination."** No. The model can still misinterpret retrieved documents or combine them incorrectly. But hallucinations are much less likely because the answer is grounded in real text.

3. **"The retriever is perfect."** Far from it. A bad retriever that returns irrelevant documents makes RAG worse than no RAG. Garbage in, garbage out. Improving retrieval quality is often the highest-leverage work in a RAG system.

4. **"RAG only works for text."** No. Multimodal RAG retrieves images, tables, audio, and video alongside text. A medical RAG system might retrieve patient X-rays, lab results, and clinical notes together.

5. **"Bigger context window means RAG is unnecessary."** Not true. Even with a 1M-token context window, you cannot fit an entire company's document corpus. You still need retrieval to find the relevant subset.

---

### Where It Is Used in Our Code

`src/phase37/phase37_rag.py` — A toy RAG system with 10 documents, bag-of-words embeddings, cosine similarity retrieval, and a tiny linear model that answers questions given retrieved context.
