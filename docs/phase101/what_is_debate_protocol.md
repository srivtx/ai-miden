# What is Debate Protocol?

## Problem

For very complex claims, a single evaluator may not have the expertise to judge correctness. A dishonest model could exploit this by burying errors in verbose or technical outputs.

## Definition

Debate Protocol is an alignment mechanism where two AI agents argue opposing sides of a question. A human (or weaker model) judges the debate and awards a winner. The agents are trained to expose each other's flaws, making it harder to hide errors. The truth is expected to have an advantage because lies are harder to defend under cross-examination.

## Analogy

In a courtroom, the jury does not investigate the crime scene. Instead, the prosecution and defense present evidence and cross-examine each other. The adversarial process is designed to surface the truth more reliably than a single narrative.

## Example

Two models debate whether a proposed code refactor introduces a bug. Model A claims it is safe; Model B claims it breaks edge case X. They cite specific lines and test cases. The judge evaluates who provided more convincing, verifiable evidence.

## Confusion

Debate Protocol does not guarantee truth. A model could be more persuasive than correct. The protocol assumes that honest arguments are easier to defend, but this is an empirical claim, not a mathematical certainty.

## Code Location

See `src/phase101/phase101_advanced_alignment.py` for a NumPy simulation of a debate-like scoring mechanism where competing proposals are evaluated.
