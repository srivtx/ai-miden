#!/usr/bin/env python3
"""
================================================================================
PHASE 8: L2 REGULARIZATION AND OVERFITTING DEMONSTRATION
================================================================================

This script is designed for COMPLETE BEGINNERS.
Every single line has a comment explaining WHAT it does and WHY it matters.

GOAL:
    Show what OVERFITTING looks like, and then show how L2 REGULARIZATION fixes it.

WHAT IS OVERFITTING?
    Imagine you are studying for a test by memorizing every single practice problem
    instead of learning the underlying concept. You do great on the practice problems
    but fail on the real test because the numbers are slightly different.
    That is exactly what a neural network does when it overfits.
    It "memorizes" the training data (including the noise!) instead of learning
    the true underlying pattern.

WHAT IS L2 REGULARIZATION?
    L2 regularization (also called "weight decay") is a technique that PENALIZES
    the model for having very large weights. It adds a cost to the loss function
    that grows as the weights get bigger. This forces the network to keep its
    weights small and simple, which prevents it from creating overly complex,
    wiggly curves that memorize noise.

================================================================================
"""

# ==============================================================================
# STEP 1: IMPORT THE TOOLS WE NEED
# ==============================================================================
# NumPy is a library for doing fast math with arrays and matrices.
# Neural networks are basically a lot of matrix multiplication, so we need this.
import numpy as np

# Matplotlib is a library for making charts and graphs.
# We will use it to draw the data and the model's predictions.
import matplotlib

# The 'Agg' backend means "Anti-Grain Geometry." It tells matplotlib to draw
# images to a FILE instead of trying to open a window on the screen.
# This is important when running code on a server or in an environment
# where there is no display screen available.
matplotlib.use('Agg')

# Pyplot is the main plotting module within matplotlib. We import it as 'plt'
# because that is the standard nickname used by almost every Python programmer.
import matplotlib.pyplot as plt

# os is a built-in module that lets us work with file paths in a way that works
# on any operating system (Windows, Mac, Linux).
import os


