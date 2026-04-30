import numpy as np

# ============================================================================
# SECTION 1: HELPER FUNCTIONS
# ============================================================================
# These are building blocks we use over and over inside the network.
# Think of them like tiny tools in a toolbox.

def relu(x):
    """
    ReLU activation: if x is positive, keep it. If negative, make it 0.
    
    WHY we do this:
    Without activation functions, a neural network is just a big linear
    equation: output = (input * weight) + bias.  No matter how many layers
    you stack, the final result is still a straight line.  That means the
    network could never learn a curve, a circle, or any non-linear pattern.
    
    ReLU (Rectified Linear Unit) bends the line.  It squashes negative
    values to zero and leaves positive values alone.  This simple "bend"
    is what gives the network the power to model curves and complex shapes.
    """
    return np.maximum(0, x)


def relu_derivative(x):
    """
    ReLU derivative: 1 where x was positive, 0 where x was negative or zero.
    
    WHY we need this:
    During backpropagation we need to know: "If I nudge this number slightly,
    how much does the output change?"  That ratio of change is called the
    derivative.  For ReLU, the slope is 1 when x is positive (output rises
    at the same speed as input) and 0 when x is negative or zero (output
    stays flat no matter what input does).
    
    We use this to decide WHERE to send the error signal backward.
    If a neuron was "off" (negative input), its derivative is 0, so we do
    NOT blame that neuron for the mistake.  If it was "on" (positive input),
    its derivative is 1, so the full error flows through to update its
    weights.
    """
    return (x > 0).astype(float)


# ============================================================================
# SECTION 2: NEURAL NETWORK CLASS
# ============================================================================
# This class holds everything the network needs: weights, biases, and the
# methods to move data forward, measure error, move error backward, and
# update parameters.

