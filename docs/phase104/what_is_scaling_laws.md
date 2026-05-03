# What is Scaling Laws?

## Problem

Training large models is expensive. Given a fixed compute budget, should you train a larger model for fewer steps, or a smaller model for more steps? How do you allocate parameters and data optimally?

## Definition

Scaling Laws describe how model performance (loss) predictably improves as a function of compute, model size (parameters), and training data size. The Chinchilla scaling laws showed that many large models were undertrained: for compute-optimal training, model size and data size should be scaled in equal proportions.

## Analogy

Building a factory, you can buy more machines or run existing machines longer. If you buy too many machines but do not run them enough, you waste capital. If you run a small number of machines forever, you hit diminishing returns. Scaling laws tell you the optimal machine-hours balance for a given budget.

## Example

GPT-3 (175B parameters) was trained on ~300 billion tokens. The Chinchilla paper showed that a 70B parameter model trained on 1.4 trillion tokens achieves better performance for the same compute. The law predicted this relationship before the model was trained.

## Confusion

Scaling laws are empirical trends, not physical laws. They hold approximately over the range they were measured, but extrapolation to radically different regimes (e.g., trillion-parameter models with novel architectures) may fail. They also describe average-case loss, not specific capabilities or safety properties.

## Code Location

See `src/phase104/phase104_architecture_search.py` for a NumPy simulation of scaling law trends and sample efficiency differences between architectures.
