# Phase 115 Summary: Structured Generation and Constrained Decoding

## What We Learned

1. **Constrained decoding enforces grammar at the token level.** It is not prompt engineering or post-hoc validation; it physically removes invalid tokens from the sampler's distribution.
2. **Grammar-based generation compiles a schema into a finite-state machine** that intersects with the tokenizer vocabulary. At each step, only tokens that keep the partial output valid are allowed.
3. **Structured output reliability requires engineering for six-nines, not nine-tens.** A 0.1% failure rate becomes thousands of errors per day at scale. Temperature = 0, batch decoding, and fallback parsers close the gap.
4. **The trade-off is latency for certainty.** Constrained decoding adds compute overhead, but it eliminates retry storms and downstream crashes.

## Prerequisites

- Phase 20: Sampling and Temperature (stochastic generation basics)
- Phase 50: Evaluating Language Models (metrics, verifiers, benchmarks)
- Phase 110: Test-Time Compute Scaling (search and refinement)

## Recommended Reading Order

1. `what_is_constrained_decoding.md` — Token-level masking, FSMs, and why prompts are insufficient
2. `what_is_grammar_based_generation.md` — JSON schema to grammar to token mask pipeline
3. `what_is_structured_output_reliability.md` — 99.99% reliability, batch overhead, and production safeguards
4. `SUMMARY.md` — Phase recap and curriculum connections

## Visual Outputs

- `src/phase115/mask_comparison.png` — Probability distribution before and after masking for a representative decoding step.
- `src/phase115/valid_mask_heatmap.png` — Valid token mask across all decoding steps in the toy grammar.

## Navigation

- **Previous:** Phase 114 (see curriculum)
- **Next:** Phase 116: Automated Red-Teaming and Scalable Oversight
