# What Is Error?

### 1. Definition (very simple)

Imagine you are guessing the weight of a watermelon. You guess 10 pounds, but it actually weighs 12 pounds. You were off by 2 pounds.

In AI, **error** is the same idea: it is **the difference between what our model predicted and what the actual true answer is**.

If our model predicts a number and the real number is different, the gap between them is the error.

Mathematically, it is simply:

**prediction - actual**

Or sometimes people write it the other way:

**actual - prediction**

Either way, the number tells us **how far off we were**.

---

### 2. Why it exists

If we never measure how wrong we are, we can never improve.

Think of error as a **feedback signal**. It is like a teacher telling you, "You were 5 points away from the right answer." That signal helps you adjust your next guess.

Without measuring error, we would be **shooting arrows in the dark**. We would have no idea whether to aim higher, lower, or stay the same.

So error exists to **guide our model toward better predictions**.

---

### 3. Real-life analogy

Imagine you are practicing **archery**.

- The **bullseye** in the center of the target is the **true answer**.
- The **arrow you shoot** is your **prediction**.
- The **distance from your arrow to the bullseye** is your **error**.

If your arrow lands exactly in the center, the distance is zero. That means your error is zero — a perfect prediction!

If your arrow lands two inches above the bullseye, your error is two inches. Now you know to aim a little lower next time.

Every shot gives you feedback (your error), and that feedback helps you get better.

---

### 4. Tiny numeric example

Let's say our model is trying to predict house prices.

**Example 1: Underestimating**
- Actual price of the house: **$300,000**
- Model's prediction: **$250,000**
- Error: **$250,000 - $300,000 = -$50,000**

We were **$50,000 too low**. The negative sign tells us our guess was below the real price.

**Example 2: Overestimating**
- Actual price of the house: **$400,000**
- Model's prediction: **$450,000**
- Error: **$450,000 - $400,000 = +$50,000**

We were **$50,000 too high**. The positive sign tells us our guess was above the real price.

**Key takeaway:** Error can be **positive** (too high) or **negative** (too low). The sign matters because it tells us which direction we missed.

---

### 5. Common confusion

**"Error" does not mean you made a mistake on purpose.**

In everyday language, "error" sounds like a human screw-up. In AI, it is just a **measurement of difference**. It is not about blame. It is math.

**Error can be negative, which can be tricky.**

If you add a negative error and a positive error together, they can cancel each other out. For example, being $50,000 too low on one house and $50,000 too high on another does not mean you are perfectly accurate overall. It means the errors canceled.

Because of this, we often do something extra to make error easier to work with later (like squaring it so negatives go away), but that is a topic for another day.

For now, just remember: **error is simply how far off you are, and it can be positive or negative.**

---

### 6. Where it is used in our code

In our project, after our **LinearRegression** model makes a prediction, we will **subtract the actual price from the predicted price** to compute the error.

That error tells us two things:
1. **How big** our miss was.
2. **Which direction** we missed (too high or too low).

This information tells us whether we need to **turn our parameter knobs up or down** to get closer to the truth on the next try.

Error is the compass that steers our model toward learning.
