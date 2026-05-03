#!/usr/bin/env python3
"""
================================================================================
Phase 20: GPT Architecture — Generative Pre-trained Transformer
================================================================================

This script is for a COMPLETE BEGINNER.

In Phase 19, BERT used the Transformer ENCODER for understanding.
GPT uses the Transformer DECODER for GENERATION.

Key differences:
  BERT: Bidirectional (sees past AND future)
  GPT:  Unidirectional (sees ONLY past)

Why? Because when generating text, you cannot peek at the future.
If you're writing "The cat sat on the...", you cannot know
what comes next until you generate it.

Key mechanism: Causal Masking
  - A triangular mask that blocks future positions
  - Position i can only attend to positions 0, 1, ..., i-1
  - This forces left-to-right generation

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


# ==============================================================================
# CAUSAL MASK
# ==============================================================================

def create_causal_mask(seq_len):
    """
    Create a causal (triangular) mask.

    The mask has 0s in the lower triangle (including diagonal)
    and -infinity in the upper triangle.

    When added to attention scores:
    - Lower triangle: scores unchanged (can attend)
    - Upper triangle: scores become -inf (blocked)
    - After softmax: upper triangle = 0
    """
    mask = np.triu(np.ones((seq_len, seq_len)), k=1)  # Upper triangle = 1
    mask = mask * -1e9  # Make upper triangle very negative
    return mask


# ==============================================================================
# CAUSAL SELF-ATTENTION
# ==============================================================================

def causal_self_attention(X, W_q, W_k, W_v):
    """
    Self-attention with causal masking.

    Each position can only attend to previous positions.
    """
    Q = X @ W_q
    K = X @ W_k
    V = X @ W_v

    d_k = Q.shape[1]
    scores = (Q @ K.T) / np.sqrt(d_k)

    # Apply causal mask
    seq_len = X.shape[0]
    causal_mask = create_causal_mask(seq_len)
    scores = scores + causal_mask

    attention_weights = softmax(scores, axis=-1)
    context = attention_weights @ V

    return context, attention_weights


# ==============================================================================
# DEMONSTRATION
# ==============================================================================

def demonstrate_causal_attention():
    """Show how causal masking works."""
    print("=" * 60)
    print("CAUSAL SELF-ATTENTION DEMONSTRATION")
    print("=" * 60)
    print()

    # Sentence: "The cat sat"
    words = ['The', 'cat', 'sat']
    X = np.random.randn(3, 4)  # 3 words, 4 dimensions

    # Initialize weights
    d_k = 3
    W_q = np.random.randn(4, d_k) * 0.1
    W_k = np.random.randn(4, d_k) * 0.1
    W_v = np.random.randn(4, d_k) * 0.1

    # Compute causal attention
    context, attention_weights = causal_self_attention(X, W_q, W_k, W_v)

    print("  Sentence: 'The cat sat'")
    print()
    print("  Attention weights (with causal mask):")
    print(f"            The    cat    sat")
    for i, word in enumerate(words):
        weights = [f'{attention_weights[i,j]:.2f}' for j in range(len(words))]
        print(f"    {word:5s}: {weights}")
    print()

    print("  Notice the triangular pattern:")
    print("    'The'  can only attend to 'The'")
    print("    'cat'  can attend to 'The' and 'cat'")
    print("    'sat'  can attend to 'The', 'cat', and 'sat'")
    print()
    print("  The upper triangle is ZERO — future positions are blocked!")
    print()

    return attention_weights


def demonstrate_generation():
    """Demonstrate how GPT generates text step by step."""
    print("=" * 60)
    print("TEXT GENERATION WITH GPT")
    print("=" * 60)
    print()

    vocab = ['The', 'cat', 'sat', 'on', 'mat', '<END>']
    vocab_size = len(vocab)

    # Simple "language model" probabilities
    # After "The" → likely "cat"
    # After "The cat" → likely "sat"
    # After "The cat sat" → likely "on"
    # etc.

    print("  Generation process:")
    print()

    generated = ["The"]
    print(f"  Step 1: Start with 'The'")

    for step in range(5):
        current = generated[-1]

        # Predict next word based on simple rules
        if current == "The":
            next_word = "cat"
        elif current == "cat":
            next_word = "sat"
        elif current == "sat":
            next_word = "on"
        elif current == "on":
            next_word = "mat"
        elif current == "mat":
            next_word = "<END>"
        else:
            next_word = "<END>"

        if next_word == "<END>":
            print(f"  Step {step+2}: Predict '<END>' → Stop")
            break

        generated.append(next_word)
        print(f"  Step {step+2}: '{ ' '.join(generated)}' → predict '{next_word}'")

    print()
    print(f"  Final output: '{' '.join(generated)}'")
    print()
    print("  At each step, the model can ONLY see previously generated words.")
    print("  This is enforced by the causal mask.")
    print()


# ==============================================================================
# BERT vs GPT COMPARISON
# ==============================================================================

def compare_bert_gpt():
    """Compare BERT and GPT architectures."""
    print("=" * 60)
    print("BERT vs GPT: THE GREAT SPLIT")
    print("=" * 60)
    print()

    print("  BERT (Bidirectional Encoder):")
    print("    ┌─────────────────────────────────────┐")
    print("    │  Input: 'The cat sat'               │")
    print("    │  ↓                                  │")
    print("    │  Encoder Block (bidirectional)      │")
    print("    │  The ←→ cat ←→ sat                  │")
    print("    │  ↓                                  │")
    print("    │  Output: Understanding              │")
    print("    └─────────────────────────────────────┘")
    print()

    print("  GPT (Autoregressive Decoder):")
    print("    ┌─────────────────────────────────────┐")
    print("    │  Input: 'The'                       │")
    print("    │  ↓                                  │")
    print("    │  Decoder Block (causal)             │")
    print("    │  The → cat → sat                    │")
    print("    │  ↓                                  │")
    print("    │  Output: 'cat' (next token)         │")
    print("    └─────────────────────────────────────┘")
    print()

    comparison = [
        ("Architecture", "Encoder only", "Decoder only"),
        ("Direction", "Bidirectional", "Unidirectional (left-to-right)"),
        ("Mask", "None", "Causal (triangular)"),
        ("Training", "Masked word prediction", "Next token prediction"),
        ("Use case", "Understanding", "Generation"),
        ("Examples", "Sentiment analysis, QA", "Story writing, code completion"),
    ]

    print("  Comparison:")
    print(f"    {'Feature':20s} {'BERT':25s} {'GPT':30s}")
    print(f"    {'-'*20} {'-'*25} {'-'*30}")
    for feature, bert, gpt in comparison:
        print(f"    {feature:20s} {bert:25s} {gpt:30s}")
    print()


# ==============================================================================
# VISUALIZATION
# ==============================================================================

def visualize_causal_mask():
    """Visualize the causal mask."""
    print("=" * 60)
    print("VISUALIZING CAUSAL MASK")
    print("=" * 60)

    seq_len = 8
    mask = create_causal_mask(seq_len)
    # Convert to binary for visualization
    mask_viz = (mask == 0).astype(int)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Mask visualization
    im = axes[0].imshow(mask_viz, cmap='RdYlGn', vmin=0, vmax=1)
    axes[0].set_title('Causal Mask (Green = Can Attend, Red = Blocked)')
    axes[0].set_xlabel('Key Position')
    axes[0].set_ylabel('Query Position')

    # Add grid lines
    for i in range(seq_len + 1):
        axes[0].axhline(i - 0.5, color='black', linewidth=0.5)
        axes[0].axvline(i - 0.5, color='black', linewidth=0.5)

    plt.colorbar(im, ax=axes[0])

    # Architecture comparison
    axes[1].text(0.5, 0.85, 'BERT', ha='center', fontsize=14, fontweight='bold',
                 bbox=dict(boxstyle='round', facecolor='lightblue'))
    axes[1].text(0.5, 0.75, 'Bidirectional\nEncoder Only', ha='center', fontsize=11)
    axes[1].text(0.5, 0.60, '↓', ha='center', fontsize=20)
    axes[1].text(0.5, 0.45, 'GPT', ha='center', fontsize=14, fontweight='bold',
                 bbox=dict(boxstyle='round', facecolor='lightgreen'))
    axes[1].text(0.5, 0.35, 'Unidirectional\nDecoder Only', ha='center', fontsize=11)

    axes[1].set_xlim(0, 1)
    axes[1].set_ylim(0, 1)
    axes[1].axis('off')
    axes[1].set_title('The Great Split', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase20/gpt_architecture.png', dpi=150)
    print("Plot saved to: src/phase20/gpt_architecture.png")
    plt.close()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("GPT: GENERATIVE PRE-TRAINED TRANSFORMER")
    print("=" * 60)
    print()
    print("  GPT = Transformer Decoder ONLY")
    print("  Reads left-to-right with causal masking")
    print("  Generates text one token at a time")
    print()

    # Demonstrate causal attention
    demonstrate_causal_attention()

    # Demonstrate generation
    demonstrate_generation()

    # Compare BERT vs GPT
    compare_bert_gpt()

    # Visualize
    visualize_causal_mask()

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - Causal mask (triangular blocking)")
    print("    - Causal self-attention")
    print("    - Text generation demonstration")
    print("    - BERT vs GPT comparison")
    print()
    print("  KEY INSIGHT:")
    print("    GPT uses ONLY the Transformer decoder.")
    print("    Causal masking forces left-to-right generation.")
    print("    The model predicts the NEXT token at each step.")
    print()
    print("  WHY THIS IS POWERFUL:")
    print("    - Can generate ANY text: stories, code, answers")
    print("    - Scales to billions of parameters (GPT-3, GPT-4)")
    print("    - One architecture handles many tasks")
    print()
    print("  NEXT QUESTION:")
    print("    'Can I put everything together and train")
    print("     a model that actually writes text?'")
    print("=" * 60)
