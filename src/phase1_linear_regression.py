import numpy as np


class LinearRegression:
    """
    Our model is a straight line: prediction = (input * weight) + bias.
    The weight and bias are parameters we can adjust.
    """

    def __init__(self, weight, bias):
        # WHY: A model needs to remember its parameters so it can use them
        # every time we ask it to make a prediction.
        self.weight = weight
        self.bias = bias

    def predict(self, X):
        # WHY: This is the heart of the model. It takes an input (X),
        # multiplies it by the weight, and adds the bias.
        # Changing the weight or bias changes every prediction.
        return np.add(np.multiply(X, self.weight), self.bias)


if __name__ == "__main__":
    # WHY: We create example data so we can see how the model behaves
    # with real numbers. This makes the abstract idea concrete.
    house_sizes = np.array([1000, 1500, 2000, 2500])  # Input: square feet
    actual_prices = np.array([200000, 300000, 400000, 500000])  # What we know the prices actually are

    # WHY: We know the true pattern is price = size * 200.
    # This means the correct weight is 200 and the correct bias is 0.
    # We will show what happens when our model uses the WRONG parameters first,
    # and then the RIGHT parameters. This proves that the parameters matter.

    # ============================================================
    # PART A: A BAD model with guessed parameters
    # ============================================================
    print("=" * 60)
    print("PART A: A BAD model (wrong weight and bias)")
    print("=" * 60)

    # WHY: We intentionally pick the wrong numbers to show that
    # if the parameters are wrong, the predictions are wrong.
    bad_model = LinearRegression(weight=100, bias=50000)
    bad_predictions = bad_model.predict(house_sizes)

    print("\nHere is what the bad model predicts:\n")
    for i in range(len(house_sizes)):
        print(f"House size: {house_sizes[i]} sq ft")
        print(f"Actual price: ${actual_prices[i]}")
        print(f"Bad model prediction: ${int(bad_predictions[i])}")
        print("-" * 40)

    # ============================================================
    # PART B: A GOOD model with the correct parameters
    # ============================================================
    print("\n" + "=" * 60)
    print("PART B: A GOOD model (correct weight and bias)")
    print("=" * 60)

    # WHY: Now we plug in the exact weight and bias from the true pattern.
    # The predictions should match the actual prices perfectly.
    good_model = LinearRegression(weight=200, bias=0)
    good_predictions = good_model.predict(house_sizes)

    print("\nHere is what the good model predicts:\n")
    for i in range(len(house_sizes)):
        print(f"House size: {house_sizes[i]} sq ft")
        print(f"Actual price: ${actual_prices[i]}")
        print(f"Good model prediction: ${int(good_predictions[i])}")
        print("-" * 40)

    # ============================================================
    # Closing note for the beginner
    # ============================================================
    # WHY: We want the reader to understand what they just saw.
    # The model structure is just multiplication and addition.
    # The magic is finding the right weight and bias.
    print("\n" + "=" * 60)
    print("WHAT DID WE LEARN?")
    print("=" * 60)
    print("""
    Right now, we are guessing the weight and bias by hand.
    In the next phases, we will learn how to MEASURE how wrong our predictions are (error/loss),
    and then how to automatically adjust the weight and bias to find the best values.
    """)
