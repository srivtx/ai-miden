## Why it exists (THE PROBLEM)

You change the tokenizer. The model's output changes. You don't notice for 3 days. Users report "the model is worse now." You have no test to catch this automatically.

ML testing is different from software testing. Software: "did the output match exactly?" ML: "is the output statistically indistinguishable from yesterday?" You can't test exact outputs because sampling introduces randomness. You need statistical tests, snapshot tests, and property-based tests.

## What to test (ML-specific)

### 1. Smoke test: does the model load and produce output?

```python
def test_model_loads():
    model = load_model("cortexcode.pt")
    output = model.generate("def add(a, b):", max_new_tokens=5)
    assert len(output) > 0
    assert "def" in output or "return" in output or "pass" in output
```

### 2. Determinism test: same seed → same output

```python
def test_deterministic():
    torch.manual_seed(42)
    out1 = model.generate("def x():", temperature=0.0)  # greedy = deterministic
    torch.manual_seed(42)
    out2 = model.generate("def x():", temperature=0.0)
    assert out1 == out2, "Same seed + greedy = must be identical"
```

### 3. Snapshot test: is the output distribution consistent?

```python
def test_output_consistency():
    """Generate 100 completions. The distribution should match last week's."""
    torch.manual_seed(42)
    prompts = load_test_prompts()  # 100 held-out prompts
    completions = []
    for p in prompts:
        c = model.generate(p, temperature=0.2)
        completions.append(len(c.split()))  # token count as proxy

    # Statistical test: did the new model produce significantly different
    # length distributions than the reference model?
    from scipy import stats
    ref_lengths = json.load(open("ref_output_lengths.json"))
    _, p_value = stats.ttest_ind(completions, ref_lengths)
    assert p_value > 0.05, f"Output distribution changed (p={p_value:.4f})"
```

### 4. Property test: does the output satisfy invariants?

```python
def test_ast_validity():
    """Most completions should be valid Python."""
    completions = []
    for prompt in test_prompts:
        c = model.generate(prompt)
        completions.append(c)

    valid = sum(1 for c in completions if is_valid_python(c))
    rate = valid / len(completions)
    assert rate > 0.5, f"Only {rate:.0%} of completions are valid Python (target: >50%)"
```

### 5. Regression test: is the model worse than last week?

```python
def test_no_regression():
    """New model must beat (or match) old model on held-out perplexity."""
    new_ppl = evaluate_perplexity(new_model, held_out_files)
    old_ppl = evaluate_perplexity(old_model, held_out_files)
    assert new_ppl <= old_ppl * 1.02, \
        f"Regressed: new={new_ppl:.2f} vs old={old_ppl:.2f}"
```

### 6. Performance regression: is the model slower?

```python
def test_latency_budget():
    """Generation must stay within latency budget."""
    t0 = time.time()
    for _ in range(10):
        model.generate("def add(a, b):", max_new_tokens=50)
    avg = (time.time() - t0) / 10
    assert avg < 0.5, f"Latency {avg:.3f}s exceeds budget of 0.5s"
```

## The test suite structure

```
tests/
├── test_smoke.py          # model loads, produces output
├── test_determinism.py    # same seed = same output
├── test_snapshot.py       # output distribution unchanged
├── test_properties.py     # invariants (AST valid, no <unk>, indented)
├── test_regression.py     # no quality regression
├── test_performance.py    # latency budget
├── test_tokenizer.py      # encode/decode round-trip, vocab size
├── test_cache.py          # KV cache produces same output
└── conftest.py            # shared fixtures (model, tokenizer, test data)
```

Run on every push: `pytest tests/ -x --timeout=120`. CI fails if any test fails. Model doesn't deploy if regression test fails.

## Key property: don't test randomness, test distribution

Testing `model.generate("hello")` 5 times and checking output strings will fail 90% of the time because of sampling randomness. Instead: test statistical properties (perplexity, AST validity rate, token uniqueness ratio) over 100+ samples. Or use `temperature=0.0` (greedy decode) for deterministic tests.

## Common confusion

1. **"ML is stochastic — you can't test it."** You test the MODEL behavior, not individual outputs. Distributional tests (perplexity, validity rate) are stable. Deterministic tests (greedy decode, same seed) are exact. Both catch real bugs.

2. **"Tests slow down development."** A smoke test that loads the model and generates 5 tokens takes 2 seconds. CI runs it on every push. It catches: missing model file, wrong dtype, API change, CUDA OOM. 2 seconds saves hours of debugging.

3. **"I'll test manually."** Manual testing catches ~30% of bugs. You test the happy path ("it works when I try it"). Automated tests also check: error paths (invalid tokenizer? corrupted model?), edge cases (empty prompt? max_length=1?), and regressions (did last commit break something?). The 70% of bugs you miss in manual testing surface in production.

## Connection to our projects

Add `tests/` to ai-miden. The CI workflow (from part 7: CI/CD) runs `pytest tests/` before allowing a merge. Every model version has a test report. Deploy only if all tests pass.

Start with: `test_smoke.py`, `test_determinism.py`, `test_tokenizer.py`. Three files, 30 lines each. Catches 80% of deployment failures.
