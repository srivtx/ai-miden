#!/usr/bin/env python3
"""
================================================================================
Phase 13: Recurrent Neural Networks — Remembering Sequences
================================================================================

This script is for a COMPLETE BEGINNER.

So far, our networks treated every input as independent.
But what about sentences? Time series? Music?

In a sequence, ORDER matters.
"The cat sat" is very different from "sat cat the."

We need a network that:
  1. Processes one element at a time
  2. Remembers what it saw before
  3. Uses the SAME weights at every step

That network is the Recurrent Neural Network (RNN).

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
# THE RNN CLASS
# ==============================================================================

class SimpleRNN:
    """
    A vanilla Recurrent Neural Network for character-level prediction.

    Architecture (unrolled across time):

        x_0 → [RNN Cell] → h_1 → [RNN Cell] → h_2 → ... → h_T
                |              |              |
               y_0            y_1            y_2

    At each time step t:
        h_t = tanh(W_xh @ x_t + W_hh @ h_{t-1} + b_h)
        y_t = softmax(W_hy @ h_t + b_y)

    The SAME weights (W_xh, W_hh, W_hy) are used at EVERY time step.
    """

    def __init__(self, vocab_size, hidden_size):
        """
        Create the RNN.

        PARAMETERS:
            vocab_size = number of unique characters (5 for H,E,L,L,O)
            hidden_size = size of hidden state memory (16)
        """
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size

        # Weights: input to hidden
        self.W_xh = np.random.randn(vocab_size, hidden_size) * 0.01

        # Weights: hidden to hidden (the "memory loop")
        self.W_hh = np.random.randn(hidden_size, hidden_size) * 0.01

        # Weights: hidden to output
        self.W_hy = np.random.randn(hidden_size, vocab_size) * 0.01

        # Biases
        self.b_h = np.zeros((1, hidden_size))
        self.b_y = np.zeros((1, vocab_size))

    def forward(self, inputs, h_prev=None):
        """
        Forward pass through the RNN.

        PARAMETERS:
            inputs = list of one-hot vectors, one per time step
            h_prev = initial hidden state (defaults to zeros)

        RETURNS:
            outputs = list of probability distributions at each step
            states = list of hidden states at each step
            caches = stored values for backprop
        """
        if h_prev is None:
            h_prev = np.zeros((1, self.hidden_size))

        outputs = []
        states = [h_prev]
        caches = []

        for t, x_t in enumerate(inputs):
            # x_t shape: (1, vocab_size)

            # Compute new hidden state
            # h_t = tanh(W_xh @ x_t + W_hh @ h_{t-1} + b_h)
            z_h = x_t @ self.W_xh + h_prev @ self.W_hh + self.b_h
            h_t = np.tanh(z_h)

            # Compute output (raw scores)
            z_y = h_t @ self.W_hy + self.b_y

            # Softmax to get probabilities
            exp_z = np.exp(z_y - np.max(z_y))
            y_t = exp_z / np.sum(exp_z)

            # Store everything
            outputs.append(y_t)
            states.append(h_t)
            caches.append({'x': x_t, 'h_prev': h_prev, 'h': h_t, 'z_h': z_h, 'z_y': z_y})

            h_prev = h_t

        return outputs, states, caches

    def compute_loss(self, outputs, targets):
        """
        Categorical cross-entropy loss.

        PARAMETERS:
            outputs = list of probability distributions
            targets = list of one-hot target vectors
        """
        loss = 0
        for y_t, target_t in zip(outputs, targets):
            # Cross entropy: -sum(target * log(prediction))
            epsilon = 1e-8
            loss += -np.sum(target_t * np.log(y_t + epsilon))
        return loss / len(outputs)

    def backward(self, outputs, targets, caches):
        """
        Backpropagation Through Time (BPTT).

        We backpropagate from the final output back to the first input,
        accumulating gradients for the shared weights.
        """
        T = len(outputs)

        # Initialize gradients
        dW_xh = np.zeros_like(self.W_xh)
        dW_hh = np.zeros_like(self.W_hh)
        dW_hy = np.zeros_like(self.W_hy)
        db_h = np.zeros_like(self.b_h)
        db_y = np.zeros_like(self.b_y)

        # Gradient flowing backward through time
        dh_next = np.zeros((1, self.hidden_size))

        # Backpropagate through each time step (in reverse)
        for t in reversed(range(T)):
            cache = caches[t]

            # Output layer gradient
            dy = outputs[t] - targets[t]
            dW_hy += cache['h'].T @ dy
            db_y += dy
            dh = dy @ self.W_hy.T + dh_next

            # tanh derivative: 1 - tanh^2(x)
            dz_h = dh * (1 - cache['h']**2)
            db_h += dz_h
            dW_xh += cache['x'].T @ dz_h
            dW_hh += cache['h_prev'].T @ dz_h

            # Gradient to pass to previous time step
            dh_next = dz_h @ self.W_hh.T

        # Clip gradients to prevent exploding
        for grad in [dW_xh, dW_hh, dW_hy, db_h, db_y]:
            np.clip(grad, -5, 5, out=grad)

        return dW_xh, dW_hh, dW_hy, db_h, db_y

    def train(self, inputs, targets, learning_rate, iterations):
        """Train the RNN on a sequence."""
        print(f"Training RNN for {iterations} iterations...")
        print(f"Vocab size: {self.vocab_size}, Hidden size: {self.hidden_size}\n")

        losses = []
        for i in range(iterations):
            outputs, states, caches = self.forward(inputs)
            loss = self.compute_loss(outputs, targets)
            losses.append(loss)

            dW_xh, dW_hh, dW_hy, db_h, db_y = self.backward(outputs, targets, caches)

            # Update weights
            self.W_xh -= learning_rate * dW_xh
            self.W_hh -= learning_rate * dW_hh
            self.W_hy -= learning_rate * dW_hy
            self.b_h -= learning_rate * db_h
            self.b_y -= learning_rate * db_y

            if i % 500 == 0:
                # Sample prediction
                preds = [np.argmax(o) for o in outputs]
                print(f"  Iteration {i:5d}: Loss = {loss:.4f}, Predictions = {preds}")

        return losses

    def predict(self, inputs):
        """Make predictions on a sequence."""
        outputs, _, _ = self.forward(inputs)
        return [np.argmax(o) for o in outputs]


# ==============================================================================
# MAIN DEMONSTRATION
# ==============================================================================

if __name__ == "__main__":

    # --------------------------------------------------------------------------
    # PART A: Prepare the "HELLO" dataset
    # --------------------------------------------------------------------------

    # Our vocabulary: H, E, L, O
    # We will teach the RNN to predict the next character.
    # Input:  H -> E -> L -> L -> O
    # Target: E -> L -> L -> O -> H (wrap around for demonstration)

    vocab = ['H', 'E', 'L', 'O']
    char_to_idx = {c: i for i, c in enumerate(vocab)}
    idx_to_char = {i: c for i, c in enumerate(vocab)}

    def char_to_onehot(char):
        """Convert a character to a one-hot vector."""
        vec = np.zeros((1, len(vocab)))
        vec[0, char_to_idx[char]] = 1
        return vec

    # Training sequence: "HELLO"
    sequence = "HELLO"

    # Inputs: H, E, L, L
    # Targets: E, L, L, O
    inputs = [char_to_onehot(c) for c in sequence[:-1]]
    targets = [char_to_onehot(c) for c in sequence[1:]]

    print("=" * 60)
    print("RECURRENT NEURAL NETWORK DEMO")
    print("=" * 60)
    print()
    print("  Task: Learn to predict the next character in 'HELLO'")
    print()
    print("  Input sequence:  H -> E -> L -> L")
    print("  Target sequence: E -> L -> L -> O")
    print()
    print("  The RNN processes one character at a time,")
    print("  updating its hidden state (memory) at each step.")
    print()

    # --------------------------------------------------------------------------
    # PART B: Train the RNN
    # --------------------------------------------------------------------------
    print("=" * 60)
    print("TRAINING THE RNN")
    print("=" * 60)

    rnn = SimpleRNN(vocab_size=len(vocab), hidden_size=16)
    losses = rnn.train(inputs, targets, learning_rate=0.1, iterations=3000)

    # Final predictions
    final_outputs, final_states, _ = rnn.forward(inputs)
    predictions = [np.argmax(o) for o in final_outputs]
    target_indices = [np.argmax(t) for t in targets]

    print()
    print("  Final Results:")
    print(f"    Input:    {' '.join(sequence[:-1])}")
    print(f"    Target:   {' '.join(sequence[1:])}")
    print(f"    Predicted: {' '.join([idx_to_char[i] for i in predictions])}")
    print(f"    Accuracy: {np.mean(np.array(predictions) == np.array(target_indices)) * 100:.0f}%")

    # --------------------------------------------------------------------------
    # PART C: Visualize hidden state evolution
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("VISUALIZING HIDDEN STATE EVOLUTION")
    print("=" * 60)
    print("  The hidden state is the RNN's memory. Let's see how it changes")
    print("  as the RNN reads each character of 'HELLO'.\n")

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Plot 1: Loss curve
    axes[0, 0].plot(losses, color='blue', linewidth=2)
    axes[0, 0].set_xlabel('Iteration')
    axes[0, 0].set_ylabel('Loss')
    axes[0, 0].set_title('Training Loss')
    axes[0, 0].grid(True, alpha=0.3)

    # Plot 2: Hidden state values over time steps
    hidden_evolution = np.array([s[0] for s in final_states[1:]])  # (T, hidden_size)
    axes[0, 1].imshow(hidden_evolution.T, cmap='viridis', aspect='auto')
    axes[0, 1].set_xlabel('Time Step')
    axes[0, 1].set_ylabel('Hidden Unit')
    axes[0, 1].set_title('Hidden State After Each Character')
    axes[0, 1].set_xticks(range(len(sequence) - 1))
    axes[0, 1].set_xticklabels(list(sequence[:-1]))

    # Plot 3: Prediction probabilities at each step
    probs = np.array([o[0] for o in final_outputs])
    x = np.arange(len(sequence) - 1)
    width = 0.2
    for i, char in enumerate(vocab):
        axes[1, 0].bar(x + i * width, probs[:, i], width, label=f'"{char}"')
    axes[1, 0].set_xlabel('Time Step')
    axes[1, 0].set_ylabel('Probability')
    axes[1, 0].set_title('Predicted Probabilities at Each Step')
    axes[1, 0].set_xticks(x + width * 1.5)
    axes[1, 0].set_xticklabels(list(sequence[:-1]))
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # Plot 4: Sequence diagram
    axes[1, 1].text(0.5, 0.8, f"Input:  {' '.join(sequence[:-1])}",
                    ha='center', va='center', fontsize=14, family='monospace')
    axes[1, 1].text(0.5, 0.6, f"Target: {' '.join(sequence[1:])}",
                    ha='center', va='center', fontsize=14, family='monospace',
                    color='green')
    axes[1, 1].text(0.5, 0.4, f"Pred:   {' '.join([idx_to_char[i] for i in predictions])}",
                    ha='center', va='center', fontsize=14, family='monospace',
                    color='blue' if predictions == target_indices else 'red')
    axes[1, 1].set_xlim(0, 1)
    axes[1, 1].set_ylim(0, 1)
    axes[1, 1].axis('off')
    axes[1, 1].set_title('Sequence Prediction')

    fig.suptitle('RNN: Learning to Predict "HELLO"', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase13/rnn_hello.png', dpi=150)
    print("Plot saved to: src/phase13/rnn_hello.png")
    plt.close()

    # --------------------------------------------------------------------------
    # PART D: Generate new text
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("GENERATING NEW TEXT")
    print("=" * 60)
    print("  Starting with 'H', let's see what the RNN generates.\n")

    # Seed with 'H'
    current_char = 'H'
    generated = [current_char]
    h = np.zeros((1, 16))

    for _ in range(10):
        x = char_to_onehot(current_char)
        outputs, states, _ = rnn.forward([x], h_prev=h)
        h = states[-1]
        probs = outputs[0][0]
        next_idx = np.random.choice(len(vocab), p=probs)
        current_char = idx_to_char[next_idx]
        generated.append(current_char)

    print(f"  Generated: {''.join(generated)}")
    print("  (The RNN learned patterns from 'HELLO' and generates similar sequences)")

    # --------------------------------------------------------------------------
    # PART E: Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - A vanilla RNN with hidden state memory")
    print("    - Forward pass: processes sequence one character at a time")
    print("    - Backpropagation Through Time (BPTT)")
    print("    - Trained on 'HELLO' to predict next character")
    print()
    print("  KEY INSIGHTS:")
    print("    - The hidden state carries memory across time steps")
    print("    - The SAME weights are used at every step (parameter sharing)")
    print("    - RNNs can generate text by feeding predictions back as input")
    print()
    print("  LIMITATION:")
    print("    - Vanilla RNNs forget distant past (vanishing gradients)")
    print("    - For long sequences, we need LSTMs")
    print()
    print("  NEXT QUESTION:")
    print("    'My RNN works for short words but forgets long sentences.")
    print("     How do I give it longer memory?'")
    print("=" * 60)
