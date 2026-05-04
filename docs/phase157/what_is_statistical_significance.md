## What Is Statistical Significance Testing?

**The Problem:**
Machine learning is full of randomness: random initialization, random data shuffling, random dropout. Two identical training runs can produce models that differ by 0.5% accuracy. When you compare two different models, how do you know if the difference is due to the architecture or just random luck?

**Definition:**
**Statistical significance testing** is a set of methods for determining whether an observed difference between two models is likely to be genuine or due to random variation. Common tests include bootstrap resampling and paired t-tests.

**Real-life analogy:**
Significance testing is like a coin-flipping experiment. You flip a coin 100 times and get 55 heads. Is the coin biased? Or is 55 just random variation? Significance testing calculates the probability of getting 55+ heads with a fair coin. If that probability is 3%, you conclude the coin is probably biased. If it is 30%, you conclude it is probably fair. In ML, the "coin" is your model's per-sample correctness, and "biased" means "genuinely better."

**Tiny numeric example:**
Model A is correct on samples: [1,1,0,1,1,0,1,1,1,0] → 70%
Model B is correct on samples: [1,0,0,1,1,0,1,0,1,0] → 50%
Paired differences: [0,1,0,0,0,0,0,1,0,0] → Model A wins on 2/10 samples
Paired t-test: t=1.58, p=0.15
Result: NOT significant at p<0.05. With only 10 samples, we cannot conclude A is better.

**Common confusion:**
- **"p < 0.05 means 95% confidence the model is better."** Not exactly. It means that if the models were equally good, there is only a 5% chance of observing a difference this large. It does not mean there is a 95% chance A is better.
- **"Non-significant means the models are equal."** No. It means we do not have enough evidence to conclude they are different. They might be very different, but our sample size is too small to detect it.
- **"Significance testing guarantees correctness."** No. It only controls the false positive rate (Type I error). A significant result can still be a false positive (5% of the time at p<0.05).
- **"You should always use p < 0.05."** The threshold depends on the cost of error. For drug trials, p < 0.01 is common. For A/B testing, p < 0.05 is standard.

**Where it appears in our code:**
`src/phase157/phase157_evaluation_harness.py` — The `bootstrap_significance()` function resamples predictions 1000 times to estimate the distribution of accuracy differences. The `paired_ttest()` function runs a paired t-test on per-sample correctness.
