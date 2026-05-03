# What Is Load Balancing Loss?

## Problem
In MoE, the gating network might send most tokens to the same few experts, leaving others idle. This defeats the purpose of having many experts and creates throughput bottlenecks (some experts are overloaded while others wait).

## Definition
Load Balancing Loss is an auxiliary loss added during training that penalizes uneven routing. It encourages the gating network to distribute tokens fairly across all experts. A common formulation computes the product of the fraction of tokens routed to each expert and the average routing weight for that expert, summed over experts.

## Analogy
Imagine a call center with 10 agents. If the auto-router always sends calls to agents 1 and 2, the other 8 sit idle. Load balancing loss is like a manager penalty: the more lopsided the distribution, the bigger the fine.

## Example
With 4 experts and 8 tokens, perfect balance means each expert gets 2 tokens. If expert 0 gets 6 tokens and the others get 2, 0, 0, the load balancing loss will be high and push the gate to spread tokens more evenly.

## Common Confusion
Load balancing loss is separate from the main task loss. It is purely a training regularizer. Some frameworks use an "expert choice" variant where tokens choose experts or vice versa, changing how balance is enforced. Do not confuse load balancing loss with the capacity factor, which is a hard limit on tokens per expert.

## Code Location
See `src/phase96/phase96_moe.py` for a NumPy calculation of load balancing loss.
