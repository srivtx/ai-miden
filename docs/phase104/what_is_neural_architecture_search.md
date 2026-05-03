# What is Neural Architecture Search?

## Problem

Designing neural networks is historically a manual, expert-driven process. Researchers propose architectures based on intuition and trial and error. This does not scale to the vast space of possible layer types, connectivity patterns, and hyperparameters.

## Definition

Neural Architecture Search (NAS) is an automated process for discovering optimal neural network architectures. A search algorithm (e.g., reinforcement learning, evolutionary search, or gradient-based methods like DARTS) explores a defined search space of operations and connections to find architectures that maximize performance on a validation set.

## Analogy

Instead of an architect designing a single building by hand, a city planner writes a program that generates thousands of floor plans, tests them for energy efficiency and space usage, and keeps the best ones. The search algorithm is the program; the floor plans are the neural architectures.

## Example

A NAS system searches over convolutional cell structures for image classification. It defines a DAG where each node is a feature map and each edge can be one of several operations (3x3 conv, 5x5 conv, max pool, etc.). After training 100 sampled architectures, it discovers a cell that outperforms the manually designed ResNet on CIFAR-10.

## Confusion

NAS is not magic. It requires massive compute because each candidate architecture must be trained and evaluated. One-shot NAS methods like DARTS reduce this cost by weight sharing, but they still require careful design of the search space and regularization.

## Code Location

See `src/phase104/phase104_architecture_search.py` for a NumPy demo comparing a structured architecture (locally connected) versus a fully connected network on a spatial task.
