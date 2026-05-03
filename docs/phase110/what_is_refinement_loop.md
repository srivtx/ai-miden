# What is a Refinement Loop?

## 1. Problem Statement

Even the best models sometimes produce outputs with minor errors—wrong facts, poor grammar, or logical inconsistencies. Instead of accepting the first draft, we can treat the output as a rough version and iteratively improve it.

## 2. Definition

A **Refinement Loop** is an inference-time strategy where a model generates an initial output, then critiques and revises it over multiple iterations. Each pass can correct errors, add detail, or restructure the response. This mimics human writing and editing processes.

## 3. Analogy

Writing an essay. Your first draft is rough. You read it, mark errors, rewrite sections, and repeat. A refinement loop is that same process automated: generate, critique, revise, critique, revise, until satisfied or a budget is exhausted.

## 4. Example

A summarization model produces a first summary. A second pass checks for factual consistency against the source. A third pass improves conciseness. After three iterations, the summary is more accurate and readable than the initial draft.

## 5. Common Confusion

Refinement loops are NOT the same as training with human feedback (RLHF). RLHF happens during training. Refinement loops happen at inference time and do not update model weights. They are also not guaranteed to converge—poorly designed loops can introduce new errors.

## 6. Code Location

See `src/phase110/phase110_test_time_compute.py` for a NumPy simulation showing how best-of-N and refinement improve accuracy.
