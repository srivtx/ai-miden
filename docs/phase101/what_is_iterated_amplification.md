# What is Iterated Amplification?

## Problem

How do you train a model to solve problems that are too hard for its human supervisor to evaluate? If the task is to prove a complex theorem, the human may not know if the proof is valid.

## Definition

Iterated Amplification is a training framework where a weak supervisor (human or smaller model) breaks a hard problem into smaller subproblems, uses the AI to solve each subproblem, and then assembles the results. Over iterations, the AI learns to solve increasingly complex tasks by leveraging its own capabilities at a simpler level.

## Analogy

A manager who cannot do every employee's job in detail can still verify whether high-level milestones make sense. The manager delegates sub-tasks, checks the logic of the assembly, and the team collectively solves a problem no single person could solve alone.

## Example

A model is trained to summarize a 100-page document. Instead of asking a human to evaluate the full summary, the human evaluates summaries of 10-page chunks. The model learns to assemble good chunk summaries into a good full summary, bootstrapping from human-level to superhuman-level summarization.

## Confusion

Iterated Amplification is not just "breaking things into steps." The key is that the supervisor evaluates the *assembly* of sub-answers, not the sub-answers themselves, allowing the AI to grow beyond the supervisor's direct capability.

## Code Location

See `src/phase101/phase101_advanced_alignment.py` for a NumPy simulation showing iterative improvement through subproblem decomposition and scoring.
