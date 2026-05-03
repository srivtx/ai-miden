#!/usr/bin/env python3
"""
================================================================================
Phase 19: BERT — Bidirectional Encoder Representations
================================================================================

This script is for a COMPLETE BEGINNER.

In Phase 18, we built the full Transformer (encoder + decoder).
But what if we ONLY want to UNDERSTAND text, not generate it?

BERT uses ONLY the encoder. It reads the whole sentence in BOTH
directions simultaneously. Then it can answer questions about the text.

Key idea: Masked Language Modeling (MLM)
  1. Take a sentence: "The cat sat on the mat"
  2. Randomly mask a word: "The [MASK] sat on the mat"
  3. Train the model to predict the masked word: "cat"

Because BERT reads bidirectionally, it looks at BOTH:
  - "The [MASK]" (left context)
  - "sat on the mat" (right context)

This is different from GPT, which only looks left.

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
# UTILITIES
# ==============================================================================

def softmax(x, axis=-1):
    exp_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return exp_x / np.sum(exp_x, axis=axis, keepdims=True)


def relu(x):
    return np.maximum(0, x)


# ==============================================================================
# SELF-ATTENTION (from Phase 18)
# ==============================================================================

def self_attention(X, W_q, W_k, W_v, mask=None):
    """Self-attention with optional mask."""
    Q = X @ W_q
    K = X @ W_k
    V = X @ W_v

    d_k = Q.shape[1]
    scores = (Q @ K.T) / np.sqrt(d_k)

    if mask is not None:
        scores = scores + mask

    attention_weights = softmax(scores, axis=-1)
    context = attention_weights @ V

    return context, attention_weights


# ==============================================================================
# BERT-STYLE ENCODER BLOCK
# ==============================================================================

def bert_encoder_block(X, W_q, W_k, W_v, W_o, W_ff1, b_ff1, W_ff2, b_ff2):
    """
    One BERT encoder block:
    1. Self-attention (bidirectional — no causal mask!)
    2. Add & Norm
    3. Feed-forward
    4. Add & Norm
    """
    # Self-attention (bidirectional — all words see all words)
    attn_output, _ = self_attention(X, W_q, W_k, W_v)
    attn_output = attn_output @ W_o

    # Add & Norm (simplified)
    X = X + attn_output

    # Feed-forward
    ff_output = relu(X @ W_ff1 + b_ff1) @ W_ff2 + b_ff2

    # Add & Norm
    X = X + ff_output

    return X


# ==============================================================================
# MASKED LANGUAGE MODELING DEMONSTRATION
# ==============================================================================

def demonstrate_mlm():
    """
    Demonstrate Masked Language Modeling with synthetic embeddings.

    We create word embeddings where:
    - "cat" and "dog" have similar vectors (animals)
    - "sat" and "ran" have similar vectors (verbs)
    - "mat" and "rug" have similar vectors (objects)

    Then we mask "cat" and see if attention helps predict it.
    """
    print("=" * 60)
    print("MASKED LANGUAGE MODELING DEMONSTRATION")
    print("=" * 60)
    print()

    # Vocabulary and embeddings
    words = ['The', 'cat', 'sat', 'on', 'the', 'mat']
    vocab_size = len(words)
    d_model = 8

    # Synthetic embeddings that encode meaning
    embeddings = np.array([
        [1.0, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],  # The (article)
        [0.1, 1.0, 0.8, 0.1, 0.1, 0.1, 0.1, 0.1],  # cat (animal)
        [0.1, 0.1, 0.1, 1.0, 0.8, 0.1, 0.1, 0.1],  # sat (verb)
        [0.1, 0.1, 0.1, 0.1, 0.1, 1.0, 0.1, 0.1],  # on (preposition)
        [1.0, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],  # the (article)
        [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 1.0, 0.8],  # mat (object)
    ])

    print("  Original sentence: 'The cat sat on the mat'")
    print()

    # Mask position 1 ("cat")
    masked_embeddings = embeddings.copy()
    masked_embeddings[1] = np.zeros(d_model)  # Replace "cat" with zeros

    print("  Masked sentence: 'The [MASK] sat on the mat'")
    print()

    # Initialize weights
    d_k = 4
    W_q = np.random.randn(d_model, d_k) * 0.1
    W_k = np.random.randn(d_model, d_k) * 0.1
    W_v = np.random.randn(d_model, d_k) * 0.1
    W_o = np.random.randn(d_k, d_model) * 0.1
    W_ff1 = np.random.randn(d_model, d_model * 2) * 0.1
    b_ff1 = np.zeros((1, d_model * 2))
    W_ff2 = np.random.randn(d_model * 2, d_model) * 0.1
    b_ff2 = np.zeros((1, d_model))

    # Pass through BERT encoder
    output = bert_encoder_block(masked_embeddings, W_q, W_k, W_v, W_o,
                                 W_ff1, b_ff1, W_ff2, b_ff2)

    # Predict masked word: compute similarity between masked position and all words
    masked_output = output[1]
    similarities = []
    for i in range(vocab_size):
        sim = np.dot(masked_output, embeddings[i]) / (np.linalg.norm(masked_output) * np.linalg.norm(embeddings[i]) + 1e-8)
        similarities.append((words[i], sim))

    similarities.sort(key=lambda x: x[1], reverse=True)

    print("  Prediction scores for [MASK] position:")
    for word, sim in similarities:
        marker = " <-- MASKED WORD" if word == "cat" else ""
        print(f"    {word:5s}: {sim:.3f}{marker}")
    print()

    # Show that bidirectional context helps
    print("  Why bidirectional matters:")
    print("    Left context:  'The [MASK]' → suggests a noun")
    print("    Right context: 'sat on the mat' → suggests an animal that sits")
    print("    Combined: most likely 'cat' or 'dog'")
    print()

    return embeddings, words, output


# ==============================================================================
# BIDIRECTIONAL vs UNIDIRECTIONAL COMPARISON
# ==============================================================================

def compare_bidirectional():
    """Show why bidirectional understanding is more powerful."""
    print("=" * 60)
    print("BIDIRECTIONAL vs UNIDIRECTIONAL")
    print("=" * 60)
    print()

    sentences = [
        "The [MASK] was so tired that it fell asleep immediately.",
        "He went to the [MASK] to deposit money.",
        "She opened the [MASK] and found a letter inside."
    ]

    answers = ["cat/person", "bank", "mailbox/door"]

    print("  For these sentences, you NEED bidirectional context:")
    print()
    for sent, ans in zip(sentences, answers):
        print(f"    {sent}")
        print(f"    Answer: {ans}")
        print()

    print("  A unidirectional model (like GPT) reading left-to-right")
    print("  would only see: 'The [MASK] was so tired...'")
    print("  It would NOT see 'fell asleep immediately' when predicting the mask.")
    print()
    print("  BERT sees BOTH sides simultaneously.")
    print()


# ==============================================================================
# VISUALIZATION
# ==============================================================================

def visualize_bert():
    """Visualize BERT architecture."""
    print("=" * 60)
    print("VISUALIZING BERT ARCHITECTURE")
    print("=" * 60)

    fig, ax = plt.subplots(figsize=(10, 8))

    # Draw BERT
    ax.text(0.5, 0.95, 'BERT: Bidirectional Encoder', ha='center', fontsize=16,
            fontweight='bold', bbox=dict(boxstyle='round', facecolor='lightblue'))

    # Input
    ax.text(0.5, 0.85, 'Input: "The cat sat on the mat"', ha='center', fontsize=12,
            bbox=dict(boxstyle='round', facecolor='lightgray'))
    ax.arrow(0.5, 0.82, 0, -0.03, head_width=0.05, head_length=0.02, fc='black')

    # Tokenize + Positional Encoding
    ax.text(0.5, 0.75, 'Tokenize + Positional Encoding', ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='lightyellow'))
    ax.arrow(0.5, 0.72, 0, -0.03, head_width=0.05, head_length=0.02, fc='black')

    # Encoder Block 1
    ax.text(0.5, 0.65, 'Encoder Block 1\n(Multi-Head Attention + FF)', ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='lightgreen'))
    ax.arrow(0.5, 0.62, 0, -0.03, head_width=0.05, head_length=0.02, fc='black')

    # Encoder Block 2
    ax.text(0.5, 0.55, 'Encoder Block 2\n(Multi-Head Attention + FF)', ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='lightgreen'))
    ax.arrow(0.5, 0.52, 0, -0.03, head_width=0.05, head_length=0.02, fc='black')

    # ... more blocks ...
    ax.text(0.5, 0.45, '...', ha='center', fontsize=14)
    ax.arrow(0.5, 0.43, 0, -0.03, head_width=0.05, head_length=0.02, fc='black')

    # Encoder Block N
    ax.text(0.5, 0.35, 'Encoder Block N\n(Multi-Head Attention + FF)', ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='lightgreen'))
    ax.arrow(0.5, 0.32, 0, -0.03, head_width=0.05, head_length=0.02, fc='black')

    # Output
    ax.text(0.5, 0.25, 'Contextualized Embeddings', ha='center', fontsize=12,
            bbox=dict(boxstyle='round', facecolor='lightcoral'))
    ax.arrow(0.5, 0.22, 0, -0.03, head_width=0.05, head_length=0.02, fc='black')

    # Classification head
    ax.text(0.5, 0.15, 'Classification Head\n(MLM / NER / QA / etc.)', ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='plum'))

    # Key difference note
    ax.text(0.05, 0.05, 'KEY: No decoder. No causal mask.\nEvery word sees every word.',
            fontsize=10, style='italic', bbox=dict(boxstyle='round', facecolor='wheat'))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase19/bert_architecture.png', dpi=150)
    print("Plot saved to: src/phase19/bert_architecture.png")
    plt.close()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("BERT: BIDIRECTIONAL ENCODER REPRESENTATIONS")
    print("=" * 60)
    print()
    print("  BERT = Transformer Encoder ONLY")
    print("  Reads the whole sentence in BOTH directions")
    print("  Pre-trained by predicting masked words")
    print()

    # Demonstrate MLM
    demonstrate_mlm()

    # Compare bidirectional vs unidirectional
    compare_bidirectional()

    # Visualize
    visualize_bert()

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - BERT encoder block (bidirectional self-attention)")
    print("    - Masked Language Modeling demonstration")
    print("    - Comparison: bidirectional vs unidirectional")
    print("    - Architecture visualization")
    print()
    print("  KEY INSIGHT:")
    print("    BERT uses ONLY the Transformer encoder.")
    print("    It reads text in BOTH directions simultaneously.")
    print("    It is pre-trained to predict masked words.")
    print("    Then it is fine-tuned for any understanding task.")
    print()
    print("  BERT vs GPT:")
    print("    BERT: Encoder only, bidirectional, understands")
    print("    GPT:  Decoder only, unidirectional, generates")
    print()
    print("  NEXT QUESTION:")
    print("    'BERT understands text. What does a purely")
    print("     generative model look like?'")
    print("=" * 60)