class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        """
        Create the network and fill it with weights and biases.
        
        Parameters:
          input_size   -- how many numbers enter the network (1 for our parabola)
          hidden_size  -- how many neurons live in the hidden layer (4 for us)
          output_size  -- how many numbers leave the network  (1 for our parabola)
        
        WHY small random initialization matters:
        If every weight starts at exactly 0, every hidden neuron computes
        the exact same thing.  They are clones.  During training they would
        all update identically forever, so the network would act like it
        only has ONE neuron.  That destroys the whole point of having many.
        
        If weights start too BIG (e.g. random numbers from 0 to 1), the
        first multiplication can blow up into the thousands, and the ReLU
        outputs become huge.  This makes the gradient explode, causing wild
        jumps during training that never settle down.
        
        Small random values (like 0.1) break the symmetry just enough that
        each neuron learns something different, while keeping numbers small
        so training stays stable.
        """
        
        # W1 connects every input to every hidden neuron.
        # Shape: (input_size, hidden_size)
        # Example: if input_size=1 and hidden_size=4, W1 is a 1x4 column.
        # Each value is a random number between 0 and 1, then scaled down by 0.1.
        self.W1 = np.random.randn(input_size, hidden_size) * 0.1
        
        # b1 is a bias for each hidden neuron.
        # Shape: (1, hidden_size)
        # Bias lets the neuron shift its activation left or right even when
        # the input is zero.  We start biases at zero because the random
        # weights already give each neuron a slightly different personality.
        self.b1 = np.zeros((1, hidden_size))
        
        # W2 connects every hidden neuron to every output neuron.
        # Shape: (hidden_size, output_size)
        # Example: if hidden_size=4 and output_size=1, W2 is a 4x1 column.
        self.W2 = np.random.randn(hidden_size, output_size) * 0.1
        
        # b2 is a bias for each output neuron.
        # Shape: (1, output_size)
        self.b2 = np.zeros((1, output_size))

    def forward(self, X):
        """
        Forward pass: take input data, push it through the network, and
        return the final prediction.
        
        Parameters:
          X  -- input data, shape (n_samples, input_size)
                Each row is one training example.  For our parabola, each
                row is a single x value.
        
        Returns:
          z2  -- raw output BEFORE any final activation (we skip activation
                 on the output for regression, so z2 IS the prediction)
          a1  -- output of the hidden layer AFTER ReLU
          z1  -- raw hidden layer BEFORE ReLU
        
        WHY we store a1 and z1:
        Backpropagation needs to know "what did each neuron output?" and
        "was it turned on or off?"  We save these values during the forward
        pass so we do not have to recompute them later.
        
        Think of forward pass as baking a cake:
          z1 = mixing the batter            (raw weighted sum)
          a1 = baking it in the oven         (after ReLU, the "cake")
          z2 = adding frosting               (final layer output)
        We write down the oven temperature and batter recipe because later
        we need them to figure out why the cake tasted too salty.
        """
        
        # Step 1 -- Hidden layer raw scores (z1):
        # X @ W1 means matrix multiply every input row by every weight.
        # The @ symbol is Python's way of saying "do matrix multiplication."
        # For each sample, we compute: input * weight1 + input * weight2 + ...
        # Then we add the bias b1 to every row.
        # Result shape: (n_samples, hidden_size)
        z1 = X @ self.W1 + self.b1
        
        # Step 2 -- Hidden layer activation (a1):
        # Apply ReLU to z1.  Negative numbers become 0, positives stay the same.
        # This is where the network gets its "bend" to model curves.
        # Result shape: (n_samples, hidden_size)
        a1 = relu(z1)
        
        # Step 3 -- Output layer raw scores (z2):
        # Take the activated hidden values (a1) and multiply by W2, then add b2.
        # For regression we do NOT apply another activation; z2 is our guess.
        # Result shape: (n_samples, output_size)
        z2 = a1 @ self.W2 + self.b2
        
        # Return all three because backward() needs a1 and z1.
        return z2, a1, z1

    def compute_loss(self, predictions, y_true):
        """
        Compute the Mean Squared Error (MSE) loss.
        
        Parameters:
          predictions  -- what the network guessed, shape (n_samples, output_size)
          y_true       -- the correct answers, shape (n_samples, output_size)
        
        WHY we use MSE:
        We need a SINGLE number that tells us "how bad are we overall?"
        Squaring the errors does three helpful things:
          1. It makes every error positive (so negative and positive mistakes
             do not cancel each other out).
          2. It punishes BIG mistakes much harder than small ones.
          3. The derivative is simple and smooth, which makes gradient
             descent stable.
        
        We take the mean so the loss does not depend on how many samples
        we have.  That lets us compare training runs with different data sizes.
        """
        errors = predictions - y_true      # positive = guess too high, negative = too low
        return np.mean(errors ** 2)        # square, then average

    def backward(self, X, y_true, predictions, a1, z1):
        """
        Backpropagation: compute how much each weight and bias contributed
        to the final error, so we know which knobs to turn and by how much.
        
        This is the heart of learning.  Every other step is just arithmetic;
        THIS step is where the network gets smarter.
        
        The core idea is the CHAIN RULE from basic algebra.
        Imagine four dominoes in a row:
          Domino 1 = W1 or b1  (a weight or bias we control)
          Domino 2 = z1        (weighted sum in hidden layer)
          Domino 3 = a1        (after ReLU activation)
          Domino 4 = z2        (final output / prediction)
        
        If we nudge Domino 1, it knocks over Domino 2, which knocks over
        Domino 3, which knocks over Domino 4.  The chain rule says:
        "Total effect on Domino 4 = (effect 1→2) × (effect 2→3) × (effect 3→4)"
        
        In math terms: d(Loss)/d(W1) = d(Loss)/d(z2) × d(z2)/d(a1) × d(a1)/d(z1) × d(z1)/d(W1)
        
        We work BACKWARD from the output because the error at the end is
        the only thing we can directly measure.  We then pass that error
        backward layer by layer, multiplying by local derivatives as we go.
        
        Parameters:
          X            -- original input data, shape (n_samples, input_size)
          y_true       -- correct answers, shape (n_samples, output_size)
          predictions  -- z2 from forward pass, shape (n_samples, output_size)
          a1           -- hidden activations, shape (n_samples, hidden_size)
          z1           -- hidden raw scores, shape (n_samples, hidden_size)
        
        Returns:
          dW1, db1, dW2, db2  -- gradients telling us how to update parameters
        """
        
        # ----------------------------------------------------------------
        # PREP: figure out how many training examples we have
        # ----------------------------------------------------------------
        n = X.shape[0]   # number of rows in X = number of samples
        
        # ----------------------------------------------------------------
        # STEP 1: Compute output error (how wrong were we at the very end?)
        # ----------------------------------------------------------------
        # We start at the output layer because that is where we can compare
        # our guess to the true answer.
        # 
        # Loss = average of (prediction - true)^2
        # d(Loss)/d(prediction) = (2/n) * (prediction - true)
        # 
        # The "2" comes from the power rule: derivative of x^2 is 2x.
        # The "/n" averages the gradient across all samples so a bigger
        # batch does not automatically create bigger updates.
        # 
        # Shape: (n_samples, output_size)
        output_error = (2 / n) * (predictions - y_true)
        
        # ----------------------------------------------------------------
        # STEP 2: Compute dW2 (chain rule: error → output → W2)
        # ----------------------------------------------------------------
        # z2 = a1 @ W2 + b2
        # 
        # If we increase W2 by 1, z2 increases by a1 (because a1 is the
        # thing W2 is multiplied by).  So d(z2)/d(W2) = a1.
        # 
        # By the chain rule:
        #   d(Loss)/d(W2) = d(Loss)/d(z2)  ×  d(z2)/d(W2)
        #                 = output_error    ×  a1
        # 
        # Matrix shapes:
        #   a1.T is (hidden_size, n_samples)
        #   output_error is (n_samples, output_size)
        #   result dW2 is (hidden_size, output_size)  ✓ matches W2
        # 
        # We use a1.T (transpose) so the inner dimensions line up for
        # matrix multiplication: (hidden_size, n) @ (n, output_size).
        dW2 = a1.T @ output_error
        
        # ----------------------------------------------------------------
        # STEP 3: Compute db2 (chain rule: error → output → b2)
        # ----------------------------------------------------------------
        # z2 = a1 @ W2 + b2
        # 
        # If we increase b2 by 1, z2 increases by exactly 1 (because b2 is
        # added directly).  So d(z2)/d(b2) = 1.
        # 
        # By the chain rule:
        #   d(Loss)/d(b2) = d(Loss)/d(z2)  ×  d(z2)/d(b2)
        #                 = output_error    ×  1
        #                 = output_error
        # 
        # We sum across all samples (axis=0) because the SAME bias is added
        # to every sample.  We keep the result as a row vector with
        # keepdims=True so the shape stays (1, output_size) and matches b2.
        db2 = np.sum(output_error, axis=0, keepdims=True)
        
        # ----------------------------------------------------------------
        # STEP 4: Send error backward to hidden layer
        # ----------------------------------------------------------------
        # We know how wrong the output is.  Now we ask: how much did each
        # hidden neuron contribute to that wrongness?
        # 
        # z2 = a1 @ W2 + b2
        # If hidden neuron j increases by 1, z2 increases by W2[j].
        # So d(z2)/d(a1) = W2.
        # 
        # By the chain rule:
        #   d(Loss)/d(a1) = d(Loss)/d(z2)  ×  d(z2)/d(a1)
        #                 = output_error    @  W2.T
        # 
        # Matrix shapes:
        #   output_error is (n_samples, output_size)
        #   W2.T is (output_size, hidden_size)
        #   result hidden_error is (n_samples, hidden_size)  ✓ matches a1
        # 
        # This is literally "propagating" the error backward through W2.
        hidden_error = output_error @ self.W2.T
        
        # ----------------------------------------------------------------
        # STEP 5: Apply ReLU derivative (only propagate error where neurons
        #         were active)
        # ----------------------------------------------------------------
        # Before ReLU we had z1.  After ReLU we had a1.
        # ReLU says: if z1 was positive, a1 = z1.  If z1 was negative, a1 = 0.
        # 
        # For positive z1: d(a1)/d(z1) = 1  (a1 changes at the same rate)
        # For negative z1: d(a1)/d(z1) = 0  (a1 never changes, it is stuck at 0)
        # 
        # By the chain rule:
        #   d(Loss)/d(z1) = d(Loss)/d(a1)  ×  d(a1)/d(z1)
        #                 = hidden_error    *  relu_derivative(z1)
        # 
        # The "*" here is ELEMENT-WISE multiplication (not matrix multiply).
        # This is CRITICAL: it zeros out the error for any neuron that was
        # "off" during the forward pass.  We do NOT update weights for dead
        # neurons because they did not influence the output.
        # 
        # Shape: (n_samples, hidden_size)  ✓ same as z1 and hidden_error
        dz1 = hidden_error * relu_derivative(z1)
        
        # ----------------------------------------------------------------
        # STEP 6: Compute dW1 (chain rule: error → output → hidden → W1)
        # ----------------------------------------------------------------
        # z1 = X @ W1 + b1
        # 
        # If we increase W1 by 1, z1 increases by X (because X is what W1
        # multiplies).  So d(z1)/d(W1) = X.
        # 
        # By the chain rule:
        #   d(Loss)/d(W1) = d(Loss)/d(z1)  ×  d(z1)/d(W1)
        #                 = dz1             @  X.T  (after transposing)
        # 
        # Wait -- why X.T @ dz1 and not dz1 @ X.T?
        # 
        # dz1 shape: (n_samples, hidden_size)
        # X shape:   (n_samples, input_size)
        # 
        # We need dW1 shape: (input_size, hidden_size) to match W1.
        # 
        # X.T is (input_size, n_samples)
        # dz1 is (n_samples, hidden_size)
        # X.T @ dz1  →  (input_size, hidden_size)  ✓ perfect match
        # 
        # Think of it as: for every input feature (row of X.T), how much
        # did every hidden neuron (column of dz1) need to change?
        dW1 = X.T @ dz1
        
        # ----------------------------------------------------------------
        # STEP 7: Compute db1
        # ----------------------------------------------------------------
        # Same logic as db2: the bias is added directly to every sample,
        # so its derivative is 1.  We sum the error contributions across
        # all samples and keep the shape as (1, hidden_size).
        db1 = np.sum(dz1, axis=0, keepdims=True)
        
        # Return all four gradients.  The train() method will use these
        # to nudge W1, b1, W2, b2 in the direction that reduces loss.
        return dW1, db1, dW2, db2

    def train(self, X, y_true, learning_rate, iterations):
        """
        Train the neural network using gradient descent.
        
        Parameters:
          X              -- input data, shape (n_samples, input_size)
          y_true         -- correct answers, shape (n_samples, output_size)
          learning_rate  -- how big of a step we take each time (e.g. 0.01)
          iterations     -- how many times we repeat the forward/backward loop
        
        WHAT gradient descent IS:
        Imagine you are blindfolded on a hilly landscape and you want to
        find the lowest valley.  You feel the ground with your foot to see
        which way is downhill, then you take one step in that direction.
        You repeat this over and over until you stop sliding downward.
        
        In our network:
          - The "landscape" is the loss function (how wrong we are).
          - Our "position" is the current values of W1, b1, W2, b2.
          - The "slope" is the gradient (dW1, db1, dW2, db2).
          - The "step size" is the learning_rate.
        
        The update rule is:
          new_weight = old_weight - learning_rate * gradient
        
        WHY we SUBTRACT the gradient:
        If the gradient is positive, increasing the weight increases loss,
        so we want to DECREASE the weight.  If the gradient is negative,
        increasing the weight decreases loss, so we want to INCREASE it.
        Subtracting the gradient always moves us downhill.
        
        WHY we loop many times:
        One step does not get us to the bottom.  We need hundreds or
        thousands of small steps to settle into the lowest valley.
        """
        
        for i in range(iterations):
            # 1) Forward pass: make a guess using current weights.
            predictions, a1, z1 = self.forward(X)
            
            # 2) Measure how bad the guess was.
            loss = self.compute_loss(predictions, y_true)
            
            # 3) Backward pass: figure out who to blame and by how much.
            dW1, db1, dW2, db2 = self.backward(X, y_true, predictions, a1, z1)
            
            # 4) Gradient descent: take a small step downhill.
            self.W1 = self.W1 - learning_rate * dW1
            self.b1 = self.b1 - learning_rate * db1
            self.W2 = self.W2 - learning_rate * dW2
            self.b2 = self.b2 - learning_rate * db2
            
            # 5) Print progress every 1000 iterations so we can watch learning.
            if i % 1000 == 0:
                print(f"  Iteration {i:5d}: loss = {loss:.6f}")
                print(f"    W1 = {self.W1.flatten()}")
                print(f"    b1 = {self.b1.flatten()}")
                print(f"    W2 = {self.W2.flatten()}")
                print(f"    b2 = {self.b2.flatten()}")
                print()


