# Part 10: Test-Time Compute

> Intelligence as a process, not a weight. Think at inference time.

## Files

- [what_is_test_time_compute.md](what_is_test_time_compute.md) — Full treatment

## Key insight

Spend compute at INFERENCE, not training. Chain of thought, self-consistency (N tries, majority vote), self-verification, tree search. A 7B model with test-time compute matches a 70B model without. Same weights, smarter process.

## Connection to the curriculum

- Applies to any trained model (no retraining needed)
- Direct neuroscience connection: System 2 (deliberative) vs System 1 (intuitive) from Kahneman
- MSPCH principle: the brain discerns when to use fast vs slow inference

## Code impact

cortexcode: Generate 5 completions per prompt, score by AST validity + uniqueness + no <unk>, return best. ~30 lines. No retraining. Quality gain: 20-40% on coherent vs gibberish.
