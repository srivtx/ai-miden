## What Is Context Injection?

---

### The Problem

You have retrieved 3 relevant documents. Now you need to feed them to the LLM so it can answer the user's question. How do you format the documents? Where do they go in the prompt? What if the documents contradict each other?

---

### Definition

**Context injection** is the process of inserting retrieved documents into the LLM's prompt so the model can use them to generate an answer.

**Standard format:**
```
You are a helpful assistant. Use the provided context to answer the question.
If the context does not contain the answer, say "I don't know."

Context:
[Document 1]
[Document 2]
[Document 3]

Question: [User's question]
Answer:
```

**Key design decisions:**
- **Order of documents:** Most relevant first, or chronological, or by source authority
- **Document separators:** Clear markers so the model knows where one document ends and another begins
- **Length limits:** Fit within the model's context window (e.g., 4K–128K tokens)
- **Citation prompts:** Ask the model to cite which document it used for each claim

---

### Real-Life Analogy

A student taking an open-book exam.
- The teacher places 5 relevant textbook pages on the student's desk.
- The student can read the pages but must formulate their own answer.
- If two pages contradict each other, the student must decide which to trust or acknowledge the disagreement.
- The student cannot use information from pages not on the desk.

Context injection is the teacher placing those pages on the desk. The LLM is the student.

---

### Tiny Numeric Example

**Retrieved documents:**
```
Doc 1: "Acme Corp revenue in Q3 2024 was $5.2 million."
Doc 2: "Acme Corp hired 50 new employees in Q3 2024."
Doc 3: "The CEO stated Q4 growth will accelerate."
```

**User question:** "What was Acme's Q3 revenue?"

**Prompt without context injection:**
```
Question: What was Acme's Q3 revenue?
Answer:
```
The model has no idea. It might hallucinate: "Acme's Q3 revenue was $10 million."

**Prompt with context injection:**
```
Use the following context to answer the question.

Context:
Doc 1: Acme Corp revenue in Q3 2024 was $5.2 million.
Doc 2: Acme Corp hired 50 new employees in Q3 2024.
Doc 3: The CEO stated Q4 growth will accelerate.

Question: What was Acme's Q3 revenue?
Answer:
```

The model reads the context and answers: "Acme's Q3 revenue was $5.2 million."

---

### Common Confusion

1. **"Context injection is the same as fine-tuning."** No. Fine-tuning changes the model's weights so it "knows" the information permanently. Context injection puts the information in the prompt so the model only has access for that one request.

2. **"More context is always better."** No. LLMs have limited context windows (4K–128K tokens). Too much irrelevant context dilutes attention and confuses the model. Quality of retrieval beats quantity of context.

3. **"The model reads all context equally carefully."** No. LLMs tend to pay more attention to the beginning and end of the context (the "lost in the middle" problem). The most relevant documents should be placed at the start or end.

4. **"Context injection prevents all hallucinations."** No. The model can still misread numbers, confuse dates, or synthesize documents incorrectly. But grounding in real text dramatically reduces hallucination rates.

5. **"You can only inject text."** No. Modern RAG systems inject tables, images, code snippets, and structured data. The context can be any modality the model understands.

---

### Where It Is Used in Our Code

`src/phase37/phase37_rag.py` — Retrieved documents are formatted into a context string and prepended to the question. A tiny linear model generates answers conditioned on the injected context, showing dramatically improved accuracy versus no context.
