"""
================================================================================
PHASE 6: MULTI-CLASS CLASSIFICATION WITH A NEURAL NETWORK
================================================================================

This script is designed for a COMPLETE BEGINNER.
If you have zero AI/ML knowledge, you are in the right place.
We will use only basic algebra and Python.

GOAL: Build a neural network that can classify points into 3 categories.
      Think of it like sorting M&Ms by color, but for dots on a graph.

We will cover:
  - Softmax (turning numbers into probabilities)
  - One-hot encoding (representing categories as vectors)
  - Categorical cross-entropy (measuring how wrong we are)
  - Backpropagation (figuring out who to blame for mistakes)
  - Visualization (making pretty graphs)

Let's go!
================================================================================
"""


# ==============================================================================
# STEP 1: IMPORT THE TOOLS WE NEED
# ==============================================================================

# NumPy is a Python library for working with numbers in big tables called "arrays."
# Think of an array like an Excel spreadsheet full of numbers.
# We can do math on the entire spreadsheet at once instead of one cell at a time.
import numpy as np

# Matplotlib is a Python library for drawing graphs and charts.
# It helps us visualize our data and our model's predictions.
# Without it, we'd just be staring at tables of numbers forever.
import matplotlib.pyplot as plt


# ==============================================================================
# STEP 2: HELPER FUNCTIONS
# ==============================================================================

# Softmax is a mathematical function that turns a list of numbers into probabilities.
# What does that mean?
#   Imagine you have three scores: [5, 2, 1]
#   Softmax converts these into:  [0.84, 0.11, 0.05]
#   Notice they all add up to 1.0! That's what probabilities do.
# We use softmax at the very end of our network to say:
#   "The model thinks there is an 84% chance it's Class 0, 11% Class 1, 5% Class 2."
def softmax(z):
    """
    Turns raw scores into probabilities that sum to 1.

    Parameters:
        z: A matrix of shape (n_samples, n_classes).
           Each row is one data point.
           Each column is the score for one class.

    Returns:
        A matrix of the same shape, but now every row sums to 1.0.
    """

    # --------------------------------------------------------------------------
    # CRITICAL TRICK: SUBTRACT THE MAXIMUM PER ROW
    # --------------------------------------------------------------------------
    # Why do we subtract the max?
    # Because we are about to calculate e^z (the exponential of z).
    # The exponential function grows EXTREMELY fast.
    # e^10   = 22,026
    # e^100  = 2.6 * 10^43   (bigger than atoms in the universe)
    # e^1000 = INFINITY      (computer says "I'm done, this is too big")
    # If any number in z is 1000, np.exp(1000) will overflow and crash or give "inf."
    #
    # THE FIX:
    #   Subtract the maximum value in each row from every value in that row.
    #   Example: row = [1000, 1001, 999]
    #            max = 1001
    #            subtract: [1000-1001, 1001-1001, 999-1001] = [-1, 0, -2]
    #   Now the largest number is 0.
    #   e^0 = 1. Everything else is smaller. No overflow!
    #
    # DOES THIS CHANGE THE RESULT?
    #   No! Because softmax divides by the sum of all exponentials.
    #   If you divide the top and bottom of a fraction by the same thing,
    #   the answer doesn't change. This is just a clever math trick.
    #
    # This is one of the most important numerical stability tricks in all of AI.
    # --------------------------------------------------------------------------
    max_per_row = np.max(z, axis=1, keepdims=True)
    # axis=1 means "look across the columns" (find max per row).
    # keepdims=True keeps the result as a column vector so we can subtract it easily.

    # Now subtract the max from every element in z.
    z_shifted = z - max_per_row

    # Calculate the exponential (e^x) of every number.
    # e^x means Euler's number (~2.718) raised to the power x.
    # After subtracting the max, the largest value is 0, so e^0 = 1.
    # All other values are negative, so their exponentials are between 0 and 1.
    exp_z = np.exp(z_shifted)

    # Sum up all the exponentials in each row.
    # We need this to divide each exponential by the total, turning them into fractions.
    sum_exp = np.sum(exp_z, axis=1, keepdims=True)
    # Again, axis=1 means sum across columns (within each row).
    # keepdims=True keeps it as a column so we can divide.

    # Divide each exponential by the sum of exponentials in its row.
    # This ensures every row sums to exactly 1.0.
    # Row 1 might be [0.7, 0.2, 0.1]
    # Row 2 might be [0.1, 0.8, 0.1]
    # Each row is a valid probability distribution.
    return exp_z / sum_exp


