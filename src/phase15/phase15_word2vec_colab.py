#!/usr/bin/env python3
"""
================================================================================
Phase 15 (Colab T4 Version): Word2Vec with PyTorch GPU
================================================================================

THIS SCRIPT IS DESIGNED FOR GOOGLE COLAB T4 (FREE GPU).

Copy-paste this into a Colab notebook cell.
It trains Word2Vec on a real dataset (text8) using PyTorch
with GPU acceleration.

The local NumPy version (phase15_word2vec.py) teaches the concepts.
This version shows what happens when you scale up.
"""

# ==============================================================================
# SETUP (run these in separate Colab cells if needed)
# ==============================================================================

# !pip install torch matplotlib scikit-learn --quiet

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import random
import urllib.request
import zipfile
import os

# Check GPU
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    device = torch.device('cuda')
else:
    print("No GPU found, using CPU")
    device = torch.device('cpu')


# ==============================================================================
# DOWNLOAD TEXT8 DATASET
# ==============================================================================

def download_text8():
    """Download text8 dataset (Wikipedia cleaned text)."""
    url = 'http://mattmahoney.net/dc/text8.zip'
    zip_path = 'text8.zip'

    if not os.path.exists('text8'):
        print("Downloading text8 dataset...")
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('.')
        print("Download complete!")
    else:
        print("text8 already downloaded.")

    with open('text8', 'r') as f:
        text = f.read()

    return text


# ==============================================================================
# PREPROCESSING
# ==============================================================================

def preprocess(text, vocab_size=5000):
    """
    Preprocess text:
    1. Split into words
    2. Build vocabulary of top vocab_size most frequent words
    3. Replace rare words with <UNK>
    4. Convert to indices
    """
    words = text.split()
    print(f"Total words in corpus: {len(words):,}")

    # Count word frequencies
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1

    # Get top vocab_size words
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    vocab_words = ['<UNK>'] + [w for w, _ in sorted_words[:vocab_size-1]]

    word_to_idx = {w: i for i, w in enumerate(vocab_words)}
    idx_to_word = {i: w for i, w in enumerate(vocab_words)}

    # Convert text to indices
    data = []
    unk_count = 0
    for word in words:
        if word in word_to_idx:
            data.append(word_to_idx[word])
        else:
            data.append(word_to_idx['<UNK>'])
            unk_count += 1

    print(f"Vocabulary size: {len(vocab_words)}")
    print(f"UNK tokens: {unk_count:,} ({unk_count/len(words)*100:.1f}%)")

    return data, word_to_idx, idx_to_word


# ==============================================================================
# SKIP-GRAM DATASET
# ==============================================================================

class SkipGramDataset:
    """Generate skip-gram training pairs with negative sampling."""

    def __init__(self, data, word_to_idx, window_size=5, negative_samples=5):
        self.data = data
        self.vocab_size = len(word_to_idx)
        self.window_size = window_size
        self.negative_samples = negative_samples

        # Compute unigram distribution for negative sampling
        counts = np.zeros(self.vocab_size)
        for idx in data:
            counts[idx] += 1
        freq = counts ** 0.75
        self.word_freq = freq / np.sum(freq)

    def generate_pairs(self, num_pairs=100000):
        """Generate training pairs."""
        pairs = []
        for _ in range(num_pairs):
            # Random center position
            pos = random.randint(self.window_size, len(self.data) - self.window_size - 1)
            center = self.data[pos]

            # Random context within window
            context_pos = random.randint(pos - self.window_size, pos + self.window_size)
            if context_pos == pos:
                context_pos = pos - 1 if pos > 0 else pos + 1
            context = self.data[context_pos]

            # Negative samples
            negatives = np.random.choice(self.vocab_size, size=self.negative_samples, p=self.word_freq)

            pairs.append((center, context, negatives))

        return pairs


# ==============================================================================
# WORD2VEC MODEL (PyTorch)
# ==============================================================================

class Word2VecModel(nn.Module):
    """PyTorch Word2Vec with negative sampling."""

    def __init__(self, vocab_size, embedding_dim):
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim

        # Center word embeddings
        self.W_in = nn.Embedding(vocab_size, embedding_dim)

        # Context word embeddings
        self.W_out = nn.Embedding(vocab_size, embedding_dim)

        # Initialize
        self.W_in.weight.data.uniform_(-0.01, 0.01)
        self.W_out.weight.data.uniform_(-0.01, 0.01)

    def forward(self, centers, contexts, negatives):
        """
        Forward pass.

        Args:
            centers: (batch_size,) center word indices
            contexts: (batch_size,) context word indices
            negatives: (batch_size, num_negatives) negative word indices

        Returns:
            loss: scalar
        """
        # Center embeddings: (batch_size, embed_dim)
        v_center = self.W_in(centers)

        # Context embeddings: (batch_size, embed_dim)
        v_context = self.W_out(contexts)

        # Positive score: (batch_size,)
        pos_score = torch.sum(v_center * v_context, dim=1)
        pos_loss = -torch.log(torch.sigmoid(pos_score) + 1e-8)

        # Negative embeddings: (batch_size, num_negatives, embed_dim)
        v_neg = self.W_out(negatives)

        # Negative scores: (batch_size, num_negatives)
        # v_center: (batch_size, 1, embed_dim)
        # v_neg: (batch_size, num_negatives, embed_dim)
        neg_score = torch.bmm(v_neg, v_center.unsqueeze(2)).squeeze(2)

        # Negative loss: want sigmoid(neg_score) to be ~0
        neg_loss = -torch.sum(torch.log(1 - torch.sigmoid(neg_score) + 1e-8), dim=1)

        # Total loss
        loss = torch.mean(pos_loss + neg_loss)

        return loss

    def get_embeddings(self):
        """Get the input word embeddings."""
        return self.W_in.weight.data.cpu().numpy()


