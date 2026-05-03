# What Is Process Reward Model?

## Problem
Outcome reward models (ORM) only score the final answer. They cannot tell *where* in a reasoning chain a mistake occurred, making it hard to train or search over intermediate steps.

## Definition
A Process Reward Model (PRM) assigns a reward to each intermediate step of a reasoning chain, not just the final result. This allows search algorithms to prune bad paths early and provides fine-grained training signal for chain-of-thought models.

## Analogy
A teacher grading only the final answer cannot tell a student which step of a long proof went wrong. A PRM is like a teacher who checks every line of the proof and marks errors immediately.

## Example
In a math problem solved in 10 steps, a PRM might score step 3 as incorrect because of a sign error. A Monte Carlo Tree Search can then backtrack from step 3 and try alternative step 3s, rather than discarding the entire chain after reaching a wrong final answer.

## Common Confusion
PRMs are expensive to train because they require human or automated labels at every step. Do not confuse PRM with "process supervision" in other domains; in reasoning, it specifically means step-level rewards.

## Code Location
See `src/phase98/phase98_system2_reasoning.py` for a simulation of reasoning chains with per-step correctness probabilities.
