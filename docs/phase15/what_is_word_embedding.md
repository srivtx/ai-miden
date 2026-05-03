# What Is Word Embedding?

## 1. Why it exists (THE PROBLEM first)
One-hot encoding treats every word as completely unrelated. "King" and "queen" are as different as "king" and "apple." There is no notion of similarity, relationships, or meaning—just isolated identity bits. This makes it impossible for a model to generalize (e.g., knowing that "king" and "queen" are both royalty).

## 2. Definition (very simple)
A word embedding is a dense, low-dimensional vector of real numbers that represents a word. Similar words end up with similar vectors, and the geometry of the space captures semantic relationships (e.g., king − man + woman ≈ queen).

## 3. Real-life analogy
GPS coordinates. Nearby cities have similar coordinates. Paris and London are close on the map. Paris and Tokyo are far apart. You can do math with coordinates: "If I go from Paris in the same direction and distance as London to Manchester, where do I land?"

## 4. Tiny numeric example
- "king" = [0.2, 0.5, −0.1]
- "queen" = [0.3, 0.4, −0.1]
- "apple" = [−0.8, 0.1, 0.9]

King and queen are close (similar numbers). Apple is far away (different numbers). A model can learn that king and queen belong to the same semantic neighborhood.

## 5. Common confusion
- "Is an embedding the same as one-hot encoding?" No. One-hot is sparse and high-dimensional; embedding is dense and low-dimensional.
- "Do we assign vectors manually?" No. They are learned automatically from text.
- "Are embeddings only for words?" No. You can embed sentences, images, users, or anything.
- "Is the dimension fixed?" No. Common choices are 50, 100, 300, or 768 dimensions.
- "Does 'similar vector' mean the words are synonyms?" Not always. It means they appear in similar contexts, which often implies related meaning.

## 6. Where it is used in our code
Used in the NLP pipeline as the first layer that converts token IDs into dense vectors before feeding them into downstream models.