# ==============================================================================
# TRAINING
# ==============================================================================

def train_word2vec(data, word_to_idx, idx_to_word, embedding_dim=100, epochs=5, batch_size=512):
    """Train Word2Vec on GPU."""
    vocab_size = len(word_to_idx)
    dataset = SkipGramDataset(data, word_to_idx, window_size=5, negative_samples=5)

    model = Word2VecModel(vocab_size, embedding_dim).to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    print(f"\nTraining Word2Vec on {device}...")
    print(f"  Vocab size: {vocab_size:,}")
    print(f"  Embedding dim: {embedding_dim}")
    print(f"  Epochs: {epochs}")
    print(f"  Batch size: {batch_size}")
    print()

    model.train()
    for epoch in range(epochs):
        pairs = dataset.generate_pairs(num_pairs=200000)

        total_loss = 0
        num_batches = 0

        for i in range(0, len(pairs), batch_size):
            batch = pairs[i:i+batch_size]
            if len(batch) < batch_size:
                continue

            centers = torch.LongTensor([p[0] for p in batch]).to(device)
            contexts = torch.LongTensor([p[1] for p in batch]).to(device)
            negatives = torch.LongTensor([p[2] for p in batch]).to(device)

            optimizer.zero_grad()
            loss = model(centers, contexts, negatives)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            num_batches += 1

        avg_loss = total_loss / num_batches
        print(f"  Epoch {epoch+1}/{epochs}: Loss = {avg_loss:.4f}")

    return model


# ==============================================================================
# EVALUATION
# ==============================================================================

def find_similar_words(model, word_to_idx, idx_to_word, word, top_k=10):
    """Find most similar words using cosine similarity."""
    embeddings = model.get_embeddings()

    if word not in word_to_idx:
        print(f"Word '{word}' not in vocabulary")
        return []

    idx = word_to_idx[word]
    vec = embeddings[idx]

    # Compute cosine similarities
    similarities = []
    for i in range(len(embeddings)):
        if i == idx:
            continue
        other = embeddings[i]
        sim = np.dot(vec, other) / (np.linalg.norm(vec) * np.linalg.norm(other) + 1e-8)
        similarities.append((idx_to_word[i], sim))

    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]


def analogy(model, word_to_idx, idx_to_word, a, b, c):
    """Solve: a is to b as c is to ?"""
    embeddings = model.get_embeddings()

    for word in [a, b, c]:
        if word not in word_to_idx:
            print(f"Word '{word}' not in vocabulary")
            return None

    vec_a = embeddings[word_to_idx[a]]
    vec_b = embeddings[word_to_idx[b]]
    vec_c = embeddings[word_to_idx[c]]

    # vec_b - vec_a + vec_c
    target = vec_b - vec_a + vec_c

    # Find closest
    best_sim = -1
    best_word = None
    for i in range(len(embeddings)):
        word = idx_to_word[i]
        if word in [a, b, c, '<UNK>']:
            continue
        sim = np.dot(target, embeddings[i]) / (np.linalg.norm(target) * np.linalg.norm(embeddings[i]) + 1e-8)
        if sim > best_sim:
            best_sim = sim
            best_word = word

    return best_word, best_sim


def visualize_embeddings(model, idx_to_word, num_words=200):
    """Visualize word embeddings using PCA."""
    embeddings = model.get_embeddings()

    # Select most common words (lower indices)
    words = [idx_to_word[i] for i in range(min(num_words, len(idx_to_word))) if idx_to_word[i] != '<UNK>']
    indices = [i for i in range(min(num_words, len(idx_to_word))) if idx_to_word[i] != '<UNK>']
    selected_embeddings = embeddings[indices]

    # PCA to 2D
    pca = PCA(n_components=2)
    reduced = pca.fit_transform(selected_embeddings)

    plt.figure(figsize=(14, 10))
    for i, word in enumerate(words):
        x, y = reduced[i]
        plt.scatter(x, y, c='blue', alpha=0.6, s=30)
        plt.annotate(word, (x, y), fontsize=8, alpha=0.8)

    plt.title('Word Embeddings Visualized with PCA', fontsize=14)
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('word2vec_pca.png', dpi=150)
    print("Visualization saved to word2vec_pca.png")
    plt.show()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    # Download and prepare data
    text = download_text8()
    data, word_to_idx, idx_to_word = preprocess(text, vocab_size=5000)

    # Train
    model = train_word2vec(data, word_to_idx, idx_to_word, embedding_dim=100, epochs=5)

    # Test similar words
    print("\n" + "="*60)
    print("SIMILAR WORDS")
    print("="*60)
    for word in ['king', 'queen', 'dog', 'cat', 'france', 'computer', 'music']:
        similar = find_similar_words(model, word_to_idx, idx_to_word, word)
        if similar:
            print(f"\n  {word}:")
            for w, sim in similar[:5]:
                print(f"    {w:15s} (sim: {sim:.3f})")

    # Test analogies
    print("\n" + "="*60)
    print("WORD ANALOGIES")
    print("="*60)
    analogies = [
        ('king', 'queen', 'man'),
        ('paris', 'france', 'london'),
        ('good', 'better', 'bad'),
    ]
    for a, b, c in analogies:
        result, sim = analogy(model, word_to_idx, idx_to_word, a, b, c)
        if result:
            print(f"  {a} : {b} :: {c} : {result} (sim: {sim:.3f})")

    # Visualize
    print("\n" + "="*60)
    print("VISUALIZING EMBEDDINGS")
    print("="*60)
    visualize_embeddings(model, idx_to_word)
