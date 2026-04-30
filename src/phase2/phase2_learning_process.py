import numpy as np

# ===================================================================
# PHASE 2: THE LEARNING PROCESS (MEASUREMENT ONLY)
# ===================================================================
# This file is for complete beginners with zero AI/ML knowledge.
# We only use basic algebra: lines, slopes, and averages.
#
# Key idea: Before a model can improve, it must first MEASURE how
# wrong it is. This file only MEASURES. It does not change anything.
# Changing (learning) comes in Phase 3.
#
# Allowed words: function, input, output, prediction, model,
# parameter, weight, bias, error, loss, derivative, gradient.
# ===================================================================


class LinearRegression:
    """
    A model that draws a straight line through data.
    
    Why a straight line?
    Because the simplest relationship between two things is a line.
    If house size goes up, price goes up. A line captures that.
    
    The line is:  prediction = weight * input + bias
    
    - weight: the slope. How much the output goes up when input goes up by 1.
    - bias:   the starting point. The prediction when input is 0.
    
    Together, weight and bias are called PARAMETERS.
    They are the "knobs" we can turn to make the line fit the data better.
    """

    def __init__(self, weight, bias):
        """
        Store the model's parameters (knobs).
        
        Why do we store them?
        Because the model needs to remember its current weight and bias
        so it can use them to make predictions later.
        """
        self.weight = weight
        self.bias = bias

    def predict(self, X):
        """
        Make predictions using the current line.
        
        prediction = weight * input + bias
        
        Why do we multiply and add?
        Because we are drawing a straight line. Every input X gets mapped
        to an output (prediction) on that line.
        """
        return X * self.weight + self.bias

    def compute_error(self, predictions, y_true):
        """
        Compute how far off each prediction is.
        
        error = prediction - actual
        
        Why subtract?
        Because we want to know the difference between what we guessed
        and the real answer.
        
        - Positive error: our guess was too high.
        - Negative error: our guess was too low.
        - Zero error:     we got it exactly right.
        """
        # Error tells us how far off each prediction is.
        # Positive = too high. Negative = too low.
        return predictions - y_true

    def compute_loss(self, predictions, y_true):
        """
        Compute one number that tells us how bad the model is overall.
        
        Steps:
          1. Find the error for each example.
          2. Square each error (so negatives don't cancel positives).
          3. Take the average of those squared errors.
        
        Why square?
        Because if one prediction is +100 too high and another is -100
        too low, the average error would be 0 — which looks perfect
        but is actually very wrong. Squaring keeps both mistakes visible.
        
        Why average?
        Because we want a single fair number, no matter how many
        houses we are looking at. 3 houses or 300, the loss scale is the same.
        
        This specific loss is called Mean Squared Error (MSE).
        """
        errors = predictions - y_true
        squared_errors = errors ** 2
        # Loss = average of squared errors.
        # One number that tells us how bad the model is overall.
        # We square so negatives don't cancel positives.
        return np.mean(squared_errors)

    def compute_gradients(self, X, predictions, y_true):
        """
        Compute the gradient: which way to turn the knobs to reduce loss.
        
        What is a gradient?
        It is a derivative. It tells us how sensitive the loss is to each
        parameter (weight and bias).
        
        - dw (gradient for weight): If we nudge the weight up a tiny bit,
          how much does the loss change?
        - db (gradient for bias):   If we nudge the bias up a tiny bit,
          how much does the loss change?
        
        Why do we care?
        Because if we know which way makes the loss go down, we know
        which way to turn the knobs. The gradient points in the direction
        of rising loss, so we should turn the knobs the opposite way.
        
        The formulas come from taking the derivative of the MSE loss
        with respect to weight and bias. Don't worry about the calculus —
        just know they measure sensitivity.
        
        Sign rule:
        - If gradient is positive, increasing that parameter makes loss worse.
          So we should DECREASE that parameter.
        - If gradient is negative, increasing that parameter makes loss better.
          So we should INCREASE that parameter.
        """
        n = len(X)               # number of examples
        errors = predictions - y_true
        dw = (2 / n) * np.sum(errors * X)  # gradient for weight
        db = (2 / n) * np.sum(errors)      # gradient for bias
        
        # The gradient tells us which way to turn the knobs to reduce loss.
        # dw = how sensitive loss is to weight.
        # db = how sensitive loss is to bias.
        return dw, db


# ===================================================================
# MAIN SCRIPT: Walk through the learning process step by step.
# ===================================================================

