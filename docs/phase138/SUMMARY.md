# Phase 138 Summary: Test-Time Search (MCTS for LLMs)

## What We Learned

1. **Monte Carlo Tree Search (MCTS) explores the output space strategically instead of sampling blindly.** It expands promising nodes, simulates rollouts, and backpropagates scores to focus compute where it matters most.
2. **Tree search reasoning represents partial solutions as nodes in a search tree.** Each node can be evaluated before completion, enabling early pruning of bad branches — something linear generation cannot do.
3. **Process rewards evaluate every reasoning step, while outcome rewards only score the final answer.** Process rewards provide dense training signal, enable precise error localization, and make MCTS far more efficient than outcome-only leaf scoring.
4. **MCTS outperforms greedy decoding and best-of-N with the same compute budget.** By abandoning bad paths after a few tokens instead of after full generations, it finds correct answers more efficiently on math and reasoning tasks.
5. **The UCB1 formula balances exploration and exploitation.** It ensures that promising branches are explored deeply while under-sampled branches still get a chance to prove their value.

## Prerequisites

- Phase 20: Sampling and Temperature (stochastic generation basics)
- Phase 95: Chain-of-Thought Prompting (structured reasoning generation)
- Phase 110: Test-Time Compute Scaling (best-of-N, search, refinement)
- Phase 137: Advanced Mechanistic Interpretability (model internals)

## Recommended Reading Order

1. `what_is_mcts_for_llms.md` — MCTS adapted for text generation: selection, expansion, simulation, backpropagation
2. `what_is_tree_search_reasoning.md` — Building a tree of reasoning steps and evaluating partial solutions
3. `what_is_process_vs_outcome_reward.md` — Why process rewards are superior to outcome rewards for search and training
4. `SUMMARY.md` — Phase recap and curriculum connections

## Visual Outputs

- `src/phase138/mcts_tree_growth.png` — Simulated MCTS tree growth over iterations, showing uneven depth expansion.
- `src/phase138/search_comparison.png` — Accuracy versus compute budget for random search, beam search, and MCTS.
- `src/phase138/value_estimates.png` — Value estimates converging for promising nodes as backpropagation proceeds.
- `src/phase138/mcts_accuracy_gsm8k.png` — Colab output: accuracy comparison of greedy, best-of-8, and MCTS on GSM8K math problems.
- `src/phase138/reasoning_chains.png` — Colab output: sample reasoning chains found by MCTS versus greedy decoding.

## Navigation

- **Previous:** [Phase 137: Advanced Mechanistic Interpretability (Circuits in 7B Models)](../phase137/SUMMARY.md)
- **Next:** Phase 139 (see curriculum)
