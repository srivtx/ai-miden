# What is Code Review?

## Problem it Solves
Even expert programmers make mistakes. In research, a single off-by-one error or incorrect learning rate can invalidate months of experiments. Code review catches these errors before they become conclusions.

## Definition
Code review is a systematic examination of source code by peers. Reviewers check for correctness, readability, test coverage, and alignment with project standards.

## Analogy
Code review is like proofreading a scientific manuscript before submission. The author knows the material, but a fresh set of eyes catches logical gaps, typos, and unclear arguments.

## Example
A researcher submits a training script for review. The reviewer notices that the validation loss is computed on the training set due to a variable reuse bug. Fixing this before publication saves the team from a retraction.

## Common Confusion
Code review is not a substitute for automated testing. Tests verify behavior against specifications; reviews verify that the human-readable code makes sense, is maintainable, and contains no obvious logic errors.

## Code Location
See `src/phase95/phase95_research_communication.py` for a demonstration where peer-review-style refactoring removes a subtle bug hidden in poorly structured research code.
