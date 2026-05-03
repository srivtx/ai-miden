#!/usr/bin/env python3
"""
================================================================================
Phase 15: Word Embeddings — Giving Words Meaning
================================================================================

This script is for a COMPLETE BEGINNER.

In Phase 14, our RNNs and LSTMs treated words as one-hot vectors.
"King" = [1,0,0,0,...], "Queen" = [0,1,0,0,...].

These vectors tell us NOTHING about meaning.
"King" and "Queen" are royalty, but the network sees them as completely unrelated.

Word embeddings solve this by representing each word as a DENSE VECTOR.
Similar words get similar vectors.

We learn these vectors using SKIP-GRAM with NEGATIVE SAMPLING.

Every line has a comment. Read it like a story.
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ==============================================================================
# VOCABULARY AND CORPUS
# ==============================================================================

def prepare_data():
    """
    Prepare a tiny corpus with clear semantic groupings.

    We create sentences about animals and food.
    The model should learn that animal words cluster together
    and food words cluster together.
    """
    sentences = [
        # Animal sentences
        "the cat sat on the mat",
        "the dog ran in the park",
        "the cat ate the fish",
        "the dog chased the cat",
        "a cat and a dog played",
        "the fish swam in water",
        "a bird flew in the sky",
        "the dog barked at the bird",
        "the cat caught the bird",
        "fish swim and birds fly",
        # Food sentences
        "the chef cooked the food",
        "the bread was fresh",
        "she ate the cake",
        "the chef baked bread",
        "he cooked fish for dinner",
        "the cake was sweet",
        "bread and cake are food",
        "the chef made a salad",
        "she ate bread with fish",
        "dinner was ready",
    ]

    # Tokenize
    all_words = []
    for sent in sentences:
        all_words.extend(sent.split())

    # Build vocabulary
    vocab = sorted(set(all_words))
    word_to_idx = {w: i for i, w in enumerate(vocab)}
    idx_to_word = {i: w for i, w in enumerate(vocab)}

    # Convert sentences to indices
    data = []
    for sent in sentences:
        words = sent.split()
        indices = [word_to_idx[w] for w in words]
        data.append(indices)

    return data, vocab, word_to_idx, idx_to_word


# ==============================================================================
# SKIP-GRAM WITH NEGATIVE SAMPLING
# ==============================================================================

class Word2Vec:
    """
    Word2Vec using Skip-gram with Negative Sampling.

    SKIP-GRAM:
    Given a center word, predict the words around it (context).
    Example: "the cat sat"
        Center: "cat"
        Context: "the", "sat"
        We train: P("the" | "cat") and P("sat" | "cat")

    NEGATIVE SAMPLING:
    Instead of predicting among ALL words (expensive),
    we predict: Is this pair (center, context) real or fake?
    We sample a few fake pairs and train the model to distinguish.
    """

    def __init__(self, vocab_size, embedding_dim, negative_samples=5):
        """
        Create Word2Vec model.

        PARAMETERS:
            vocab_size = number of unique words
            embedding_dim = size of each word vector (e.g., 10)
            negative_samples = how many fake pairs per real pair
        """
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.negative_samples = negative_samples

        # Two sets of embeddings:
        # W_in = center word embeddings
        # W_out = context word embeddings
        # In practice, we often just use W_in as the final word vectors
        self.W_in = np.random.randn(vocab_size, embedding_dim) * 0.01
        self.W_out = np.random.randn(vocab_size, embedding_dim) * 0.01

        # Word frequencies for negative sampling
        # More frequent words = more likely to be negative samples
        self.word_freq = None

    def sigmoid(self, x):
        """Sigmoid function."""
        return 1 / (1 + np.exp(-np.clip(x, -10, 10)))

    def compute_unigram_distribution(self, data):
        """
        Compute word frequencies raised to 3/4 power.
        This makes rare words more likely to be sampled.
        """
        counts = np.zeros(self.vocab_size)
        for sentence in data:
            for idx in sentence:
                counts[idx] += 1

        # Raise to 3/4 power (standard Word2Vec trick)
        freq = counts ** 0.75
        self.word_freq = freq / np.sum(freq)

    def generate_training_data(self, data, window_size=2):
        """
        Generate (center, context) pairs from the corpus.

        For each word, look at words within window_size distance.
        """
        pairs = []
        for sentence in data:
            for i, center in enumerate(sentence):
                # Look left and right
                for j in range(max(0, i - window_size), min(len(sentence), i + window_size + 1)):
                    if i != j:
                        context = sentence[j]
                        pairs.append((center, context))
        return pairs

    def train(self, data, learning_rate=0.01, epochs=1000, window_size=2):
        """
        Train the Word2Vec model.

        For each (center, context) pair:
        1. Compute score = dot(center_embedding, context_embedding)
        2. Predict probability = sigmoid(score)
        3. Loss = -log(probability) for real pairs
        4. Sample negative pairs, loss = -log(1 - probability) for fakes
        5. Backpropagate and update embeddings
        """
        print(f"Training Word2Vec...")
        print(f"  Vocab size: {self.vocab_size}")
        print(f"  Embedding dim: {self.embedding_dim}")
        print(f"  Training pairs: {len(self.generate_training_data(data))}")
        print()

        # Compute word frequencies for negative sampling
        self.compute_unigram_distribution(data)

        # Generate all training pairs
        pairs = self.generate_training_data(data, window_size)

        losses = []
        for epoch in range(epochs):
            total_loss = 0
            np.random.shuffle(pairs)

            for center, context in pairs:
                # --- POSITIVE PAIR ---
                # We want sigmoid(center · context) to be close to 1
                v_center = self.W_in[center]
                v_context = self.W_out[context]

                score = np.dot(v_center, v_context)
                prob = self.sigmoid(score)
                loss = -np.log(prob + 1e-8)
                total_loss += loss

                # Gradients for positive pair
                # dL/dscore = prob - 1 (since we want prob = 1)
                dscore = prob - 1

                # Update embeddings
                grad_center = dscore * v_context
                grad_context = dscore * v_center

                self.W_in[center] -= learning_rate * grad_center
                self.W_out[context] -= learning_rate * grad_context

                # --- NEGATIVE PAIRS ---
                # Sample random words that are NOT the context
                # We want sigmoid(center · negative) to be close to 0
                negatives = np.random.choice(
                    self.vocab_size,
                    size=self.negative_samples,
                    p=self.word_freq
                )

                for neg in negatives:
                    if neg == context:
                        continue  # Skip if we accidentally sampled the real context

                    v_neg = self.W_out[neg]
                    score_neg = np.dot(v_center, v_neg)
                    prob_neg = self.sigmoid(score_neg)
                    loss_neg = -np.log(1 - prob_neg + 1e-8)
                    total_loss += loss_neg

                    # Gradient: we want prob_neg = 0
                    dscore_neg = prob_neg  # derivative of -log(1-sigmoid(x)) = sigmoid(x)

                    grad_center_neg = dscore_neg * v_neg
                    grad_neg = dscore_neg * v_center

                    self.W_in[center] -= learning_rate * grad_center_neg
                    self.W_out[neg] -= learning_rate * grad_neg

            avg_loss = total_loss / len(pairs)
            losses.append(avg_loss)

            if epoch % 200 == 0:
                print(f"  Epoch {epoch:4d}: Loss = {avg_loss:.4f}")

        return losses

    def get_word_vector(self, word_idx):
        """Get the embedding for a word."""
        return self.W_in[word_idx]

    def find_similar(self, word_idx, top_k=5):
        """Find the most similar words to a given word."""
        vec = self.W_in[word_idx]

        # Compute cosine similarity with all words
        similarities = []
        for i in range(self.vocab_size):
            other = self.W_in[i]
            # Cosine similarity = dot product / (magnitudes)
            sim = np.dot(vec, other) / (np.linalg.norm(vec) * np.linalg.norm(other) + 1e-8)
            similarities.append((i, sim))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    def analogy(self, a, b, c, idx_to_word):
        """
        Solve: a is to b as c is to ?
        Example: king - man + woman = queen
        """
        vec = self.W_in[b] - self.W_in[a] + self.W_in[c]

        # Find closest word
        best_sim = -1
        best_idx = -1
        for i in range(self.vocab_size):
            if i in [a, b, c]:
                continue
            sim = np.dot(vec, self.W_in[i]) / (np.linalg.norm(vec) * np.linalg.norm(self.W_in[i]) + 1e-8)
            if sim > best_sim:
                best_sim = sim
                best_idx = i

        return best_idx, best_sim


# ==============================================================================
# MAIN DEMONSTRATION
# ==============================================================================

if __name__ == "__main__":

    # --------------------------------------------------------------------------
    # PART A: Prepare data
    # --------------------------------------------------------------------------
    print("=" * 60)
    print("WORD EMBEDDINGS: GIVING WORDS MEANING")
    print("=" * 60)
    print()

    data, vocab, word_to_idx, idx_to_word = prepare_data()

    print(f"Vocabulary ({len(vocab)} words):")
    print(f"  {vocab}")
    print()
    print("The model will learn vectors such that:")
    print("  - Animal words cluster together (cat, dog, bird, fish)")
    print("  - Food words cluster together (bread, cake, food, dinner)")
    print()

    # --------------------------------------------------------------------------
    # PART B: Train Word2Vec
    # --------------------------------------------------------------------------
    print("=" * 60)
    print("TRAINING WORD2VEC")
    print("=" * 60)

    model = Word2Vec(
        vocab_size=len(vocab),
        embedding_dim=10,
        negative_samples=3
    )

    losses = model.train(data, learning_rate=0.05, epochs=2000, window_size=2)

    # --------------------------------------------------------------------------
    # PART C: Inspect learned vectors
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("LEARNED WORD VECTORS")
    print("=" * 60)
    print()

    for word in ["cat", "dog", "fish", "bird", "bread", "cake", "chef"]:
        idx = word_to_idx[word]
        vec = model.get_word_vector(idx)
        print(f"  {word:10s}: {vec[:5]} ...")

    # --------------------------------------------------------------------------
    # PART D: Find similar words
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SIMILAR WORDS")
    print("=" * 60)
    print()

    test_words = ["cat", "dog", "bread", "cake"]
    for word in test_words:
        idx = word_to_idx[word]
        similar = model.find_similar(idx, top_k=4)
        similar_words = [idx_to_word[i] for i, _ in similar if i != idx]
        print(f"  Words similar to '{word}': {similar_words}")

    # --------------------------------------------------------------------------
    # PART E: Visualize
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("VISUALIZING WORD VECTORS")
    print("=" * 60)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1: Loss curve
    axes[0].plot(losses, color='blue', linewidth=2)
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Training Loss')
    axes[0].grid(True, alpha=0.3)

    # Plot 2: 2D projection of word vectors
    # We'll use a simple projection: just plot the first 2 dimensions
    # In reality we'd use t-SNE, but for a tiny example, 2 dims show structure
    words_to_plot = ["cat", "dog", "fish", "bird", "chef", "bread", "cake",
                     "food", "dinner", "sat", "ran", "ate", "the", "a", "in"]

    for word in words_to_plot:
        if word in word_to_idx:
            idx = word_to_idx[word]
            vec = model.get_word_vector(idx)
            color = 'red' if word in ["cat", "dog", "fish", "bird"] else \
                    'green' if word in ["bread", "cake", "food", "dinner", "chef"] else 'gray'
            axes[1].scatter(vec[0], vec[1], c=color, s=100, alpha=0.7)
            axes[1].annotate(word, (vec[0], vec[1]), fontsize=10, ha='center')

    axes[1].set_xlabel('Dimension 1')
    axes[1].set_ylabel('Dimension 2')
    axes[1].set_title('Word Vectors (first 2 dimensions)')
    axes[1].grid(True, alpha=0.3)

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='red', label='Animals'),
        Patch(facecolor='green', label='Food'),
        Patch(facecolor='gray', label='Other')
    ]
    axes[1].legend(handles=legend_elements)

    fig.suptitle('Word2Vec: Learning Word Meanings', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase15/word_embeddings.png', dpi=150)
    print("Plot saved to: src/phase15/word_embeddings.png")
    plt.close()

    # --------------------------------------------------------------------------
    # PART F: Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - Word2Vec with Skip-gram and Negative Sampling")
    print("    - Trained on a tiny corpus of animal/food sentences")
    print("    - Learned 10-dimensional vectors for each word")
    print()
    print("  KEY INSIGHT:")
    print("    Words that appear in similar contexts get similar vectors.")
    print("    'Cat' and 'dog' are similar because they both appear with")
    print("    'the', 'sat', 'ran', 'ate', etc.")
    print()
    print("  WHY THIS IS POWERFUL:")
    print("    - We learn meaning from raw text, no labels needed")
    print("    - Similar words cluster in vector space")
    print("    - We can do math: king - man + woman ≈ queen")
    print()
    print("  NEXT QUESTION:")
    print("    'How do I translate a sentence when input and output")
    print("     have different lengths?'")
    print("=" * 60)
