### 1. Why it exists (THE PROBLEM first)

Collaborative filtering breaks down when the rating matrix is extremely sparse. If two users have only one movie in common, their similarity score is based on a single data point and is basically noise. Worse, CF cannot predict anything for user-item pairs that have no overlapping neighbors. We need a way to generalize from sparse observations — to discover hidden patterns (latent factors) that explain why certain users like certain items, even when those users have never directly been compared.

### 2. Definition (very simple)

Matrix Factorization (MF) decomposes the giant user-item rating matrix into two smaller matrices: one representing users in a low-dimensional "taste" space, and one representing items in the same space. A user's predicted rating for an item is the dot product of their taste vector and the item's attribute vector.

### 3. Real-life analogy

Think of music genres. Every song has an invisible "rock-ness," "jazz-ness," and "classical-ness" score. Every listener has the same three scores representing their taste. A heavy-metal fan has high rock-ness taste. A smooth-jazz track has high jazz-ness and low rock-ness. The predicted match is the dot product of the fan's taste vector and the song's genre vector. Matrix factorization learns these invisible genre scores automatically from listening history alone.

### 4. Tiny numeric example

A 4-user x 5-item rating matrix (missing entries = 0 for this demo) is factorized into rank-2 latent matrices:

User matrix U (4 users x 2 latent factors):

| User | Factor 1 | Factor 2 |
|---|---|---|
| U1 | 0.9 | 0.1 |
| U2 | 0.8 | 0.2 |
| U3 | 0.1 | 0.9 |
| U4 | 0.2 | 0.8 |

Item matrix V (2 latent factors x 5 items):

| Factor | I1 | I2 | I3 | I4 | I5 |
|---|---|---|---|---|---|
| F1 | 0.8 | 0.7 | 0.1 | 0.9 | 0.2 |
| F2 | 0.1 | 0.2 | 0.9 | 0.1 | 0.8 |

Prediction for U1 on I3 = (0.9 * 0.1) + (0.1 * 0.9) = 0.18. Low score = U1 will not like I3.
Prediction for U1 on I1 = (0.9 * 0.8) + (0.1 * 0.1) = 0.73. High score = U1 will like I1.

### 5. Common confusion

- **MF is related to SVD but not identical.** Classical SVD requires a dense matrix with no missing values. Real rating matrices are sparse, so MF uses iterative methods (SGD, ALS) that ignore missing entries instead of filling them with zeros.
- **Latent factors are not hand-labeled genres.** They are learned automatically. Factor 1 might correlate with action movies, but it could also capture budget, pacing, or era. The model does not name them.
- **Adding too many factors causes overfitting.** If k = 500 for 100 users, the model memorizes noise. Regularization (L2 on embeddings) is essential.
- **Bias terms are separate from latent factors.** A user's overall generosity (always giving 5 stars) and an item's baseline popularity are modeled as scalar biases, not as part of the latent vectors.
- **MF works for implicit feedback too.** Even without star ratings, binary signals (clicked / not clicked) can be weighted and factorized using techniques like weighted alternating least squares (W-ALS).

### 6. Where it is used in our code

`src/phase74/phase74_recommendation_systems.py` demonstrates SVD-style matrix factorization on a synthetic rating matrix. It shows how reconstructing the matrix from only two latent factors generalizes to missing entries and produces different recommendations than pure collaborative filtering.
