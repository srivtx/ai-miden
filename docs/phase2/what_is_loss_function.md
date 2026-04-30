# What is a Loss Function?

---

## 1. Definition (very simple)

A **loss function** is a function that takes all the individual errors from every example and combines them into **ONE single number** that tells you how bad the model is overall.

Think of it like averaging all your mistakes into one score. Instead of looking at 100 separate wrong answers, you get one score that says "you got a 72 out of 100."

---

## 2. Why it exists

Imagine you have 1,000 examples. If you looked at 1,000 separate errors, your brain would melt. You couldn't easily decide "is my model getting better or worse?"

You need **ONE number** to tell you:
- "Your model is terrible" (huge number)
- "Your model is pretty good" (small number)

The loss function creates that single number. It is like turning a messy pile of data into one simple score.

---

## 3. Real-life analogy

Imagine you are in school and you have 6 test scores:

- Math: 85
- Science: 90
- History: 78
- English: 92
- Art: 88
- PE: 95

Instead of carrying around 6 numbers everywhere, you compute one **GPA** (like 88.0). That one number tells you how you are doing overall.

The loss function does the exact same thing for your model's errors. It takes all the individual mistakes and squishes them into one overall score.

---

## 4. Tiny numeric example

Let's look at a real loss function called **Mean Squared Error (MSE)**.

Suppose we have a model that predicts house prices. Here are three examples:

**Example 1:**
- Actual price: 10
- Predicted price: 8
- Error: 8 − 10 = **−2**
- Squared error: (−2)² = **4**

**Example 2:**
- Actual price: 20
- Predicted price: 23
- Error: 23 − 20 = **+3**
- Squared error: (3)² = **9**

**Example 3:**
- Actual price: 30
- Predicted price: 28
- Error: 28 − 30 = **−2**
- Squared error: (−2)² = **4**

Now we combine them:
- Total squared error = 4 + 9 + 4 = **17**
- Mean squared error = 17 ÷ 3 = **5.67**

**Why do we square the errors?**

If we just added the raw errors (−2 + 3 + −2 = −1), the negatives and positives would cancel each other out. That would hide how bad we really are! Squaring makes every error positive so they all count against us.

---

## 5. Common confusion

**Loss is NOT the same as error.**

- **Error** is per-example. It is like measuring how far ONE arrow landed from the bullseye.
- **Loss** is the overall score. It is like measuring the average distance of ALL your arrows from the bullseye.

Also remember: **a lower loss is better.**

- Zero loss means perfect predictions (you hit the bullseye every time).
- A huge loss means your model is way off (you missed the target completely).

---

## 6. Where it is used in our code

In our code, after we compute predictions for all our house examples, we will use a loss function (MSE) to compute **one number** that tells us how good or bad our current **weight** and **bias** are.

Then we will try to make that number as small as possible. The smaller the loss, the better our model is at predicting house prices!
