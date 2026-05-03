### 1. Why it exists (THE PROBLEM first)

A modern platform has millions of users and billions of items. At serving time, you cannot compute the dot product between one user's vector and every single item vector — that would take seconds and cost a fortune. You need a way to pre-compute representations so that finding the top 100 recommendations feels like a Google search: instant, scalable, and cheap.

### 2. Definition (very simple)

A Two-Tower Model uses two separate neural networks — one for the user (query tower) and one for the item (candidate tower) — that embed both sides into the same vector space. At serving time, the item vectors are pre-computed and indexed. When a user arrives, you run only the query tower once and use Approximate Nearest Neighbor (ANN) search to retrieve the closest item vectors in milliseconds.

### 3. Real-life analogy

Imagine two key makers. One examines your house (the query tower) and cuts a unique key shape. The other examines every door lock in the city (the candidate tower) and records each lock's internal shape. Instead of trying your key in every door, the city publishes a catalog of lock shapes. You simply flip to the page showing shapes closest to your key. That is ANN retrieval. The two towers ensure the key and lock shapes are measured in the same units.

### 4. Tiny numeric example

User features: age bracket, country, last 3 genres watched.
Item features: movie genre vector, release year bucket, director embedding.

Query tower:
- Input: user features (dim 20)
- Hidden layer: 32 neurons, ReLU
- Output: 8-dim user embedding

Candidate tower:
- Input: item features (dim 25)
- Hidden layer: 32 neurons, ReLU
- Output: 8-dim item embedding

Score = dot(user_embedding, item_embedding).

For 10 million items, pre-computing all item embeddings takes minutes. At query time, ANN search (e.g., ScaNN, FAISS) finds the top 100 items in ~5 milliseconds.

### 5. Common confusion

- **Two-tower is a retrieval model, not a ranker.** It finds a rough set of candidates quickly. A separate, heavier ranking model (often a cross-attention model) usually re-ranks the top 100 into a final ordered list.
- **The towers usually do NOT share weights.** The query and candidate inputs are fundamentally different (user history vs. item metadata), so forcing them through the same weights hurts performance.
- **You need ANN for it to make sense.** Without approximate nearest neighbor search, you are still doing a linear scan over all items. The tower architecture alone does not solve the scale problem.
- **Training requires negative sampling.** For each positive (user, item) pair, you must sample negatives — either random negatives, batch negatives, or hard negatives — so the model learns to distinguish good matches from bad ones.
- **It optimizes for recall, not precision at rank 1.** Because it is a retrieval step, the goal is to make sure the best items are somewhere in the top 500. The final ranker handles exact ordering.

### 6. Where it is used in our code

`src/phase74/phase74_recommendation_systems_colab.py` implements a two-tower retrieval model in PyTorch on the MovieLens dataset. The user tower processes user ID embeddings, while the item tower processes item ID embeddings plus genre features. The script demonstrates how this architecture scales retrieval compared to a flat matrix factorization model.
