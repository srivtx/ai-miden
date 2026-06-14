# Part 0: Foundations

> Before you can build a generative model, you need five foundational concepts. These are the *language* of generative modeling. Every file in the rest of this curriculum uses them.

---

## The five files in this part

| File | One-line summary |
|---|---|
| `what_is_probability.md` | Probability is a measure of belief, not frequency. The math of uncertainty. |
| `what_is_sampling.md` | Sampling is drawing from a distribution. The hard part is doing it for high-dimensional distributions. |
| `what_is_kl_divergence.md` | KL divergence is the distance between two probability distributions. The loss function for generative models. |
| `what_is_elbo.md` | The ELBO is a lower bound on log p(x). The objective you maximize when you can't compute p(x) directly. |
| `what_is_score_function.md` | The score is the gradient of log p(x). The thing diffusion models learn. |

## Reading order

1. **Start with `what_is_probability.md`.** Generative models are probability distributions over images, text, or other data. You need to know what "probability" means formally.
2. **Then `what_is_sampling.md`.** Once you have a distribution, you want to *draw samples* from it. Most of the work in modern generative models is fast sampling.
3. **Then `what_is_kl_divergence.md`.** To train a generative model, you need to measure how close your model's distribution is to the data distribution. KL is the standard measure.
4. **Then `what_is_elbo.md`.** When you can't compute p(x) directly, you maximize a *lower bound* on it. This is the central training trick.
5. **Then `what_is_score_function.md`.** The score is the gradient of log p(x). It is the central object of modern diffusion models. Every diffusion paper talks about "learning the score."

## The synthesis

A generative model is, ultimately, a *differentiable probability distribution* over data. To build one, you need to:
1. **Define a distribution** p(x) parameterized by some θ.
2. **Train θ** to make p_θ(x) close to the data distribution p_data(x). This usually means minimizing KL(p_data || p_θ) or maximizing the ELBO.
3. **Sample** from p_θ(x) to generate new data.

The five concepts above give you the language to do each of these. They are not specific to any model. They are the foundation.

## Where this leads

After Part 0, you can read any generative model paper. The math will look like:
- "We minimize KL(q || p)" — Part 0.3
- "We maximize the ELBO" — Part 0.4
- "We learn the score" — Part 0.5
- "We sample by integrating the reverse SDE" — Part 0.5

You will understand all of it. Go to Part 1.
