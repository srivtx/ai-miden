"""
Phase 37: Retrieval-Augmented Generation — Colab T4 PyTorch Version
================================================================================
Run this on Google Colab with a T4 GPU.

This script implements a toy RAG pipeline in PyTorch:
1. Documents are embedded using a small neural network
2. Query is embedded with the same network
3. FAISS-like nearest neighbor retrieval finds top-k docs
4. A tiny seq2seq model generates answers from retrieved context
5. Compare accuracy with and without retrieval

Note: Uses tiny models for fast training on T4.
================================================================================
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# ==============================================================================
# DATA
# ==============================================================================

vocab = ['<pad>', '<unk>', 'revenue', 'profit', 'employees', 'quarter', 'product',
         'launch', 'market', 'growth', 'ceo', 'acquisition', 'loss', 'sales',
         'customer', 'milestone', 'funding', 'ipo', 'partnership', 'technology',
         'innovation', 'five', 'two', 'million', 'hundred', 'twenty', 'percent',
         'one', 'next', 'year', 'drove', 'improved', 'exceeded', 'expectations',
         'was', 'the', 'in', 'to', 'after', 'of', 'due', 'issues', 'reached',
         'users', 'planned', 'for', 'says', 'announced', 'with', 'company',
         'started', 'drove', 'a', 'on', 'and', 'by', 'at', 'from', 'about',
         'what', 'how', 'many', 'did', 'when', 'is', 'where', 'does', 'who',
         'answer', 'question', 'context', 'unknown']

word2idx = {w: i for i, w in enumerate(vocab)}

def encode(text, max_len=20):
    tokens = text.lower().split()
    indices = [word2idx.get(t, word2idx['<unk>']) for t in tokens[:max_len]]
    indices += [word2idx['<pad>']] * (max_len - len(indices))
    return torch.tensor(indices, dtype=torch.long)

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

queries = [
    ("what was the revenue", "five point two million"),
    ("how many employees", "two hundred"),
    ("what did the ceo announce", "acquisition"),
    ("what drove sales", "product launch"),
    ("when is the ipo", "next year"),
]

# ==============================================================================
# MODELS
# ==============================================================================

class Embedder(nn.Module):
    def __init__(self, vocab_size, dim=32):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, dim)
        self.pool = nn.AdaptiveAvgPool1d(1)

    def forward(self, x):
        # x: (batch, seq_len)
        h = self.embed(x)  # (batch, seq_len, dim)
        h = h.permute(0, 2, 1)  # (batch, dim, seq_len)
        return self.pool(h).squeeze(-1)  # (batch, dim)


class TinySeq2Seq(nn.Module):
    """Simple encoder-decoder for answer generation."""
    def __init__(self, vocab_size, dim=32):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, dim)
        self.encoder = nn.LSTM(dim, dim, batch_first=True)
        self.decoder = nn.LSTM(dim, dim, batch_first=True)
        self.out = nn.Linear(dim, vocab_size)

    def forward(self, src, tgt):
        # Encode context
        src_emb = self.embed(src)
        _, hidden = self.encoder(src_emb)

        # Decode answer
        tgt_emb = self.embed(tgt)
        out, _ = self.decoder(tgt_emb, hidden)
        return self.out(out)

# ==============================================================================
# TRAINING
# ==============================================================================

# Train embedder to place similar docs/queries close together
def train_embedder(embedder, epochs=100):
    optimizer = torch.optim.Adam(embedder.parameters(), lr=1e-3)

    # Training pairs: (query, relevant_doc_index)
    pairs = [(0, 0), (1, 2), (2, 4), (3, 3), (4, 7)]

    doc_tensors = torch.stack([encode(d) for d in documents]).to(device)

    for epoch in range(epochs):
        total_loss = 0
        for qi, di in pairs:
            q = encode(queries[qi][0]).unsqueeze(0).to(device)
            d = doc_tensors[di].unsqueeze(0)

            q_emb = embedder(q)
            d_emb = embedder(d)

            # Positive pair should be close
            pos_sim = F.cosine_similarity(q_emb, d_emb)

            # Negative pairs should be far
            neg_loss = 0
            for ni in range(len(documents)):
                if ni != di:
                    n = doc_tensors[ni].unsqueeze(0)
                    n_emb = embedder(n)
                    neg_sim = F.cosine_similarity(q_emb, n_emb)
                    neg_loss += torch.clamp(neg_sim - pos_sim + 0.5, min=0)

            loss = -pos_sim + neg_loss / (len(documents) - 1)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        if (epoch + 1) % 20 == 0:
            print(f"  Epoch {epoch+1}, Loss: {total_loss/len(pairs):.4f}")


print("Training embedder...")
embedder = Embedder(len(vocab), dim=32).to(device)
train_embedder(embedder, epochs=100)

# Train seq2seq on (context + query -> answer) pairs
def train_seq2seq(model, epochs=200):
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    # Prepare training data: for each query, use retrieved doc as context
    pairs = [(0, 0), (1, 2), (2, 4), (3, 3), (4, 7)]

    for epoch in range(epochs):
        total_loss = 0
        for qi, di in pairs:
            context = documents[di]
            query = queries[qi][0]
            answer = queries[qi][1]

            src_text = context + " <sep> " + query
            src = encode(src_text, max_len=40).unsqueeze(0).to(device)
            tgt = encode(answer, max_len=10).unsqueeze(0).to(device)

            logits = model(src, tgt)
            loss = F.cross_entropy(logits.reshape(-1, len(vocab)), tgt.reshape(-1))

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        if (epoch + 1) % 40 == 0:
            print(f"  Epoch {epoch+1}, Loss: {total_loss/len(pairs):.4f}")


print("\nTraining generator...")
generator = TinySeq2Seq(len(vocab), dim=32).to(device)
train_seq2seq(generator, epochs=200)

# ==============================================================================
# RETRIEVAL AND GENERATION
# ==============================================================================

def retrieve(query_text, k=2):
    q = encode(query_text).unsqueeze(0).to(device)
    q_emb = embedder(q)

    doc_embs = embedder(torch.stack([encode(d) for d in documents]).to(device))
    sims = F.cosine_similarity(q_emb, doc_embs, dim=1)
    top_k = torch.topk(sims, k).indices.cpu().tolist()
    return top_k, sims[top_k].cpu().tolist()


def generate(context, query):
    src_text = context + " <sep> " + query
    src = encode(src_text, max_len=40).unsqueeze(0).to(device)

    # Greedy decode
    tgt = torch.tensor([[word2idx['<pad>']]], device=device)
    output_tokens = []

    for _ in range(10):
        logits = generator(src, tgt)
        next_token = logits[0, -1].argmax().item()
        if next_token == word2idx['<pad>']:
            break
        output_tokens.append(next_token)
        tgt = torch.tensor([[next_token]], device=device)

    return ' '.join([vocab[t] for t in output_tokens if t < len(vocab)])


print("\nEvaluating...")
correct_with = 0
correct_without = 0

for qi, (query, expected) in enumerate(queries):
    # Without RAG
    pred_no = generate("", query)
    no_ok = expected in pred_no or any(w in pred_no for w in expected.split())
    correct_without += no_ok

    # With RAG
    top_k, sims = retrieve(query, k=2)
    context = documents[top_k[0]]
    pred_yes = generate(context, query)
    yes_ok = expected in pred_yes or any(w in pred_yes for w in expected.split())
    correct_with += yes_ok

    print(f"Query: '{query}'")
    print(f"  Expected:    {expected}")
    print(f"  Without RAG: {pred_no} {'✓' if no_ok else '✗'}")
    print(f"  With RAG:    {pred_yes} {'✓' if yes_ok else '✗'}")
    print(f"  Retrieved:   {documents[top_k[0]]} (sim={sims[0]:.3f})")
    print()

print(f"Accuracy without RAG: {correct_without}/{len(queries)}")
print(f"Accuracy with RAG:    {correct_with}/{len(queries)}")

# ==============================================================================
# VISUALIZATION
# ==============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Embedding similarities
ax = axes[0, 0]
sim_matrix = np.zeros((len(queries), len(documents)))
for i, (q, _) in enumerate(queries):
    for j in range(len(documents)):
        q_emb = embedder(encode(q).unsqueeze(0).to(device))
        d_emb = embedder(encode(documents[j]).unsqueeze(0).to(device))
        sim_matrix[i, j] = F.cosine_similarity(q_emb, d_emb).item()

im = ax.imshow(sim_matrix, cmap='YlOrRd', aspect='auto')
ax.set_xticks(range(len(documents)))
ax.set_xticklabels([f'D{i}' for i in range(len(documents))], fontsize=8)
ax.set_yticks(range(len(queries)))
ax.set_yticklabels([q[:15] + '...' for q, _ in queries], fontsize=8)
ax.set_title('Query-Document Similarities')
plt.colorbar(im, ax=ax)

# Plot 2: Retrieval accuracy
ax = axes[0, 1]
cats = ['Without RAG', 'With RAG']
vals = [correct_without, correct_with]
colors = ['salmon', 'lightgreen']
bars = ax.bar(cats, vals, color=colors)
ax.set_ylabel('Correct')
ax.set_title('Accuracy Comparison')
for bar, v in zip(bars, vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
            f'{v}/{len(queries)}', ha='center', va='bottom', fontweight='bold')
ax.set_ylim(0, len(queries) + 0.5)
ax.grid(True, alpha=0.3, axis='y')

# Plot 3: Embedding space (PCA)
ax = axes[1, 0]
all_embs = []
labels = []
for d in documents:
    all_embs.append(embedder(encode(d).unsqueeze(0).to(device)).detach().cpu().numpy()[0])
    labels.append('doc')
for q, _ in queries:
    all_embs.append(embedder(encode(q).unsqueeze(0).to(device)).detach().cpu().numpy()[0])
    labels.append('query')

all_embs = np.array(all_embs)
mean = all_embs.mean(axis=0)
centered = all_embs - mean
cov = centered.T @ centered
_, eigvecs = np.linalg.eigh(cov)
pca = centered @ eigvecs[:, -2:]

for i, (x, y) in enumerate(pca[:len(documents)]):
    ax.scatter(x, y, c='blue', s=80, alpha=0.6)
    ax.annotate(f'D{i}', (x, y), fontsize=7)
for i, (x, y) in enumerate(pca[len(documents):]):
    ax.scatter(x, y, c='red', s=80, marker='x')
    ax.annotate(f'Q{i}', (x, y), fontsize=7, color='red')
ax.set_title('Embedding Space (PCA)')
ax.grid(True, alpha=0.3)

# Plot 4: Training curves
ax = axes[1, 1]
ax.text(0.5, 0.7, 'RAG Pipeline', ha='center', va='center', fontsize=14, fontweight='bold')
ax.text(0.5, 0.5, '1. Embed documents\n2. Embed query\n3. Retrieve top-k\n4. Inject context\n5. Generate answer',
        ha='center', va='center', fontsize=11, family='monospace')
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.tight_layout()
plt.savefig('phase37_rag_results.png', dpi=150, bbox_inches='tight')
print("\nSaved: phase37_rag_results.png")
plt.close()

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================
print("\n" + "=" * 70)
print("FINAL RESULTS")
print("=" * 70)
print(f"Accuracy without RAG: {correct_without}/{len(queries)}")
print(f"Accuracy with RAG:    {correct_with}/{len(queries)}")
print("\nKey RAG properties demonstrated:")
print("1. Documents and queries embedded into shared vector space.")
print("2. Cosine similarity retrieves semantically relevant documents.")
print("3. Retrieved context injected into generation prompt.")
print("4. Grounded generation reduces hallucination on private data.")
print("=" * 70)

# To run in Colab:
# 1. Upload this file or paste into a cell
# 2. Runtime -> Change runtime type -> GPU
# 3. Run all cells
# Training takes ~20 seconds on T4.
