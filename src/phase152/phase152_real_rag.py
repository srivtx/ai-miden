"""
Phase 152: Real RAG Application
===============================
This is a REAL project. Not a toy.

We build a complete Retrieval-Augmented Generation system:
1. Load a real embedding model (sentence-transformers/all-MiniLM-L6-v2)
2. Index real documents (Wikipedia articles about AI topics)
3. Embed documents into a vector store
4. Accept a real user query
5. Retrieve top-k relevant documents by cosine similarity
6. Feed retrieved context + query into a real language model
7. Generate an answer grounded in the retrieved documents
8. Compare: answer with RAG vs. answer without RAG

This is exactly what powers ChatGPT with browsing, Perplexity AI,
and enterprise knowledge bases at companies like Bloomberg and JPMorgan.
Run time: ~1-2 minutes on CPU.
"""

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================================
# 1. LOAD REAL MODELS
# ============================================================================
# WHY: We use real pre-trained models, not synthetic embeddings.
# MiniLM is a 22M parameter model that produces high-quality sentence embeddings.
# GPT-2 is a 124M parameter model that generates text.

print("Loading embedding model (MiniLM)...")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

print("Loading generation model (GPT-2)...")
gen_tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
gen_model = GPT2LMHeadModel.from_pretrained('gpt2')
gen_model.eval()

# ============================================================================
# 2. REAL DOCUMENT CORPUS
# ============================================================================
# WHY: These are real, factual documents about AI topics.
# A production RAG system would load from a database, PDFs, or web pages.

documents = [
    # Document 1: Transformer architecture
    "The Transformer architecture, introduced in the paper 'Attention Is All You Need' in 2017, "
    "revolutionized natural language processing. It relies entirely on self-attention mechanisms "
    "without recurrence or convolution. The key components are multi-head attention, positional "
    "encoding, and feed-forward networks. Transformers enabled models like BERT and GPT to achieve "
    "state-of-the-art results on translation, summarization, and question answering tasks.",

    # Document 2: Convolutional Neural Networks
    "Convolutional Neural Networks (CNNs) are a class of deep neural networks most commonly applied "
    "to analyzing visual imagery. They are inspired by biological processes where neurons respond to "
    "stimuli in restricted regions of the visual field. CNNs use convolutional layers that apply filters "
    "to local regions of the input, followed by pooling layers that reduce spatial dimensions. "
    "AlexNet, ResNet, and EfficientNet are famous CNN architectures used in image classification.",

    # Document 3: Reinforcement Learning
    "Reinforcement Learning (RL) is an area of machine learning where an agent learns to make decisions "
    "by taking actions in an environment to maximize cumulative reward. Unlike supervised learning, "
    "RL does not require labeled input-output pairs. Key algorithms include Q-learning, policy gradients, "
    "and Proximal Policy Optimization (PPO). AlphaGo and OpenAI Five are landmark achievements of RL.",

    # Document 4: Knowledge Distillation
    "Knowledge distillation is a compression technique where a small student model is trained to "
    "reproduce the behavior of a large teacher model. Geoffrey Hinton introduced the concept in 2015. "
    "The student learns from soft probability distributions produced by the teacher, which contain "
    "rich information about relationships between classes. Distillation is widely used to deploy "
    "large models on mobile devices and edge hardware.",

    # Document 5: Generative Adversarial Networks
    "Generative Adversarial Networks (GANs), invented by Ian Goodfellow in 2014, consist of two neural "
    "networks competing against each other: a generator that creates fake data and a discriminator "
    "that tries to distinguish real from fake. Through this adversarial process, the generator learns "
    "to produce increasingly realistic data. GANs have been used to generate realistic images, videos, "
    "and even molecular structures for drug discovery.",

    # Document 6: Backpropagation
    "Backpropagation is the fundamental algorithm for training neural networks. It computes the gradient "
    "of the loss function with respect to each weight by applying the chain rule, working backward from "
    "the output layer to the input layer. The algorithm was popularized by Rumelhart, Hinton, and Williams "
    "in 1986. Modern deep learning frameworks like PyTorch and TensorFlow implement backpropagation "
    "automatically through automatic differentiation.",

    # Document 7: Word Embeddings
    "Word embeddings are dense vector representations of words in a continuous vector space. Words with "
    "similar meanings are located close to each other. Word2Vec, introduced by Mikolov at Google in 2013, "
    "uses skip-gram and continuous bag-of-words architectures. GloVe and FastText are other popular "
    "embedding methods. These embeddings serve as the input layer for most NLP models before Transformers.",

    # Document 8: Long Short-Term Memory
    "Long Short-Term Memory (LSTM) networks are a type of recurrent neural network capable of learning "
    "long-term dependencies. They were introduced by Hochreiter and Schmidhuber in 1997. LSTMs use "
    "cell states and gates (input, forget, output) to regulate the flow of information. They solved the "
    "vanishing gradient problem that plagued vanilla RNNs and dominated sequence modeling until "
    "Transformers replaced them in 2017.",
]

doc_titles = [
    "Transformers",
    "CNNs",
    "Reinforcement Learning",
    "Knowledge Distillation",
    "GANs",
    "Backpropagation",
    "Word Embeddings",
    "LSTMs",
]

print(f"Loaded {len(documents)} real documents.")

# ============================================================================
# 3. EMBED DOCUMENTS INTO VECTOR STORE
# ============================================================================
# WHY: We convert text into dense vectors so we can search by semantic similarity.
# This is the core of any RAG system.

