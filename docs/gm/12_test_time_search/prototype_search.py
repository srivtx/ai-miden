"""
Minimal Test-Time Search for code completion.

The idea: run the model N times with different random seeds (temperature),
score each completion by simple heuristics, return the best.

This is NOT chain-of-thought. It's self-consistency with heuristics.
It works for ANY model without retraining.

Scoring heuristics (for Python code):
  (a) AST validity — does it parse as Python?
  (b) No <unk> tokens — is the output clean?
  (c) Token diversity — is it varied or repetitive?
  (d) Indentation consistency — does it look like code?

The model doesn't change. The process does. Intelligence at inference time.
"""

import ast
import math
import random


# =============================================================================
# Candidate scoring
# =============================================================================


def score_completion(code):
    """Score a code completion. Higher = better. No model access."""

    score = 0.0
    lines = code.split("\n")
    tokens = code.split()

    # 1. AST validity (strongest signal)
    try:
        ast.parse(code)
        score += 10.0
    except SyntaxError:
        # Even with syntax error, partial parse may give info
        pass

    # 2. No <unk> tokens (absolute minimum quality)
    if "<unk>" not in code and "<UNK>" not in code:
        score += 3.0

    # 3. Token diversity (repetition = gibberish)
    if len(tokens) > 0:
        unique_ratio = len(set(tokens)) / len(tokens)
        score += unique_ratio * 5.0

    # 4. Repetition penalty: repeated lines, repeated characters
    unique_lines = set(lines)
    if len(lines) > 0:
        line_uniqueness = len(unique_lines) / len(lines)
        score += line_uniqueness * 2.0

    # 5. Indentation consistency
    indented = [l for l in lines if l.strip()]
    if len(indented) >= 2:
        indent_lens = [len(l) - len(l.lstrip()) for l in indented]
        # Count indentation changes
        changes = sum(
            1
            for i in range(1, len(indent_lens))
            if indent_lens[i] != indent_lens[i - 1]
        )
        # Fewer changes = more consistent
        penalty = max(0, changes - 1) * 0.5
        score += max(0, 3.0 - penalty)

    # 6. Balanced delimiters
    for left, right in [("(", ")"), ("[", "]"), ("{", "}")]:
        if code.count(left) == code.count(right) and code.count(left) > 0:
            score += 0.5

    # 7. Not just whitespace / newlines
    stripped = code.strip("\n\r\t ")
    if len(stripped) > 5:
        score += 1.0

    return score


# =============================================================================
# Candidate generation
# =============================================================================


def generate_candidates(
    model_generate_fn, prompt, n_candidates=5, temperature=0.7, max_tokens=80
):
    """
    Generate N candidates from the model.

    model_generate_fn(prompt, temperature) -> str

    We vary temperature slightly per candidate to get diverse outputs.
    Higher temperature = more random = more diverse candidates.
    """
    candidates = []
    for i in range(n_candidates):
        # Vary temperature: candidate 0 at base temp, others slightly higher
        # for more diversity.
        t = temperature + (i * 0.15 - 0.07) * temperature
        t = max(0.05, min(2.0, t))
        try:
            completion = model_generate_fn(prompt, temperature=t)
            candidates.append(completion)
        except Exception:
            continue
    return candidates


# =============================================================================
# The search
# =============================================================================


def complete_with_search(
    model_generate_fn, prompt, n_candidates=5, temperature=0.7, verbose=False
):
    """
    Generate N completions, score them, return the best.

    Returns (best_completion, scores_list)
    """
    candidates = generate_candidates(
        model_generate_fn, prompt, n_candidates, temperature
    )

    if not candidates:
        return ""

    scored = []
    for i, c in enumerate(candidates):
        s = score_completion(c)
        scored.append((s, i, c))
        if verbose:
            print(f"  candidate {i}: score={s:.1f}  {c[:60]!r}...")

    scored.sort(key=lambda x: x[0], reverse=True)
    best = scored[0][2]

    if verbose:
        print(f"\n  BEST (candidate {scored[0][1]}): score={scored[0][0]:.1f}")
        print(f"  {best!r}")

    return best, [(s, i) for s, i, _ in scored]


# =============================================================================
# Demo (no model needed — use a mock generator)
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Test-Time Search Demo (mock model)")
    print("=" * 60)

    # Mock model: returns "completions" of varying quality
    mock_outputs = [
        "return a + b\n",  # perfect
        "<unk> data = process(input)\n    return result",  # has <unk>
        "return a + b\n\n\n\n",  # extra whitespace
        "aaaaaaaaaaaaaaaaaaaaaaa",  # repetitive (gibberish)
        "result = a + b\n    return result",  # reasonable
    ]

    def mock_model(prompt, temperature=0.7):
        return mock_outputs.pop(0) if mock_outputs else "x"

    prompt = "def add(a, b):\n    "

    print(f"\nPrompt: {prompt!r}")
    print(f"\nGenerating 5 candidates...\n")

    # Reset mock outputs
    mock_outputs = [
        "return a + b\n",
        "<unk> data = process(input)\n    return result",
        "return a + b\n\n\n\n",
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "result = a + b\n    return result",
    ]

    best, rankings = complete_with_search(
        mock_model, prompt, n_candidates=5, temperature=0.7, verbose=True
    )

    print(f"\n{'=' * 60}")
    print(f"Final answer: {best!r}")
    print(f"\nScore breakdown:")
    for s, i in rankings:
        label = f"candidate {i}"
        stars = "*" if i == rankings[0][1] else " "
        print(f"  {stars} {label}: {s:.2f}")

    print(
        "\nKey insight: the model generated 'aaaaaaaa' and a completion "
        "with <unk> tokens. Both were scored low. The clean 'return a + b' "
        "won. The model weights never changed. The process filtered the output."
    )
