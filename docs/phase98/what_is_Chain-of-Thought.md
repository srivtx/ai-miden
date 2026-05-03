# What Is Chain-of-Thought?

## Problem
Large language models sometimes fail on multi-step reasoning tasks because they try to jump directly to the answer without explicit intermediate reasoning.

## Definition
Chain-of-Thought (CoT) is a prompting and training technique where the model generates a sequence of intermediate reasoning steps before producing the final answer. This decomposes hard problems into easier subproblems and improves reliability.

## Analogy
Solving a complex puzzle in your head is hard. Writing down each deduction on paper makes it easier to track progress and catch mistakes. CoT is the model "showing its work."

## Example
Prompt: "A train travels 60 mph for 2 hours, then 40 mph for 3 hours. What is the average speed?"
CoT response: "First, distance 1 = 60 * 2 = 120 miles. Second, distance 2 = 40 * 3 = 120 miles. Total distance = 240 miles. Total time = 5 hours. Average speed = 240 / 5 = 48 mph."

## Common Confusion
Chain-of-Thought is not the same as "longer outputs." It specifically means structured, step-by-step reasoning. Simply adding more text without logical steps does not constitute CoT.

## Code Location
See `src/phase98/phase98_system2_reasoning.py` for a toy simulation of reasoning chains.
