#!/usr/bin/env python3
"""
================================================================================
Phase 17: Attention Mechanism — Focusing on What Matters
================================================================================

This script is for a COMPLETE BEGINNER.

In Phase 16, our decoder only saw a single thought vector.
For long sentences, the thought vector forgets important details.

Attention fixes this by letting the decoder LOOK BACK at the encoder
at every step. It asks: "Which input word is most relevant RIGHT NOW?"

The key idea: Query, Key, Value.
  - Query = what am I looking for? (decoder's current state)
  - Key = what do I contain? (encoder's states)
  - Value = what information do I have? (encoder's states)

Relevance = dot(Query, Key)
Output = weighted sum of Values, weighted by relevance.

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
# ATTENTION MECHANISM (from scratch)
# ==============================================================================

def softmax(x, axis=-1):
    """Softmax over specified axis."""
    exp_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return exp_x / np.sum(exp_x, axis=axis, keepdims=True)


def dot_product_attention(query, keys, values):
    """
    Compute attention: weighted sum of values based on query-key similarity.

    PARAMETERS:
        query = vector representing what we are looking for (1, d_k)
        keys = matrix where each row is a key (seq_len, d_k)
        values = matrix where each row is a value (seq_len, d_v)

    RETURNS:
        context = weighted sum of values (1, d_v)
        attention_weights = how much we focus on each position (seq_len,)
    """
    # Step 1: Compute scores = query dot each key
    # query: (1, d_k), keys: (seq_len, d_k)
    # scores: (seq_len,)
    scores = np.dot(keys, query.T).squeeze()

    # Step 2: Scale by sqrt(d_k) to prevent huge values
    d_k = query.shape[1]
    scores = scores / np.sqrt(d_k)

    # Step 3: Softmax to get attention weights (sum to 1)
    attention_weights = softmax(scores)

    # Step 4: Weighted sum of values
    # attention_weights: (seq_len,), values: (seq_len, d_v)
    # context: (d_v,)
    context = np.dot(attention_weights, values)

    return context, attention_weights


# ==============================================================================
# DEMONSTRATION: Translation with Attention
# ==============================================================================

def demonstrate_attention():
    """
    Demonstrate attention with a concrete translation example.

    We will translate "The cat sat" to French.
    At each decoder step, we compute attention over encoder states
    and see which English word the decoder focuses on.
    """
    print("=" * 60)
    print("ATTENTION DEMONSTRATION")
    print("=" * 60)
    print()
    print("  Task: Translate 'The cat sat' to French")
    print("  French: 'Le chat s'est assis'")
    print()

    # Encoder states (simplified, 4 dimensions each)
    # Each row represents one input word's encoding
    encoder_states = np.array([
        [1.0, 0.1, 0.1, 0.1],  # The (article)
        [0.1, 1.0, 0.2, 0.1],  # cat (animal)
        [0.1, 0.2, 1.0, 0.1],  # sat (verb)
    ])

    english_words = ['The', 'cat', 'sat']
    french_words = ['Le', 'chat', "s'est", 'assis']

    # In attention, keys and values come from encoder states
    keys = encoder_states
    values = encoder_states

    print("  Encoder states (simplified):")
    for i, word in enumerate(english_words):
        print(f"    {word:5s}: {encoder_states[i]}")
    print()

    # Decoder steps
    print("  Decoder steps with attention:")
    print()

    # Step 1: Decoder wants to output "Le" (article)
    # Query looks for articles
    query_le = np.array([[0.9, 0.1, 0.1, 0.1]])  # Looking for article-like features
    context, weights = dot_product_attention(query_le, keys, values)
    print(f"  Step 1: Output 'Le'")
    print(f"    Attention weights: {dict(zip(english_words, [f'{w:.2f}' for w in weights]))}")
    print(f"    Focuses on: '{english_words[np.argmax(weights)]}' (correct!)")
    print()

    # Step 2: Decoder wants to output "chat" (animal)
    query_chat = np.array([[0.1, 0.9, 0.1, 0.1]])  # Looking for animal features
    context, weights = dot_product_attention(query_chat, keys, values)
    print(f"  Step 2: Output 'chat'")
    print(f"    Attention weights: {dict(zip(english_words, [f'{w:.2f}' for w in weights]))}")
    print(f"    Focuses on: '{english_words[np.argmax(weights)]}' (correct!)")
    print()

    # Step 3: Decoder wants to output "s'est assis" (verb)
    query_assis = np.array([[0.1, 0.1, 0.9, 0.1]])  # Looking for verb features
    context, weights = dot_product_attention(query_assis, keys, values)
    print(f"  Step 3: Output 'assis'")
    print(f"    Attention weights: {dict(zip(english_words, [f'{w:.2f}' for w in weights]))}")
    print(f"    Focuses on: '{english_words[np.argmax(weights)]}' (correct!)")
    print()

    return encoder_states, english_words, french_words


# ==============================================================================
# VISUALIZATION: Attention Heatmap
# ==============================================================================

def visualize_attention():
    """Create a visualization of attention weights."""
    print("=" * 60)
    print("VISUALIZING ATTENTION")
    print("=" * 60)

    # Create synthetic attention matrix
    # Rows = decoder steps (output words)
    # Columns = encoder steps (input words)
    # Values = attention weight

    input_words = ['The', 'cat', 'sat', 'on', 'the', 'mat']
    output_words = ['Le', 'chat', 's\'est', 'assis', 'sur', 'le', 'tapis']

    # Synthetic attention pattern
    # 'Le' -> 'The'
    # 'chat' -> 'cat'
    # 's'est' -> 'sat'
    # 'assis' -> 'sat'
    # 'sur' -> 'on'
    # 'le' -> 'the'
    # 'tapis' -> 'mat'
    attention_matrix = np.zeros((len(output_words), len(input_words)))
    attention_matrix[0, 0] = 0.8  # Le -> The
    attention_matrix[1, 1] = 0.9  # chat -> cat
    attention_matrix[2, 2] = 0.7  # s'est -> sat
    attention_matrix[3, 2] = 0.8  # assis -> sat
    attention_matrix[4, 3] = 0.9  # sur -> on
    attention_matrix[5, 4] = 0.8  # le -> the
    attention_matrix[6, 5] = 0.9  # tapis -> mat

    # Add some noise for realism
    attention_matrix += np.random.rand(*attention_matrix.shape) * 0.1
    attention_matrix = attention_matrix / attention_matrix.sum(axis=1, keepdims=True)

    fig, ax = plt.subplots(figsize=(10, 8))

    im = ax.imshow(attention_matrix, cmap='Blues', aspect='auto')

    # Set ticks
    ax.set_xticks(np.arange(len(input_words)))
    ax.set_yticks(np.arange(len(output_words)))
    ax.set_xticklabels(input_words)
    ax.set_yticklabels(output_words)

    # Add text annotations
    for i in range(len(output_words)):
        for j in range(len(input_words)):
            text = ax.text(j, i, f'{attention_matrix[i, j]:.2f}',
                          ha="center", va="center", color="black", fontsize=10)

    ax.set_xlabel('Input Words (English)', fontsize=12)
    ax.set_ylabel('Output Words (French)', fontsize=12)
    ax.set_title('Attention Heatmap: Which Input Word Does Each Output Word Focus On?',
                 fontsize=12, fontweight='bold')

    plt.colorbar(im, ax=ax, label='Attention Weight')
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase17/attention_heatmap.png', dpi=150)
    print("Plot saved to: src/phase17/attention_heatmap.png")
    plt.close()


# ==============================================================================
# MATHEMATICAL WALKTHROUGH
# ==============================================================================

def math_walkthrough():
    """Show the exact math of attention with real numbers."""
    print()
    print("=" * 60)
    print("MATHEMATICAL WALKTHROUGH")
    print("=" * 60)
    print()
    print("  Query  = [0.5, 0.1, 0.9]  (what the decoder is looking for)")
    print("  Key1   = [0.4, 0.2, 0.8]  (features of input word 1)")
    print("  Key2   = [0.9, 0.8, 0.1]  (features of input word 2)")
    print("  Key3   = [0.1, 0.9, 0.1]  (features of input word 3)")
    print()

    query = np.array([0.5, 0.1, 0.9])
    keys = np.array([
        [0.4, 0.2, 0.8],
        [0.9, 0.8, 0.1],
        [0.1, 0.9, 0.1]
    ])
    values = np.array([
        [1.0, 0.0],
        [0.0, 1.0],
        [0.5, 0.5]
    ])

    # Step 1: Dot products
    scores = np.dot(keys, query)
    print(f"  Step 1: Compute scores = Query dot Keys")
    print(f"    Score1 = {scores[0]:.3f}")
    print(f"    Score2 = {scores[1]:.3f}")
    print(f"    Score3 = {scores[2]:.3f}")
    print()

    # Step 2: Scale
    scores = scores / np.sqrt(3)
    print(f"  Step 2: Scale by sqrt(3) = {np.sqrt(3):.3f}")
    print(f"    Scaled scores: {[f'{s:.3f}' for s in scores]}")
    print()

    # Step 3: Softmax
    weights = softmax(scores)
    print(f"  Step 3: Apply softmax")
    print(f"    Weights: {[f'{w:.3f}' for w in weights]}")
    print(f"    (Sum = {np.sum(weights):.3f})")
    print()

    # Step 4: Weighted sum
    context = np.dot(weights, values)
    print(f"  Step 4: Weighted sum of Values")
    print(f"    Context = {weights[0]:.3f} * [1,0] + {weights[1]:.3f} * [0,1] + {weights[2]:.3f} * [0.5,0.5]")
    print(f"    Context = [{context[0]:.3f}, {context[1]:.3f}]")
    print()
    print(f"  Result: The output focuses {weights[0]*100:.1f}% on Value 1.")


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":

    # Demonstrate attention with translation example
    demonstrate_attention()

    # Visualize attention heatmap
    visualize_attention()

    # Show the math
    math_walkthrough()

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - Dot-product attention from scratch")
    print("    - Query, Key, Value mechanism")
    print("    - Attention visualization (heatmap)")
    print("    - Mathematical walkthrough with real numbers")
    print()
    print("  KEY INSIGHT:")
    print("    Attention lets the decoder focus on relevant encoder")
    print("    positions at each step. It replaces the single thought")
    print("    vector with a dynamic weighted combination.")
    print()
    print("  WHY THIS IS POWERFUL:")
    print("    - No bottleneck: decoder can access all encoder states")
    print("    - Interpretable: we can see which words the model focuses on")
    print("    - Works for long sequences")
    print()
    print("  NEXT QUESTION:")
    print("    'Attention is great, but RNNs are slow. Can we process")
    print("     ALL words at once instead of one at a time?'")
    print("=" * 60)
