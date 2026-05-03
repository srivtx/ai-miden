#!/usr/bin/env python3
"""
================================================================================
Phase 74 (Colab T4): Recommendation Systems — Real-Workflow Training
================================================================================

Copy-paste into Google Colab with T4 GPU.

This script trains a Matrix Factorization model and a Two-Tower retrieval model
on the MovieLens 100k dataset using BPR pairwise ranking loss.

Evaluation uses Hit Rate and NDCG — the metrics that actually matter for
recommendation ranking, not MSE.

Every block has heavy comments explaining WHY we do what we do.
"""

import os
import urllib.request
import zipfile
import random
from collections import defaultdict

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ==============================================================================
# 1. DATA LOADING: MovieLens 100k
# ==============================================================================
# WHY MovieLens? It is the standard academic benchmark for recommendation.
# It contains 100,000 ratings from 943 users on 1,682 movies.
# We use it because it is small enough to train in minutes on a T4,
# but real enough to show actual ranking metrics.
# ==============================================================================

DATA_URL = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"
DATA_ZIP = "/tmp/ml-100k.zip"
EXTRACT_DIR = "/tmp/ml-100k"

if not os.path.exists(EXTRACT_DIR):
    print("Downloading MovieLens 100k...")
    urllib.request.urlretrieve(DATA_URL, DATA_ZIP)
    with zipfile.ZipFile(DATA_ZIP, 'r') as z:
        z.extractall("/tmp")
    print("Downloaded and extracted.")

# Ratings: user_id, item_id, rating, timestamp (1-indexed in raw file)
ratings_path = os.path.join(EXTRACT_DIR, "ml-100k", "u.data")
all_ratings = []
with open(ratings_path, 'r') as f:
    for line in f:
        u, i, r, t = line.strip().split('\t')
        all_ratings.append((int(u) - 1, int(i) - 1, int(r), int(t)))

# Item genres: 19 binary genre flags (action, comedy, etc.)
genres_path = os.path.join(EXTRACT_DIR, "ml-100k", "u.item")
item_genres = {}
with open(genres_path, 'r', encoding='latin-1') as f:
    for line in f:
        parts = line.strip().split('|')
        movie_id = int(parts[0]) - 1
        genre_vec = [int(g) for g in parts[5:24]]
        item_genres[movie_id] = genre_vec

num_users = max(u for u, i, r, t in all_ratings) + 1
num_items = max(i for u, i, r, t in all_ratings) + 1
print(f"Users: {num_users}, Items: {num_items}, Ratings: {len(all_ratings)}")


# ==============================================================================
# 2. TRAIN / TEST SPLIT: Leave-One-Out
# ==============================================================================
# WHY leave-one-out? In recommendation research, the standard protocol is to
# hold out the most recent interaction per user for testing. This simulates
# the real task: "given everything the user has done so far, can you predict
# what they will do next?" Random splits are easier but less realistic.
# ==============================================================================

random.seed(42)
user_items = defaultdict(list)
for u, i, r, t in all_ratings:
    user_items[u].append((i, r, t))

train_data = []
test_data = []

for u, interactions in user_items.items():
    # Sort by time so the last one is the most recent
    interactions.sort(key=lambda x: x[2])
    # Hold out the last interaction for this user
    test_item, test_rating, _ = interactions[-1]
    test_data.append((u, test_item, test_rating))
    # Everything else is training
    for i, r, t in interactions[:-1]:
        train_data.append((u, i, r))

print(f"Train interactions: {len(train_data)}, Test interactions: {len(test_data)}")

# Build a fast lookup of what each user has seen in training
user_train_set = defaultdict(set)
for u, i, r in train_data:
    user_train_set[u].add(i)


# ==============================================================================
# 3. MATRIX FACTORIZATION MODEL
# ==============================================================================
# WHY embeddings? Each user and item gets a learned vector.
# The predicted score is the dot product plus biases.
# Biases capture "this user rates everything high" and "this movie is popular"
# without wasting latent dimensions on those simple effects.
# ==============================================================================

