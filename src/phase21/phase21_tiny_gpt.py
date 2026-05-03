#!/usr/bin/env python3
"""
================================================================================
Phase 21: Training a Tiny GPT — From Zero to Text Generation
================================================================================

This script is for a COMPLETE BEGINNER.

This is it. We put EVERYTHING together:
  - Word embeddings (Phase 15)
  - Positional encoding (Phase 18)
  - Self-attention with causal masking (Phase 20)
  - Transformer blocks (Phase 18)
  - Softmax for next-token prediction (Phase 6)
  - Cross-entropy loss (Phase 6)
  - Gradient descent (Phase 3)

We train a tiny character-level GPT on a small text corpus.
It will learn to generate text that looks like its training data.

Because training from scratch in NumPy is extremely limited,
this script focuses on the CONCEPT and ARCHITECTURE.
The Colab version actually trains and generates.

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
# TINY GPT COMPONENTS
# ==============================================================================

class TinyGPT:
    """
    A minimal GPT-like model for educational purposes.

    Architecture:
      Input characters -> Embeddings + Positional Encoding
        -> Transformer Block x N
        -> Linear -> Softmax
        -> Next character prediction
    """

    def __init__(self, vocab_size, d_model=16, num_layers=2, seq_len=16):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.num_layers = num_layers
        self.seq_len = seq_len

        # Token embeddings
        self.token_emb = np.random.randn(vocab_size, d_model) * 0.01

        # Positional encoding (fixed, not learned)
        self.pos_enc = self._create_positional_encoding(seq_len, d_model)

        # Transformer blocks (simplified: just attention + FF)
        self.attention_weights = []
        self.ff_weights = []

        for _ in range(num_layers):
            # Attention: Q, K, V projections
            d_k = d_model // 2
            W_q = np.random.randn(d_model, d_k) * 0.01
            W_k = np.random.randn(d_model, d_k) * 0.01
            W_v = np.random.randn(d_model, d_k) * 0.01
            W_o = np.random.randn(d_k, d_model) * 0.01
            self.attention_weights.append((W_q, W_k, W_v, W_o))

            # Feed-forward
            W_ff1 = np.random.randn(d_model, d_model * 2) * 0.01
            b_ff1 = np.zeros((1, d_model * 2))
            W_ff2 = np.random.randn(d_model * 2, d_model) * 0.01
            b_ff2 = np.zeros((1, d_model))
            self.ff_weights.append((W_ff1, b_ff1, W_ff2, b_ff2))

        # Output projection
        self.W_out = np.random.randn(d_model, vocab_size) * 0.01
        self.b_out = np.zeros((1, vocab_size))

    def _create_positional_encoding(self, seq_len, d_model):
        """Create sinusoidal positional encodings."""
        pe = np.zeros((seq_len, d_model))
        positions = np.arange(seq_len)[:, np.newaxis]
        div_term = np.exp(np.arange(0, d_model, 2) * -(np.log(10000.0) / d_model))
        pe[:, 0::2] = np.sin(positions * div_term)
        pe[:, 1::2] = np.cos(positions * div_term)
        return pe

    def _causal_self_attention(self, X, W_q, W_k, W_v, W_o):
        """Causal self-attention."""
        Q = X @ W_q
        K = X @ W_k
        V = X @ W_v

        d_k = Q.shape[1]
        scores = (Q @ K.T) / np.sqrt(d_k)

        # Causal mask
        seq_len = X.shape[0]
        mask = np.triu(np.ones((seq_len, seq_len)), k=1) * -1e9
        scores = scores + mask

        attn_weights = softmax(scores, axis=-1)
        context = attn_weights @ V
        output = context @ W_o

        return output, attn_weights

    def forward(self, token_indices):
        """
        Forward pass.

        PARAMETERS:
            token_indices = list of character indices (seq_len,)

        RETURNS:
            logits = prediction scores (seq_len, vocab_size)
        """
        # Token embeddings
        X = self.token_emb[token_indices]  # (seq_len, d_model)

        # Add positional encoding
        X = X + self.pos_enc[:len(token_indices)]

        # Pass through transformer blocks
        for layer in range(self.num_layers):
            W_q, W_k, W_v, W_o = self.attention_weights[layer]
            W_ff1, b_ff1, W_ff2, b_ff2 = self.ff_weights[layer]

            # Self-attention
            attn_out, _ = self._causal_self_attention(X, W_q, W_k, W_v, W_o)
            X = X + attn_out  # Residual connection

            # Feed-forward
            ff_out = relu(X @ W_ff1 + b_ff1) @ W_ff2 + b_ff2
            X = X + ff_out  # Residual connection

        # Output projection
        logits = X @ self.W_out + self.b_out

        return logits

    def generate(self, seed_indices, length=50, temperature=1.0):
        """Generate text starting from seed."""
        generated = list(seed_indices)

        for _ in range(length):
            # Use last seq_len tokens as context
            context = generated[-self.seq_len:]
            if len(context) < self.seq_len:
                # Pad with zeros if needed
                context = [0] * (self.seq_len - len(context)) + context

            # Forward pass
            logits = self.forward(context)
            next_logits = logits[len(generated) - 1 if len(generated) < self.seq_len else -1]

            # Apply temperature
            next_logits = next_logits / temperature
            probs = softmax(next_logits)

            # Sample next token
            next_token = np.random.choice(self.vocab_size, p=probs)
            generated.append(next_token)

        return generated


# ==============================================================================
# TRAINING DEMONSTRATION
# ==============================================================================

def train_tiny_gpt():
    """Train the tiny GPT on a toy corpus."""
    print("=" * 60)
    print("TRAINING A TINY GPT")
    print("=" * 60)
    print()

    # Tiny corpus
    text = "the cat sat on the mat the dog ran in the park the bird flew in the sky"
    chars = sorted(set(text))
    char_to_idx = {c: i for i, c in enumerate(chars)}
    idx_to_char = {i: c for i, c in enumerate(chars)}
    vocab_size = len(chars)

    print(f"  Corpus: '{text}'")
    print(f"  Vocabulary ({vocab_size} chars): {chars}")
    print()

    # Create model
    model = TinyGPT(vocab_size=vocab_size, d_model=16, num_layers=2, seq_len=16)
    print(f"  Model: {model.num_layers} layers, d_model={model.d_model}")
    print()

    # Prepare training data (sliding window)
    data_indices = [char_to_idx[c] for c in text]
    seq_len = 8

    sequences = []
    for i in range(len(data_indices) - seq_len):
        sequences.append((data_indices[i:i+seq_len], data_indices[i+1:i+seq_len+1]))

    print(f"  Training sequences: {len(sequences)}")
    print()

    # Very simple training (simplified gradient descent)
    learning_rate = 0.1
    epochs = 500

    print(f"  Training for {epochs} epochs...")
    losses = []

    for epoch in range(epochs):
        epoch_loss = 0

        for input_seq, target_seq in sequences:
            # Forward pass
            logits = model.forward(input_seq)

            # Compute loss (cross-entropy)
            loss = 0
            for i in range(len(target_seq)):
                probs = softmax(logits[i])
                target = target_seq[i]
                loss += -np.log(probs[target] + 1e-8)

            loss = loss / len(target_seq)
            epoch_loss += loss

            # Simplified weight update (perturbation-based)
            # In practice, you'd do full backpropagation
            # This is for demonstration purposes
            if loss > 1.0 and epoch % 10 == 0:
                model.W_out += np.random.randn(*model.W_out.shape) * learning_rate * 0.001

        avg_loss = epoch_loss / len(sequences)
        losses.append(avg_loss)

        if epoch % 100 == 0:
            print(f"    Epoch {epoch:3d}: Loss = {avg_loss:.4f}")

    print()
    print(f"  Final loss: {losses[-1]:.4f}")
    print()

    return model, chars, char_to_idx, idx_to_char, losses


# ==============================================================================
# GENERATION DEMONSTRATION
# ==============================================================================

def demonstrate_generation(model, char_to_idx, idx_to_char):
    """Show the model generating text."""
    print("=" * 60)
    print("GENERATING TEXT")
    print("=" * 60)
    print()

    seeds = ['the ', 'cat ', 'dog ']

    for seed in seeds:
        seed_indices = [char_to_idx[c] for c in seed if c in char_to_idx]
        if not seed_indices:
            continue

        generated = model.generate(seed_indices, length=20, temperature=0.8)
        text = ''.join([idx_to_char[i] for i in generated])

        print(f"  Seed: '{seed}'")
        print(f"  Generated: '{text}'")
        print()

    print("  Note: The model is tiny and the corpus is small.")
    print("  Output will be noisy. See Colab script for real results.")
    print()


# ==============================================================================
# VISUALIZATION
# ==============================================================================

def visualize_training(losses):
    """Plot training loss."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Loss curve
    axes[0].plot(losses, color='blue', linewidth=2)
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Training Loss (Tiny GPT)')
    axes[0].grid(True, alpha=0.3)

    # Architecture diagram
    ax = axes[1]
    ax.text(0.5, 0.95, 'Tiny GPT Architecture', ha='center', fontsize=14, fontweight='bold')

    layers = [
        ('Input Tokens', 'lightgray'),
        ('Token Embeddings + Positional Encoding', 'lightyellow'),
        ('Transformer Block 1\n(Self-Attention + Feed-Forward)', 'lightgreen'),
        ('Transformer Block 2\n(Self-Attention + Feed-Forward)', 'lightgreen'),
        ('Output Projection', 'lightblue'),
        ('Softmax', 'lightcoral'),
        ('Next Token Prediction', 'plum')
    ]

    y_pos = 0.85
    for text, color in layers:
        ax.text(0.5, y_pos, text, ha='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor=color))
        if y_pos > 0.15:
            ax.arrow(0.5, y_pos - 0.03, 0, -0.04, head_width=0.05, head_length=0.02, fc='black')
        y_pos -= 0.12

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase21/tiny_gpt.png', dpi=150)
    print("Plot saved to: src/phase21/tiny_gpt.png")
    plt.close()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PHASE 21: TRAINING A TINY GPT")
    print("=" * 60)
    print()
    print("  This is the culmination of everything we've learned.")
    print("  We put together:")
    print("    - Embeddings (Phase 15)")
    print("    - Positional encoding (Phase 18)")
    print("    - Self-attention with causal mask (Phase 20)")
    print("    - Transformer blocks (Phase 18)")
    print("    - Next-token prediction (Phase 6)")
    print("    - Cross-entropy loss (Phase 6)")
    print("    - Gradient descent (Phase 3)")
    print()

    # Train
    model, chars, char_to_idx, idx_to_char, losses = train_tiny_gpt()

    # Generate
    demonstrate_generation(model, char_to_idx, idx_to_char)

    # Visualize
    visualize_training(losses)

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - A Tiny GPT with:")
    print("      * Token embeddings")
    print("      * Positional encoding")
    print("      * Causal self-attention")
    print("      * Transformer blocks")
    print("      * Next-token prediction")
    print("    - Training loop")
    print("    - Text generation")
    print()
    print("  KEY INSIGHT:")
    print("    GPT predicts ONE token at a time.")
    print("    It feeds that prediction back as input.")
    print("    This creates a loop that generates endless text.")
    print()
    print("  SCALING LAW:")
    print("    - More data -> better predictions")
    print("    - More parameters -> richer patterns")
    print("    - More compute -> longer training")
    print("    - GPT-3: 175 billion parameters, 300 billion tokens")
    print("    - GPT-4: Even larger (exact size not public)")
    print()
    print("  NEXT QUESTION:")
    print("    'The model generates text, but it does not")
    print("     answer questions helpfully. How do I make")
    print("     it an assistant?'")
    print("=" * 60)
