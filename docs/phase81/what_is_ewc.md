# What Is EWC?

## 1. Why it exists (THE PROBLEM first)

Catastrophic forgetting happens because training on a new task changes **all** weights indiscriminately. But not all weights are equally important for the old task. Some weights control critical decisions (e.g., "round edges = circle"), while others are barely used. If we could identify which weights matter for Task A and **penalize** changes to them during Task B training, we could preserve old knowledge while still learning new things. That's the problem EWC solves.

## 2. Definition

**Elastic Weight Consolidation (EWC)** is a regularization method that computes how important each weight is for a previously learned task (using Fisher information), then adds a quadratic penalty to the loss function that discourages large changes to important weights.

Loss during Task B:
$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{Task B}} + \frac{\lambda}{2} \sum_i F_i (w_i - w_i^{*})^2$$

Where $F_i$ is the Fisher information for weight $i$, $w_i^{*}$ is the weight's value after Task A, and $\lambda$ controls penalty strength.

## 3. Real-life analogy

Imagine you're renovating a house. The house has load-bearing walls and decorative walls. EWC is like having a structural engineer mark the load-bearing walls in red. When you renovate the kitchen (Task B), you're free to knock down decorative walls, but every time you touch a red-marked wall, you get fined proportionally to how load-bearing it is. The house stays standing while you modernize the kitchen.

## 4. Tiny numeric example

Suppose after Task A, two weights are:
- $w_1 = 1.5$, highly important for Task A (Fisher $F_1 = 10.0$)
- $w_2 = 0.5$, barely matters for Task A (Fisher $F_2 = 0.1$)

During Task B, the gradient wants to update:
- $w_1 \to 0.0$
- $w_2 \to 2.0$

EWC penalty for $w_1$: $10.0 \times (0.0 - 1.5)^2 = 22.5$
EWC penalty for $w_2$: $0.1 \times (2.0 - 0.5)^2 = 0.225$

The optimizer will resist changing $w_1$ (large penalty) but freely change $w_2$ (tiny penalty). Task A knowledge, preserved.

## 5. Common confusion

- **"EWC freezes important weights."** No, it **penalizes** changes. Weights can still move if the new task's gradient is strong enough. It's elastic, not frozen.
- **"Fisher information requires the second derivative (Hessian)."** No. EWC uses a cheap approximation: Fisher $F_i = \mathbb{E}[(\frac{\partial \log p}{\partial w_i})^2]$, which only requires first derivatives (gradients squared and averaged over data).
- **"EWC works for unlimited tasks."** Not perfectly. As tasks accumulate, the quadratic penalties conflict. EWC is great for 2-10 tasks, but degrades for 100+ tasks without extensions.
- **"You need Task A data to compute EWC."** You need Task A data **once** to compute Fisher information after Task A training. After that, EWC operates without Task A data during Task B.
- **"Higher lambda is always better."** Too high $\lambda$ and the model can't learn Task B at all. Too low and forgetting happens. It's a trade-off hyperparameter.
- **"EWC is the same as L2 regularization toward zero."** L2 pulls all weights toward zero. EWC pulls important weights toward their Task A values, and ignores unimportant ones. Completely different.

## 6. Where it is used in our code

In `src/phase81/phase81_continual_learning.py`, after training on Task A, we compute Fisher information by accumulating squared gradients over Task A's data. Then during Task B training, we add the EWC penalty term to the cross-entropy loss. The `compute_fisher()` function samples from Task A, computes gradients, and squares them. The `ewc_loss()` function adds $\frac{\lambda}{2} \sum F_i (w_i - w_i^*)^2$. We compare Task A accuracy: naive (~50%), EWC (~80-90%).

In `src/phase81/phase81_continual_learning_colab.py`, we implement EWC for split MNIST, computing Fisher on the first 5 digits and penalizing changes when learning digits 6-9.