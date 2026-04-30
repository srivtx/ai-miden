#!/usr/bin/env python3
"""
================================================================================
Phase 5: Binary Classification with a Simple Neural Network
================================================================================

This script is designed for a COMPLETE BEGINNER with zero AI/ML knowledge.
You only need basic algebra to understand this.

We will build a tiny neural network that learns to answer YES/NO questions.
For example: "Given the coordinates of a point, is it in the BLUE group?"

Every line has a comment. Read it like a story.
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

# NumPy is a library for doing math with lists of numbers (called "arrays").
# It makes matrix multiplication fast and easy.
import numpy as np

# Matplotlib is a plotting library. Think of it as "Microsoft Excel for Python."
# It lets us draw graphs, charts, and visualizations so we can SEE what our
# model is doing instead of just staring at numbers.
import matplotlib.pyplot as plt


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def sigmoid(z):
    """
    The sigmoid function takes ANY number and squeezes it into 0 to 1.

    WHY: Neural networks compute weighted sums which can be huge or tiny.
    But for YES/NO questions, we need a PROBABILITY between 0 and 1.
    Sigmoid is the bridge.

    Formula: sigmoid(z) = 1 / (1 + e^(-z))

    If z is very positive: e^(-z) is tiny, so sigmoid ≈ 1 (YES)
    If z is very negative: e^(-z) is huge, so sigmoid ≈ 0 (NO)
    If z = 0: sigmoid = 0.5 (exactly 50/50)

    Example:
        sigmoid(5)   ≈ 0.993  (very confident YES)
        sigmoid(-5)  ≈ 0.007  (very confident NO)
        sigmoid(0)   =  0.5   (completely unsure)
    """
    return 1 / (1 + np.exp(-z))


def sigmoid_derivative(z):
    """
    The derivative of sigmoid.

    WHY: During backpropagation, we need to know how sensitive the sigmoid
    output is to its input. This tells us how much to adjust the weights.

    The derivative of sigmoid(z) is: sigmoid(z) * (1 - sigmoid(z))
    This is a beautiful property that makes the math simple.

    What does "derivative" mean in plain English?
    It means: "If I nudge the input a tiny bit, how much does the output change?"
    If the derivative is large, the output is very sensitive to changes.
    If the derivative is small, the output barely notices changes.
    """
    s = sigmoid(z)
    return s * (1 - s)


# ==============================================================================
# THE NEURAL NETWORK CLASS
# ==============================================================================

class BinaryClassifier:
    """
    A tiny neural network with one hidden layer.

    It learns to answer YES/NO questions. For example:
    "Given the coordinates of a point, is it in group 1?"

    ARCHITECTURE (think of it like a factory assembly line):

        INPUT (2 numbers: x, y)
          |
          v
        HIDDEN LAYER (4 neurons with ReLU activation)
          |
          v
        OUTPUT (1 neuron with sigmoid activation)
          |
          v
        PROBABILITY (0 to 1)

    Why a hidden layer?
    Without it, the model could only draw straight lines.
    With it, the model can draw curved, bent decision boundaries.
    """

    def __init__(self, input_size, hidden_size):
        """
        Create weight matrices and bias vectors.

        PARAMETERS:
            input_size  = how many numbers the model sees at once.
                          Here: 2 (the x-coordinate and y-coordinate of a point).

            hidden_size = how many neurons in the hidden middle layer.
                          Here: 4. More neurons = more capacity to learn,
                          but also more computation.

        SHAPES EXPLAINED:
            W1 shape: (input_size, hidden_size) = (2, 4)
                Each of the 2 inputs connects to each of the 4 hidden neurons.
                Think of W1 as a table of 2 rows and 4 columns.
                W1[0, 2] = how much input 0 influences hidden neuron 2.

            b1 shape: (1, hidden_size) = (1, 4)
                Each hidden neuron gets its own bias (an extra knob to tweak).
                Bias lets the neuron shift its activation up or down
                regardless of the input.

            W2 shape: (hidden_size, 1) = (4, 1)
                Each of the 4 hidden neurons connects to the single output neuron.

            b2 shape: (1, 1)
                The output neuron gets one bias.

        WHY SMALL RANDOM VALUES?
            If all weights start at ZERO, every hidden neuron computes the exact
            same thing. They would all update identically during training, and
            the network would be no better than having just ONE neuron.
            This is called the "symmetry problem."

            Small random values BREAK that symmetry so each neuron can
            specialize and learn something different.

            WHY SMALL (multiply by 0.1)?
            If weights are too large, the sigmoid gets saturated (stuck near 0 or 1),
            and the gradients become tiny. The network stops learning.
            Small weights keep the network in the "learning zone" initially.
        """
        # W1: weights from input layer to hidden layer.
        # np.random.randn gives numbers from a normal distribution (bell curve).
        # Multiplying by 0.1 makes them small.
        self.W1 = np.random.randn(input_size, hidden_size) * 0.1

        # b1: biases for the hidden layer.
        # Bias is like the "default mood" of a neuron before it sees any input.
        self.b1 = np.random.randn(1, hidden_size) * 0.1

        # W2: weights from hidden layer to output layer.
        self.W2 = np.random.randn(hidden_size, 1) * 0.1

        # b2: bias for the output layer.
        self.b2 = np.random.randn(1, 1) * 0.1

    def forward(self, X):
        """
        Pass data through the network to get a prediction.

        This is called "forward" because data flows forward from input to output.
        It is like an assembly line: each step transforms the data a little.

        PARAMETERS:
            X = input data, shape: (n_samples, input_size)
                n_samples = how many examples we are processing at once.
                input_size = how many numbers describe each example (here: 2).

        RETURNS:
            prob = predicted probability of class 1 (YES), shape: (n_samples, 1)
            a1   = hidden layer activations (needed later for backprop)
            z1   = hidden layer raw scores (needed later for ReLU derivative)
        """
        # ----------------------------------------------------------------------
        # STEP 1: Compute hidden layer raw scores.
        # ----------------------------------------------------------------------
        # z1 = X @ W1 + b1
        #
        # The "@" symbol means MATRIX MULTIPLICATION.
        # Think of it as: for every sample, take a weighted sum of inputs.
        #
        # Example with one sample [x, y]:
        #   z1[0] = x * W1[0,0] + y * W1[1,0] + b1[0]
        #   z1[1] = x * W1[0,1] + y * W1[1,1] + b1[1]
        #   ... and so on for all 4 hidden neurons.
        #
        # W1 contains the "importance" of each input for each neuron.
        # If W1[0,2] is large and positive, input 0 strongly pushes neuron 2 UP.
        # If W1[0,2] is large and negative, input 0 strongly pushes neuron 2 DOWN.
        z1 = X @ self.W1 + self.b1

        # ----------------------------------------------------------------------
        # STEP 2: Apply ReLU activation.
        # ----------------------------------------------------------------------
        # a1 = np.maximum(0, z1)
        #
        # ReLU stands for "Rectified Linear Unit."
        # It is the simplest non-linear function:
        #   If the number is positive, keep it.
        #   If the number is negative, make it zero.
        #
        # WHY DO WE NEED NON-LINEARITY?
        # Without ReLU (or some other non-linear function), stacking layers
        # would just be fancy matrix multiplication. Multiple linear layers
        # collapse into a single linear layer. The network could ONLY draw
        # straight lines. It could never learn curved or bent boundaries.
        #
        # ReLU adds a "bend" to the line. With enough bends, the network
        # can approximate ANY shape. This is the secret sauce of deep learning.
        a1 = np.maximum(0, z1)

        # ----------------------------------------------------------------------
        # STEP 3: Compute output layer raw score.
        # ----------------------------------------------------------------------
        # z2 = a1 @ W2 + b2
        #
        # Now we take the activated hidden values and combine them into
        # ONE final number (the output). Each hidden neuron "votes" via W2.
        # W2[2,0] = how much hidden neuron 2 influences the final output.
        z2 = a1 @ self.W2 + self.b2

        # ----------------------------------------------------------------------
        # STEP 4: Squash to probability using sigmoid.
        # ----------------------------------------------------------------------
        # prob = sigmoid(z2)
        #
        # z2 could be any number: -1000, 0, +1000.
        # But we need a PROBABILITY between 0 and 1.
        # Sigmoid does the squeezing.
        prob = sigmoid(z2)

        # Return everything we need.
        # We return a1 and z1 because backward propagation needs them.
        return prob, a1, z1

    def compute_loss(self, prob, y_true):
        """
        Compute Binary Cross-Entropy (BCE) loss.

        WHY DO WE NEED LOSS?
        Loss is a single number that tells us "how wrong are we?"
        If loss is high, our predictions are terrible.
        If loss is low, our predictions are good.
        Training means: adjust the weights to make this number as SMALL as possible.

        WHY BINARY CROSS-ENTROPY INSTEAD OF MEAN SQUARED ERROR (MSE)?
        MSE is great for regression (predicting continuous values like house prices).
        But for CLASSIFICATION (YES/NO), MSE has a problem:

        When the model is very confident but WRONG (e.g., predicts 0.99 when
        the true answer is 0), MSE gives a loss of about 1.0.
        But BCE gives a HUGE loss (approaching infinity). This huge penalty
        forces the model to fix its confidence quickly.

        BCE is designed specifically for probabilities. It uses logarithms,
        which have a beautiful property: log(1) = 0 and log(near 0) = -infinity.
        This means being confidently wrong is punished SEVERELY.

        THE FORMULA IN WORDS:
            For each sample:
                If true answer is YES (y=1): we want prob close to 1.
                    If prob is 1, log(prob) = 0, so we pay NO penalty.
                    If prob is 0.01, log(0.01) = -4.6, so we pay a BIG penalty.

                If true answer is NO (y=0): we want prob close to 0.
                    If prob is 0, log(1 - prob) = 0, so we pay NO penalty.
                    If prob is 0.99, log(0.01) = -4.6, so we pay a BIG penalty.

            We add the penalties for all samples, take the negative
            (so that LOWER loss is BETTER), and average.

        THE FORMULA IN MATH:
            loss = -mean( y_true * log(prob) + (1 - y_true) * log(1 - prob) )
        """
        # log(0) is mathematically undefined (it is negative infinity).
        # In computers, log(0) crashes with a warning or error.
        # We add a tiny number (epsilon) to prevent this.
        epsilon = 1e-8

        # Clip probabilities so they are never exactly 0 or exactly 1.
        # This is a safety net. Even if the model is 100% confident,
        # we pretend it is 99.999999% confident to avoid log(0).
        prob = np.clip(prob, epsilon, 1 - epsilon)

        # Compute the loss using the BCE formula.
        # y_true * np.log(prob) handles the YES cases.
        # (1 - y_true) * np.log(1 - prob) handles the NO cases.
        # Only one of these two terms is active for each sample.
        loss = -np.mean(y_true * np.log(prob) + (1 - y_true) * np.log(1 - prob))
        return loss

    def backward(self, X, y_true, prob, a1, z1):
        """
        Backpropagation: trace the blame backward through the network.

        WHAT IS BACKPROPAGATION?
        We just computed the loss: "how wrong are we?"
        Now we need to know: "WHICH weights caused the mistake, and by how much?"
        Backpropagation is the algorithm that answers this.

        It uses the CHAIN RULE from calculus.
        The chain rule says: if A affects B, and B affects C,
        then the effect of A on C = (effect of A on B) * (effect of B on C).

        Think of it like a row of dominoes.
        The final domino is the LOSS.
        We know the last domino fell. We walk backward and ask:
        "Which domino pushed it, and how hard?"

        PARAMETERS:
            X      = input data, shape (n_samples, input_size)
            y_true = true labels, shape (n_samples, 1)
            prob   = predicted probabilities from forward pass, shape (n_samples, 1)
            a1     = hidden activations from forward pass, shape (n_samples, hidden_size)
            z1     = hidden raw scores from forward pass, shape (n_samples, hidden_size)

        RETURNS:
            dW1, db1, dW2, db2 = gradients (directions to nudge each parameter)
        """
        # n = number of examples we are processing.
        # We divide by n later so our gradients are AVERAGES.
        # This makes the learning rate stable regardless of dataset size.
        n = X.shape[0]

        # ==================================================================
        # OUTPUT LAYER GRADIENTS
        # ==================================================================

        # Step 1: Compute the error at the output.
        # output_error = prob - y_true
        #
        # This is the DERIVATIVE of the loss with respect to z2.
        # It tells us: "How much higher or lower should z2 be?"
        #
        # If prob = 0.9 and y_true = 1, error = -0.1.
        #   This means our prediction is a bit TOO HIGH. We need to lower z2.
        # If prob = 0.2 and y_true = 1, error = -0.8.
        #   This means our prediction is WAY TOO LOW. We need to raise z2 a lot.
        # If prob = 0.5 and y_true = 0, error = 0.5.
        #   This means our prediction is TOO HIGH. We need to lower z2.
        #
        # This simple formula (prob - y_true) is a beautiful shortcut.
        # It combines the derivative of BCE and the derivative of sigmoid.
        output_error = prob - y_true  # shape: (n_samples, 1)

        # Step 2: Compute gradient for W2.
        # dW2 = a1.T @ output_error / n
        #
        # W2 connects hidden activations (a1) to the output.
        # To find how much W2 contributed to the error, we look at:
        #   1. How active each hidden neuron was (a1)
        #   2. How wrong the output was (output_error)
        #
        # The "@" does a matrix multiplication. a1.T is the transpose of a1.
        # We transpose a1 so the shapes line up for multiplication.
        # Dividing by n gives us the AVERAGE gradient per sample.
        dW2 = a1.T @ output_error / n

        # Step 3: Compute gradient for b2.
        # db2 = sum(output_error, axis=0) / n
        #
        # Bias affects every sample equally.
        # If the output is too high for ALL samples, we need to lower b2.
        # We simply average the errors across all samples.
        # keepdims=True keeps the shape as (1, 1) instead of flattening to ().
        db2 = np.sum(output_error, axis=0, keepdims=True) / n

        # ==================================================================
        # HIDDEN LAYER GRADIENTS
        # ==================================================================

        # Step 4: Send the error backward through W2 to the hidden layer.
        # hidden_error = output_error @ W2.T
        #
        # The output neuron blames the hidden neurons for its mistake.
        # W2.T tells us "how much blame does each hidden neuron receive?"
        # If W2[2,0] is large, hidden neuron 2 receives a lot of blame.
        hidden_error = output_error @ self.W2.T  # shape: (n_samples, hidden_size)

        # Step 5: Apply the ReLU derivative.
        # dz1 = hidden_error * (z1 > 0)
        #
        # ReLU's derivative is simple:
        #   If z1 > 0: derivative = 1 (gradient passes through unchanged)
        #   If z1 <= 0: derivative = 0 (gradient is blocked)
        #
        # WHY DOES THIS MAKE SENSE?
        # If a ReLU neuron was "dead" (outputting 0), it did not influence
        # the output at all. Therefore, it deserves NO blame.
        # If a ReLU neuron was active (outputting a positive number), it DID
        # influence the output, so it receives full blame.
        #
        # (z1 > 0) gives True/False. We multiply by hidden_error.
        # In NumPy, True acts like 1 and False acts like 0 in multiplication.
        dz1 = hidden_error * (z1 > 0).astype(float)

        # Step 6: Compute gradient for W1.
        # dW1 = X.T @ dz1 / n
        #
        # W1 connects inputs (X) to hidden neurons.
        # To find how much W1 contributed to the error, we look at:
        #   1. The input values (X)
        #   2. The blame that reached the hidden layer (dz1)
        #
        # If input x was large AND the hidden neuron got a lot of blame,
        # then the weight connecting x to that neuron needs a big update.
        dW1 = X.T @ dz1 / n

        # Step 7: Compute gradient for b1.
        # db1 = sum(dz1, axis=0) / n
        #
        # Same logic as db2: average the blame across all samples.
        db1 = np.sum(dz1, axis=0, keepdims=True) / n

        # Return all four gradients.
        # These tell us exactly how to adjust each parameter to reduce loss.
        return dW1, db1, dW2, db2

    def train(self, X, y_true, learning_rate, iterations):
        """
        Train the model by repeating forward + backward + update.

        This is GRADIENT DESCENT for binary classification.
        Think of loss as a mountain. We want to hike DOWN to the valley
        (the lowest possible loss).
        The gradient tells us which way is UP. So we walk the OPPOSITE way.

        PARAMETERS:
            X             = input data
            y_true        = true labels
            learning_rate = how big of a step we take each time.
                            Too big = we overshoot the valley and bounce around.
                            Too small = we take forever to reach the valley.
                            Here we use 0.1, which is a moderate step size.

            iterations    = how many times we repeat the loop.
                            More iterations = more learning, but also more time.
                            Here we use 10000, which is enough for this toy problem.
        """
        # Loop many times. Each loop is called an "epoch" or "iteration."
        for i in range(iterations):
            # ------------------------------------------------------------------
            # 1. FORWARD PASS: Make predictions.
            # ------------------------------------------------------------------
            # We pass the data through the network to get probabilities.
            # We also save a1 and z1 because backward() needs them.
            prob, a1, z1 = self.forward(X)

            # ------------------------------------------------------------------
            # 2. COMPUTE LOSS: Measure how wrong we are.
            # ------------------------------------------------------------------
            # This gives us a single number representing our "badness."
            loss = self.compute_loss(prob, y_true)

            # ------------------------------------------------------------------
            # 3. BACKWARD PASS: Compute gradients (who is to blame?).
            # ------------------------------------------------------------------
            # We trace the error backward through the network.
            # dW1 = how much to change W1
            # db1 = how much to change b1
            # dW2 = how much to change W2
            # db2 = how much to change b2
            dW1, db1, dW2, db2 = self.backward(X, y_true, prob, a1, z1)

            # ------------------------------------------------------------------
            # 4. UPDATE PARAMETERS: Nudge weights in the opposite direction.
            # ------------------------------------------------------------------
            # WHY OPPOSITE?
            # The gradient points in the direction of STEEPEST ASCENT
            # (the direction that INCREASES loss the fastest).
            # We want to DECREASE loss, so we go the opposite way.
            #
            # new_W1 = old_W1 - learning_rate * dW1
            #
            # If dW1 is positive, increasing W1 would increase loss.
            # So we DECREASE W1.
            # If dW1 is negative, increasing W1 would decrease loss.
            # Wait -- if dW1 is negative, then -learning_rate * dW1 is POSITIVE,
            # so we INCREASE W1. Perfect!
            self.W1 -= learning_rate * dW1
            self.b1 -= learning_rate * db1
            self.W2 -= learning_rate * dW2
            self.b2 -= learning_rate * db2

            # ------------------------------------------------------------------
            # 5. PRINT PROGRESS.
            # ------------------------------------------------------------------
            # Every 1000 iterations, print the current loss.
            # This lets us see if the model is learning (loss should go down).
            if i % 1000 == 0:
                print(f"Iteration {i:5d} | Loss: {loss:.4f}")

    def predict(self, X):
        """
        Return 0 or 1 for each input.

        PARAMETERS:
            X = input data, shape (n_samples, input_size)

        RETURNS:
            predictions = 0 or 1 for each sample, shape (n_samples, 1)

        LOGIC:
            prob, _, _ = self.forward(X)
            return (prob >= 0.5).astype(int)

        WHY 0.5?
            Sigmoid outputs 0.5 when the raw score (z2) is exactly 0.
            0.5 is the natural midpoint between 0 and 1.
            If the model is more than 50% confident, we say YES (class 1).
            If the model is less than 50% confident, we say NO (class 0).

        COULD WE USE A DIFFERENT THRESHOLD?
            Yes! In real applications, we might use 0.7 if false positives
            are very bad (e.g., medical diagnosis). Or 0.3 if false negatives
            are very bad (e.g., spam detection).
            But 0.5 is the standard default.
        """
        # Get probabilities from the forward pass.
        prob, _, _ = self.forward(X)

        # Create a boolean array: True where prob >= 0.5, False otherwise.
        # .astype(int) converts True to 1 and False to 0.
        return (prob >= 0.5).astype(int)


# ==============================================================================
# MAIN SCRIPT
# ==============================================================================

if __name__ == "__main__":
    # The code below only runs when we execute this file directly.
    # It does NOT run if we import this file as a module in another script.

    # --------------------------------------------------------------------------
    # PART A: Generate synthetic data
    # --------------------------------------------------------------------------
    # We will create FAKE data so we can test our model.
    # In real life, you would load data from a CSV file or database.
    # But fake data lets us control exactly what is happening.

    # Set a random seed so the random numbers are the SAME every time.
    # This makes our results reproducible.
    # If you run this script 10 times, you will get the exact same points.
    np.random.seed(42)

    # CLASS 0 (NO): points clustered around (0, 0)
    # np.random.randn(50, 2) creates 50 random points with 2 coordinates each.
    # The numbers come from a standard normal distribution (mean=0, std=1).
    # Multiplying by 0.5 makes the cluster tighter (std=0.5).
    # Adding np.array([0, 0]) shifts the center to the origin.
    X0 = np.random.randn(50, 2) * 0.5 + np.array([0, 0])

    # CLASS 1 (YES): points clustered around (3, 3)
    # Same logic, but shifted to (3, 3).
    # The two groups are far apart, so the model SHOULD be able to separate them.
    X1 = np.random.randn(50, 2) * 0.5 + np.array([3, 3])

    # Stack them together vertically.
    # X now has 100 rows (50 from class 0 + 50 from class 1) and 2 columns (x, y).
    X = np.vstack([X0, X1])

    # Create the labels.
    # y is a column vector with 100 rows.
    # The first 50 are 0 (NO), the next 50 are 1 (YES).
    y = np.vstack([np.zeros((50, 1)), np.ones((50, 1))])

    # The model must learn to draw a line (or curve) that separates
    # the red group (class 0) from the blue group (class 1).

    # --------------------------------------------------------------------------
    # PART B: Create and train the model
    # --------------------------------------------------------------------------
    # Create an instance of our BinaryClassifier.
    # input_size = 2 because each point has 2 coordinates (x, y).
    # hidden_size = 4 because we want 4 hidden neurons.
    # 4 is enough for this simple problem. More would also work.
    model = BinaryClassifier(input_size=2, hidden_size=4)

    # learning_rate = 0.1
    # This controls how aggressively we update the weights.
    # 0.1 means: "take 10% of the gradient step."
    # If this were 1.0, we might overshoot and never settle.
    # If this were 0.001, we would learn very slowly.
    learning_rate = 0.1

    # iterations = 10000
    # We will repeat the forward-backward-update loop 10,000 times.
    # This is enough for the model to converge on this simple dataset.
    # On harder datasets, you might need 100,000 or millions.
    iterations = 10000

    print("Training binary classifier...")
    print("-" * 40)

    # Train the model!
    # This is where the magic happens. The model adjusts its weights
    # to minimize the loss.
    model.train(X, y, learning_rate, iterations)

    # --------------------------------------------------------------------------
    # PART C: Evaluate the model
    # --------------------------------------------------------------------------
    # After training, we want to know: how good is the model?

    # Make predictions on the SAME data we trained on.
    # (In real projects, you would use separate "test data" that the model
    # has never seen, to check if it GENERALIZES.)
    predictions = model.predict(X)

    # Compute accuracy: percentage of correct predictions.
    # predictions == y creates a boolean array (True for correct, False for wrong).
    # np.mean turns True into 1.0 and False into 0.0, then averages them.
    # Multiply by 100 to get a percentage.
    accuracy = np.mean(predictions == y) * 100

    print("\n" + "=" * 60)
    print(f"Final accuracy: {accuracy:.1f}%")
    print("=" * 60)

    # Show 5 example points with their true label, predicted probability,
    # and predicted class. This helps us see what the model is doing.
    print("\nExample predictions (first 5 points):")
    print("-" * 60)
    probs, _, _ = model.forward(X[:5])
    for i in range(5):
        pred = predictions[i, 0]
        true = y[i, 0]
        p = probs[i, 0]
        print(f"  Point {i}: true={int(true)}, prob={p:.3f}, predict={pred}")
        print(f"           Meaning: the model is {p*100:.1f}% confident this is class {pred}.")
        if int(true) == pred:
            print(f"           RESULT: CORRECT!")
        else:
            print(f"           RESULT: WRONG.")
        print()

    # --------------------------------------------------------------------------
    # PART D: Visualize the decision boundary
    # --------------------------------------------------------------------------
    # Numbers are great, but pictures are BETTER.
    # We will draw a colored background showing where the model says YES vs NO.
    # This creates a "map" of the model's brain.

    # STEP 1: Find the range of our data.
    # We want the plot to cover all points plus a little padding.
    # X[:, 0] means "all rows, column 0" (all x-coordinates).
    # X[:, 1] means "all rows, column 1" (all y-coordinates).
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1

    # STEP 2: Build a fine grid of points across the entire area.
    # np.linspace(x_min, x_max, 200) creates 200 evenly spaced numbers
    # between x_min and x_max.
    # np.meshgrid takes those x-values and y-values and creates TWO matrices:
    #   xx = a grid where every row is the same x-values
    #   yy = a grid where every column is the same y-values
    # Together, they represent EVERY combination of x and y in the area.
    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, 200),
        np.linspace(y_min, y_max, 200)
    )

    # STEP 3: Flatten the grids and stack them into coordinate pairs.
    # xx.ravel() turns the 2D grid into a 1D list (all x-coordinates).
    # yy.ravel() turns the 2D grid into a 1D list (all y-coordinates).
    # np.c_ stacks them side by side into pairs: [[x1, y1], [x2, y2], ...]
    # This gives us 200 * 200 = 40,000 points to evaluate.
    grid = np.c_[xx.ravel(), yy.ravel()]

    # STEP 4: Ask the model to predict YES/NO for every point on the grid.
    # model.predict(grid) returns 0 or 1 for all 40,000 points.
    # We reshape the result back into a 200x200 grid so we can plot it.
    Z = model.predict(grid)
    Z = Z.reshape(xx.shape)

    # STEP 5: Draw the decision boundary as a filled contour.
    # plt.contourf fills regions with color based on the prediction.
    # levels=[-0.5, 0.5, 1.5] creates two regions:
    #   Region 1: values from -0.5 to 0.5  -> colored red
    #   Region 2: values from 0.5 to 1.5   -> colored blue
    # alpha=0.3 makes the background slightly transparent so the data points
    # show through clearly.
    plt.contourf(xx, yy, Z, levels=[-0.5, 0.5, 1.5], colors=["red", "blue"], alpha=0.3)

    # STEP 6: Plot the REAL data points on top of the background.
    # We use different colors and shapes so we can tell the two classes apart.
    # Class 0 = red circles
    # Class 1 = blue squares
    # edgecolor="black" adds a black outline so points are visible against
    # the colored background.
    # s=60 controls the size of the markers.
    plt.scatter(X0[:, 0], X0[:, 1], color="red", edgecolor="black", label="Class 0 (NO)", s=60)
    plt.scatter(X1[:, 0], X1[:, 1], color="blue", edgecolor="black", label="Class 1 (YES)", s=60)

    # STEP 7: Add labels, title, and legend.
    # These make the graph self-explanatory. Without them, it is just
    # a pretty picture with no meaning.
    plt.title("Binary Classification: Decision Boundary")
    plt.xlabel("Feature 1 (x-coordinate)")
    plt.ylabel("Feature 2 (y-coordinate)")
    plt.legend()

    # STEP 8: Show the plot!
    # This opens a window with the graph.
    # The red background means "the model predicts NO here."
    # The blue background means "the model predicts YES here."
    # The boundary between red and blue is the "decision boundary."
    # This is the "line" the model learned to separate the two groups.
    plt.show()

    # --------------------------------------------------------------------------
    # PART E: Summary
    # --------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    print("We built a neural network that answers YES/NO questions.")
    print("It uses sigmoid to produce probabilities.")
    print("It uses binary cross-entropy to measure wrongness.")
    print("The colored background shows the decision boundary.")
    print("Points on one side = NO (red). Points on the other side = YES (blue).")
    print("=" * 60)
