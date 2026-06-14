# What Is Probability?

**The Problem:** You have a coin. You flip it 10 times. You get 7 heads. Is the coin biased? You have a neural network. It outputs 0.7 for "cat" and 0.3 for "dog". What does 0.7 *mean*? You have a generative model that samples images. Some look real, some look fake. How do you *measure* how realistic they are? All of these questions require a *formal* notion of probability.

**Definition:** *Probability* is a function $P$ from events to real numbers in $[0, 1]$ that satisfies:
1. $P(\Omega) = 1$ (the probability of the whole space is 1)
2. $P(A \cup B) = P(A) + P(B)$ for disjoint $A, B$ (additivity)
3. $P(A) \geq 0$ for all $A$ (non-negativity)

This is the *Kolmogorov axioms*. Everything in probability theory is derived from these three rules.

**Two interpretations** of what $P(A)$ *means*:
- **Frequentist**: $P(A)$ is the long-run frequency of $A$ in repeated trials.
- **Bayesian**: $P(A)$ is a degree of belief in $A$, updated by evidence via Bayes' rule.

Generative models use both. The *data distribution* p_data(x) is frequentist (the empirical distribution of training examples). The *model* distribution p_θ(x) is a parameterized belief about what images look like. We update the belief (train θ) by minimizing the divergence between them.

**How It Works (Step-by-Step):**

1. **Sample space $\Omega$**: the set of all possible outcomes. For a coin flip, $\Omega = \{\text{heads}, \text{tails}\}$. For an image, $\Omega = \mathbb{R}^{H \times W \times 3}$ (a continuous, high-dimensional space).
2. **Event $A \subseteq \Omega$**: a subset of the sample space. "The image is a cat" is an event.
3. **Probability $P(A)$**: a number in $[0, 1]$. $P(\emptyset) = 0$, $P(\Omega) = 1$.
4. **Probability distribution $p$**: a function that gives the probability density at each point. For continuous $\Omega$, $\int_\Omega p(x) dx = 1$.
5. **Joint probability $p(x, y)$**: the probability of $x$ and $y$ together.
6. **Conditional probability $p(x | y) = p(x, y) / p(y)$**: the probability of $x$ given $y$.
7. **Marginal probability $p(x) = \int p(x, y) dy$**: the probability of $x$ ignoring $y$.
8. **Independence**: $x \perp y$ iff $p(x, y) = p(x) p(y)$.

**Real-life analogy:** Probability is a *map of beliefs*. If you have a coin and you say "I believe the probability of heads is 0.5", you are saying "0.5 of my map is heads." If you flip it 10 times and get 7 heads, you update the map: now the heads region is larger. Probability is the math of *updating maps from evidence*.

**Tiny numeric example:** Coin flip. $P(\text{heads}) = 0.5$, $P(\text{tails}) = 0.5$. After 10 flips, you have 7 heads and 3 tails. The empirical probability is now $\hat{P}(\text{heads}) = 0.7$. If the coin is fair, this is unlikely. The probability of getting 7+ heads out of 10 fair flips is $\binom{10}{7} (0.5)^{10} = 120/1024 \approx 0.117$. So there's an 11.7% chance this happened by luck. If you flip 1000 times and get 700 heads, the chance of that happening by luck is astronomically small. So you conclude the coin is biased.

**Common confusion:**

- "Probability = frequency." No, this is only one interpretation (frequentist). Bayesian probability is a *belief*, not a frequency. A doctor saying "you have a 30% chance of this disease" is expressing a belief, not a frequency.
- "p(x) is the probability of x." For *discrete* x, yes. For *continuous* x, p(x) is a *density*, not a probability. The probability of x is 0; the probability of an interval around x is $\int p(x') dx'$. This is why we say "the probability density function" for continuous distributions.
- "High probability = truth." No. Probability is a measure of *belief given evidence*. If your evidence is wrong, your probability is wrong.
- "All probabilities are between 0 and 1." Yes, this is one of the axioms. If you compute a "probability" outside $[0, 1]$, you have made an error.
- "Probabilities are additive only for disjoint events." Yes. For *overlapping* events, you must use inclusion-exclusion.
- "Independent means uncorrelated." Yes, in probability. In statistics, "uncorrelated" means zero covariance, which is weaker than independence. Two variables can be uncorrelated but dependent (e.g., $y = x^2$ has zero correlation but $y$ depends on $x$).

**Key properties:**

- **Sum/integral to 1**: $\sum_x p(x) = 1$ (discrete) or $\int p(x) dx = 1$ (continuous).
- **Chain rule**: $p(x_1, x_2, \ldots, x_n) = p(x_1) p(x_2 | x_1) p(x_3 | x_1, x_2) \cdots$.
- **Bayes' rule**: $p(y | x) = p(x | y) p(y) / p(x)$.
- **Law of large numbers**: as $N \to \infty$, the empirical mean $\bar{x} = \frac{1}{N} \sum_i x_i$ converges to the true mean $\mathbb{E}[x]$.
- **Central limit theorem**: the sum of many independent random variables is approximately Gaussian.

**Tech comparison:**

| Concept | Probability | Logic | Frequency |
|---|---|---|---|
| Truth value | Real number in $[0,1]$ | True / False | Count |
| Operations | Sum, integral | AND, OR, NOT | Count |
| Update rule | Bayes' rule | Modus ponens | Maximum likelihood |
| Used in | ML, statistics, physics | Computer science, math | Surveys, A/B testing |

**Connection to generative models:** A generative model is a *learned probability distribution* over data. To train it, you compare its distribution to the data distribution using KL divergence (see `what_is_kl_divergence.md`). To use it, you sample from it (see `what_is_sampling.md`). Both operations require a formal notion of probability.
