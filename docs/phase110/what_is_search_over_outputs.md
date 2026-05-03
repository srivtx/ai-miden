# What is Search Over Outputs?

## 1. Problem Statement

Language models generate text autoregressively, one token at a time. A single sampled path through the token space may miss better answers that diverge at an early token. We need ways to explore the output space systematically rather than committing to one path.

## 2. Definition

**Search Over Outputs** is the practice of generating multiple candidate outputs and using a search algorithm to select or combine them. Methods include best-of-N sampling, beam search, tree-of-thoughts, and Monte Carlo Tree Search (MCTS) applied to reasoning steps. The goal is to find higher-quality solutions in the output distribution.

## 3. Analogy

Imagine navigating a maze. Instead of picking one path and hoping it leads to the exit, you send out multiple explorers. Each reports back, and you choose the path with the best outcome. Search over outputs is sending those explorers into the space of possible answers.

## 4. Example

In mathematical reasoning, a model generates multiple solution chains. A verifier scores each chain. A tree search expands promising partial solutions and prunes low-scoring branches, eventually returning the highest-scoring complete proof.

## 5. Common Confusion

Search over outputs is NOT just generating more samples and picking randomly. It requires a scoring or verification mechanism to discriminate good outputs from bad. Without a verifier, increasing N may not help because low-quality samples dilute the pool.

## 6. Code Location

See `src/phase110/phase110_test_time_compute.py` for a NumPy simulation of best-of-N sampling with a verifier.
