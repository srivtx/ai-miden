# What is Equalized Odds?

## 1. Why it exists (THE PROBLEM)

Demographic parity forces equal approval rates across groups, but what if one group is truly more qualified? Rejecting qualified applicants from Group A just to match Group B's lower approval rate feels unfair too. The deeper question is: **among people who deserve the positive outcome, are they treated equally?** And conversely: **among people who do not deserve it, are false alarms equally distributed?** Equalized odds exists because fairness should be about equal error rates, not just equal headcounts.

## 2. Definition

**Equalized odds** requires that a classifier's true positive rate (TPR) and false positive rate (FPR) are equal across all groups.

> TPR = P( Y_hat = 1 | Y = 1, G = 0 ) = P( Y_hat = 1 | Y = 1, G = 1 )
> FPR = P( Y_hat = 1 | Y = 0, G = 0 ) = P( Y_hat = 1 | Y = 0, G = 1 )

The **equalized odds violation** is usually measured as the maximum difference in TPR or FPR across groups.

## 3. Real-life analogy

Two basketball coaches scout players. Coach A drafts 80% of players who can actually play (high TPR) and 10% of players who cannot (low FPR). Coach B drafts only 50% of good players and 25% of bad players. Even if both coaches draft the same total number of players, Coach B is unfair to the talented kids from his region. Equalized odds says: if you are good, your chance of being picked should not depend on your zip code.

## 4. Tiny numeric example

A fraud detector flags transactions for 200 users in each group.

| Group | Truly Fraud | Flagged (TP) | TPR   | Truly Safe | Flagged (FP) | FPR   |
|-------|-------------|--------------|-------|------------|--------------|-------|
| A     | 50          | 40           | 80%   | 150        | 15           | 10%   |
| B     | 50          | 40           | 80%   | 150        | 15           | 10%   |

TPR difference = 0%, FPR difference = 0%. Equalized odds is **satisfied**.

Now imagine Group B is treated worse:

| Group | Truly Fraud | Flagged (TP) | TPR   | Truly Safe | Flagged (FP) | FPR   |
|-------|-------------|--------------|-------|------------|--------------|-------|
| A     | 50          | 40           | 80%   | 150        | 15           | 10%   |
| B     | 50          | 25           | 50%   | 150        | 30           | 20%   |

TPR difference = 30%, FPR difference = 10%. Equalized odds is **violated**.

## 5. Common confusion

- **"Equalized odds is the same as equal accuracy."** No. A model can have equal overall accuracy for two groups but very different TPR and FPR if the base rates differ.
- **"If TPR is equal, FPR will automatically be equal too."** No. A model can match TPR across groups while having wildly different FPR. Both must be checked.
- **"Equalized odds is easy to achieve."** No. When the underlying base rates differ across groups, achieving equalized odds often requires accepting lower overall accuracy.
- **"It only applies to binary classification."** While easiest to state for binary cases, the principle extends to multi-class settings via equal error rates per class.
- **"Demographic parity is better than equalized odds."** Neither is universally better. They encode different ethical intuitions and are mathematically incompatible when base rates differ.
- **"Equalized odds fixes algorithmic bias completely."** No. It fixes one specific aspect: error-rate equality. The model might still use a proxy for group membership in ways that are problematic.

## 6. Where it is used in our code

In `src/phase76/phase76_fairness_bias.py`, we compute the true positive rate and false positive rate for each group separately. We then report the equalized odds violation as the largest gap between any of these rates. After applying sample reweighting, we show that the TPR and FPR gaps shrink, moving the classifier closer to equalized odds. In `src/phase76/phase76_fairness_bias_colab.py`, we use fairlearn to measure equalized odds violations on a real dataset and compare them before and after applying a fairness constraint.
