# What Is Negative Sampling?

## 1. Why it exists (THE PROBLEM first)
Skip-gram needs to compare the correct context word against every single word in the vocabulary (50,000+ words) to compute the softmax loss. That is computationally expensive and slow for every single training step.

## 2. Definition (very simple)
Negative sampling is an approximation technique that updates only the correct (positive) word pair and a small handful of randomly chosen (negative) word pairs, instead of all words in the vocabulary.

## 3. Real-life analogy
Police lineup. Instead of checking the suspect against every person in the city, you show them alongside 5 random people. If the witness still picks the suspect, you can be confident. You didn't need the whole city to verify.

## 4. Tiny numeric example
Correct (positive) pair: ("cat", "sat")
Negative samples (3 random words): "apple", "car", "blue"
Pairs to update:
1. ("cat", "sat") — positive, should score high
2. ("cat", "apple") — negative, should score low
3. ("cat", "car") — negative, should score low
4. ("cat", "blue") — negative, should score low

Instead of updating 50,000 output weights, we update only 4. Speedup: ~12,500x.

## 5. Common confusion
- "Are negative words actually wrong?" They are randomly sampled, so most are unrelated. That's the point.
- "Does negative sampling hurt accuracy?" Slightly, but the massive speed gain makes it practical to train on far more data, which usually wins.
- "How many negatives should we sample?" Common choices are 5–20, depending on dataset size.
- "Is this only for skip-gram?" No. It is used in many contrastive learning setups.
- "Do we sample negative words uniformly?" Often no—frequent words like "the" are down-sampled to avoid being negatives too often.

## 6. Where it is used in our code
Applied inside the skip-gram training step: after selecting the true context word, we draw a small set of random negative words and compute the loss only over this tiny subset.
