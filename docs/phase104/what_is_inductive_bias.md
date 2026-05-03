# What is Inductive Bias?

## Problem

A fully connected neural network with enough parameters can memorize any dataset, but it generalizes poorly on structured data like images or sequences because it must learn structure from scratch with every training example.

## Definition

Inductive Bias is the set of assumptions a learning algorithm uses to predict outputs for inputs it has not seen. In neural networks, it is encoded by the architecture. Convolutions impose translation invariance; recurrent connections impose temporal locality; attention imposes permutation equivariance.

## Analogy

A jigsaw puzzle solver who knows all edge pieces form the border has an inductive bias. They will solve the puzzle faster than someone who treats every piece identically and has no prior assumption about borders. The bias is the assumption; the speedup is better sample efficiency.

## Example

On MNIST, a fully connected network needs millions of parameters to reach 98% accuracy. A small convolutional network with weight sharing and local receptive fields reaches the same accuracy with tens of thousands of parameters because it assumes that a stroke detector useful in the top-left corner is also useful in the bottom-right corner.

## Confusion

Inductive bias is not "bias" in the statistical or social sense. It is a necessary feature of any learning system. Without inductive bias, learning is impossible (the no free lunch theorem). The wrong inductive bias, however, can harm performance (e.g., using a CNN for tabular data with no spatial structure).

## Code Location

See `src/phase104/phase104_architecture_search.py` for a NumPy demo showing how a locally connected layer (spatial inductive bias) outperforms a fully connected layer on a structured grid task.
