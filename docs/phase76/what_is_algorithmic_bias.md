# What is Algorithmic Bias?

## 1. Why it exists (THE PROBLEM)

AI models learn from historical data, and history is full of human prejudice. When a bank's old loan records show that women were approved less often than men, a model trained on those records learns to associate "female" with "higher risk" even when income and credit score are identical. The problem is not that the model is malicious; it is that the model is a **mirror**, and the mirror reflects an unfair world. Algorithmic bias exists because **"the data said so" is not the same as "it is fair."**

## 2. Definition

**Algorithmic bias** is a systematic tendency for a model to produce predictions that disadvantage certain groups, stemming from skewed training data, biased labels, or features that act as proxies for protected attributes.

## 3. Real-life analogy

Imagine teaching a child to sort job applicants by showing them only resumes from the last fifty years. The child would notice that most CEOs were men and might start assuming men are better leaders. The child is not evil; they were simply trained on a biased sample. Algorithmic bias is the same: the model learns the patterns we show it, and if those patterns are unfair, the model becomes unfair too.

## 4. Tiny numeric example

Consider 200 loan applicants split evenly between Group A and Group B. Everyone has the same average credit score.

| Group | Qualified (True) | Approved (Model) | Approval Rate of Qualified |
|-------|------------------|------------------|----------------------------|
| A     | 80               | 64               | 80%                        |
| B     | 80               | 40               | 50%                        |

The model learned from historical data where Group B was under-approved. It now replicates that 30-point gap even though both groups are equally qualified. That gap is algorithmic bias.

## 5. Common confusion

- **"The model is biased because the engineers are prejudiced."** No. Most algorithmic bias comes from the training data, not from engineer intent. The model copies patterns it sees.
- **"If I remove the gender column, the bias disappears."** No. Gender correlates with zip code, job title, and shopping habits. The model infers gender from proxy features.
- **"High overall accuracy means the model is fair."** No. A model can be 95% accurate overall while being 50% accurate for one group. Overall metrics hide subgroup failure.
- **"Bias only happens in hiring and lending."** No. Bias appears in healthcare (under-diagnosing certain groups), criminal justice (risk scores), and search results (stereotypical associations).
- **"Fairness is a single number you can optimize."** No. Fairness has many incompatible definitions. Optimizing one often hurts another.
- **"Fixing bias always makes the model worse for everyone."** No. Sometimes a fairer model generalizes better because it stops overfitting to spurious correlations.

## 6. Where it is used in our code

In `src/phase76/phase76_fairness_bias.py`, we deliberately create a synthetic loan dataset where Group B is under-approved relative to their true qualification. We then train a logistic classifier on this biased data and show that the model replicates the historical gap. In `src/phase76/phase76_fairness_bias_colab.py`, we load the real Adult Census dataset and inspect how a standard classifier encodes demographic disparities.
