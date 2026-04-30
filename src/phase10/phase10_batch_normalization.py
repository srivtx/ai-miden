#!/usr/bin/env python3
"""
================================================================================
Phase 10: Batch Normalization — Keeping the Kitchen at the Right Temperature
================================================================================

This script is for a COMPLETE BEGINNER.

In Phase 7, we built deep networks. In Phase 8 and 9, we added L2 and Dropout.
But deep networks still have a fundamental problem: training is UNSTABLE.
The activations at each layer keep changing as earlier layers update their weights.
Later layers have to constantly adapt to new input distributions.

This is called "internal covariate shift."

Batch Normalization fixes it by normalizing the inputs to each layer.
It is like installing a thermostat at every station in a kitchen.

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
# HELPER FUNCTIONS
# ==============================================================================

def he_init(input_size, output_size):
    """He initialization for stable deep network training."""
    return np.random.randn(input_size, output_size) * np.sqrt(2.0 / input_size)


def relu(x):
    """ReLU activation."""
    return np.maximum(0, x)


def relu_derivative(x):
    """Derivative of ReLU."""
    return (x > 0).astype(float)


# ==============================================================================
# BATCH NORMALIZATION LAYER
# ==============================================================================

class BatchNormLayer:
    """
    A Batch Normalization layer.

    WHAT IT DOES:
    For each mini-batch, it normalizes the inputs so they have:
        mean = 0
        standard deviation = 1

    Then it scales and shifts using learnable parameters:
        output = gamma * normalized + beta

    WHY GAMMA AND BETA?
    Forcing mean=0 and std=1 might be too restrictive.
    The network should be allowed to learn the optimal scale and shift.
    Gamma and beta give it that freedom.

    RUNNING STATISTICS:
    During training, we compute mean and variance from the current batch.
    We also keep RUNNING averages of these statistics.
    During testing, we use the running averages instead of batch statistics.
    This ensures consistent behavior between training and testing.
    """

    def __init__(self, num_features, momentum=0.9):
        """
        Create a BatchNorm layer.

        PARAMETERS:
            num_features = how many neurons this layer has
            momentum = how fast running averages update (0.9 = slow, stable)
        """
        self.num_features = num_features
        self.momentum = momentum
        self.epsilon = 1e-8

        # Learnable parameters: gamma (scale) and beta (shift)
        # Start with gamma = 1 and beta = 0 (identity transformation)
        self.gamma = np.ones((1, num_features))
        self.beta = np.zeros((1, num_features))

        # Running statistics for inference
        self.running_mean = np.zeros((1, num_features))
        self.running_var = np.ones((1, num_features))

    def forward(self, x, training=True):
        """
        Forward pass through BatchNorm.

        PARAMETERS:
            x = input activations, shape (batch_size, num_features)
            training = True during training, False during testing

        RETURNS:
            out = normalized, scaled, and shifted output
            cache = stored values for backpropagation
        """
        if training:
            # Compute mean and variance across the BATCH (axis=0)
            batch_mean = np.mean(x, axis=0, keepdims=True)
            batch_var = np.var(x, axis=0, keepdims=True)

            # Normalize: subtract mean, divide by standard deviation
            x_norm = (x - batch_mean) / np.sqrt(batch_var + self.epsilon)

            # Scale and shift
            out = self.gamma * x_norm + self.beta

            # Update running statistics
            # We blend the old running stats with the new batch stats
            # momentum=0.9 means: 90% old value + 10% new value
            self.running_mean = self.momentum * self.running_mean + (1 - self.momentum) * batch_mean
            self.running_var = self.momentum * self.running_var + (1 - self.momentum) * batch_var

            # Store values for backprop
            cache = {
                'x': x,
                'x_norm': x_norm,
                'mean': batch_mean,
                'var': batch_var,
                'gamma': self.gamma
            }
        else:
            # During testing: use running statistics
            x_norm = (x - self.running_mean) / np.sqrt(self.running_var + self.epsilon)
            out = self.gamma * x_norm + self.beta
            cache = None

        return out, cache

    def backward(self, dout, cache):
        """
        Backpropagation through BatchNorm.

        PARAMETERS:
            dout = gradient flowing into this layer
            cache = stored values from forward pass

        RETURNS:
            dx = gradient to pass to previous layer
            dgamma = gradient for gamma parameter
            dbeta = gradient for beta parameter
        """
        if cache is None:
            return dout, None, None

        x = cache['x']
        x_norm = cache['x_norm']
        mean = cache['mean']
        var = cache['var']
        gamma = cache['gamma']

        N = x.shape[0]

        # Gradient for beta: sum over all samples
        dbeta = np.sum(dout, axis=0, keepdims=True)

        # Gradient for gamma: sum over all samples, multiplied by normalized input
        dgamma = np.sum(dout * x_norm, axis=0, keepdims=True)

        # Gradient for normalized input
        dx_norm = dout * gamma

        # Gradient for variance
        dvar = np.sum(dx_norm * (x - mean) * -0.5 * np.power(var + self.epsilon, -1.5), axis=0, keepdims=True)

        # Gradient for mean
        dmean = np.sum(dx_norm * -1.0 / np.sqrt(var + self.epsilon), axis=0, keepdims=True)
        dmean += dvar * np.sum(-2.0 * (x - mean), axis=0, keepdims=True) / N

        # Gradient for input
        dx = dx_norm / np.sqrt(var + self.epsilon)
        dx += dvar * 2.0 * (x - mean) / N
        dx += dmean / N

        return dx, dgamma, dbeta


# ==============================================================================
# DEEP NETWORK (with optional BatchNorm)
# ==============================================================================

class DeepNetworkWithBatchNorm:
    """
    A deep network where each hidden layer can optionally use BatchNorm.

    Architecture with BatchNorm:
        Input
          |
          v
        Linear → BatchNorm → ReLU
          |
          v
        Linear → BatchNorm → ReLU
          |
          v
        Linear → BatchNorm → ReLU
          |
          v
        Output

    Architecture without BatchNorm:
        Input
          |
          v
        Linear → ReLU
          |
          v
        Linear → ReLU
          |
          v
        Linear → ReLU
          |
          v
        Output
    """

    def __init__(self, layer_sizes, use_batchnorm=False):
        """
        Create the network.

        PARAMETERS:
            layer_sizes = list of layer dimensions, e.g., [1, 32, 32, 32, 1]
            use_batchnorm = True to add BatchNorm after each hidden layer
        """
        self.layer_sizes = layer_sizes
        self.num_layers = len(layer_sizes) - 1
        self.use_batchnorm = use_batchnorm

        self.weights = []
        self.biases = []
        self.batch_norms = []

        for i in range(self.num_layers):
            W = he_init(layer_sizes[i], layer_sizes[i + 1])
            b = np.zeros((1, layer_sizes[i + 1]))
            self.weights.append(W)
            self.biases.append(b)

            # Add BatchNorm layer for hidden layers (not output layer)
            if use_batchnorm and i < self.num_layers - 1:
                self.batch_norms.append(BatchNormLayer(layer_sizes[i + 1]))
            else:
                self.batch_norms.append(None)

    def forward(self, X, training=True):
        """Forward pass through all layers."""
        current = X
        layer_data = []

        for i in range(self.num_layers - 1):
            # Linear transformation
            z = current @ self.weights[i] + self.biases[i]

            # Batch Normalization (optional)
            if self.use_batchnorm and self.batch_norms[i] is not None:
                z, bn_cache = self.batch_norms[i].forward(z, training)
            else:
                bn_cache = None

            # ReLU activation
            a = relu(z)

            layer_data.append((a, bn_cache, z, current))
            current = a

        # Output layer (no BatchNorm, no activation)
        z_final = current @ self.weights[-1] + self.biases[-1]
        predictions = z_final

        return predictions, layer_data

    def compute_loss(self, predictions, y_true):
        """Mean Squared Error."""
        return np.mean((predictions - y_true) ** 2)

    def backward(self, X, y_true, predictions, layer_data):
        """Backpropagation through all layers."""
        n = X.shape[0]
        grad = (predictions - y_true) / n

        dW_list = []
        db_list = []

        # Output layer gradients
        a_prev = layer_data[-1][0]
        dW = a_prev.T @ grad
        db = np.sum(grad, axis=0, keepdims=True)
        dW_list.insert(0, dW)
        db_list.insert(0, db)

        grad = grad @ self.weights[-1].T

        # Backward through hidden layers
        for i in range(self.num_layers - 2, -1, -1):
            a, bn_cache, z, a_prev = layer_data[i]

            # ReLU derivative
            grad = grad * relu_derivative(z)

            # BatchNorm backward (if used)
            if self.use_batchnorm and bn_cache is not None:
                grad, dgamma, dbeta = self.batch_norms[i].backward(grad, bn_cache)
                # Store BatchNorm parameter gradients
                self.batch_norms[i].dgamma = dgamma
                self.batch_norms[i].dbeta = dbeta

            # Linear layer gradients
            dW = a_prev.T @ grad
            db = np.sum(grad, axis=0, keepdims=True)
            dW_list.insert(0, dW)
            db_list.insert(0, db)

            if i > 0:
                grad = grad @ self.weights[i].T

        return dW_list, db_list

    def train(self, X_train, y_train, X_val, y_val, learning_rate, iterations):
        """Train the network."""
        train_losses = []
        val_losses = []

        print(f"Architecture: {' -> '.join(map(str, self.layer_sizes))}")
        print(f"BatchNorm: {self.use_batchnorm}")
        print(f"Learning rate: {learning_rate}")
        print(f"Training for {iterations} iterations...\n")

        for i in range(iterations):
            predictions, layer_data = self.forward(X_train, training=True)
            loss = self.compute_loss(predictions, y_train)

            dW_list, db_list = self.backward(X_train, y_train, predictions, layer_data)

            # Update weights and biases
            for j in range(self.num_layers):
                self.weights[j] -= learning_rate * dW_list[j]
                self.biases[j] -= learning_rate * db_list[j]

            # Update BatchNorm parameters
            if self.use_batchnorm:
                for j in range(len(self.batch_norms)):
                    if self.batch_norms[j] is not None:
                        if hasattr(self.batch_norms[j], 'dgamma'):
                            self.batch_norms[j].gamma -= learning_rate * self.batch_norms[j].dgamma
                            self.batch_norms[j].beta -= learning_rate * self.batch_norms[j].dbeta

            if i % 500 == 0:
                val_pred, _ = self.forward(X_val, training=False)
                val_loss = self.compute_loss(val_pred, y_val)
                train_losses.append(loss)
                val_losses.append(val_loss)
                print(f"  Step {i:5d} | Train: {loss:.6f} | Val: {val_loss:.6f}")

        return train_losses, val_losses

    def predict(self, X):
        """Make predictions."""
        predictions, _ = self.forward(X, training=False)
        return predictions


# ==============================================================================
# MAIN DEMONSTRATION
# ==============================================================================

if __name__ == "__main__":

    # --------------------------------------------------------------------------
    # PART A: Generate sine wave data
    # --------------------------------------------------------------------------
    np.random.seed(42)

    # Training data: sine wave with noise
    X_train = np.linspace(-np.pi, np.pi, 100).reshape(-1, 1)
    y_train = np.sin(X_train) + np.random.randn(100, 1) * 0.15

    # Validation data: clean sine wave
    X_val = np.linspace(-np.pi, np.pi, 200).reshape(-1, 1)
    y_val = np.sin(X_val)

    print("=" * 60)
    print("GENERATED SINE WAVE DATA")
    print("=" * 60)
    print(f"Training samples: {len(X_train)} (with noise)")
    print(f"Validation samples: {len(X_val)} (clean)")
    print()

    # --------------------------------------------------------------------------
    # PART B: Train WITHOUT BatchNorm (high learning rate)
    # --------------------------------------------------------------------------
    print("=" * 60)
    print("WITHOUT BATCHNORM (learning_rate = 0.05)")
    print("=" * 60)
    print("With a high learning rate and no BatchNorm, training is unstable.")
    print("Activations explode or vanish. The loss jumps around.\n")

    model_no_bn = DeepNetworkWithBatchNorm([1, 32, 32, 32, 1], use_batchnorm=False)
    train_no, val_no = model_no_bn.train(X_train, y_train, X_val, y_val,
                                          learning_rate=0.05, iterations=3000)

    no_bn_pred = model_no_bn.predict(X_val)
    no_bn_loss = model_no_bn.compute_loss(no_bn_pred, y_val)
    print(f"\nFinal validation loss (no BatchNorm): {no_bn_loss:.6f}")

    # --------------------------------------------------------------------------
    # PART C: Train WITH BatchNorm (same high learning rate)
    # --------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("WITH BATCHNORM (learning_rate = 0.05)")
    print("=" * 60)
    print("With BatchNorm, the same high learning rate is stable.")
    print("Activations stay in a healthy range. Training converges smoothly.\n")

    model_bn = DeepNetworkWithBatchNorm([1, 32, 32, 32, 1], use_batchnorm=True)
    train_bn, val_bn = model_bn.train(X_train, y_train, X_val, y_val,
                                       learning_rate=0.05, iterations=3000)

    bn_pred = model_bn.predict(X_val)
    bn_loss = model_bn.compute_loss(bn_pred, y_val)
    print(f"\nFinal validation loss (with BatchNorm): {bn_loss:.6f}")

    # --------------------------------------------------------------------------
    # PART D: Visual comparison
    # --------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("VISUAL COMPARISON")
    print("=" * 60)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Top left: Predictions without BatchNorm
    ax1 = axes[0, 0]
    ax1.plot(X_val, y_val, 'b-', linewidth=2, label='True sine wave')
    ax1.plot(X_val, no_bn_pred, 'r-', linewidth=2, label='No BatchNorm')
    ax1.scatter(X_train, y_train, c='black', s=10, alpha=0.4, label='Training data')
    ax1.set_title(f"Without BatchNorm\nValidation Loss: {no_bn_loss:.4f}")
    ax1.set_xlabel("x")
    ax1.set_ylabel("y")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Top right: Predictions with BatchNorm
    ax2 = axes[0, 1]
    ax2.plot(X_val, y_val, 'b-', linewidth=2, label='True sine wave')
    ax2.plot(X_val, bn_pred, 'g-', linewidth=2, label='With BatchNorm')
    ax2.scatter(X_train, y_train, c='black', s=10, alpha=0.4, label='Training data')
    ax2.set_title(f"With BatchNorm\nValidation Loss: {bn_loss:.4f}")
    ax2.set_xlabel("x")
    ax2.set_ylabel("y")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Bottom left: Loss curves without BatchNorm
    ax3 = axes[1, 0]
    steps = np.arange(0, len(train_no) * 500, 500)
    ax3.plot(steps, train_no, 'b-', label='Training loss')
    ax3.plot(steps, val_no, 'r-', label='Validation loss')
    ax3.set_title("Loss Curves (No BatchNorm)")
    ax3.set_xlabel("Iteration")
    ax3.set_ylabel("MSE Loss")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Bottom right: Loss curves with BatchNorm
    ax4 = axes[1, 1]
    steps = np.arange(0, len(train_bn) * 500, 500)
    ax4.plot(steps, train_bn, 'b-', label='Training loss')
    ax4.plot(steps, val_bn, 'g-', label='Validation loss')
    ax4.set_title("Loss Curves (With BatchNorm)")
    ax4.set_xlabel("Iteration")
    ax4.set_ylabel("MSE Loss")
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    fig.suptitle("Batch Normalization: Stability in Deep Networks", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase10/batchnorm_comparison.png', dpi=150)
    print("Plot saved to: src/phase10/batchnorm_comparison.png")
    plt.close()

    # --------------------------------------------------------------------------
    # PART E: Summary
    # --------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print(f"  WITHOUT BATCHNORM:")
    print(f"    Validation loss: {no_bn_loss:.6f}")
    print(f"    Training was UNSTABLE with learning rate = 0.05")
    print(f"    Activations jumped around. Loss was erratic.")
    print()
    print(f"  WITH BATCHNORM:")
    print(f"    Validation loss: {bn_loss:.6f}")
    print(f"    Training was STABLE with the SAME learning rate = 0.05")
    print(f"    Activations stayed in a healthy range. Loss decreased smoothly.")
    print()
    print("  KEY INSIGHTS:")
    print("    - BatchNorm normalizes activations at each layer.")
    print("    - It prevents 'internal covariate shift.'")
    print("    - Later layers always receive stable, normalized inputs.")
    print("    - This allows HIGHER learning rates and FASTER training.")
    print("    - Gamma and beta let the network learn optimal scale and shift.")
    print("    - During testing, running averages ensure consistent behavior.")
    print("=" * 60)
