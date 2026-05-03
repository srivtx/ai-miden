# What is Model Explainability?

## 1. Why it exists (THE PROBLEM)

Modern machine learning models — especially deep neural networks — can contain millions or billions of parameters. They are powerful, but they are also **black boxes**: you feed data in, you get a prediction out, and you have no idea *why* the model made that specific choice.

This is fine when the stakes are low (recommending a movie), but dangerous when the stakes are high:
- A loan application is rejected. Was it because of income, or a spurious correlation with zip code?
- A medical model predicts cancer. Which part of the scan convinced it?
- A self-driving car slams the brakes. What did it see?

Without explanations, you cannot debug, trust, audit, or legally justify a model's decisions.

## 2. Definition (very simple)

**Model explainability** is the study of techniques that make a model's behavior understandable to humans. It asks: *"Given this input, why did the model output that?"*

Explainability comes in two flavors:
- **Global explanations**: How does the model behave in general? Which features matter most across the whole dataset?
- **Local explanations**: Why did the model make *this specific* prediction for *this specific* instance?

## 3. Real-life analogy

Imagine a strict bouncer at a club who rejects some people and admits others. You want to understand the rules.

- **Global explanation**: You watch all night and notice he mostly cares about dress code and age. That is a global pattern.
- **Local explanation**: Your friend is rejected. You ask the bouncer why, and he points to her sneakers. That is a local, instance-level reason.

Model explainability gives you both perspectives: the overall "rules of the club" and the specific reason for each decision.

## 4. Tiny numeric example

Consider a tiny logistic model that approves loans:

```
score = 2.0 * income - 1.5 * debt + 0.1 * age
approval = 1 if score > 0 else 0
```

**Global**: The coefficients tell us income matters most (2.0), debt is second (-1.5), and age barely matters (0.1).

**Local**: For Alice with `[income=3, debt=2, age=30]`:
```
score = 2.0*3 - 1.5*2 + 0.1*30 = 6 - 3 + 3 = 6 > 0  → approved
```
Each term tells us exactly how much each feature pushed the score up or down. This model is *inherently interpretable* because it is linear.

Deep neural networks are not linear, so we need extra tools to extract this kind of story.

## 5. Common confusion (5+ bullet points)

- **Explainability vs. interpretability**: These words are often used interchangeably, but pedantically, *interpretability* refers to models that are simple enough to understand by construction (like linear regression), while *explainability* refers to post-hoc tools that probe complex models (like SHAP on a neural net).
- **Higher accuracy does not mean less explainable**: A small random forest can be less interpretable than a large linear model. The issue is model family, not just size.
- **Explanations can be wrong**: An explanation method tells you what the method *thinks* the model is doing. It does not guarantee the model is actually doing that. This is called the "faithfulness" problem.
- **There is no single best explanation**: Different methods (SHAP, LIME, saliency) can disagree. That does not mean one is right and one is wrong; they answer slightly different questions.
- **Attention is not always explanation**: Attention weights show where a model looked, but "looking" does not always mean "caring." A model can attend to a word for syntactic reasons and still base its decision on another word.
- **Fairness and explainability are cousins**: Explainability helps you *find* bias; fairness metrics help you *measure* it. You usually need both.

## 6. Where it is used in our code

- `src/phase75/phase75_xai_numpy.py` — Demonstrates four explanation techniques on the same toy MLP so you can compare their outputs side-by-side.
- `src/phase75/phase75_xai_colab.py` — Uses PyTorch to apply explanation methods to a small neural network with autograd.
