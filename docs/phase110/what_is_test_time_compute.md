# What is Test-Time Compute?

## 1. Problem Statement

Scaling model size (parameters, training data) is expensive and hits diminishing returns. However, at inference time, we often have more compute available than we use. Can we trade inference-time computation for better results without making the model bigger?

## 2. Definition

**Test-Time Compute** refers to spending additional computation during inference (test time) to improve output quality. Instead of generating a single greedy or sampled output, the model uses extra compute to search, verify, refine, or reason through multiple candidate solutions before returning an answer.

## 3. Analogy

Think of a student taking a math test. A rushed student writes the first answer that comes to mind. A careful student spends extra time checking their work, trying alternate methods, and verifying the result. Test-time compute is that extra careful effort applied at inference.

## 4. Example

A code generation model produces 20 candidate programs for a programming problem, runs them against test cases, and returns the one that passes the most tests. The model itself did not grow, but the answer quality improved because more inference compute was spent evaluating candidates.

## 5. Common Confusion

Test-time compute is NOT the same as training longer or using a bigger model. It is purely an inference-time strategy. It also does not guarantee improvement if the search or verification mechanism is poorly designed.

## 6. Code Location

See `src/phase110/phase110_test_time_compute.py` for a NumPy simulation of best-of-N sampling and accuracy vs N trade-off.
