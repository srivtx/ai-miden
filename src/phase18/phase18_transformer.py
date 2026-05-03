#!/usr/bin/env python3
"""
================================================================================
Phase 18: The Transformer Architecture
================================================================================

This script is for a COMPLETE BEGINNER.

In Phase 17, we added attention to RNNs. But RNNs are still slow.
They process one word at a time. GPUs have thousands of cores!

The Transformer is the breakthrough that changed everything.
It REMOVES RNNs entirely and replaces them with attention.

Key insight: Instead of reading left-to-right, the Transformer
lets EVERY word attend to EVERY other word SIMULTANEOUSLY.

Architecture:
  Input: "The cat sat"
    |
    v
  Positional Encoding (add position info)
    |
    v
  Multi-Head Self-Attention (words talk to each other)
    |
    v
  Feed-Forward Network (process each word independently)
    |
    v
  Output: Predictions

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
    """Softmax over specified axis."""
    exp_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return exp_x / np.sum(exp_x, axis=axis, keepdims=True)


def relu(x):
    return np.maximum(0, x)


# ==============================================================================
# POSITIONAL ENCODING
# ==============================================================================

def positional_encoding(seq_len, d_model):
    """
    Create positional encoding vectors.

    Each position gets a unique encoding based on sine and cosine
    functions of different frequencies. This lets the model
    distinguish position 0 from position 5, even for the same word.
    """
    positions = np.arange(seq_len)[:, np.newaxis]  # (seq_len, 1)
    div_term = np.exp(np.arange(0, d_model, 2) * -(np.log(10000.0) / d_model))

    pe = np.zeros((seq_len, d_model))
    pe[:, 0::2] = np.sin(positions * div_term)  # Even indices: sine
    pe[:, 1::2] = np.cos(positions * div_term)  # Odd indices: cosine

    return pe


# ==============================================================================
# SELF-ATTENTION (Single Head)
# ==============================================================================

def self_attention(X, W_q, W_k, W_v, W_o):
    """
    Compute self-attention for input X.

    PARAMETERS:
        X = input matrix (seq_len, d_model)
        W_q, W_k, W_v, W_o = weight matrices

    RETURNS:
        output = attended output (seq_len, d_model)
        attention_weights = (seq_len, seq_len)
    """
    # Step 1: Create Q, K, V by projecting X
    Q = X @ W_q  # (seq_len, d_k)
    K = X @ W_k  # (seq_len, d_k)
    V = X @ W_v  # (seq_len, d_v)

    # Step 2: Compute attention scores
    # score[i,j] = how much word i should attend to word j
    d_k = Q.shape[1]
    scores = (Q @ K.T) / np.sqrt(d_k)  # (seq_len, seq_len)

    # Step 3: Softmax to get attention weights
    attention_weights = softmax(scores, axis=-1)  # (seq_len, seq_len)

    # Step 4: Weighted sum of values
    context = attention_weights @ V  # (seq_len, d_v)

    # Step 5: Output projection
    output = context @ W_o  # (seq_len, d_model)

    return output, attention_weights


# ==============================================================================
# MULTI-HEAD ATTENTION
# ==============================================================================

def multi_head_attention(X, W_q_list, W_k_list, W_v_list, W_o, num_heads):
    """
    Multi-head attention: run self-attention multiple times in parallel.

    Each head learns a different type of relationship.
    """
    seq_len, d_model = X.shape
    head_outputs = []
    head_attentions = []

    for h in range(num_heads):
        # Compute Q, K, V for this head
        d_k = W_q_list[h].shape[1]
        Q = X @ W_q_list[h]
        K = X @ W_k_list[h]
        V = X @ W_v_list[h]

        # Attention scores
        scores = (Q @ K.T) / np.sqrt(d_k)
        attention_weights = softmax(scores, axis=-1)
        context = attention_weights @ V

        head_outputs.append(context)
        head_attentions.append(attention_weights)

    # Concatenate all heads
    concatenated = np.concatenate(head_outputs, axis=-1)  # (seq_len, num_heads * d_v)

    # Project back to d_model
    output = concatenated @ W_o  # (seq_len, d_model)

    return output, head_attentions


# ==============================================================================
# TRANSFORMER BLOCK
# ==============================================================================

def transformer_block(X, W_q_list, W_k_list, W_v_list, W_o, W_ff1, b_ff1, W_ff2, b_ff2, num_heads):
    """
    One Transformer block:
    1. Multi-head self-attention
    2. Add & Norm (simplified: just add)
    3. Feed-forward network
    4. Add & Norm (simplified: just add)
    """
    # Self-attention
    attn_output, attentions = multi_head_attention(X, W_q_list, W_k_list, W_v_list, W_o, num_heads)

    # Add & Norm (simplified)
    X = X + attn_output

    # Feed-forward
    ff_output = relu(X @ W_ff1 + b_ff1) @ W_ff2 + b_ff2

    # Add & Norm (simplified)
    X = X + ff_output

    return X, attentions


# ==============================================================================
# MAIN DEMONSTRATION
# ==============================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("THE TRANSFORMER ARCHITECTURE")
    print("=" * 60)
    print()
    print("  The Transformer replaces RNNs with pure attention.")
    print("  Every word attends to every other word simultaneously.")
    print()

    # --------------------------------------------------------------------------
    # PART A: Positional Encoding
    # --------------------------------------------------------------------------
    print("=" * 60)
    print("PART A: POSITIONAL ENCODING")
    print("=" * 60)
    print()
    print("  Problem: Attention has no sense of position.")
    print("  'Dog bites man' and 'Man bites dog' look the same.")
    print()
    print("  Solution: Add a unique position vector to each word.")
    print()

    seq_len = 10
    d_model = 16

    pe = positional_encoding(seq_len, d_model)
    print(f"  Positional encoding shape: {pe.shape}")
    print(f"  Position 0: {pe[0, :4]} ...")
    print(f"  Position 5: {pe[5, :4]} ...")
    print(f"  Position 9: {pe[9, :4]} ...")
    print()
    print("  Notice: Each position has a unique pattern.")
    print()

    # --------------------------------------------------------------------------
    # PART B: Self-Attention Walkthrough
    # --------------------------------------------------------------------------
    print("=" * 60)
    print("PART B: SELF-ATTENTION")
    print("=" * 60)
    print()
    print("  Sentence: 'The cat sat'")
    print("  We create synthetic word embeddings:")
    print()

    # Synthetic embeddings for "The cat sat"
    words = ['The', 'cat', 'sat']
    X = np.array([
        [1.0, 0.1, 0.1, 0.1],  # The
        [0.1, 1.0, 0.2, 0.1],  # cat
        [0.1, 0.2, 1.0, 0.1],  # sat
    ])
    d_model = 4

    for i, word in enumerate(words):
        print(f"    {word:5s}: {X[i]}")
    print()

    # Initialize weights (small random)
    d_k = 3
    W_q = np.random.randn(d_model, d_k) * 0.1
    W_k = np.random.randn(d_model, d_k) * 0.1
    W_v = np.random.randn(d_model, d_k) * 0.1
    W_o = np.random.randn(d_k, d_model) * 0.1

    # Compute self-attention
    output, attention_weights = self_attention(X, W_q, W_k, W_v, W_o)

    print("  Attention weights (who attends to whom):")
    print(f"            The    cat    sat")
    for i, word in enumerate(words):
        weights = [f'{attention_weights[i,j]:.2f}' for j in range(len(words))]
        print(f"    {word:5s}: {weights}")
    print()
    print("  Each row shows how much a word attends to other words.")
    print(f"  'cat' attends to itself most: {attention_weights[1,1]:.2f}")
    print()

    # --------------------------------------------------------------------------
    # PART C: Multi-Head Attention
    # --------------------------------------------------------------------------
    print("=" * 60)
    print("PART C: MULTI-HEAD ATTENTION")
    print("=" * 60)
    print()
    print("  We run attention 2 times (2 heads) with different weights.")
    print("  Each head learns a different relationship type.")
    print()

    num_heads = 2
    d_k = 2

    W_q_list = [np.random.randn(d_model, d_k) * 0.1 for _ in range(num_heads)]
    W_k_list = [np.random.randn(d_model, d_k) * 0.1 for _ in range(num_heads)]
    W_v_list = [np.random.randn(d_model, d_k) * 0.1 for _ in range(num_heads)]
    W_o_mha = np.random.randn(num_heads * d_k, d_model) * 0.1

    output_mha, head_attentions = multi_head_attention(X, W_q_list, W_k_list, W_v_list, W_o_mha, num_heads)

    print(f"  Head 1 attention:")
    for i, word in enumerate(words):
        weights = [f'{head_attentions[0][i,j]:.2f}' for j in range(len(words))]
        print(f"    {word:5s}: {weights}")

    print(f"\n  Head 2 attention:")
    for i, word in enumerate(words):
        weights = [f'{head_attentions[1][i,j]:.2f}' for j in range(len(words))]
        print(f"    {word:5s}: {weights}")
    print()
    print("  Each head captures different patterns!")
    print()

    # --------------------------------------------------------------------------
    # PART D: Visualize Positional Encoding
    # --------------------------------------------------------------------------
    print("=" * 60)
    print("VISUALIZING POSITIONAL ENCODING")
    print("=" * 60)

    pe_viz = positional_encoding(50, 64)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Plot 1: Positional encoding matrix
    im = axes[0].imshow(pe_viz, cmap='viridis', aspect='auto')
    axes[0].set_xlabel('Dimension')
    axes[0].set_ylabel('Position')
    axes[0].set_title('Positional Encoding Matrix')
    plt.colorbar(im, ax=axes[0])

    # Plot 2: Transformer architecture diagram
    axes[1].text(0.5, 0.9, 'Input + Positional Encoding', ha='center', fontsize=12,
                 bbox=dict(boxstyle='round', facecolor='lightblue'))
    axes[1].arrow(0.5, 0.85, 0, -0.05, head_width=0.05, head_length=0.02, fc='black')
    axes[1].text(0.5, 0.75, 'Multi-Head Self-Attention', ha='center', fontsize=12,
                 bbox=dict(boxstyle='round', facecolor='lightyellow'))
    axes[1].arrow(0.5, 0.7, 0, -0.05, head_width=0.05, head_length=0.02, fc='black')
    axes[1].text(0.5, 0.6, 'Add & Norm', ha='center', fontsize=11,
                 bbox=dict(boxstyle='round', facecolor='lightgreen'))
    axes[1].arrow(0.5, 0.55, 0, -0.05, head_width=0.05, head_length=0.02, fc='black')
    axes[1].text(0.5, 0.45, 'Feed-Forward Network', ha='center', fontsize=12,
                 bbox=dict(boxstyle='round', facecolor='lightcoral'))
    axes[1].arrow(0.5, 0.4, 0, -0.05, head_width=0.05, head_length=0.02, fc='black')
    axes[1].text(0.5, 0.3, 'Add & Norm', ha='center', fontsize=11,
                 bbox=dict(boxstyle='round', facecolor='lightgreen'))
    axes[1].arrow(0.5, 0.25, 0, -0.05, head_width=0.05, head_length=0.02, fc='black')
    axes[1].text(0.5, 0.15, 'Output', ha='center', fontsize=12,
                 bbox=dict(boxstyle='round', facecolor='lightgray'))

    axes[1].set_xlim(0, 1)
    axes[1].set_ylim(0, 1)
    axes[1].axis('off')
    axes[1].set_title('Transformer Block', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase18/transformer_architecture.png', dpi=150)
    print("Plot saved to: src/phase18/transformer_architecture.png")
    plt.close()

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - Positional encoding (sine/cosine based)")
    print("    - Self-attention (Q, K, V from same input)")
    print("    - Multi-head attention (parallel attention heads)")
    print("    - Transformer block (attention + feed-forward)")
    print()
    print("  KEY INSIGHT:")
    print("    The Transformer removes RNNs entirely.")
    print("    All words attend to all words simultaneously.")
    print("    This is massively parallelizable on GPUs.")
    print()
    print("  WHY THIS CHANGED EVERYTHING:")
    print("    - No sequential bottleneck (unlike RNNs)")
    print("    - Can handle long-range dependencies easily")
    print("    - Scales to billions of parameters")
    print("    - GPT, BERT, T5, Claude — all use Transformers")
    print()
    print("  NEXT QUESTION:")
    print("    'The Transformer encoder reads the whole sentence")
    print("     in both directions. Can I use ONLY this for")
    print("     understanding tasks?'")
    print("=" * 60)