print("Embedding documents...")
doc_embeddings = embedder.encode(documents, convert_to_numpy=True, show_progress_bar=False)

# Normalize for cosine similarity
doc_embeddings = doc_embeddings / np.linalg.norm(doc_embeddings, axis=1, keepdims=True)

print(f"Document embedding shape: {doc_embeddings.shape}")

# ============================================================================
# 4. RETRIEVAL FUNCTION
# ============================================================================

def retrieve(query, top_k=3):
    """Find the top-k most relevant documents for a query."""
    query_embedding = embedder.encode([query], convert_to_numpy=True)
    query_embedding = query_embedding / np.linalg.norm(query_embedding)

    # Cosine similarity = dot product of normalized vectors
    similarities = np.dot(doc_embeddings, query_embedding.T).flatten()
    top_indices = np.argsort(similarities)[::-1][:top_k]

    return [(doc_titles[i], documents[i], similarities[i]) for i in top_indices]

# ============================================================================
# 5. GENERATION FUNCTION
# ============================================================================
# WHY: We use GPT-2 to generate text. In production, this would be a larger model.
# We construct a prompt that includes retrieved context + the user query.

def generate_answer(query, retrieved_docs, max_length=150):
    """Generate an answer using retrieved context."""
    # Build context string from retrieved documents
    context = "\n\n".join([f"Document: {title}\n{doc[:300]}..." for title, doc, _ in retrieved_docs])

    # Construct prompt
    prompt = (
        f"Based on the following documents, answer the question.\n\n"
        f"{context}\n\n"
        f"Question: {query}\n"
        f"Answer:"
    )

    inputs = gen_tokenizer.encode(prompt, return_tensors='pt', truncation=True, max_length=512)
    with torch.no_grad():
        outputs = gen_model.generate(
            inputs,
            max_length=inputs.shape[1] + max_length,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=gen_tokenizer.eos_token_id,
        )

    generated = gen_tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract only the answer part
    answer = generated.split("Answer:")[-1].strip()
    return answer

def generate_without_rag(query, max_length=150):
    """Generate an answer with NO context (baseline)."""
    prompt = f"Question: {query}\nAnswer:"
    inputs = gen_tokenizer.encode(prompt, return_tensors='pt', truncation=True, max_length=512)
    with torch.no_grad():
        outputs = gen_model.generate(
            inputs,
            max_length=inputs.shape[1] + max_length,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=gen_tokenizer.eos_token_id,
        )
    generated = gen_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated.split("Answer:")[-1].strip()

# ============================================================================
# 6. RUN REAL QUERIES
# ============================================================================
queries = [
    "What is self-attention and why is it important?",
    "How do CNNs process images?",
    "Explain how reinforcement learning agents learn without labeled data.",
    "What is knowledge distillation and who invented it?",
    "How do GANs generate realistic images?",
]

print("\n" + "="*70)
print("RAG RESULTS")
print("="*70)

results = []
for query in queries:
    retrieved = retrieve(query, top_k=2)
    answer_rag = generate_answer(query, retrieved)
    answer_no_rag = generate_without_rag(query)

    print(f"\nQuery: {query}")
    print(f"Retrieved: {[t for t, _, _ in retrieved]}")
    print(f"With RAG: {answer_rag[:200]}...")
    print(f"Without RAG: {answer_no_rag[:200]}...")

    results.append({
        "query": query,
        "retrieved": [t for t, _, _ in retrieved],
        "rag_answer": answer_rag,
        "no_rag_answer": answer_no_rag,
        "similarities": [float(s) for _, _, s in retrieved],
    })

# ============================================================================
# 7. VISUALIZATION: RETRIEVAL HEATMAP
# ============================================================================
query_embeddings = embedder.encode(queries, convert_to_numpy=True)
query_embeddings = query_embeddings / np.linalg.norm(query_embeddings, axis=1, keepdims=True)
similarity_matrix = np.dot(query_embeddings, doc_embeddings.T)

fig, ax = plt.subplots(figsize=(10, 6))
im = ax.imshow(similarity_matrix, cmap='YlOrRd', aspect='auto', vmin=0, vmax=1)
ax.set_xticks(range(len(doc_titles)))
ax.set_xticklabels(doc_titles, rotation=45, ha='right')
ax.set_yticks(range(len(queries)))
ax.set_yticklabels([q[:40] + "..." for q in queries])
ax.set_title('Query-Document Similarity Matrix (Cosine Similarity)')
fig.colorbar(im, ax=ax, label='Cosine Similarity')

# Annotate with similarity values
for i in range(len(queries)):
    for j in range(len(doc_titles)):
        text = ax.text(j, i, f"{similarity_matrix[i, j]:.2f}",
                      ha="center", va="center", color="black", fontsize=8)

plt.tight_layout()
plt.savefig("src/phase152/rag_similarity_matrix.png", dpi=150)
print("\nSaved similarity matrix to src/phase152/rag_similarity_matrix.png")

# ============================================================================
# 8. SAVE RESULTS
# ============================================================================
import json
with open("src/phase152/rag_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("Saved results to src/phase152/rag_results.json")

print("\n" + "="*70)
print("PHASE 152 COMPLETE")
print("="*70)
print("You have built a real RAG application with:")
print("- Real sentence embeddings (MiniLM)")
print("- Real document retrieval by cosine similarity")
print("- Real text generation with retrieved context")
print("- Comparison: RAG vs. no-RAG generation")