# ==============================================================================
# STEP 2: DEFINE THE OverfittingDemo CLASS
# ==============================================================================
# A "class" is a blueprint for creating objects. Here, our object is a neural network.
# We put all the logic (forward pass, backward pass, training) inside this class
# so it is organized and easy to reuse.
class OverfittingDemo:
    """
    This class builds a deep neural network and trains it.
    It can optionally use L2 regularization.
    """

    # ==========================================================================
    # STEP 2a: INITIALIZATION (The "__init__" method)
    # ==========================================================================
    # This method runs automatically when we create a new object from this class.
    # It sets up the network's structure and initializes its weights.
    def __init__(self, layer_sizes, lambda_l2=0.0):
        """
        layer_sizes: A list of integers. Each number is how many neurons are in
                     that layer. For example, [1, 64, 64, 64, 1] means:
                     - Layer 0: 1 neuron  (input layer, takes 1 number)
                     - Layer 1: 64 neurons (hidden layer)
                     - Layer 2: 64 neurons (hidden layer)
                     - Layer 3: 64 neurons (hidden layer)
                     - Layer 4: 1 neuron  (output layer, predicts 1 number)

        lambda_l2:   The strength of L2 regularization.
                     - 0.0 means NO regularization at all.
                     - 0.01 means mild regularization (small penalty for big weights).
                     - Larger values mean STRONGER regularization.
        """

        # Store the layer sizes so we can use them later.
        self.layer_sizes = layer_sizes

        # Store the regularization strength.
        self.lambda_l2 = lambda_l2

        # Create two empty lists to hold the weights and biases.
        # We will fill these in the loop below.
        self.weights = []
        self.biases = []

        # ----------------------------------------------------------------------
        # WHY DO WE NEED WEIGHTS AND BIASES?
        # ----------------------------------------------------------------------
        # A neural network learns by adjusting numbers called "weights" and "biases."
        # Each connection between neurons has a weight.
        # Each neuron has a bias.
        # The network's prediction is just a giant mathematical formula using
        # these weights and biases. Training means finding the best values.

        # ----------------------------------------------------------------------
        # LOOP THROUGH EACH PAIR OF LAYERS TO CREATE WEIGHTS AND BIASES
        # ----------------------------------------------------------------------
        # range(len(layer_sizes) - 1) gives us one fewer iteration than layers,
        # because weights connect one layer to the NEXT layer.
        for i in range(len(layer_sizes) - 1):
            # Get the number of neurons in the current layer and the next layer.
            input_size = layer_sizes[i]
            output_size = layer_sizes[i + 1]

            # ------------------------------------------------------------------
            # WHAT IS "HE INITIALIZATION"?
            # ------------------------------------------------------------------
            # If we start weights at 0, the network cannot learn (symmetry problem).
            # If we start them too big or too small, signals explode or vanish.
            # "He initialization" is a smart way to pick starting weights.
            # It uses a normal distribution scaled by sqrt(2 / input_size).
            # This works especially well with ReLU activation functions.
            # Think of it as giving the network a "fair starting position"
            # so it has a good chance of learning.
            # ------------------------------------------------------------------
            W = np.random.randn(input_size, output_size) * np.sqrt(2.0 / input_size)

            # Biases start at zero. This is a common and safe choice.
            b = np.zeros((1, output_size))

            # Add the created weight matrix and bias vector to our lists.
            self.weights.append(W)
            self.biases.append(b)

    # ==========================================================================
    # STEP 2b: FORWARD PASS
    # ==========================================================================
    # The forward pass is how the network makes a prediction.
    # Data flows from the input layer, through the hidden layers, to the output.
    def forward(self, X):
        """
        X: The input data. Shape is (number_of_samples, number_of_features).
           For us, it will be (30, 1) for training and (100, 1) for validation.

        Returns:
            output: The network's final predictions.
            activations: A list of all neuron values AFTER activation functions.
            pre_activations: A list of all neuron values BEFORE activation functions.
        """

        # The first "activation" is just the raw input data.
        # We put it in a list so we can keep track of every layer's values.
        activations = [X]

        # This list will store the values BEFORE we apply the activation function.
        # We need these later for the backward pass (calculus requires them).
        pre_activations = []

        # Start with the input.
        A = X

        # ----------------------------------------------------------------------
        # LOOP THROUGH EVERY LAYER EXCEPT THE LAST ONE
        # ----------------------------------------------------------------------
        # The last layer is special because it does NOT use ReLU (it uses linear).
        # Linear output means "just output the number directly" which is what
        # we want for regression (predicting a continuous value like a sine wave).
        for i in range(len(self.weights) - 1):
            # Z = (data @ weights) + bias
            # The '@' symbol means matrix multiplication in Python.
            Z = A @ self.weights[i] + self.biases[i]

            # Save Z before we change it. We need this for backpropagation.
            pre_activations.append(Z)

            # ------------------------------------------------------------------
            # WHAT IS ReLU?
            # ------------------------------------------------------------------
            # ReLU stands for "Rectified Linear Unit."
            # It is the simplest useful activation function: max(0, x)
            # If x is positive, output x. If x is negative, output 0.
            # WHY? Without an activation function, stacking layers is pointless;
            # the whole network would just be one big linear equation.
            # ReLU introduces non-linearity, allowing the network to learn
            # complex curves and shapes (like a sine wave!).
            # ------------------------------------------------------------------
            A = np.maximum(Z, 0)  # This is ReLU.

            # Save the activated values for backpropagation.
            activations.append(A)

        # ----------------------------------------------------------------------
        # THE LAST LAYER (OUTPUT LAYER)
        # ----------------------------------------------------------------------
        # For regression problems, the output layer should be LINEAR.
        # We do NOT apply ReLU here because we want the network to be able
        # to predict negative numbers (sine waves go below zero!).
        i = len(self.weights) - 1
        Z = A @ self.weights[i] + self.biases[i]
        pre_activations.append(Z)
        A = Z  # Linear activation (no change).
        activations.append(A)

        # The final A is our prediction.
        return A, activations, pre_activations

    # ==========================================================================
    # STEP 2c: COMPUTE LOSS
    # ==========================================================================
    # The "loss" tells us how wrong our predictions are.
    # Lower loss = better predictions.
    # With L2 regularization, we add an EXTRA penalty for having large weights.
    def compute_loss(self, predictions, y_true):
        """
        predictions: What the network guessed. Shape (m, 1).
        y_true:      The correct answers. Shape (m, 1).

        Returns:
            total_loss: The loss we will actually optimize (MSE + L2 penalty).
            mse:        The raw Mean Squared Error (useful for tracking).
        """

        # Number of samples. We use this to average the error.
        m = predictions.shape[0]

        # ----------------------------------------------------------------------
        # MEAN SQUARED ERROR (MSE)
        # ----------------------------------------------------------------------
        # MSE measures the average squared difference between predictions and truth.
        # We square the differences so negative and positive errors don't cancel out.
        # We also punish BIG errors much more than small errors (because of the square).
        # Example: an error of 2 contributes 4 to the loss. An error of 10 contributes 100.
        # Formula: MSE = mean((predictions - y_true) ** 2)
        # ----------------------------------------------------------------------
        mse = np.mean((predictions - y_true) ** 2)

        # ----------------------------------------------------------------------
        # L2 REGULARIZATION PENALTY
        # ----------------------------------------------------------------------
        # If lambda_l2 is greater than 0, we add a penalty for large weights.
        # The penalty is: lambda_l2 * sum of (weight squared) across ALL weights.
        # WHY SQUARED? Because it is easy to differentiate (calculus).
        # The derivative of w^2 is 2w. This gives us a simple gradient.
        # ----------------------------------------------------------------------
        if self.lambda_l2 > 0.0:
            # Start the penalty at zero.
            l2_penalty = 0.0

            # Loop through every weight matrix in the network.
            for W in self.weights:
                # np.sum(W ** 2) adds up the square of every single weight in this matrix.
                l2_penalty += np.sum(W ** 2)

            # Multiply by lambda_l2 to scale the penalty according to our chosen strength.
            l2_penalty = self.lambda_l2 * l2_penalty

            # ------------------------------------------------------------------
            # WHY ADD THE PENALTY TO THE LOSS?
            # ------------------------------------------------------------------
            # The network tries to MINIMIZE the total loss.
            # If large weights make the total loss bigger, the network will
            # naturally prefer SMALLER weights to bring the total loss down.
            # It is like adding a "speed limit" for weights.
            # This forces the model to keep weights small.
            # ------------------------------------------------------------------
            total_loss = mse + l2_penalty
        else:
            # If lambda_l2 is 0, there is no penalty. Total loss is just MSE.
            total_loss = mse

        return total_loss, mse

    # ==========================================================================
    # STEP 2d: BACKWARD PASS (BACKPROPAGATION)
    # ==========================================================================
    # Backpropagation is how the network learns from its mistakes.
    # It uses calculus (the chain rule) to figure out which weights are responsible
    # for the error, and in what direction they should change.
    def backward(self, X, y_true, predictions, activations, pre_activations):
        """
        Uses the chain rule to compute gradients of the loss with respect to
        every weight and bias in the network.

        Returns:
            A dictionary of gradients for weights and biases.
        """

        # Number of training examples. Needed to average the gradient.
        m = X.shape[0]

        # This dictionary will store all the gradients.
        grads = {}

        # ----------------------------------------------------------------------
        # GRADIENT OF THE LOSS WITH RESPECT TO THE FINAL OUTPUT
        # ----------------------------------------------------------------------
        # Since our loss is MSE = mean((pred - y)^2), the derivative is:
        # dL/dpred = (2/m) * (pred - y)
        # This tells us: "If we increase the prediction a tiny bit, how much does
        # the loss change?"
        dZ = (2.0 / m) * (predictions - y_true)

        # ----------------------------------------------------------------------
        # LOOP BACKWARDS THROUGH THE LAYERS
        # ----------------------------------------------------------------------
        # We start at the output layer and move toward the input layer.
        # This is why it is called "back" propagation.
        for i in range(len(self.weights) - 1, -1, -1):

            # activations[i] is the output of the PREVIOUS layer (the input to this layer).
            A_prev = activations[i]

            # ------------------------------------------------------------------
            # GRADIENT FOR WEIGHTS (dW)
            # ------------------------------------------------------------------
            # The standard backprop gradient for weights is:
            # dW = A_prev.T @ dZ
            # This comes from the chain rule of calculus.
            # It tells us how much each weight contributed to the final error.
            dW = A_prev.T @ dZ

            # ------------------------------------------------------------------
            # ADD THE L2 GRADIENT
            # ------------------------------------------------------------------
            # Remember, our total loss = MSE + lambda * sum(W^2).
            # The gradient of lambda * W^2 with respect to W is 2 * lambda * W.
            # So we ADD this to the standard gradient.
            #
            # WHY DOES THIS PUSH WEIGHTS TOWARD ZERO?
            # Because at every training step, the update rule is:
            # W_new = W_old - learning_rate * dW
            # If dW contains a positive term (2*lambda*W), then when we subtract it,
            # we are subtracting a piece proportional to W itself.
            # If W is positive, we subtract a positive amount.
            # If W is negative, dW is negative, so subtracting a negative = adding,
            # which pushes W toward zero from below.
            # Either way, W gets dragged closer to zero.
            # ------------------------------------------------------------------
            if self.lambda_l2 > 0.0:
                dW = dW + 2.0 * self.lambda_l2 * self.weights[i]

            # ------------------------------------------------------------------
            # GRADIENT FOR BIASES (db)
            # ------------------------------------------------------------------
            # The gradient for a bias is just the sum of the upstream gradients.
            # We keepdims=True so the shape stays (1, output_size) for broadcasting.
            db = np.sum(dZ, axis=0, keepdims=True)

            # Store the gradients in our dictionary.
            grads[f'dW{i}'] = dW
            grads[f'db{i}'] = db

            # ------------------------------------------------------------------
            # PROPAGATE THE ERROR BACK TO THE PREVIOUS LAYER (if there is one)
            # ------------------------------------------------------------------
            if i > 0:
                # dA_prev = dZ @ W.T
                # This distributes the blame backward through the connections.
                dA = dZ @ self.weights[i].T

                # Now we must account for the ReLU activation function.
                # ReLU: A = max(0, Z). The derivative is 1 where Z > 0, and 0 elsewhere.
                # So we "gate" the gradient: wherever Z was negative, kill the gradient.
                dZ = dA * (pre_activations[i - 1] > 0)

        return grads

    # ==========================================================================
    # STEP 2e: TRAINING LOOP
    # ==========================================================================
    # Training means repeating the forward pass, loss calculation, backward pass,
    # and weight update thousands of times until the network gets good.
    def train(self, X_train, y_train, X_val, y_val, learning_rate, iterations):
        """
        Trains the network on the training data.

        X_train, y_train: Training inputs and correct outputs.
        X_val, y_val:     Validation inputs and correct outputs.
                           We do NOT train on these! We only check our performance
                           on them to see if we are overfitting.
        learning_rate:    How big of a step we take when updating weights.
                           Too big = unstable. Too small = very slow learning.
        iterations:       How many times to repeat the training step.

        Returns:
            train_loss_history: List of training losses recorded every 500 steps.
            val_loss_history:   List of validation losses recorded every 500 steps.
        """

        # Create empty lists to track how the loss changes over time.
        # We will plot these later.
        train_loss_history = []
        val_loss_history = []

        # ==================================================================
        # THE MAIN TRAINING LOOP
        # ==================================================================
        for step in range(iterations):
            # --------------------------------------------------------------
            # 1. FORWARD PASS ON TRAINING DATA
            # --------------------------------------------------------------
            # Make predictions using the CURRENT weights.
            predictions, activations, pre_activations = self.forward(X_train)

            # --------------------------------------------------------------
            # 2. COMPUTE LOSS ON TRAINING DATA
            # --------------------------------------------------------------
            # We only use the training loss to calculate gradients.
            # (Note: compute_loss returns total_loss and mse. We need total_loss
            #  for gradients, but we log the raw mse for clarity.)
            total_loss, train_mse = self.compute_loss(predictions, y_train)

            # --------------------------------------------------------------
            # 3. BACKWARD PASS
            # --------------------------------------------------------------
            # Calculate gradients. These tell us which direction to move the weights.
            grads = self.backward(X_train, y_train, predictions, activations, pre_activations)

            # --------------------------------------------------------------
            # 4. UPDATE WEIGHTS AND BIASES (GRADIENT DESCENT)
            # --------------------------------------------------------------
            # We subtract the gradient times the learning rate.
            # WHY SUBTRACT? Because the gradient points in the direction of
            # INCREASING loss. We want to DECREASE loss, so we go the opposite way.
            for i in range(len(self.weights)):
                self.weights[i] = self.weights[i] - learning_rate * grads[f'dW{i}']
                self.biases[i] = self.biases[i] - learning_rate * grads[f'db{i}']

            # --------------------------------------------------------------
            # 5. LOG PROGRESS EVERY 500 ITERATIONS
            # --------------------------------------------------------------
            # We do not log every single step because that would be too much output.
            # Every 500 steps is a good balance.
            if step % 500 == 0 or step == iterations - 1:
                # Evaluate on training data (raw MSE, no L2 penalty for reporting).
                train_preds, _, _ = self.forward(X_train)
                _, current_train_mse = self.compute_loss(train_preds, y_train)

                # Evaluate on VALIDATION data.
                # We use the validation data to see how well the model generalizes
                # to data it has NEVER seen during training.
                val_preds, _, _ = self.forward(X_val)
                _, current_val_mse = self.compute_loss(val_preds, y_val)

                # Store these values in our history lists.
                train_loss_history.append(current_train_mse)
                val_loss_history.append(current_val_mse)

                # Print a nice status message.
                print(f"  Step {step:5d} | Train MSE: {current_train_mse:.6f} | Val MSE: {current_val_mse:.6f}")

        return train_loss_history, val_loss_history

    # ==========================================================================
    # STEP 2f: PREDICT METHOD
    # ==========================================================================
    # A simple helper method that just runs the forward pass and returns predictions.
    # This is useful when we want to plot the model's curve without re-training.
    def predict(self, X):
        """
        X: Input data.
        Returns: The network's predictions.
        """
        predictions, _, _ = self.forward(X)
        return predictions


