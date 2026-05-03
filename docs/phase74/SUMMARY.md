← [Previous: Phase 73: Speech & Audio](docs/phase73/SUMMARY.md) | [Next: Phase 75: Explainable AI (XAI)](docs/phase75/SUMMARY.md) →

---

## Phase 74 Summary: Recommendation Systems

**The Question:** "My application has thousands of users and millions of items. How do I show each user exactly what they want without manually curating lists?"

---

### What We Learned

1. **Collaborative Filtering**
   - Recommends items by finding similar users or similar items
   - Uses only interaction history (ratings, clicks, purchases)
   - Suffers from sparsity and cold-start problems but is intuitive and powerful

2. **Matrix Factorization**
   - Decomposes the user-item matrix into low-rank latent factor matrices
   - Generalizes to unseen interactions by learning hidden "taste" dimensions
   - Often augmented with bias terms for users and items

3. **Two-Tower Model**
   - Separates user encoding (query tower) from item encoding (candidate tower)
   - Embeds both into the same vector space for fast dot-product scoring
   - Enables billion-scale retrieval via Approximate Nearest Neighbor (ANN) indexing

4. **Ranking Loss (BPR / WARP)**
   - Optimizes relative order of items rather than absolute ratings
   - BPR pushes observed items above randomly sampled negatives
   - WARP weights mistakes by how far down the list they occur

---

### Results

- Popularity baseline is the floor: no personalization
- User-based CF personalizes but struggles with sparse overlap
- MF generalizes better by learning latent factors (SVD-style)
- Two-tower models scale to massive catalogs via ANN retrieval
- BPR loss aligns training with the true goal of ranking

---

### Phase 74 Files

| File | Purpose |
|---|---|
| `docs/phase74/what_is_collaborative_filtering.md` | Finding recommendations through user and item similarity |
| `docs/phase74/what_is_matrix_factorization.md` | Learning latent factors via SVD-style decomposition |
| `docs/phase74/what_is_two_tower_model.md` | Query tower + candidate tower for scalable retrieval |
| `docs/phase74/what_is_ranking_loss.md` | BPR, WARP, and pairwise learning-to-rank |
| `src/phase74/phase74_recommendation_systems.py` | NumPy demo: popularity, CF, MF, and visualization |
| `src/phase74/phase74_recommendation_systems_colab.py` | PyTorch training on MovieLens with BPR, Hit Rate, NDCG |

---

### Connects To

- **Phase 72:** Real Agents with Tool Use — We built systems that act. Now we personalize what they surface.
- **Phase 53:** Classical Reinforcement Learning — Recommendation can also be framed as sequential decision-making (bandits, RL).

---

← [Previous: Phase 73: Speech & Audio](docs/phase73/SUMMARY.md) | [Next: Phase 75: Explainable AI (XAI)](docs/phase75/SUMMARY.md) →
