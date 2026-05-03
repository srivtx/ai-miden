# What Is A/B Testing?

## 1. Why It Exists (THE PROBLEM)

You change the color of a "Buy" button from green to red and sales jump 10%. Did the color cause the increase, or was it a holiday weekend? Without a controlled comparison, you cannot know if your intervention worked or if external factors changed simultaneously. You need a way to compare two worlds: one with the change, and one without, under identical conditions.

## 2. Definition

A/B testing (randomized controlled trial) is an experiment where subjects are randomly assigned to a control group (A) or a treatment group (B), and the difference in outcomes is attributed to the treatment alone—because randomization balances all other factors.

## 3. Real-Life Analogy

Imagine two identical gardens. You sprinkle fertilizer on one and leave the other alone. If the fertilized garden grows taller tomatoes, you can blame the fertilizer—because random placement ensured both gardens got the same sunlight and rain on average. A/B testing is the digital equivalent: random assignment neutralizes hidden biases.

## 4. Tiny Numeric Example

A website tests a new headline. 100 users are randomly split:

| Group    | Users | Conversions | Rate |
|----------|-------|-------------|------|
| Control  | 50    | 10          | 20%  |
| Treatment| 50    | 16          | 32%  |

Naive difference: 32% - 20% = 12 percentage points.

But is this real or noise? A two-proportion z-test yields p = 0.11. At α = 0.05, we fail to reject the null hypothesis. The observed lift might be a fluke. A/B testing forces us to quantify uncertainty before declaring victory.

## 5. Common Confusion

- **"A higher conversion rate in B always means B is better."** Small samples produce large random swings; statistical significance (p-value) matters.
- **"You can stop the test early when you see a winner."** Peeking inflates false-positive rates dramatically (the "optional stopping" problem).
- **"Randomization guarantees perfect balance."** It guarantees balance *in expectation*; any single experiment can have imbalance.
- **"P-value tells you the probability the treatment works."** A p-value of 0.03 does not mean a 97% chance of effect; it means a 3% chance of seeing this data if there were no effect.
- **"A/B tests work on any sample size."** Underpowered tests cannot detect small but meaningful effects, leading to false negatives.
- **"Statistical significance equals business significance."** A 0.1% lift can be statistically significant with millions of users but economically meaningless.

## 6. Where It Is Used in Our Code

In `src/phase79/phase79_causal_inference.py`, we simulate a randomized A/B test by randomly assigning treatment in synthetic data, then compute the Average Treatment Effect (ATE) as the simple mean difference between treated and control groups. We visualize how ATE estimates converge toward the true effect as sample size increases.
