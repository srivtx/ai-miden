## What Is Context Injection?

**The Problem:**
You have retrieved three relevant documents, but the language model can only read 512 tokens at a time. The three documents total 2000 tokens. How do you fit the retrieved information into the model's limited attention window? And how do you format it so the model knows which text is context and which is the user's question?

**Definition:**
**Context injection** is the process of formatting retrieved documents into a prompt so the language model can use them to answer a query. It involves selecting the most relevant passages, ordering them, and wrapping them with instructions that tell the model how to use the context.

**Real-life analogy:**
Context injection is like giving a student an open-book exam. The teacher (RAG system) selects 3 relevant pages from the textbook (retrieval) and staples them to the exam paper (injection). The student knows they can use those pages to answer the questions. If the teacher stapled the wrong pages, the student cannot answer. If the teacher stapled 50 pages, the student runs out of time. The art is selecting the right amount of the right content.

**Tiny numeric example:**
Bad injection (no structure):
"What is distillation? Knowledge distillation is a compression technique... Geoffrey Hinton... GANs consist of two networks..."

Good injection (structured):
"Based on the following documents, answer the question.\n\nDocument: Knowledge Distillation\nKnowledge distillation is a compression technique where a small student model is trained to reproduce the behavior of a large teacher model. Geoffrey Hinton introduced the concept in 2015.\n\nQuestion: What is knowledge distillation and who invented it?\nAnswer:"

**Common confusion:**
- **"You should inject as many documents as possible."** No. Models have context limits. Long contexts dilute attention. Injecting 10 documents when 2 are relevant hurts performance.
- **"The order of documents does not matter."** It does. Models pay more attention to the beginning and end of context. The most relevant document should go first.
- **"Context injection is just string concatenation."** It is string concatenation with structure. The prompt template, separators, and instructions all affect how well the model uses the context.
- **"Injecting context fixes all hallucination."** It reduces hallucination on fact-based questions but not on reasoning errors. The model can still misinterpret a correctly retrieved document.
- **"You only inject text."** Modern systems inject tables, images, code snippets, and structured data. The context can be any modality the model understands.
- **"Injecting raw documents is best."** Often, you should extract only the most relevant sentences or paragraphs from a document, not the full text. This is called "reranking" or "passage extraction."

**Where it appears in our code:**
`src/phase152/phase152_real_rag.py` — The `generate_answer()` function builds a structured prompt with document titles, truncated document text, and the user query. The prompt template explicitly instructs the model to base its answer on the documents.