def one_hot(y, num_classes):
    """
    Converts class labels into one-hot encoded vectors.

    What is one-hot encoding?
    -------------------------
    Computers love numbers, but they don't understand categories like "cat", "dog", "bird."
    We could use 0, 1, 2, but the computer might think 2 is "bigger" than 1,
    which doesn't make sense for categories.

    One-hot encoding solves this by giving EACH class its own column.
    Class 0 -> [1, 0, 0]
    Class 1 -> [0, 1, 0]
    Class 2 -> [0, 0, 1]

    The "1" is in the position of the correct class.
    All other positions are 0.
    This is called "one-hot" because exactly one position is "hot" (1), the rest are "cold" (0).

    Why do we need this?
    --------------------
    Our loss function (categorical cross-entropy) multiplies the true labels
    by the predicted probabilities. If the true label is [0, 1, 0],
    when we multiply by predictions [0.2, 0.7, 0.1], we get [0, 0.7, 0].
    Only the correct class survives! This is exactly what we want.

    Parameters:
        y:           A column vector of shape (n_samples, 1) containing class labels (0, 1, 2, ...).
        num_classes: The total number of different classes.

    Returns:
        A matrix of shape (n_samples, num_classes) where each row is a one-hot vector.
    """

    # Get the number of samples (data points).
    n_samples = y.shape[0]

    # Create a big table of zeros with shape (n_samples, num_classes).
    # Every row starts as [0, 0, 0].
    one_hot_matrix = np.zeros((n_samples, num_classes))

    # We need to set the correct position in each row to 1.
    # y.flatten() turns y from a column vector into a flat list like [0, 2, 1, 0, 2].
    # np.arange(n_samples) creates [0, 1, 2, 3, ...] representing row indices.
    # So we are saying:
    #   Row 0, column y[0] -> set to 1
    #   Row 1, column y[1] -> set to 1
    #   Row 2, column y[2] -> set to 1
    #   ... and so on.
    one_hot_matrix[np.arange(n_samples), y.flatten()] = 1

    return one_hot_matrix


# ==============================================================================
# STEP 3: THE MULTI-CLASS CLASSIFIER CLASS
# ==============================================================================

