"""
Phase 37: Retrieval-Augmented Generation (RAG)

This script demonstrates a toy RAG system using only NumPy.

We build:
1. A corpus of 10 documents about a fictional company (Acme Corp)
2. Bag-of-words embeddings for each document
3. A query embedding using the same vocabulary
4. Cosine similarity retrieval to find top-k relevant documents
5. A tiny linear model that answers questions given retrieved context
6. Comparison: accuracy with RAG vs. without RAG (no context)

Why NumPy? So every retrieval and similarity computation is visible.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================================
# 1. VOCABULARY AND DOCUMENTS
# ============================================================================
# We define a small vocabulary and 10 documents about Acme Corp.
# Each document is a simple sentence.
# ============================================================================

vocab = ['revenue', 'profit', 'employees', 'quarter', 'product', 'launch',
         'market', 'growth', 'ceo', 'acquisition', 'expansion', 'loss',
         'sales', 'customer', 'milestone', 'funding', 'ipo', 'partnership',
         'technology', 'innovation']
vocab_size = len(vocab)

documents = [
    "revenue in quarter three was five point two million",
    "profit margin improved to twenty percent this quarter",
    "employees grew to two hundred after expansion",
    "product launch in market drove sales growth",
    "ceo announced acquisition of tech startup",
    "loss in quarter one due to funding issues",
    "customer milestone reached one million users",
    "ipo planned for next year says ceo",
    "partnership with innovation technology company announced",
    "sales growth exceeded market expectations this quarter",
]

# Queries and their expected answers (based on documents)
queries = [
    ("what was the revenue", "five point two million"),
    ("how many employees", "two hundred"),
    ("what did the ceo announce", "acquisition"),
    ("what drove sales", "product launch"),
    ("when is the ipo", "next year"),
]

print("=" * 70)
print("PHASE 37: RETRIEVAL-AUGMENTED GENERATION (RAG)")
print("=" * 70)
print(f"Vocabulary size: {vocab_size}")
print(f"Documents: {len(documents)}")
print(f"Queries: {len(queries)}")
print()

# ============================================================================
# 2. EMBEDDING FUNCTION: BAG OF WORDS
# ============================================================================
# For simplicity, we use a one-hot-ish bag-of-words embedding.
# Each word in the vocabulary gets a unique random vector.
# A document's embedding is the sum of its word vectors.
# This captures semantic overlap without needing a pre-trained model.
# ============================================================================

np.random.seed(42)
# Each word gets a random 10-dimensional vector
word_vectors = np.random.randn(vocab_size, 10) * 0.5

def text_to_embedding(text):
    """Convert text to embedding by summing word vectors."""
    words = text.lower().split()
    emb = np.zeros(10)
    for w in words:
        if w in vocab:
            idx = vocab.index(w)
            emb += word_vectors[idx]
    return emb

# Embed all documents
doc_embeddings = np.array([text_to_embedding(d) for d in documents])

# ============================================================================
# 3. RETRIEVAL: COSINE SIMILARITY
# ============================================================================

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)

def retrieve(query, k=2):
    """Return indices of top-k most similar documents."""
    q_emb = text_to_embedding(query)
    similarities = np.array([cosine_similarity(q_emb, d_emb) for d_emb in doc_embeddings])
    top_k = np.argsort(similarities)[-k:][::-1]
    return top_k, similarities[top_k]

# ============================================================================
# 4. TINY ANSWER MODEL
# ============================================================================
# We train a simple linear classifier that maps a document embedding
# to one of 5 answer "classes" (represented as one-hot vectors).
# In practice, this is a tiny stand-in for an LLM.
# ============================================================================

# Define 5 answer classes as fixed target vectors
answer_classes = ['five point two million', 'two hundred', 'acquisition',
                  'product launch', 'next year']
answer_vectors = np.eye(len(answer_classes))

# Training data: each document maps to its closest answer class
def doc_to_answer_idx(doc):
    # Simple heuristic mapping
    if 'revenue' in doc and 'five' in doc:
        return 0
    elif 'employees' in doc:
        return 1
    elif 'ceo' in doc and 'acquisition' in doc:
        return 2
    elif 'sales' in doc and 'launch' in doc:
        return 3
    elif 'ipo' in doc:
        return 4
    # Default: find most similar answer by word overlap
    best = 0
    best_score = -1
    for i, ans in enumerate(answer_classes):
        score = len(set(doc.split()) & set(ans.split()))
        if score > best_score:
            best_score = score
            best = i
    return best

# Train linear model: W such that doc_emb @ W ≈ answer_vector
X = doc_embeddings
Y = np.array([answer_vectors[doc_to_answer_idx(d)] for d in documents])

# Ridge regression: W = (X^T X + lambda I)^-1 X^T Y
lambda_reg = 0.1
W_model = np.linalg.inv(X.T @ X + lambda_reg * np.eye(X.shape[1])) @ X.T @ Y

def predict_answer(context_emb):
    """Predict answer given a context embedding."""
    logits = context_emb @ W_model
    return answer_classes[np.argmax(logits)]

# ============================================================================
# 5. EVALUATE WITH AND WITHOUT RAG
# ============================================================================

print("Evaluating queries...\n")

correct_with_rag = 0
correct_without_rag = 0

for query, expected in queries:
    # Without RAG: predict from query embedding alone
    query_emb = text_to_embedding(query)
    pred_no_rag = predict_answer(query_emb)

    # With RAG: retrieve top-2 docs, aggregate their embeddings
    top_k, sims = retrieve(query, k=2)
    context_emb = np.mean(doc_embeddings[top_k], axis=0)
    pred_with_rag = predict_answer(context_emb)

    no_rag_correct = expected in pred_no_rag or pred_no_rag in expected
    rag_correct = expected in pred_with_rag or pred_with_rag in expected

    correct_without_rag += no_rag_correct
    correct_with_rag += rag_correct

    print(f"Query: '{query}'")
    print(f"  Expected:      {expected}")
    print(f"  Without RAG:   {pred_no_rag} {'✓' if no_rag_correct else '✗'}")
    print(f"  With RAG:      {pred_with_rag} {'✓' if rag_correct else '✗'}")
    print(f"  Retrieved:     {[documents[i] for i in top_k]}")
    print()

print(f"Accuracy without RAG: {correct_without_rag}/{len(queries)} ({100*correct_without_rag/len(queries):.0f}%)")
print(f"Accuracy with RAG:    {correct_with_rag}/{len(queries)} ({100*correct_with_rag/len(queries):.0f}%)")

# ============================================================================
# 6. VISUALIZATION
# ============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# ---- Plot 1: Document-Query Similarity Heatmap ----
ax = axes[0, 0]
sim_matrix = np.zeros((len(queries), len(documents)))
for i, (query, _) in enumerate(queries):
    for j in range(len(documents)):
        sim_matrix[i, j] = cosine_similarity(text_to_embedding(query), doc_embeddings[j])

im = ax.imshow(sim_matrix, cmap='YlOrRd', aspect='auto')
ax.set_xticks(range(len(documents)))
ax.set_xticklabels([f'D{i}' for i in range(len(documents))], fontsize=8)
ax.set_yticks(range(len(queries)))
ax.set_yticklabels([q[:20] + '...' for q, _ in queries], fontsize=8)
ax.set_xlabel('Documents')
ax.set_ylabel('Queries')
ax.set_title('Query-Document Cosine Similarity')
plt.colorbar(im, ax=ax)

# ---- Plot 2: Top Retrieval for Each Query ----
ax = axes[0, 1]
for i, (query, _) in enumerate(queries):
    top_k, sims = retrieve(query, k=3)
    ax.scatter([i] * len(top_k), top_k, s=sims*300, c='steelblue', alpha=0.6)
ax.set_xticks(range(len(queries)))
ax.set_xticklabels([f'Q{i}' for i in range(len(queries))])
ax.set_yticks(range(len(documents)))
ax.set_yticklabels([f'D{i}' for i in range(len(documents))])
ax.set_xlabel('Queries')
ax.set_ylabel('Retrieved Document')
ax.set_title('Top-3 Retrieved Documents (size = similarity)')
ax.grid(True, alpha=0.3)

# ---- Plot 3: Accuracy Comparison ----
ax = axes[1, 0]
categories = ['Without RAG', 'With RAG']
accuracies = [correct_without_rag, correct_with_rag]
colors = ['salmon', 'lightgreen']
bars = ax.bar(categories, accuracies, color=colors)
ax.set_ylabel('Correct Answers')
ax.set_title(f'Accuracy: {correct_without_rag} vs. {correct_with_rag} / {len(queries)}')
for bar, acc in zip(bars, accuracies):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
            f'{acc}/{len(queries)}', ha='center', va='bottom', fontweight='bold')
ax.set_ylim(0, len(queries) + 0.5)
ax.grid(True, alpha=0.3, axis='y')

# ---- Plot 4: Document Embeddings (PCA to 2D) ----
ax = axes[1, 1]
# Simple PCA
mean = doc_embeddings.mean(axis=0)
centered = doc_embeddings - mean
cov = centered.T @ centered
eigvals, eigvecs = np.linalg.eigh(cov)
pca = centered @ eigvecs[:, -2:]  # top 2 components

for i, (x, y) in enumerate(pca):
    ax.scatter(x, y, color='steelblue', s=100)
    ax.annotate(f'D{i}', (x, y), textcoords="offset points", xytext=(5, 5), fontsize=8)

# Plot query embeddings
for i, (query, _) in enumerate(queries):
    q_emb = text_to_embedding(query) - mean
    q_pca = q_emb @ eigvecs[:, -2:]
    ax.scatter(q_pca[0], q_pca[1], color='red', s=80, marker='x')
    ax.annotate(f'Q{i}', (q_pca[0], q_pca[1]), textcoords="offset points", xytext=(5, -10), fontsize=8, color='red')

ax.set_xlabel('PC1')
ax.set_ylabel('PC2')
ax.set_title('Document & Query Embeddings (PCA)')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('src/phase37/rag_concepts.png', dpi=150, bbox_inches='tight')
print("\nSaved visualization: src/phase37/rag_concepts.png")
plt.close()

# ============================================================================
# 7. SUMMARY
# ============================================================================
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Documents: {len(documents)}")
print(f"Queries: {len(queries)}")
print(f"Retrieval: Top-2 documents by cosine similarity")
print()
print(f"Without RAG: {correct_without_rag}/{len(queries)} correct ({100*correct_without_rag/len(queries):.0f}%)")
print(f"With RAG:    {correct_with_rag}/{len(queries)} correct ({100*correct_with_rag/len(queries):.0f}%)")
print()
print("Key observations:")
print("1. Without context, the model cannot answer questions about private data.")
print("2. Retrieval finds relevant documents based on semantic similarity.")
print("3. Injected context grounds the answer in real documents.")
print("4. RAG dramatically improves accuracy on knowledge-intensive tasks.")
print()
print("This demonstrates the core idea of RAG:")
print("- Embed documents into a vector store")
print("- Embed the query with the same model")
print("- Retrieve top-k most similar documents")
print("- Inject them into the prompt as context")
print("- Generate answer conditioned on retrieved evidence")
print("=" * 70)
