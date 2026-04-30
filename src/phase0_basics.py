# Phase 0: The Very Basics - What is AI?
#
# This script is for complete beginners. No fancy words.
# We will learn: What is a function? What is input and output?
# What is a prediction? How does AI learn from examples?

# ============================================================
# PART 1: What is a function?
# ============================================================
#
# Think of a function like a blender. You put something in (fruit),
# the blender does something to it (chops and mixes),
# and you get something out (a smoothie).
#
# In math and programming, a function takes an INPUT,
# does something with it, and gives you an OUTPUT.


def add_two(x):
    """
    A function is like a blender: put something in, get something out.

    We put a number IN (call it 'x'),
    and we get a number OUT (x + 2).
    """
    return x + 2


# ============================================================
# PART 2: What is a prediction?
# ============================================================
#
# A prediction is a smart guess.
# You look at what happened in the past (examples),
# you notice a pattern,
# and you use that pattern to guess what will happen next.
#
# Example: Imagine a pizza shop.
# You notice these prices on the menu:
#   - Size 10 inches -> $5
#   - Size 12 inches -> $6
#   - Size 14 inches -> $7
#
# What is the pattern?
# If you look closely: size * 0.5 = price
#   10 * 0.5 = 5
#   12 * 0.5 = 6
#   14 * 0.5 = 7
#
# Now you can PREDICT the price of a pizza you have never seen before!


def predict_pizza_price(size):
    """
    Predicts the price of a pizza based on its size.

    We looked at real examples from a pizza shop
    and discovered the pattern: price = size * 0.5

    So this function takes a size (input) and returns a price (output).
    """
    return size * 0.5


# ============================================================
# PART 3: Running the examples
# ============================================================
# The block below only runs when you run this file directly.
# It won't run if you import this file into another file.

if __name__ == "__main__":

    print("=" * 60)
    print("WELCOME TO PHASE 0: THE BASICS")
    print("=" * 60)
    print()

    # --- Example 1: A simple function ---
    print("Part 1: A Simple Function (add_two)")
    print("-" * 40)

    result1 = add_two(3)
    print("Input: 3, Output:", result1)

    result2 = add_two(10)
    print("Input: 10, Output:", result2)
    print()

    # --- Example 2: Learning from examples to make predictions ---
    print("Part 2: Making Predictions (Pizza Prices)")
    print("-" * 40)
    print("We saw these examples at the pizza shop:")
    print("  Size 10 inches -> $5")
    print("  Size 12 inches -> $6")
    print("  Size 14 inches -> $7")
    print()
    print("The pattern we discovered: size * 0.5 = price")
    print()

    # Show predictions for sizes we have already seen
    print("Let's check our prediction rule against the examples:")
    print("Input: 10, Output (Prediction):", predict_pizza_price(10))
    print("Input: 12, Output (Prediction):", predict_pizza_price(12))
    print("Input: 14, Output (Prediction):", predict_pizza_price(14))
    print()

    # Show prediction for a NEW size we have never seen before
    print("Now let's predict the price of a NEW pizza size we have never seen:")
    new_size = 16
    predicted_price = predict_pizza_price(new_size)
    print(f"Input: {new_size}, Output (Prediction): {predicted_price}")
    print()

    # Explain the big idea
    print("=" * 60)
    print("THE BIG IDEA:")
    print("=" * 60)
    print()
    print(
        "This is a very simple AI idea. We looked at examples, "
        "found the pattern, and now we use that pattern to make "
        "predictions on new sizes we have never seen before."
    )
    print()
    print("Real AI does the same thing, just with much more complicated")
    print("patterns and millions of examples!")
    print()
