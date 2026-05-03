# What Is Expert Choice?

## Problem
Standard top-k routing lets tokens choose experts. This can lead to "hot" experts receiving more tokens than they can process, requiring capacity factors and padding, which wastes compute.

## Definition
Expert Choice is an alternative routing strategy where each expert selects its top-k tokens, rather than each token selecting its top-k experts. This guarantees a fixed number of tokens per expert, eliminates the need for capacity padding, and naturally balances load.

## Analogy
Instead of students picking their favorite teachers (leading to overcrowded classrooms), each teacher picks the students they are best suited to help. Every classroom has the same number of students, and no one is turned away.

## Example
In a batch of 64 tokens with 8 experts, each expert might choose its top 8 tokens. Every expert processes exactly 8 tokens, so there is no wasted capacity. A token can be chosen by multiple experts or none, which requires handling in the aggregation step.

## Common Confusion
Expert Choice changes the direction of the routing decision but does not eliminate the need for load balancing entirely. If the same tokens are always chosen by all experts, the model may still fail to specialize. It is a design choice, not a magic solution.

## Code Location
See `src/phase96/phase96_moe.py` for a discussion of routing variants in the code comments.
