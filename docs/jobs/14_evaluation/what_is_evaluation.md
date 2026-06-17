## Why it exists (THE PROBLEM)

You train a new model. You look at 3 samples. They look better. You deploy. Next day: users report worse completions. You don't have a MEASUREMENT to back your intuition. You don't know if "looks better" means 2% improvement or 20% regression on a tail of 5,000 unseen prompts.

**Model evaluation** replaces intuition with numbers. Every model version has a report card: perplexity on held-out code, pass@k on a test suite, BLEU score against reference completions, latency at p50/p95/p99. If the new model scores worse on ANY metric, it doesn't deploy. If all metrics improve, auto-deploy.

**AB testing** compares two models in production. Route 5% of users to the new model, 95% to the old. Measure: completion acceptance rate (does the user keep the suggestion?), edit distance from final code, user satisfaction. After 1 week, if the new model wins on all metrics, promote to 100%.

## Definition (very simple)

**Evaluation metrics for code completion:**

| Metric | What it measures | How |
|---|---|---|
| **Perplexity** | Does the model predict the next token well? | Cross-entropy on held-out code |
| **Exact Match** | Does the model produce the exact right code? | Full match of output vs reference |
| **BLEU** | How close is the completion to the reference? | N-gram overlap |
| **Edit Similarity** | How many keystrokes to fix the completion? | Levenshtein distance |
| **Pass@k** | Can the model solve the problem in k attempts? | HumanEval: 164 Python problems |
| **AST Validity** | Does the completion parse as valid Python? | Fraction that pass `ast.parse()` |
| **Compile Rate** | Does it compile? (for typed languages) | `python -m py_compile` |
| **Acceptance Rate** | Does the user KEEP the suggestion? | Log keystroke: did they delete it? |

The best single metric for code completion: **Edit Similarity**. How many characters does the user delete from the model's suggestion? If the model suggests `return a + b` and the user keeps it (0 deletions), Edit Sim = 1.0. If the model suggests `pretty_repr(cls) == [1]` and the user deletes all of it, Edit Sim = 0.0. THIS is what matters — not BLEU, not perplexity.

## Practice: Evaluation suite for cortexcode

```python
def evaluate_held_out(model, tokenizer, test_files):
    """Compute perplexity on held-out code files."""
    total_loss = 0
    total_tokens = 0
    model.eval()
    with torch.no_grad():
        for filepath in test_files:
            text = Path(filepath).read_text()
            tokens = tokenizer.encode(text)
            # Batch by block_size
            for i in range(0, len(tokens) - block_size, block_size):
                x = torch.tensor([tokens[i:i+block_size]])
                y = torch.tensor([tokens[i+1:i+1+block_size]])
                _, loss = model(x, y)
                total_loss += loss.item() * len(y[0])
                total_tokens += len(y[0])
    return math.exp(total_loss / total_tokens)  # perplexity


def evaluate_completion_quality(model, tokenizer, test_pairs, n_candidates=1):
    """For each (prompt, expected) pair, compute edit similarity."""
    from Levenshtein import distance as levenshtein

    scores = []
    for prompt, expected in test_pairs:
        best_sim = 0
        for _ in range(n_candidates):
            completion = model.generate(tokenizer.encode(prompt), ...)
            d = levenshtein(completion, expected)
            max_len = max(len(completion), len(expected))
            sim = 1 - d / max_len
            best_sim = max(best_sim, sim)
        scores.append(best_sim)
    return np.mean(scores)  # average best-of-N edit similarity


def compare_models(model_a, model_b, test_pairs, n_candidates=5):
    """AB test: does model_b beat model_a on edit similarity?"""
    scores_a = evaluate_completion_quality(model_a, tokenizer, test_pairs, n_candidates)
    scores_b = evaluate_completion_quality(model_b, tokenizer, test_pairs, n_candidates)

    # Paired t-test (n=100+ test pairs for significance)
    from scipy import stats
    t_stat, p_value = stats.ttest_rel(scores_a, scores_b)

    print(f"Model A (old): {scores_a:.4f}")
    print(f"Model B (new): {scores_b:.4f}")
    print(f"Delta: {scores_b - scores_a:+.4f}")
    print(f"P-value: {p_value:.4f} {'SIGNIFICANT' if p_value < 0.05 else 'NOT significant'}")

    if scores_b > scores_a and p_value < 0.05:
        print("DEPLOY model B.")
    else:
        print("KEEP model A.")
```

## Key properties

| | No evaluation | Evaluation suite |
|---|---|---|
| Deploy decision | "It looks better" | P-value < 0.05 on 3 metrics |
| Regressions detected | Never | Within 5 minutes of training finishing |
| Minimum test size | N/A | 100+ held-out files for ppl, 100+ prompt pairs for edit sim |
| Trust | Intuition (50/50 chance of being wrong) | Statistics (5% chance of being wrong) |

## Common confusion

1. **"Perplexity correlates with quality."** Weakly. Perplexity measures NEXT-TOKEN PREDICTION, which rewards memorization of the training distribution. It doesn't measure whether the completion is USEFUL. A model with perplexity 1.0 that always says "return None" is useless. A model with perplexity 2.0 that gives good suggestions is better. Perplexity is a training diagnostic, not a quality metric.

2. **"1-5 test examples is enough."** No. Five examples can show anything. A model that's 10% worse on 1 example and 2% better on 4 examples looks better. With 5 examples, you need a MASSIVE difference to reach significance. Minimum: 100 held-out files for perplexity, 100 prompt pairs for edit similarity. Statistical power demands sample size.

3. **"AB testing requires a production system."** In Colab, you can't do live AB testing. But you CAN do OFFLINE AB testing: simulate 1000 prompts, measure edit similarity for model A vs model B. This is the same math, just not live traffic. Run it before every deploy decision.

4. **"If the new model is better on all metrics, deploy it."** Not necessarily. Check the DISTRIBUTION, not just the mean. Model B might be better on average but catastrophically worse on 5% of prompts (long-tail regression). Always plot a histogram of per-prompt improvement. If there's a thick left tail (B is much worse on some prompts), investigate before deploying.

## Connection to cortexcode

Add `evaluate_held_out()` and `compare_models()` to the training pipeline. After every training run: compute perplexity on 100 held-out files, compute edit similarity on 100 prompt pairs, compare to the previous best model. Only save the new model if it significantly beats the old one. Automate the quality gate.