# ==============================================================================
# STEP 3: MAIN EXECUTION BLOCK
# ==============================================================================
# This block only runs when we execute the script directly (not when importing it).
if __name__ == "__main__":

    # ======================================================================
    # PART A: GENERATE THE DATA
    # ======================================================================
    # We need data to train on. We will create a simple problem:
    # Learn the sine wave function, y = sin(x).
    # But we will make it HARD by adding lots of noise and using very few points.

    # A random seed makes sure that every time we run the script,
    # we get the EXACT same random numbers. This makes our experiment repeatable.
    np.random.seed(42)

    # Number of training samples. We use ONLY 30.
    # WHY SO FEW? Because a big network with little data is a PERFECT recipe
    # for overfitting. The network has more than enough "memory" to memorize
    # all 30 points instead of learning the smooth sine wave.
    n_samples = 30

    # Create training X values: 30 random numbers between -3 and +3.
    # np.random.rand(n_samples, 1) gives numbers between 0 and 1.
    # Multiplying by 6 gives 0 to 6. Subtracting 3 gives -3 to +3.
    # np.sort sorts them along axis 0 so they are in order left-to-right.
    # This makes the plots look nicer.
    X_train = np.sort(np.random.rand(n_samples, 1) * 6 - 3, axis=0)

    # Create training Y values: the sine of X, plus NOISE.
    # np.sin(X_train) is the TRUE underlying pattern we want the model to learn.
    # np.random.randn(n_samples, 1) * 0.3 adds random Gaussian noise.
    # Standard deviation of 0.3 is quite a lot of noise relative to sine's range (-1 to 1).
    # This means the training data is WIGGLY and messy.
    y_train = np.sin(X_train) + np.random.randn(n_samples, 1) * 0.3

    # Create VALIDATION data.
    # np.linspace(-3, 3, 100) creates 100 evenly spaced points from -3 to 3.
    # reshape(-1, 1) makes it a column vector with shape (100, 1).
    X_val = np.linspace(-3, 3, 100).reshape(-1, 1)

    # Validation targets are the TRUE sine wave with NO NOISE.
    # WHY NO NOISE? Because validation data represents the "real world" pattern
    # we are trying to learn. We want to see if the model found the TRUE sine wave
    # or if it just memorized the noisy training points.
    y_val = np.sin(X_val)

    # Print an explanation for the user.
    print("=" * 60)
    print("DATA GENERATION EXPLANATION")
    print("=" * 60)
    print("We created FEW training points (30) with LOTS of noise.")
    print("This setup is DESIGNED to overfit.")
    print("The validation data is clean, so we can see if the model")
    print("memorized the noise or learned the true sine wave.")
    print("=" * 60)
    print()

    # ======================================================================
    # PART B: TRAIN WITHOUT L2 REGULARIZATION (THE OVERFITTING MODEL)
    # ======================================================================
    print("=" * 60)
    print("TRAINING WITHOUT L2 REGULARIZATION")
    print("=" * 60)
    print("We use a BIG network ([1, 64, 64, 64, 1]) with FEW data points.")
    print("This is a recipe for overfitting: the network has ~4,000 parameters")
    print("but only 30 training examples. It can easily memorize every point.")
    print()

    # Create the model with lambda_l2=0.0 (no regularization).
    model_overfit = OverfittingDemo([1, 64, 64, 64, 1], lambda_l2=0.0)

    # Train the model.
    # Learning rate 0.001 means we take small, careful steps.
    # 5000 iterations means we have plenty of time to converge.
    train_losses, val_losses = model_overfit.train(
        X_train, y_train, X_val, y_val, learning_rate=0.001, iterations=5000
    )

    # ======================================================================
    # PART C: TRAIN WITH L2 REGULARIZATION (THE REGULARIZED MODEL)
    # ======================================================================
    print()
    print("=" * 60)
    print("TRAINING WITH L2 REGULARIZATION")
    print("=" * 60)
    print("We use the EXACT same network, but now lambda_l2=0.01.")
    print("This adds a penalty for large weights.")
    print("The network is now forced to find a SMOOTHER solution.")
    print()

    # Create the model with lambda_l2=0.01 (moderate regularization).
    model_reg = OverfittingDemo([1, 64, 64, 64, 1], lambda_l2=0.01)

    # Train the regularized model with the same data and settings.
    train_losses_l2, val_losses_l2 = model_reg.train(
        X_train, y_train, X_val, y_val, learning_rate=0.001, iterations=5000
    )

    # ======================================================================
    # PART D: VISUALIZE THE RESULTS
    # ======================================================================
    # We will create a 2x2 grid of plots to compare the two models side-by-side.
    # A picture is worth a thousand words, especially for understanding overfitting!

    # Create a figure and 4 subplots arranged in 2 rows and 2 columns.
    # figsize=(14, 10) makes the figure 14 inches wide and 10 inches tall.
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # ------------------------------------------------------------------
    # TOP LEFT: Overfitting Model (No L2) - Predictions vs Truth
    # ------------------------------------------------------------------
    ax = axes[0, 0]

    # Plot the training data as black dots.
    # These are the NOISY points the model learned from.
    ax.scatter(X_train, y_train, color='black', label='Training Data (Noisy)', zorder=5)

    # Plot the TRUE sine wave as a blue line.
    # This is the "correct answer" we wish the model had learned.
    ax.plot(X_val, y_val, color='blue', linewidth=2, label='True Sine Wave', zorder=3)

    # Plot the overfitted model's predictions on the validation set as a red line.
    # If the model overfit, this line will be very wiggly and try to hit every black dot.
    preds_overfit = model_overfit.predict(X_val)
    ax.plot(X_val, preds_overfit, color='red', linewidth=2, label='Model Prediction', zorder=4)

    # Set the title. Include the final validation MSE so we can compare numerically.
    ax.set_title(f"Overfitting Model (No L2)\nFinal Val MSE: {val_losses[-1]:.4f}", fontsize=12)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # ------------------------------------------------------------------
    # TOP RIGHT: Overfitting Model (No L2) - Training Curves
    # ------------------------------------------------------------------
    ax = axes[0, 1]

    # The x-axis represents how far into training we are.
    # We logged every 500 iterations, so we create a list of step numbers.
    steps = np.arange(len(train_losses)) * 500

    # Plot training loss in blue.
    # This should go DOWN because the model is getting better at fitting the training data.
    ax.plot(steps, train_losses, color='blue', linewidth=2, label='Training Loss')

    # Plot validation loss in red.
    # In an overfitting scenario, this starts going DOWN but then goes UP.
    # WHY DOES IT GO UP? Because the model starts memorizing training noise
    # instead of learning the true pattern. The more it memorizes, the worse
    # it performs on new, clean data.
    ax.plot(steps, val_losses, color='red', linewidth=2, label='Validation Loss')

    ax.set_title("Training Curves (No L2)\nBlue = Train, Red = Val", fontsize=12)
    ax.set_xlabel("Training Iteration")
    ax.set_ylabel("Mean Squared Error (MSE)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # ------------------------------------------------------------------
    # BOTTOM LEFT: Regularized Model (L2) - Predictions vs Truth
    # ------------------------------------------------------------------
    ax = axes[1, 0]

    # Plot the same training data and true sine wave.
    ax.scatter(X_train, y_train, color='black', label='Training Data (Noisy)', zorder=5)
    ax.plot(X_val, y_val, color='blue', linewidth=2, label='True Sine Wave', zorder=3)

    # Plot the regularized model's predictions in GREEN.
    # With L2, this curve should be much SMOOTHER and closer to the true blue line.
    # It will NOT try to hit every noisy black dot perfectly.
    preds_reg = model_reg.predict(X_val)
    ax.plot(X_val, preds_reg, color='green', linewidth=2, label='Model Prediction (L2)', zorder=4)

    ax.set_title(f"Regularized Model (L2)\nFinal Val MSE: {val_losses_l2[-1]:.4f}", fontsize=12)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # ------------------------------------------------------------------
    # BOTTOM RIGHT: Regularized Model (L2) - Training Curves
    # ------------------------------------------------------------------
    ax = axes[1, 1]

    # Again, the x-axis is training steps.
    steps_l2 = np.arange(len(train_losses_l2)) * 500

    # Plot training loss in blue.
    ax.plot(steps_l2, train_losses_l2, color='blue', linewidth=2, label='Training Loss')

    # Plot validation loss in red.
    # With L2 regularization, BOTH curves should go down and then STAY CLOSE together.
    # WHY? Because L2 prevents the model from memorizing noise.
    # It is forced to find a simple, smooth solution that works for BOTH
    # the training data AND the validation data.
    ax.plot(steps_l2, val_losses_l2, color='red', linewidth=2, label='Validation Loss')

    ax.set_title("Training Curves (With L2)\nBlue = Train, Red = Val", fontsize=12)
    ax.set_xlabel("Training Iteration")
    ax.set_ylabel("Mean Squared Error (MSE)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # ------------------------------------------------------------------
    # ADD A BIG TITLE FOR THE ENTIRE FIGURE
    # ------------------------------------------------------------------
    fig.suptitle(
        "Overfitting vs L2 Regularization\n"
        "Top Row = No Regularization (Overfitting) | "
        "Bottom Row = L2 Regularization (Generalization)",
        fontsize=14,
        fontweight='bold'
    )

    # Tight layout makes sure the subplots don't overlap with each other.
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # ------------------------------------------------------------------
    # SAVE THE FIGURE TO A FILE
    # ------------------------------------------------------------------
    # We save the plot in the same directory as this script so we can find it easily.
    script_directory = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_directory, 'overfitting_vs_l2.png')
    plt.savefig(output_path, dpi=150)

    print()
    print(f"Figure saved successfully to: {output_path}")

    # ======================================================================
    # PART E: PRINT A TEXT SUMMARY
    # ======================================================================
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("WITHOUT L2 (Overfitting):")
    print(f"  - Final Training Loss:   {train_losses[-1]:.6f}")
    print(f"  - Final Validation Loss: {val_losses[-1]:.6f}")
    print("  - Training loss is LOW, but validation loss is HIGH.")
    print("  - This means the model memorized the training noise.")
    print("  - The prediction curve is wiggly and does not match the true sine wave.")
    print()
    print("WITH L2 (Generalization):")
    print(f"  - Final Training Loss:   {train_losses_l2[-1]:.6f}")
    print(f"  - Final Validation Loss: {val_losses_l2[-1]:.6f}")
    print("  - Training loss is higher, but validation loss is LOWER.")
    print("  - This means the model learned the TRUE underlying pattern.")
    print("  - The prediction curve is smooth and follows the sine wave.")
    print()
    print("KEY TAKEAWAYS:")
    print("  1. L2 forces the model to prefer simple, smooth solutions.")
    print("  2. It penalizes large weights that create wiggly curves.")
    print("  3. A slightly higher training loss is OK if validation loss is lower.")
    print("  4. Validation loss is the TRUE measure of how good your model is.")
    print("=" * 60)
