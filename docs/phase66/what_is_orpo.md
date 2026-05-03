# What is ORPO?

## 1. Why it exists (THE PROBLEM first)

DPO simplified RLHF, but it still requires two separate training stages: first
you run Supervised Fine-Tuning (SFT) to get a model that follows instructions,
then you run DPO to align it with preferences. Each stage needs its own
dataset, hyperparameter tuning, and compute budget. Researchers asked: can we
combine SFT and preference optimization into a single training step?

## 2. Definition (very simple)

Odds Ratio Preference Optimization (ORPO) is a method that jointly optimizes a
language model on instruction-following data and preference data in a single
stage. It adds a preference term to the standard SFT loss so the model learns
to answer correctly AND prefer better answers at the same time.

## 3. Real-life analogy

Imagine a cooking school. SFT is the theory class where you read recipes. DPO
is the taste-test lab where you compare dishes. ORPO is a hands-on kitchen
where the instructor gives you a recipe, you cook it, and immediately the class
tastes your dish against a bad version and learns why yours is better — all in
one session.

## 4. Tiny numeric example

Suppose the policy outputs probabilities for two responses:

- Chosen (good): p = 0.55
- Rejected (bad): p = 0.45

SFT loss (negative log-likelihood of chosen):

```
L_SFT = -log(0.55) = 0.598
```

Odds of chosen: 0.55 / (1 - 0.55) = 1.222
Odds of rejected: 0.45 / (1 - 0.45) = 0.818
Log-odds ratio: log(1.222) - log(0.818) = 0.200 - (-0.201) = 0.401

Preference term with lambda = 0.5:

```
L_pref = -log(sigmoid(0.401)) = -log(0.599) = 0.513
```

Total ORPO loss:

```
L_ORPO = L_SFT + lambda * L_pref
       = 0.598 + 0.5 * 0.513
       = 0.854
```

If training increases chosen probability to 0.70:

```
L_SFT = -log(0.70) = 0.357
Odds chosen = 2.333, odds rejected = 0.429
Log-odds ratio = 0.847 - (-0.846) = 1.693
L_pref = -log(sigmoid(1.693)) = -log(0.845) = 0.168
L_ORPO = 0.357 + 0.5 * 0.168 = 0.441
```

The loss dropped because the model simultaneously learned to generate the
chosen response and to distinguish it from the rejected one.

## 5. Common confusion (5+ bullet points)

- **"ORPO does not need preference data."** It does. The preference data is
mixed with the SFT data during training. Without preference pairs, the
odds-ratio term vanishes and ORPO becomes plain SFT.
- **"ORPO eliminates the reference model because it is better."** ORPO
eliminates the reference model because it uses odds ratios instead of
log-probability differences against a reference. This is a side effect of the
math, not necessarily an improvement in all cases.
- **"Lambda controls learning rate."** Lambda trades off between learning the
response format (SFT) and learning preferences (odds ratio). A higher lambda
prioritizes alignment over fluency.
- **"ORPO is always faster than DPO."** ORPO saves one training stage, but each
ORPO step computes two loss terms. The total wall-clock time depends on dataset
size and hardware.
- **"Odds ratio is the same as probability ratio."** Odds = p / (1-p). If
p=0.9, odds=9. If p=0.5, odds=1. The odds ratio amplifies differences when
probabilities are near 1 or 0, making it more sensitive than a raw probability
ratio.
- **"ORPO can train on only rejected examples."** Both chosen and rejected are
needed to compute the odds ratio. Without both, there is no comparison signal.

## 6. Where it is used in our code

`src/phase66/phase66_dpo_orpo.py` computes the ORPO loss step-by-step, showing
how the SFT term and the odds-ratio term combine. `src/phase66/phase66_dpo_orpo_colab.py`
demonstrates full ORPO training with the TRL ORPOTrainer on a combined
instruction and preference dataset.