class MultiClassClassifier:
    """
    A neural network for classifying data into multiple categories.

    Architecture:
    -------------
    INPUT LAYER  ->  HIDDEN LAYER  ->  OUTPUT LAYER
       (2)             (8)               (3)

    INPUT: 2 numbers (x and y coordinates of a point).
    HIDDEN: 8 neurons that learn to find patterns.
    OUTPUT: 3 numbers (one score for each class).

    The output scores go through softmax to become probabilities.
    """

    def __init__(self, input_size, hidden_size, num_classes):
        """
        Create the weights and biases for our network.

        Parameters:
            input_size:   How many numbers come into the network.
                          For our spiral data, each point has an x and y coordinate, so 2.
            hidden_size:  How many neurons in the hidden layer.
                          More neurons = more capacity to learn complex patterns.
                          For spirals, we need at least a few to learn curves.
            num_classes:  How many categories we want to predict.
                          We have 3 spirals, so 3 classes.
        """

        # ----------------------------------------------------------------------
        # WEIGHTS AND BIASES FOR THE FIRST LAYER (INPUT -> HIDDEN)
        # ----------------------------------------------------------------------
        # W1 is the weight matrix connecting input to hidden layer.
        # Shape: (input_size, hidden_size)
        # Why this shape?
        #   Every input neuron connects to every hidden neuron.
        #   If we have 2 inputs and 8 hidden neurons, we need 2 * 8 = 16 connections.
        #   We arrange them in a matrix so we can do matrix multiplication.
        #
        # We initialize with small random numbers.
        # Why random?
        #   If all weights started at 0, every neuron would learn the exact same thing.
        #   Randomness breaks the symmetry so neurons specialize.
        # Why small?
        #   Big random numbers would create huge outputs, making learning unstable.
        self.W1 = np.random.randn(input_size, hidden_size) * 0.01

        # b1 is the bias for the hidden layer.
        # Shape: (1, hidden_size)
        # Bias is like an "adjustment knob" for each neuron.
        # It lets the neuron activate even when all inputs are zero.
        self.b1 = np.zeros((1, hidden_size))

        # ----------------------------------------------------------------------
        # WEIGHTS AND BIASES FOR THE SECOND LAYER (HIDDEN -> OUTPUT)
        # ----------------------------------------------------------------------
        # W2 connects the hidden layer to the output layer.
        # Shape: (hidden_size, num_classes)
        # Every hidden neuron connects to every output neuron.
        # If 8 hidden and 3 classes, that's 8 * 3 = 24 weights.
        self.W2 = np.random.randn(hidden_size, num_classes) * 0.01

        # b2 is the bias for the output layer.
        # Shape: (1, num_classes)
        # Each output class gets its own bias.
        self.b2 = np.zeros((1, num_classes))

    def forward(self, X):
        """
        Push data through the network from input to output.
        This is called "forward" because we move forward through the layers.

        Parameters:
            X: Input data of shape (n_samples, input_size).
               Each row is one point. Each column is one feature.

        Returns:
            prob: The predicted probabilities for each class (after softmax).
            a1:   The activations of the hidden layer (needed for backprop).
            z1:   The raw scores of the hidden layer (needed for backprop).
        """

        # ----------------------------------------------------------------------
        # LAYER 1: INPUT TO HIDDEN
        # ----------------------------------------------------------------------
        # Matrix multiplication: X @ W1
        #   X has shape (n_samples, input_size)
        #   W1 has shape (input_size, hidden_size)
        #   Result has shape (n_samples, hidden_size)
        # Each row now contains the weighted sum of inputs for each hidden neuron.
        z1 = X @ self.W1 + self.b1
        # We add b1 (bias). NumPy "broadcasts" the bias across all rows automatically.

        # Apply the ReLU activation function.
        # ReLU stands for "Rectified Linear Unit."
        # It is the simplest non-linear function: f(x) = max(0, x)
        # If a number is negative, make it 0.
        # If a number is positive, leave it alone.
        # Why do we need non-linearity?
        #   Without it, no matter how many layers we stack, the whole network
        #   would just be one big linear equation. It could only draw straight lines.
        #   ReLU lets us draw curves and complex shapes, which we NEED for spirals.
        a1 = np.maximum(0, z1)

        # ----------------------------------------------------------------------
        # LAYER 2: HIDDEN TO OUTPUT
        # ----------------------------------------------------------------------
        # Multiply hidden activations by W2 and add bias b2.
        #   a1 has shape (n_samples, hidden_size)
        #   W2 has shape (hidden_size, num_classes)
        #   Result has shape (n_samples, num_classes)
        # This means EACH SAMPLE now has ONE SCORE PER CLASS.
        # Row 1 might be: [2.5, -1.0, 0.3]
        # This means the model thinks sample 1 is most like class 0.
        z2 = a1 @ self.W2 + self.b2

        # Apply softmax to turn raw scores into probabilities.
        # Before softmax: scores can be any number (positive, negative, huge, tiny).
        # After softmax: each row sums to 1.0, every number is between 0 and 1.
        prob = softmax(z2)

        # We return prob (the final answer), a1 (hidden activations), and z1 (hidden raw scores).
        # a1 and z1 are needed later to calculate gradients.
        return prob, a1, z1

    def compute_loss(self, prob, y_one_hot):
        """
        Calculate how wrong our predictions are.
        We use "categorical cross-entropy" loss.

        What is cross-entropy?
        ----------------------
        It measures the distance between two probability distributions:
          1. The TRUE distribution (our one-hot labels)
          2. The PREDICTED distribution (our softmax probabilities)

        If the model is 100% confident and CORRECT, loss = 0.
        If the model is 100% confident and WRONG, loss = infinity.
        (We clip probabilities to avoid actual infinity.)

        Parameters:
            prob:       Predicted probabilities of shape (n_samples, num_classes).
            y_one_hot:  True labels in one-hot form, same shape.

        Returns:
            A single number representing the average loss across all samples.
        """

        # ----------------------------------------------------------------------
        # NUMERICAL SAFETY: CLIP PROBABILITIES
        # ----------------------------------------------------------------------
        # Log(0) is negative infinity.
        # If our model ever predicts probability 0 for the correct class,
        # taking the log would give -inf, which breaks everything.
        # So we clip probabilities to be at least 1e-8 (0.00000001)
        # and at most 1 - 1e-8.
        # This is a tiny adjustment that prevents crashes.
        epsilon = 1e-8
        prob = np.clip(prob, epsilon, 1 - epsilon)

        # ----------------------------------------------------------------------
        # THE CATEGORICAL CROSS-ENTROPY FORMULA
        # ----------------------------------------------------------------------
        # Step 1: Take the natural logarithm (ln) of every predicted probability.
        #         ln transforms probabilities into "surprise" values.
        #         High probability -> low surprise (small negative number)
        #         Low probability  -> high surprise (big negative number)
        #
        # Step 2: Multiply by the one-hot true labels.
        #         Because one-hot has 0s everywhere except the correct class,
        #         ONLY the log-probability of the CORRECT CLASS survives.
        #         Everything else becomes 0.
        #
        # Step 3: Sum across classes (axis=1).
        #         Each row now has one number: the negative log-likelihood of the correct class.
        #
        # Step 4: Take the mean across all samples.
        #         This gives us the average "surprise" per sample.
        #
        # We put a negative sign in front because log of a probability is negative,
        # and we want loss to be POSITIVE (easier to think about).
        # ----------------------------------------------------------------------
        loss = -np.mean(np.sum(y_one_hot * np.log(prob), axis=1))

        return loss

    def backward(self, X, y_one_hot, prob, a1, z1):
        """
        Backpropagation: figure out which weights are responsible for the error.
        
        We work BACKWARD from the output to the input,
        calculating how much each weight contributed to the mistake.
        This is just the chain rule from calculus, but we do it step by step.

        Parameters:
            X:          Input data, shape (n_samples, input_size).
            y_one_hot:  True labels in one-hot form.
            prob:       Predicted probabilities from forward().
            a1:         Hidden layer activations from forward().
            z1:         Hidden layer raw scores from forward().

        Returns:
            dW1, db1: Gradients for the first layer weights and biases.
            dW2, db2: Gradients for the second layer weights and biases.
        """

        # Get the number of samples. We divide by this to get the AVERAGE gradient.
        n = X.shape[0]

        # ----------------------------------------------------------------------
        # OUTPUT LAYER GRADIENT
        # ----------------------------------------------------------------------
        # Here is one of the most beautiful results in all of deep learning:
        #
        # When you combine SOFTMAX with CATEGORICAL CROSS-ENTROPY,
        # the gradient simplifies to: (prediction - target) / n
        #
        # Why is this beautiful?
        #   Normally, the chain rule for softmax + cross-entropy is complicated.
        #   But all the messy terms CANCEL OUT, leaving just (prob - y_one_hot).
        #
        # What does this mean intuitively?
        #   If we predict [0.9, 0.05, 0.05] and truth is [1, 0, 0],
        #   The error is [0.9-1, 0.05-0, 0.05-0] = [-0.1, 0.05, 0.05]
        #   The negative sign for the correct class says "predict MORE for class 0."
        #   The positive signs for wrong classes say "predict LESS for classes 1 and 2."
        #   The size of the number tells us HOW MUCH to adjust.
        #
        # We divide by n to get the average error per sample.
        # This makes the gradient stable regardless of batch size.
        # ----------------------------------------------------------------------
        output_error = (prob - y_one_hot) / n

        # ----------------------------------------------------------------------
        # GRADIENTS FOR W2 AND b2 (SECOND LAYER)
        # ----------------------------------------------------------------------
        # To find how W2 should change, we multiply the hidden activations (a1)
        # by the output error.
        #
        # Why a1.T @ output_error?
        #   a1.T has shape (hidden_size, n_samples)
        #   output_error has shape (n_samples, num_classes)
        #   Result has shape (hidden_size, num_classes) -> same as W2!
        #
        # Intuition: each weight in W2 connects one hidden neuron to one output.
        # If a hidden neuron was very active (high a1) AND the output was wrong,
        # that connection should change a lot.
        dW2 = a1.T @ output_error

        # For the bias, we just sum the error across all samples.
        # Bias is the same for every sample, so its gradient is the total error.
        db2 = np.sum(output_error, axis=0, keepdims=True)
        # keepdims=True keeps the shape as (1, num_classes) instead of flattening.

        # ----------------------------------------------------------------------
        # BACKPROPAGATE ERROR TO HIDDEN LAYER
        # ----------------------------------------------------------------------
        # We need to know how much each hidden neuron contributed to the output error.
        # We do this by sending the error backward through W2.
        #
        # output_error has shape (n_samples, num_classes)
        # W2.T has shape (num_classes, hidden_size)
        # Result has shape (n_samples, hidden_size)
        #
        # This tells us: "For each sample, how wrong was each hidden neuron?"
        hidden_error = output_error @ self.W2.T

        # ----------------------------------------------------------------------
        # RELU GRADIENT
        # ----------------------------------------------------------------------
        # ReLU is: f(x) = max(0, x)
        # Its derivative is:
        #   If x > 0: derivative = 1 (pass the error through unchanged)
        #   If x <= 0: derivative = 0 (block the error completely)
        #
        # We check which z1 values are positive.
        # (z1 > 0) gives True/False. We convert to 1.0/0.0 with astype(float).
        # Then we multiply element-wise: error only flows where ReLU was "open."
        # ----------------------------------------------------------------------
        dz1 = hidden_error * (z1 > 0).astype(float)

        # ----------------------------------------------------------------------
        # GRADIENTS FOR W1 AND b1 (FIRST LAYER)
        # ----------------------------------------------------------------------
        # Same logic as W2, but now using X (the input) instead of a1.
        # X.T has shape (input_size, n_samples)
        # dz1 has shape (n_samples, hidden_size)
        # dW1 has shape (input_size, hidden_size) -> same as W1!
        dW1 = X.T @ dz1

        # Bias gradient is the sum of dz1 across all samples.
        db1 = np.sum(dz1, axis=0, keepdims=True)

        return dW1, db1, dW2, db2

    def train(self, X, y_one_hot, learning_rate, iterations):
        """
        Train the network using gradient descent.
        
        Gradient descent is like walking down a mountain in the fog.
        You can't see the bottom, but you can feel which way is downhill.
        The gradient tells us which way is uphill, so we walk the opposite direction.

        Parameters:
            X:              Input data.
            y_one_hot:      True labels in one-hot form.
            learning_rate:  How big of a step we take downhill.
                            Too small = takes forever.
                            Too big = we might fall off the cliff (diverge).
            iterations:     How many times we update the weights.
        """

        # Loop many times. Each loop is one "step" downhill.
        for i in range(iterations):

            # ------------------------------------------------------------------
            # FORWARD PASS: make predictions with current weights
            # ------------------------------------------------------------------
            prob, a1, z1 = self.forward(X)

            # ------------------------------------------------------------------
            # COMPUTE LOSS: measure how wrong we are
            # ------------------------------------------------------------------
            loss = self.compute_loss(prob, y_one_hot)

            # ------------------------------------------------------------------
            # BACKWARD PASS: calculate gradients
            # ------------------------------------------------------------------
            dW1, db1, dW2, db2 = self.backward(X, y_one_hot, prob, a1, z1)

            # ------------------------------------------------------------------
            # UPDATE WEIGHTS: take a step downhill
            # ------------------------------------------------------------------
            # The gradient points uphill (toward more loss).
            # We subtract the gradient to move downhill (toward less loss).
            # We multiply by learning_rate to control step size.
            self.W1 -= learning_rate * dW1
            self.b1 -= learning_rate * db1
            self.W2 -= learning_rate * dW2
            self.b2 -= learning_rate * db2

            # ------------------------------------------------------------------
            # PRINT PROGRESS
            # ------------------------------------------------------------------
            # Every 1000 iterations, print the loss so we can see improvement.
            if i % 1000 == 0:
                print(f"  Iteration {i:5d}: Loss = {loss:.4f}")
                # :5d means integer with 5 digits of padding.
                # :.4f means float with 4 decimal places.

    def predict(self, X):
        """
        Use the trained model to predict classes for new data.

        Parameters:
            X: Input data of shape (n_samples, input_size).

        Returns:
            An array of predicted class labels (0, 1, or 2).
        """

        # Run forward pass to get probabilities.
        prob, _, _ = self.forward(X)

        # np.argmax finds the POSITION of the highest number in each row.
        # axis=1 means "look across the columns."
        # Example:
        #   prob = [[0.1, 0.8, 0.1],
        #           [0.7, 0.2, 0.1]]
        #   argmax -> [1, 0]
        #   That means sample 0 is predicted class 1, sample 1 is predicted class 0.
        # The position IS the class label. That's why argmax works perfectly here.
        return np.argmax(prob, axis=1)