class MatrixFactorization(nn.Module):
    def __init__(self, num_users, num_items, embedding_dim=32):
        super().__init__()
        self.user_emb = nn.Embedding(num_users, embedding_dim)
        self.item_emb = nn.Embedding(num_items, embedding_dim)
        self.user_bias = nn.Embedding(num_users, 1)
        self.item_bias = nn.Embedding(num_items, 1)
        self.global_bias = nn.Parameter(torch.zeros(1))

        # WHY Xavier init: prevents dot products from exploding on the first
        # forward pass, which would make gradients unstable.
        nn.init.xavier_uniform_(self.user_emb.weight)
        nn.init.xavier_uniform_(self.item_emb.weight)

    def forward(self, user_ids, item_ids):
        u = self.user_emb(user_ids)
        i = self.item_emb(item_ids)
        dot = (u * i).sum(dim=1)
        score = (dot
                 + self.user_bias(user_ids).squeeze()
                 + self.item_bias(item_ids).squeeze()
                 + self.global_bias)
        return score


# ==============================================================================
# 4. TWO-TOWER RETRIEVAL MODEL
# ==============================================================================
# WHY two towers? In production, you have millions of items.
# You cannot run a full dot product against every item for every user.
# Two towers let you pre-compute all item embeddings offline, index them
# with FAISS / ScaNN, and retrieve top-k in milliseconds at query time.
#
# The user tower transforms user history into a query vector.
# The item tower transforms item metadata into a candidate vector.
# Both vectors live in the same space, so dot product measures relevance.
# ==============================================================================

class TwoTowerModel(nn.Module):
    def __init__(self, num_users, num_items, num_genres, embedding_dim=32):
        super().__init__()
        self.user_emb = nn.Embedding(num_users, embedding_dim)
        self.item_id_emb = nn.Embedding(num_items, embedding_dim)
        self.item_genre_fc = nn.Linear(num_genres, embedding_dim)

        # Small MLPs give the towers expressive power beyond a raw embedding
        self.user_tower = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim),
            nn.ReLU(),
            nn.Linear(embedding_dim, embedding_dim)
        )
        self.item_tower = nn.Sequential(
            nn.Linear(embedding_dim * 2, embedding_dim),
            nn.ReLU(),
            nn.Linear(embedding_dim, embedding_dim)
        )

    def forward(self, user_ids, item_ids):
        # --- User Tower ---
        u = self.user_emb(user_ids)
        u_vec = self.user_tower(u)

        # --- Item Tower ---
        i_id = self.item_id_emb(item_ids)

        # Look up genre vectors for the batch items
        # WHY genres? They give the item tower real semantic signal
        # instead of relying purely on item ID memorization.
        batch_size = item_ids.size(0)
        i_genre = torch.zeros(batch_size, 19, device=item_ids.device)
        for idx, mid in enumerate(item_ids.cpu().numpy()):
            if mid in item_genres:
                i_genre[idx] = torch.tensor(item_genres[mid], dtype=torch.float32)
        i_genre = i_genre.to(item_ids.device)

        i_feat = torch.cat([i_id, self.item_genre_fc(i_genre)], dim=1)
        i_vec = self.item_tower(i_feat)

        # Score = alignment in shared embedding space
        return (u_vec * i_vec).sum(dim=1)


# ==============================================================================
# 5. BPR PAIRWISE TRAINING LOOP
# ==============================================================================
# WHY BPR? We do not care about predicting the exact star rating.
# We care that the model scores observed items higher than unobserved items.
# BPR samples one positive and one negative per user, then pushes the
# positive score above the negative score using a sigmoid margin.
#
# This is computationally cheap and directly optimizes ranking.
# ==============================================================================

