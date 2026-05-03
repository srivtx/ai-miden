# What is Constitutional AI?

## Problem

RLHF (Reinforcement Learning from Human Feedback) works, but it has a bottleneck: human labelers cannot effectively supervise superhuman models. As models become more capable than their human evaluators, standard preference ranking breaks down because humans cannot reliably spot subtle errors in expert-level outputs.

## Definition

Constitutional AI is a method where a model critiques and revises its own outputs according to a set of principles (a "constitution") before training on the revised data. Instead of relying solely on human feedback, the model uses another instance of itself (or the same model in a different mode) to evaluate outputs against written rules.

## Analogy

Imagine a lawyer drafting a contract. Before submitting it, the lawyer runs it through a checklist of ethical guidelines and legal standards. If a clause violates a principle, the lawyer revises it. The checklist is the constitution; the self-review is Constitutional AI.

## Example

A model is asked to give advice on a sensitive medical topic. The constitution includes "Do not provide specific medical diagnoses." The model generates a draft, a critique model flags the violation, and a revision model rewrites the response to be informational without diagnosing.

## Confusion

Constitutional AI does not mean the model has "morals." It is a training procedure. The constitution is written by humans, and the model is trained to behave as if it follows those rules. It can still fail or be jailbroken.

## Code Location

See `src/phase101/phase101_advanced_alignment.py` for a NumPy simulation of a critique-and-revise loop where a critic scores answers and iterative revision improves the score.
