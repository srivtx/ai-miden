# Phase 101: Advanced Alignment — Summary

This phase explored methods for supervising AI systems that may eventually exceed human evaluative capability, moving beyond standard RLHF toward scalable oversight mechanisms.

## What We Learned

- **RLHF has a supervision ceiling.** As models become more capable than their human labelers, preference ranking breaks down because humans cannot reliably evaluate expert-level outputs. New methods are needed for superhuman alignment.

- **Constitutional AI scales oversight through self-critique.** By having the model evaluate its own outputs against a written constitution, alignment becomes more interpretable and less dependent on expensive per-example human labeling, reducing cost by over 80% in toy simulations.

- **Iterated Amplification bootstraps beyond direct supervision.** A weak supervisor decomposes hard problems into verifiable subproblems, and the model composes its own solutions to grow geometrically in capability while the supervisor's evaluation burden stays constant.

- **Debate Protocol turns model capability against itself.** Two adversarial agents argue opposing sides of a question, and a weaker judge evaluates the debate. The adversarial pressure surfaces errors that a single model might hide in verbose or technical outputs.

- **These approaches are complementary, not competing.** Constitutional AI provides explicit rules, Iterated Amplification provides hierarchical decomposition, and Debate provides adversarial verification. A robust alignment pipeline might use all three.

## Prerequisites

- Familiarity with RLHF and reward modeling (Phase 22).
- Understanding of Chain-of-Thought reasoning (Phase 98).
- Basic knowledge of probability and decision theory.

## Recommended Reading Order

1. `what_is_constitutional_ai.md` — Start with the most practical method: how models can align themselves using written principles.
2. `what_is_iterated_amplification.md` — The theoretical foundation for scalable oversight through problem decomposition.
3. `what_is_debate_protocol.md` — The adversarial complement: how argumentation surfaces hidden errors.

## Visual Outputs

Running `src/phase101/phase101_advanced_alignment.py` produces:

- `phase101_advanced_alignment.png` — Two-panel figure showing:
  - Critique-and-revise score trajectory over 20 iterations, demonstrating convergence.
  - Debate Protocol outcomes across 5 rounds, comparing competing proposal scores side by side.

## Navigation

- **Previous:** Phase 100 — Automated Circuit Discovery (MechInterp)
- **Next:** Phase 102 — Synthetic Data Bootstrapping