def train_bpr(model, train_data, num_items, epochs=10, lr=0.005, batch_size=1024):
    optimizer = optim.Adam(model.parameters(), lr=lr)
    model.train()

    for epoch in range(epochs):
        random.shuffle(train_data)
        total_loss = 0.0

        for start in range(0, len(train_data), batch_size):
            batch = train_data[start:start + batch_size]
            users = torch.LongTensor([u for u, i, r in batch]).to(device)
            pos_items = torch.LongTensor([i for u, i, r in batch]).to(device)

            # Sample random negatives: items the user has NOT seen in training
            neg_items = []
            for u, i, r in batch:
                neg = random.randint(0, num_items - 1)
                while neg in user_train_set[u]:
                    neg = random.randint(0, num_items - 1)
                neg_items.append(neg)
            neg_items = torch.LongTensor(neg_items).to(device)

            pos_score = model(users, pos_items)
            neg_score = model(users, neg_items)

            # BPR loss: -log(sigmoid(pos - neg))
            # WHY +1e-10? Numerical stability. If pos << neg, sigmoid -> 0,
            # and log(0) is -infinity. The epsilon prevents NaN gradients.
            loss = -torch.log(torch.sigmoid(pos_score - neg_score) + 1e-10).mean()

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        print(f"  Epoch {epoch + 1:2d}/{epochs} — Loss: {total_loss:.4f}")


# ==============================================================================
# 6. EVALUATION: HIT RATE & NDCG
# ==============================================================================
# WHY these metrics? In recommendation, 99.9% of items are irrelevant.
# Accuracy would be 99.9% by always saying "no." That is useless.
# Instead we ask:
#   - Hit Rate@K: Did the true item appear in the top K?
#   - NDCG@K: How high up the list was the true item?
#
# Both reflect the actual user experience of scrolling a ranked list.
# ==============================================================================

def evaluate(model, test_data, num_items, K=10):
    model.eval()
    hits = 0
    ndcg_accum = 0.0

    with torch.no_grad():
        for u, test_item, _ in test_data:
            # Score every item for this user
            all_items = torch.arange(num_items).to(device)
            user_tensor = torch.LongTensor([u] * num_items).to(device)
            scores = model(user_tensor, all_items).cpu().numpy()

            # Mask out items the user already saw in training
            # WHY? Recommending something the user already watched is cheating.
            for i in user_train_set[u]:
                scores[i] = -1e9

            top_k = np.argsort(scores)[::-1][:K]

            # Hit Rate
            if test_item in top_k:
                hits += 1
                # NDCG: rank position starts at 0, so log2(rank + 2)
                rank = np.where(top_k == test_item)[0][0]
                ndcg_accum += 1.0 / np.log2(rank + 2)

    hit_rate = hits / len(test_data)
    ndcg = ndcg_accum / len(test_data)
    return hit_rate, ndcg


# ==============================================================================
# 7. RUN EXPERIMENTS
# ==============================================================================

print("\n" + "=" * 60)
print("Training Matrix Factorization (BPR Loss)")
print("=" * 60)
mf_model = MatrixFactorization(num_users, num_items, embedding_dim=32).to(device)
train_bpr(mf_model, train_data, num_items, epochs=10, lr=0.005)
hr_mf, ndcg_mf = evaluate(mf_model, test_data, num_items, K=10)
print(f"MF  -> HitRate@10: {hr_mf:.4f}, NDCG@10: {ndcg_mf:.4f}")

print("\n" + "=" * 60)
print("Training Two-Tower Retrieval (BPR Loss)")
print("=" * 60)
tt_model = TwoTowerModel(num_users, num_items, num_genres=19, embedding_dim=32).to(device)
train_bpr(tt_model, train_data, num_items, epochs=10, lr=0.005)
hr_tt, ndcg_tt = evaluate(tt_model, test_data, num_items, K=10)
print(f"TT  -> HitRate@10: {hr_tt:.4f}, NDCG@10: {ndcg_tt:.4f}")


# ==============================================================================
# 8. SUMMARY
# ==============================================================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Matrix Factorization   HitRate@10={hr_mf:.4f}  NDCG@10={ndcg_mf:.4f}")
print(f"Two-Tower Retrieval    HitRate@10={hr_tt:.4f}  NDCG@10={ndcg_tt:.4f}")
print()
print("Key Insights:")
print("  1. BPR loss optimizes ranking, not star ratings.")
print("  2. Two-tower models enable fast ANN retrieval at serving time.")
print("  3. Evaluation must reflect the ranking goal (Hit Rate, NDCG).")
print("  4. Masking training items during evaluation prevents cheating.")
print("=" * 60)
