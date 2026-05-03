### 1. Why it exists (THE PROBLEM first)

Supervised learning requires expensive labeled datasets. We needed a way to teach a model deep language understanding **without human annotations**—to let the model learn grammar, facts, and reasoning patterns purely from raw text.

### 2. Definition (very simple)

**Masked Language Modeling (MLM)** is a pre-training objective where a random subset of tokens (typically 15%) in an input sentence is hidden (masked), and the model is trained to predict the original words using only the surrounding context. This forces the model to build rich, bidirectional representations of language.

### 3. Real-life analogy

Think of **Mad Libs**. You are given a sentence with blanks: "The ___ chased the mouse." To fill in the blank, you use the surrounding words—knowing that "chased the mouse" strongly suggests "cat." The better your grasp of English, the more accurately you fill in the blanks. MLM turns all of Wikipedia into one giant Mad Libs worksheet.

### 4. Tiny numeric example

Input:

```
"The [MASK] sat on the mat and looked at the [MASK]."
```

Target predictions:

- Mask 1 → "cat" (logit: 4.2)
- Mask 2 → "mouse" (logit: 3.8)

During training, the model computes cross-entropy loss against these targets. Because it must predict both blanks from the same sentence, it learns that cats sit on mats and look at mice—without ever being explicitly told that rule.

### 5. Common confusion

- **Not every word is masked.** Usually only 15% of tokens are hidden; the rest remain visible so the model has enough context.
- **It is not next-token prediction.** MLM predicts missing words in the middle using both sides; causal language modeling predicts the next word using only the past.
- **The model still sees the full sentence structure.** It is not given a jumbled bag of words; it sees the exact positions of all unmasked tokens.
- **In BERT's variant, the selected token is not always replaced with [MASK].** 10% of the time it is kept unchanged, and 10% of the time it is replaced with a random token, which prevents the model from simply memorizing the mask position.
- **MLM is only a training objective.** At inference time for downstream tasks, you typically do not mask anything; you use the pre-trained representations.

### 6. Where it is used in our code

Used during the unsupervised pre-training phase of any encoder-based model (such as BERT) to learn general language representations before task-specific fine-tuning.
