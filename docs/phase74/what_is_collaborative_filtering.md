### 1. Why it exists (THE PROBLEM first)

Imagine a streaming service with 50,000 movies and 10 million users. Showing every user the same "Top 10" list is a waste: a horror fan does not want romantic comedies, and a documentary lover does not care about superhero blockbusters. The problem is not a lack of data — users constantly rate, click, watch, and skip. The problem is making sense of those raw interactions so that each user sees a personalized slice of the catalog. Without personalization, discovery dies and users leave.

### 2. Definition (very simple)

Collaborative Filtering (CF) recommends items by looking at what similar users liked, or what items similar to the ones you liked were enjoyed by others. It uses **only** past user-item interactions (ratings, clicks, purchases). It does not need to know that a movie is a "comedy" or that a user is "25 years old."

### 3. Real-life analogy

You walk into a bookstore and ask the clerk for a recommendation. The clerk does not scan the book's contents or your DNA. Instead, she remembers that you loved the same three novels as another customer last month, and that customer just raved about a new mystery thriller. She recommends the thriller. That is user-based collaborative filtering.

### 4. Tiny numeric example

Three users and four items. Ratings are 1-5 stars (0 = unseen).

| User | Item A | Item B | Item C | Item D |
|---|---|---|---|---|
| U1 | 5 | 3 | 0 | 1 |
| U2 | 4 | 0 | 0 | 2 |
| U3 | 1 | 1 | 0 | 5 |

U1 and U2 both liked Item A (5 and 4) and disliked Item D (1 and 2). Their tastes are similar. Item C is unseen by both. If U2 rated Item C highly, CF would predict U1 would like it too.

- Cosine similarity(U1, U2) is high because their co-rated items move together.
- Prediction for U1 on Item C = weighted average of similar users' ratings for Item C.

### 5. Common confusion

- **CF does not use item features.** It only cares about who interacted with what. A movie's genre, director, and budget are completely ignored unless you switch to content-based or hybrid methods.
- **User-based vs. Item-based CF are different.** User-based finds similar people. Item-based finds similar items (e.g., "people who bought X also bought Y"). They feel similar but answer different questions.
- **The sparsity problem is severe.** In a real catalog, a user has seen 0.01% of items. With so few overlapping ratings, similarity estimates become noisy and unreliable.
- **Cold start is brutal.** A brand-new user with zero history cannot be matched to anyone. A brand-new item with zero ratings cannot be recommended by CF alone.
- **Similarity metrics matter.** Cosine similarity ignores rating scale (a user who rates everything 4 vs. a user who rates everything 5 may look identical). Pearson correlation fixes this by centering on each user's mean.
- **Popular items dominate.** Items with millions of ratings appear in every similarity computation, biasing recommendations toward blockbusters and burying niche gems.

### 6. Where it is used in our code

`src/phase74/phase74_recommendation_systems.py` implements user-based collaborative filtering with cosine similarity on a synthetic sparse rating matrix. It compares CF predictions against a popularity baseline and matrix factorization.