# ==============================================================================
# STEP 4: MAIN SCRIPT
# ==============================================================================

if __name__ == "__main__":
    # This block only runs when we execute the script directly.
    # It won't run if we import this file as a module in another script.

    # ==========================================================================
    # PART A: GENERATE SPIRAL DATA
    # ==========================================================================
    # We are going to create fake data: three intertwined spirals.
    # Why spirals?
    #   Because spirals are NOT linearly separable.
    #   You cannot draw a straight line to separate them.
    #   This forces our neural network to learn something non-trivial.
    #   If we used blobs, a simple line would work, and we wouldn't need a network.

    # Set the random seed so the random numbers are the same every time.
    # This makes the experiment reproducible.
    np.random.seed(42)

    # How many points per spiral.
    n_points = 100

    # How many spirals (classes) we want.
    n_classes = 3

    # Lists to hold our data before we combine them.
    X_list = []  # Will hold coordinate pairs [x1, x2]
    y_list = []  # Will hold class labels (0, 1, 2)

    # Loop over each class to generate one spiral at a time.
    for class_id in range(n_classes):

        # ---------------------------------------------------------------------
        # SPIRAL MATH (Don't worry, it's just polar coordinates!)
        # ---------------------------------------------------------------------
        # r is the radius. It goes from 0 to 1 linearly.
        # This means points start at the center and move outward.
        r = np.linspace(0, 1, n_points)

        # t is the angle (theta).
        # Each spiral gets a different starting angle.
        # Class 0 starts at angle 0, class 1 starts at angle 4, class 2 starts at angle 8.
        # They each sweep through 4 radians of angle.
        # We add random noise (np.random.randn * 0.2) to make the spiral fuzzy.
        # Without noise, the spirals would be perfect lines and too easy to classify.
        t = np.linspace(class_id * 4, (class_id + 1) * 4, n_points) + np.random.randn(n_points) * 0.2

        # Convert polar coordinates (r, t) to Cartesian coordinates (x1, x2).
        # x = r * sin(theta)
        # y = r * cos(theta)
        # The "* 2.0" makes the spirals twist twice as much (tighter spirals).
        x1 = r * np.sin(t * 2.0)
        x2 = r * np.cos(t * 2.0)

        # Stack x1 and x2 side by side into columns.
        # Result shape: (n_points, 2)
        # Each row is one point: [x1, x2]
        X_list.append(np.column_stack([x1, x2]))

        # Create labels: every point in this spiral gets the same class_id.
        # np.full(n_points, class_id) creates [class_id, class_id, ..., class_id].
        y_list.append(np.full(n_points, class_id))

    # Combine all spirals into one big dataset.
    # np.vstack stacks arrays vertically (one on top of the other).
    # Final X shape: (n_points * n_classes, 2) = (300, 2)
    X = np.vstack(X_list)

    # np.hstack stacks arrays horizontally (side by side).
    # Then reshape into a column vector with shape (300, 1).
    y = np.hstack(y_list).reshape(-1, 1)

    # Print some info so the user knows what we made.
    print("=" * 60)
    print("GENERATED SPIRAL DATA")
    print("=" * 60)
    print(f"Total samples: {X.shape[0]}")
    print(f"Features per sample: {X.shape[1]} (x and y coordinates)")
    print(f"Number of classes: {n_classes}")
    print("We created 3 intertwined spirals. No straight line can separate them.")
    print()

    # ==========================================================================
    # PART B: ONE-HOT ENCODE THE LABELS
    # ==========================================================================
    # Our model outputs probabilities for each class.
    # To compare outputs to labels, labels must be in the same format.
    # One-hot encoding converts 0, 1, 2 into [1,0,0], [0,1,0], [0,0,1].
    y_one_hot = one_hot(y, n_classes)

    print("=" * 60)
    print("ONE-HOT ENCODING")
    print("=" * 60)
    print("Example: label 0 becomes [1. 0. 0.]")
    print("         label 1 becomes [0. 1. 0.]")
    print("         label 2 becomes [0. 0. 1.]")
    print(f"One-hot matrix shape: {y_one_hot.shape}")
    print()

    # ==========================================================================
    # PART C: CREATE AND TRAIN THE MODEL
    # ==========================================================================
    # We create a neural network with:
    #   - 2 inputs (x, y coordinates)
    #   - 8 hidden neurons (enough to learn curves, but not too many)
    #   - 3 outputs (one score per spiral class)
    #
    # Why 8 hidden neurons?
    #   Spirals are curved. A single straight line cannot separate them.
    #   With only 2 or 3 hidden neurons, the network might struggle.
    #   With 8, it has enough "brain power" to learn the curves.
    #   More neurons = more capacity, but also more risk of overfitting.

    model = MultiClassClassifier(input_size=2, hidden_size=8, num_classes=n_classes)

    # learning_rate = 0.5 means we take fairly big steps.
    # For this simple problem, a bigger learning rate converges fast.
    learning_rate = 0.5

    # 10,000 iterations is plenty for this small dataset.
    iterations = 10000

    print("=" * 60)
    print("TRAINING")
    print("=" * 60)
    print("Training multi-class classifier on spiral data...")
    print("Architecture: 2 inputs -> 8 hidden (ReLU) -> 3 outputs (Softmax)")
    print()

    # Train the model!
    model.train(X, y_one_hot, learning_rate, iterations)

    print()

    # ==========================================================================
    # PART D: EVALUATE THE MODEL
    # ==========================================================================
    # Use the trained model to predict classes for ALL our data points.
    predictions = model.predict(X)

    # Calculate accuracy: what percentage did we get right?
    # y.flatten() turns the column vector into a flat array so shapes match.
    # predictions == y.flatten() gives True/False for each sample.
    # np.mean() treats True as 1 and False as 0, giving the fraction correct.
    accuracy = np.mean(predictions == y.flatten()) * 100

    print("=" * 60)
    print("EVALUATION")
    print("=" * 60)
    print(f"Final Accuracy: {accuracy:.2f}%")
    print()

    # Show a simple confusion breakdown per class.
    # For each true class, count how many were predicted as each class.
    print("Confusion breakdown (True Class -> Predicted Class):")
    for true_class in range(n_classes):
        # Find all samples that actually belong to this class.
        mask = (y.flatten() == true_class)
        # Of those, what did we predict?
        preds_for_this_class = predictions[mask]
        # Count correct predictions.
        correct = np.sum(preds_for_this_class == true_class)
        total = np.sum(mask)
        print(f"  Class {true_class}: {correct}/{total} correct")
    print()

    # ==========================================================================
    # PART E: VISUALIZE THE DECISION BOUNDARIES
    # ==========================================================================
    # We will create a dense grid of points covering the data range.
    # For each grid point, we predict which class the model thinks it belongs to.
    # Then we color the grid by predicted class.
    # This shows us the "decision regions" of our model.

    print("=" * 60)
    print("VISUALIZATION")
    print("=" * 60)
    print("Drawing decision boundaries...")
    print()

    # Determine the range of our data.
    # We add a little padding (±0.5) so the edges look nice.
    x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5

    # Create a grid of points.
    # h is the step size. Smaller = smoother but slower.
    h = 0.02
    # np.arange generates numbers from x_min to x_max, stepping by h.
    # np.meshgrid turns two 1D arrays into two 2D grids.
    # xx and yy are the x and y coordinates of every grid point.
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))

    # Flatten the grids into lists of points.
    # np.c_ stacks columns side by side.
    # Result shape: (n_grid_points, 2)
    grid_points = np.c_[xx.ravel(), yy.ravel()]

    # Predict the class for every point on the grid.
    grid_predictions = model.predict(grid_points)

    # Reshape the predictions back into the shape of the grid.
    # This lets us use plt.contourf to draw colored regions.
    grid_predictions = grid_predictions.reshape(xx.shape)

    # Create the plot.
    plt.figure(figsize=(10, 8))
    # figsize=(10, 8) makes the figure 10 inches wide and 8 inches tall.

    # Draw the decision regions.
    # contourf fills the space between contour lines with colors.
    # alpha=0.3 makes the colors semi-transparent so we can see the data points on top.
    # cmap=plt.cm.Spectral gives us a nice multi-color palette.
    plt.contourf(xx, yy, grid_predictions, alpha=0.3, cmap=plt.cm.Spectral)

    # Define colors and markers for each class.
    # We use a list so we can loop over classes easily.
    colors = ['red', 'green', 'blue']
    markers = ['o', 's', '^']
    labels = ['Class 0', 'Class 1', 'Class 2']

    # Plot the actual data points on top of the decision regions.
    for class_id in range(n_classes):
        # Select only the points that belong to this class.
        idx = (y.flatten() == class_id)
        # Plot them with a specific color and marker shape.
        plt.scatter(X[idx, 0], X[idx, 1],
                    c=colors[class_id],
                    marker=markers[class_id],
                    edgecolors='black',
                    s=50,
                    label=labels[class_id])
        # edgecolors='black' puts a black outline around each point.
        # s=50 controls the size of the points.

    # Add labels and title.
    plt.title("Multi-Class Classification: 3 Spirals", fontsize=16)
    plt.xlabel("x1 (first feature)", fontsize=12)
    plt.ylabel("x2 (second feature)", fontsize=12)

    # Add a legend so the viewer knows which color is which class.
    plt.legend(fontsize=12)

    # Show the plot.
    plt.show()

    # ==========================================================================
    # PART F: SUMMARY
    # ==========================================================================
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("We built a network that classifies points into 3 categories.")
    print("Softmax turns scores into probabilities that sum to 1.")
    print("Categorical cross-entropy measures wrongness across all classes.")
    print("One-hot encoding lets us represent class labels as vectors.")
    print("The colored regions show where the model predicts each class.")
    print("=" * 60)