# ============================================================================
# SECTION 3: MAIN DEMONSTRATION
# ============================================================================
# We will show TWO things:
#   A) A straight line CANNOT fit a curve (linear regression fails)
#   B) A neural network CAN fit a curve (non-linear patterns succeed)
#
# The data is simple: y = x^2 (a parabola).
# Every high-school student knows this is a curve, not a line.

if __name__ == "__main__":
    
    # ----------------------------------------------------------------
    # PART A: Linear Regression on a Parabola
    # ----------------------------------------------------------------
    print("=" * 60)
    print("PART A: Linear Regression on a Parabola")
    print("=" * 60)
    print()
    
    # Create 20 evenly spaced x values from -2 to 2, shaped as a column.
    # Shape: (20, 1)
    x = np.linspace(-2, 2, 20).reshape(-1, 1)
    
    # The true y values are x squared -- a classic U-shaped parabola.
    # Shape: (20, 1)
    y = x ** 2
    
    # Compute the BEST possible straight line through this curve.
    # These are the normal equations for simple linear regression.
    # Even the mathematically perfect line will still be terrible.
    w = np.sum((x - x.mean()) * (y - y.mean())) / np.sum((x - x.mean()) ** 2)
    b = y.mean() - w * x.mean()
    
    # Use that best line to predict every y value.
    linear_pred = x * w + b
    
    # Measure how far off the line is, on average.
    linear_loss = np.mean((linear_pred - y) ** 2)
    
    print(f"Best straight line: y = {w:.4f} * x + {b:.4f}")
    print(f"Linear regression loss (MSE): {linear_loss:.6f}")
    print()
    print("Sample predictions vs actual:")
    print("  x      prediction    actual     error")
    print("  " + "-" * 40)
    for i in [0, 5, 10, 15, 19]:
        print(f"  {x[i,0]:+.2f}     {linear_pred[i,0]:+.4f}      {y[i,0]:+.4f}    {linear_pred[i,0] - y[i,0]:+.4f}")
    print()
    
    # Linear regression tries to draw a straight line through a curve.
    # It cannot fit this data.
    print("COMMENT: Linear regression tries to draw a straight line through a curve.")
    print("         It cannot fit this data no matter how long it trains,")
    print("         because the model is structurally limited to lines.")
    print()
    
    # ----------------------------------------------------------------
    # PART B: Neural Network on a Parabola
    # ----------------------------------------------------------------
    print("=" * 60)
    print("PART B: Neural Network on a Parabola")
    print("=" * 60)
    print()
    
    # Create a neural network with:
    #   1 input  (the x value)
    #   8 hidden neurons (enough ReLU pieces to build a smooth curve)
    #   1 output (the predicted y value)
    nn = NeuralNetwork(input_size=1, hidden_size=8, output_size=1)
    
    # learning_rate = 0.01 means we take 1% of the gradient each step.
    # Small steps prevent overshooting the valley.
    learning_rate = 0.01
    
    # 10,000 iterations gives the network plenty of time to settle.
    iterations = 10000
    
    print("Training neural network...")
    print()
    nn.train(x, y, learning_rate, iterations)
    
    # Get the final predictions after all training is done.
    final_predictions, _, _ = nn.forward(x)
    final_nn_loss = nn.compute_loss(final_predictions, y)
    
    print()
    print("Training complete!")
    print()
    print(f"Final neural network loss (MSE): {final_nn_loss:.6f}")
    print()
    print("Sample predictions vs actual:")
    print("  x      prediction    actual     error")
    print("  " + "-" * 40)
    for i in [0, 5, 10, 15, 19]:
        print(f"  {x[i,0]:+.2f}     {final_predictions[i,0]:+.4f}      {y[i,0]:+.4f}    {final_predictions[i,0] - y[i,0]:+.4f}")
    print()
    
    # The neural network learned to approximate the curve because ReLU
    # activation lets it bend.
    print("COMMENT: The neural network learned to approximate the curve")
    print("         because ReLU activation lets it bend.  Each hidden")
    print("         neuron acts like a small hinge; together they build")
    print("         a piecewise-linear shape that closely matches x^2.")
    print()
    
    # ----------------------------------------------------------------
    # PART C: Side-by-Side Comparison
    # ----------------------------------------------------------------
    print("=" * 60)
    print("COMPARISON:")
    print("=" * 60)
    print()
    print(f"  Linear regression loss:      {linear_loss:.6f}")
    print(f"  Neural network loss:         {final_nn_loss:.6f}")
    print()
    
    # The neural network wins because it can learn non-linear (curved) patterns.
    print("The neural network wins because it can learn non-linear (curved)")
    print("patterns.  Linear regression is trapped in a straight line;")
    print("the neural network can fold and shape its prediction to match")
    print("the curve.  That is the power of hidden layers + activation")
    print("functions + backpropagation.")
    print()