if __name__ == "__main__":

    # -----------------------------------------------------------------
    # Setup: Our data
    # -----------------------------------------------------------------
    # We use the same simple house data every time.
    # This makes it easy to see if our model is improving.
    house_sizes = np.array([1000, 1500, 2000, 2500])
    actual_prices = np.array([200000, 300000, 400000, 500000])

    # We intentionally start with BAD parameters.
    # Why? So we can see the model measure how bad it is,
    # and later (in Phase 3) see it improve.
    model = LinearRegression(weight=100, bias=50000)

    print("=" * 60)
    print("PHASE 2: MEASURING HOW WRONG WE ARE")
    print("=" * 60)
    print()
    print("We will NOT change the model yet.")
    print("We will only MEASURE: predictions, errors, loss, and gradients.")
    print()

    # =================================================================
    # STEP 1: Make predictions
    # =================================================================
    # Why predict first?
    # Because we cannot measure how wrong we are until we have guesses
    # to compare against the real answers.
    print("=" * 60)
    print("STEP 1: Make predictions")
    print("=" * 60)
    print("Formula: prediction = weight * size + bias")
    print(f"Current weight = {model.weight}, bias = {model.bias}")
    print()

    predictions = model.predict(house_sizes)

    for size, actual, pred in zip(house_sizes, actual_prices, predictions):
        print(f"  House size: {size:>6} sq ft")
        print(f"    Actual price:    ${actual:,.0f}")
        print(f"    Prediction:      ${pred:,.0f}")
        print()

    # =================================================================
    # STEP 2: Compute errors
    # =================================================================
    # Why compute error?
    # Because we need to know, for each house, whether we guessed
    # too high or too low. This is the raw difference.
    print("=" * 60)
    print("STEP 2: Compute errors")
    print("=" * 60)
    print("Error = Prediction - Actual")
    print("Positive = too high. Negative = too low. Zero = perfect.")
    print()

    errors = model.compute_error(predictions, actual_prices)

    for size, actual, pred, err in zip(house_sizes, actual_prices, predictions, errors):
        direction = "too high" if err > 0 else "too low" if err < 0 else "perfect"
        print(f"  House size {size}: Error = {pred:,.0f} - {actual:,.0f} = {err:>10,.0f} ({direction})")
    print()

    # =================================================================
    # STEP 3: Compute loss (MSE)
    # =================================================================
    # Why compute loss?
    # Because we want ONE number that fairly summarizes all errors.
    # Loss lets us compare two models: the one with lower loss is better.
    print("=" * 60)
    print("STEP 3: Compute loss (MSE)")
    print("=" * 60)
    print("Loss = average of (error squared)")
    print("This is one number telling us how bad our model is. Lower is better.")
    print()

    loss = model.compute_loss(predictions, actual_prices)
    print(f"  Loss = {loss:,.2f}")
    print()

    # =================================================================
    # STEP 4: Compute gradients
    # =================================================================
    # Why compute gradients?
    # Because we want to know WHICH WAY to turn the knobs (weight and bias)
    # to make the loss go down. The gradient is like a compass pointing
    # toward higher loss — so we should walk the opposite direction.
    print("=" * 60)
    print("STEP 4: Compute gradients")
    print("=" * 60)
    print("dw tells us how to adjust weight. db tells us how to adjust bias.")
    print()

    dw, db = model.compute_gradients(house_sizes, predictions, actual_prices)

    print(f"  dw (gradient for weight) = {dw:,.2f}")
    print(f"  db (gradient for bias)   = {db:,.2f}")
    print()

    # Explain the sign clearly.
    # Why does sign matter?
    # Because it tells us whether to increase or decrease each parameter.
    print("Sign explanation:")
    print("  If gradient is positive, we should DECREASE the parameter.")
    print("  If gradient is negative, we should INCREASE the parameter.")
    print()

    if dw > 0:
        print(f"  dw is positive ({dw:,.2f}) → DECREASE weight")
    elif dw < 0:
        print(f"  dw is negative ({dw:,.2f}) → INCREASE weight")
    else:
        print(f"  dw is zero → weight is already perfect")

    if db > 0:
        print(f"  db is positive ({db:,.2f}) → DECREASE bias")
    elif db < 0:
        print(f"  db is negative ({db:,.2f}) → INCREASE bias")
    else:
        print(f"  db is zero → bias is already perfect")
    print()

    # =================================================================
    # STEP 5: Closing note
    # =================================================================
    # Why summarize?
    # Because beginners need to see the big picture: we measured everything
    # but we have not changed anything yet. That change is Phase 3.
    print("=" * 60)
    print("STEP 5: Summary")
    print("=" * 60)
    print()
    print("We now know HOW wrong we are (loss) and WHICH way to turn")
    print("the knobs (gradients).")
    print()
    print("In Phase 3, we will learn how to use the gradients to")
    print("automatically adjust the weight and bias.")
    print()
    print("=" * 60)
