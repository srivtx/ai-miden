import numpy as np


class LinearRegression:
    """
    A model that learns to predict a straight-line pattern.
    It starts with random guesses and improves using gradient descent.
    """

    def __init__(self, weight, bias):
        """
        Create the model with starting values for weight and bias.
        These are PARAMETERS - numbers the model will adjust during learning.
        """
        self.weight = weight
        self.bias = bias

    def predict(self, X):
        """
        Use the current weight and bias to make a prediction.
        Formula: prediction = input * weight + bias
        This is the MODEL FUNCTION - it turns inputs into outputs.
        """
        return X * self.weight + self.bias

    def compute_loss(self, predictions, y_true):
        """
        Measure how WRONG the predictions are.
        Loss = average of (error squared) for all examples.
        We square the errors so negative and positive mistakes both count,
        and big mistakes count much more than small ones.
        """
        errors = predictions - y_true
        return np.mean(errors ** 2)

    def compute_gradients(self, X, predictions, y_true):
        """
        Calculate the DERIVATIVES of the loss with respect to weight and bias.
        A derivative tells us: if I change this parameter slightly,
        how much does the loss change?
        This gives us the GRADIENT - the direction of steepest increase.
        """
        n = len(X)
        errors = predictions - y_true
        # How much does the loss change if we tweak the weight?
        dw = (2 / n) * np.sum(errors * X)
        # How much does the loss change if we tweak the bias?
        db = (2 / n) * np.sum(errors)
        return dw, db

    def train(self, X, y_true, learning_rate, iterations):
        """
        This method IS gradient descent.
        We repeat the same steps many times to find the best weight and bias.
        """
        # Loop over the dataset many times. Each pass is one ITERATION.
        for i in range(iterations):
            # Step 1: Make predictions using the CURRENT weight and bias.
            predictions = self.predict(X)

            # Step 2: Calculate the loss to see how wrong we are.
            loss = self.compute_loss(predictions, y_true)

            # Step 3: Compute the gradients.
            # The gradient tells us WHICH WAY IS UPHILL on the loss surface.
            # If the gradient is positive, increasing the parameter increases loss.
            dw, db = self.compute_gradients(X, predictions, y_true)

            # Step 4: Update the parameters.
            # We subtract learning_rate * gradient to WALK DOWNHILL.
            # If gradient is positive, we decrease the parameter (go down).
            # If gradient is negative, we increase the parameter (still go down).
            # The LEARNING RATE controls step size - too big and we overshoot,
            # too small and learning takes forever.
            self.weight = self.weight - (learning_rate * dw)
            self.bias = self.bias - (learning_rate * db)

            # Step 5: Print progress every 100 iterations.
            # We repeat this many times to reach the bottom of the loss valley.
            if i % 100 == 0:
                print(f"Iteration {i}: Loss = {loss:.4f}, Weight = {self.weight:.4f}, Bias = {self.bias:.4f}")


if __name__ == "__main__":
    # A SIMPLE dataset where the pattern is obvious:
    # y = 2 * x + 0, so the true weight is 2 and true bias is 0.
    X = np.array([1, 2, 3, 4, 5])
    y = np.array([2, 4, 6, 8, 10])

    print("=" * 60)
    print("PHASE 3: GRADIENT DESCENT (THE MODEL LEARNS!)")
    print("=" * 60)

    # Start with weight=0 and bias=0.
    # The model knows NOTHING at the start - it is just guessing.
    model = LinearRegression(weight=0.0, bias=0.0)

    print(f"Starting weight: {model.weight}")
    print(f"Starting bias:   {model.bias}")

    # Show how bad the initial predictions are.
    initial_predictions = model.predict(X)
    print("\nInitial predictions (before learning):")
    for xi, pred, actual in zip(X, initial_predictions, y):
        print(f"  Input {xi}: predicted {pred:.2f}, actual {actual}")

    # Set the hyperparameters.
    learning_rate = 0.01
    iterations = 1000

    print(f"\nTraining with learning_rate={learning_rate} for {iterations} iterations...\n")
    model.train(X, y, learning_rate, iterations)

    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)

    print(f"Final weight: {model.weight:.4f}")
    print(f"Final bias:   {model.bias:.4f}")

    final_predictions = model.predict(X)
    print("\nPredictions vs Actual:")
    for xi, pred, actual in zip(X, final_predictions, y):
        print(f"  Input {xi}: predicted {pred:.2f}, actual {actual}")

    # The model started knowing nothing (weight=0, bias=0) and learned the correct
    # pattern just by repeatedly measuring error and adjusting parameters. This is optimization.
