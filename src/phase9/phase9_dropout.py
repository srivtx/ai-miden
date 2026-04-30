#!/usr/bin/env python3
"""
================================================================================
Phase 9: Dropout — Breaking Up Neuron Cliques
================================================================================

This script is for a COMPLETE BEGINNER.

In Phase 8, we learned about L2 regularization. It shrinks weights to prevent
overfitting. But L2 has a weakness: it keeps ALL neurons active. Some neurons
become lazy and just copy what their neighbors do. They form "cliques."

Dropout fixes this by randomly turning off neurons during training.
It forces every neuron to learn independently.

Every line has a comment. Read it like a story.
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import numpy as np

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend: saves to file, no popup window
import matplotlib.pyplot as plt


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def he_init(input_size, output_size):
    """He initialization for stable deep network training."""
    return np.random.randn(input_size, output_size) * np.sqrt(2.0 / input_size)


def relu(x):
    """ReLU: keep positive values, zero out negative ones."""
    return np.maximum(0, x)


def relu_derivative(x):
    """Derivative of ReLU: 1 where positive, 0 where negative."""
    return (x > 0).astype(float)


# ==============================================================================
# THE NETWORK CLASS (with optional Dropout)
# ==============================================================================

class NetworkWithDropout:
    """
    A deep neural network that can use dropout during training.

    WHAT IS DROPOUT?
    During each training step, we randomly "turn off" some neurons.
    The turned-off neurons output zero. They do not participate.

    WHY DO THIS?
    Without dropout, neurons form cliques. Neuron B copies Neuron A.
    Neuron C copies both. If Neuron A disappears, the whole clique breaks.

    With dropout, Neuron A might be turned off on some training steps.
    Neuron B cannot copy A anymore. B is FORCED to learn on its own.
    After many steps, every neuron learns independently.

    THIS IS THE KEY IDEA:
    Dropout = training with one hand tied behind your back.
    The network becomes robust because it cannot rely on any single neuron.
    """

    def __init__(self, layer_sizes, dropout_rate=0.0):
        """
        Create the network.

        PARAMETERS:
            layer_sizes = list of layer dimensions, e.g., [1, 64, 64, 1]
            dropout_rate = fraction of neurons to drop (0.0 = no dropout)
                           0.5 means 50% of neurons are randomly disabled
        """
        self.layer_sizes = layer_sizes
        self.num_layers = len(layer_sizes) - 1
        self.dropout_rate = dropout_rate

        self.weights = []
        self.biases = []

        for i in range(self.num_layers):
            W = he_init(layer_sizes[i], layer_sizes[i + 1])
            b = np.zeros((1, layer_sizes[i + 1]))
            self.weights.append(W)
            self.biases.append(b)

    def forward(self, X, training=True):
        """
        Forward pass with optional dropout.

        PARAMETERS:
            X = input data
            training = True during training (dropout active)
                       False during testing (all neurons active)

        RETURNS:
            predictions = final output
            layer_data = list of (activation, mask, pre_activation) for each hidden layer
        """
        current = X
        layer_data = []  # Store activations, masks, and pre-activations for backprop

        # Process all hidden layers
        for i in range(self.num_layers - 1):
            # Compute raw scores
            z = current @ self.weights[i] + self.biases[i]

            # Apply ReLU
            a = relu(z)

            mask = None

            # Apply dropout ONLY during training, and ONLY if dropout_rate > 0
            if training and self.dropout_rate > 0.0:
                # Create a random mask.
                # For each neuron, generate a random number between 0 and 1.
                # If the number is GREATER than dropout_rate, keep the neuron.
                # If the number is LESS than dropout_rate, drop the neuron.
                # Example: dropout_rate = 0.5
                #   Random number 0.7 > 0.5 → KEEP (multiply by 1)
                #   Random number 0.3 < 0.5 → DROP (multiply by 0)
                mask = (np.random.rand(*a.shape) > self.dropout_rate).astype(float)

                # Apply the mask: surviving neurons stay, dropped neurons become 0
                a = a * mask

                # Scale surviving neurons by 1 / (1 - dropout_rate)
                # WHY SCALE?
                # During training, only (1 - dropout_rate) fraction of neurons are active.
                # During testing, ALL neurons are active.
                # If we do not scale, the total signal during testing would be
                # much stronger than during training.
                # By scaling during training, we keep the signal consistent.
                # Example: dropout_rate = 0.5, keep_rate = 0.5
                #   Scale factor = 1 / 0.5 = 2.0
                #   Each surviving neuron is doubled.
                #   During testing, all neurons are active at normal strength.
                #   The total signal matches what the network saw during training.
                a = a / (1.0 - self.dropout_rate)

            layer_data.append((a, mask, z))
            current = a

        # Final layer (no dropout, no activation — this is regression)
        z_final = current @ self.weights[-1] + self.biases[-1]
        predictions = z_final

        return predictions, layer_data

    def compute_loss(self, predictions, y_true):
        """Mean Squared Error loss."""
        return np.mean((predictions - y_true) ** 2)

    def backward(self, X, y_true, predictions, layer_data):
        """
        Backpropagation with dropout masks.

        THE KEY DIFFERENCE FROM NORMAL BACKPROP:
        We only propagate error through neurons that were ACTIVE during forward pass.
        Dead neurons do not get blamed for mistakes they did not make.
        """
        n = X.shape[0]
        grad = (predictions - y_true) / n

        dW_list = []
        db_list = []

        # Work backward from the last layer to the first
        for i in range(self.num_layers - 1, -1, -1):
            if i == self.num_layers - 1:
                # Last layer: previous activation is from the last hidden layer
                a_prev = layer_data[i - 1][0] if i > 0 else X
            else:
                a_prev = layer_data[i - 1][0] if i > 0 else X

            dW = a_prev.T @ grad
            db = np.sum(grad, axis=0, keepdims=True)
            dW_list.insert(0, dW)
            db_list.insert(0, db)

            if i > 0:
                grad = grad @ self.weights[i].T
                grad = grad * relu_derivative(layer_data[i - 1][2])

                # APPLY DROPOUT MASK DURING BACKPROP
                # If a neuron was dropped during forward pass, it should not
                # receive any gradient. We multiply by the same mask.
                mask = layer_data[i - 1][1]
                if mask is not None:
                    grad = grad * mask
                    # Also divide by keep probability to match forward pass scaling
                    grad = grad / (1.0 - self.dropout_rate)

        return dW_list, db_list

    def train(self, X_train, y_train, X_val, y_val, learning_rate, iterations):
        """Train the network, tracking both training and validation loss."""
        train_losses = []
        val_losses = []

        print(f"Architecture: {' -> '.join(map(str, self.layer_sizes))}")
        print(f"Dropout rate: {self.dropout_rate}")
        print(f"Training for {iterations} iterations...\n")

        for i in range(iterations):
            # Forward pass WITH dropout (training=True)
            predictions, layer_data = self.forward(X_train, training=True)
            loss = self.compute_loss(predictions, y_train)

            # Backward pass
            dW_list, db_list = self.backward(X_train, y_train, predictions, layer_data)

            # Update weights
            for j in range(self.num_layers):
                self.weights[j] = self.weights[j] - learning_rate * dW_list[j]
                self.biases[j] = self.biases[j] - learning_rate * db_list[j]

            # Evaluate on validation set WITHOUT dropout (training=False)
            if i % 500 == 0:
                val_pred, _ = self.forward(X_val, training=False)
                val_loss = self.compute_loss(val_pred, y_val)
                train_losses.append(loss)
                val_losses.append(val_loss)
                print(f"  Step {i:5d} | Train: {loss:.6f} | Val: {val_loss:.6f}")

        return train_losses, val_losses

    def predict(self, X):
        """Make predictions. Dropout is OFF."""
        predictions, _ = self.forward(X, training=False)
        return predictions


# ==============================================================================
# MAIN DEMONSTRATION
# ==============================================================================

if __name__ == "__main__":

    # --------------------------------------------------------------------------
    # PART A: Generate noisy sine wave data (designed to overfit)
    # --------------------------------------------------------------------------
    np.random.seed(42)

    # Few training points with lots of noise
    n_samples = 40
    X_train = np.sort(np.random.rand(n_samples, 1) * 6 - 3, axis=0)
    y_train = np.sin(X_train) + np.random.randn(n_samples, 1) * 0.3

    # Clean validation data
    X_val = np.linspace(-3, 3, 100).reshape(-1, 1)
    y_val = np.sin(X_val)

    print("=" * 60)
    print("GENERATED DATA")
    print("=" * 60)
    print(f"Training samples: {n_samples} (with noise)")
    print(f"Validation samples: {len(X_val)} (clean sine wave)")
    print("Few points + noise = easy to overfit.\n")

    # --------------------------------------------------------------------------
    # PART B: Train WITHOUT dropout
    # --------------------------------------------------------------------------
    print("=" * 60)
    print("NETWORK WITHOUT DROPOUT")
    print("=" * 60)
    print("All 64 neurons are always active.")
    print("Neurons can form cliques and copy each other.\n")

    model_no_drop = NetworkWithDropout([1, 64, 64, 1], dropout_rate=0.0)
    train_no, val_no = model_no_drop.train(X_train, y_train, X_val, y_val,
                                            learning_rate=0.005, iterations=8000)

    no_drop_pred = model_no_drop.predict(X_val)
    no_drop_val_loss = model_no_drop.compute_loss(no_drop_pred, y_val)
    print(f"\nFinal validation loss (no dropout): {no_drop_val_loss:.6f}")

    # --------------------------------------------------------------------------
    # PART C: Train WITH dropout
    # --------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("NETWORK WITH DROPOUT (50%)")
    print("=" * 60)
    print("On each training step, 50% of neurons are randomly turned off.")
    print("Neurons cannot rely on each other. They must learn independently.\n")

    model_drop = NetworkWithDropout([1, 64, 64, 1], dropout_rate=0.5)
    train_drop, val_drop = model_drop.train(X_train, y_train, X_val, y_val,
                                             learning_rate=0.005, iterations=8000)

    drop_pred = model_drop.predict(X_val)
    drop_val_loss = model_drop.compute_loss(drop_pred, y_val)
    print(f"\nFinal validation loss (with dropout): {drop_val_loss:.6f}")

    # --------------------------------------------------------------------------
    # PART D: Visual comparison
    # --------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("VISUAL COMPARISON")
    print("=" * 60)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Top left: Predictions without dropout
    ax1 = axes[0, 0]
    ax1.plot(X_val, y_val, 'b-', linewidth=2, label='True sine wave')
    ax1.plot(X_val, no_drop_pred, 'r-', linewidth=2, label='No dropout predictions')
    ax1.scatter(X_train, y_train, c='black', s=20, alpha=0.5, label='Noisy training data')
    ax1.set_title(f"Without Dropout\nValidation Loss: {no_drop_val_loss:.4f}")
    ax1.set_xlabel("x")
    ax1.set_ylabel("y")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Top right: Predictions with dropout
    ax2 = axes[0, 1]
    ax2.plot(X_val, y_val, 'b-', linewidth=2, label='True sine wave')
    ax2.plot(X_val, drop_pred, 'g-', linewidth=2, label='With dropout predictions')
    ax2.scatter(X_train, y_train, c='black', s=20, alpha=0.5, label='Noisy training data')
    ax2.set_title(f"With Dropout (50%)\nValidation Loss: {drop_val_loss:.4f}")
    ax2.set_xlabel("x")
    ax2.set_ylabel("y")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Bottom left: Loss curves without dropout
    ax3 = axes[1, 0]
    steps = np.arange(0, len(train_no) * 500, 500)
    ax3.plot(steps, train_no, 'b-', label='Training loss')
    ax3.plot(steps, val_no, 'r-', label='Validation loss')
    ax3.set_title("Loss Curves (No Dropout)")
    ax3.set_xlabel("Iteration")
    ax3.set_ylabel("MSE Loss")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Bottom right: Loss curves with dropout
    ax4 = axes[1, 1]
    steps = np.arange(0, len(train_drop) * 500, 500)
    ax4.plot(steps, train_drop, 'b-', label='Training loss')
    ax4.plot(steps, val_drop, 'g-', label='Validation loss')
    ax4.set_title("Loss Curves (With Dropout)")
    ax4.set_xlabel("Iteration")
    ax4.set_ylabel("MSE Loss")
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    fig.suptitle("Dropout: Breaking Up Neuron Cliques", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase9/dropout_comparison.png', dpi=150)
    print("Plot saved to: src/phase9/dropout_comparison.png")
    plt.close()

    # --------------------------------------------------------------------------
    # PART E: Summary
    # --------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print(f"  WITHOUT DROPOUT:")
    print(f"    Validation loss: {no_drop_val_loss:.6f}")
    print(f"    The network memorized training noise.")
    print(f"    Neurons formed cliques and copied each other.")
    print()
    print(f"  WITH DROPOUT (50%):")
    print(f"    Validation loss: {drop_val_loss:.6f}")
    print(f"    The network learned the true sine wave pattern.")
    print(f"    Every neuron learned to be useful independently.")
    print()
    print("  KEY INSIGHTS:")
    print("    - Dropout randomly turns off neurons during training.")
    print("    - Surviving neurons are scaled up to keep signal stable.")
    print("    - During testing, ALL neurons are active (no dropout).")
    print("    - Dropout forces robust, independent feature learning.")
    print("    - It is like training with one hand tied behind your back.")
    print("=" * 60)
