"""
Minimal Fill-in-the-Middle (FIM) training.

Standard autoregressive: the model sees [prefix], predicts [suffix].
  Training: "def add(a, b):\n    return a + b" -> predict each next token

FIM (used by Copilot): the model sees [prefix] [suffix], predicts [middle].
  Training: "def add(a, b):\n    <FILL>  return a + b" -> predict the argument

Why this matters: For code completion, the user's cursor is IN THE MIDDLE
of code. They need the model to fill the gap, not just append at the end.
Training with FIM teaches the model to complete from both sides.

Two common FIM formats:
  PSM (Prefix-Suffix-Middle): <PRE>...<SUF>...<MID>...
  SPM (Suffix-Prefix-Middle): <SUF>...<PRE>...<MID>...
"""

import random


def create_fim_example(
    code, fim_rate=0.5, spm_rate=0.5
):
    """
    Convert a code snippet into a FIM training example.

    Args:
        code: the full code string
        fim_rate: probability of creating a FIM example (vs regular)
        spm_rate: probability of SPM format (vs PSM)

    Returns: (input_tokens, target_tokens), or None if full example
    """
    if random.random() > fim_rate:
        # Standard autoregressive: no FIM
        return None

    tokens = code.split()
    if len(tokens) < 6:
        return None

    # Pick a random span to be the "middle" (what gets filled)
    span_start = random.randint(1, len(tokens) - 3)
    span_end = random.randint(span_start, len(tokens) - 2)
    span_len = span_end - span_start

    prefix = tokens[:span_start]
    middle = tokens[span_start:span_end]
    suffix = tokens[span_end:]

    # Special tokens (in practice, these are added to the tokenizer)
    PRE = "<PRE>"
    SUF = "<SUF>"
    MID = "<MID>"
    EOT = "<EOT>"

    if random.random() < spm_rate:
        # SPM format: <SUF> suffix <PRE> prefix <MID> middle <EOT>
        input_seq = [SUF] + suffix + [PRE] + prefix + [MID]
        target_seq = middle + [EOT]
    else:
        # PSM format: <PRE> prefix <SUF> suffix <MID> middle <EOT>
        input_seq = [PRE] + prefix + [SUF] + suffix + [MID]
        target_seq = middle + [EOT]

    return " ".join(input_seq), " ".join(target_seq)


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Fill-in-the-Middle (FIM) Training Demo")
    print("=" * 60)

    examples = [
        "def add(a, b):\n    return a + b",
        "class Stack:\n    def __init__(self):\n        self.items = []\n    def push(self, item):\n        self.items.append(item)",
        "def process_data(data, verbose=False):\n    if verbose:\n        print('Processing...')\n    result = [x * 2 for x in data]\n    return result",
    ]

    for i, code in enumerate(examples):
        print(f"\n--- Example {i+1} ---")
        print(f"Full code:\n  {code}\n")

        # Force FIM for demo
        result = create_fim_example(code, fim_rate=1.0, spm_rate=i % 2 * 1.0)
        if result:
            inp, tar = result
            fmt = "SPM" if "<SUF>" in inp.split()[0] else "PSM"
            print(f"  Format: {fmt}")
            print(f"  Input:  {inp}")
            print(f"  Target: {tar}")
            print()
            # Show what the model sees
            inp_tokens = inp.split()
            tar_tokens = tar.split()
            # Find the <MID> position
            if "<MID>" in inp_tokens:
                mid_pos = inp_tokens.index("<MID>")
                prefix_part = " ".join(inp_tokens[: mid_pos + 1])
                suffix_part = " ".join(inp_tokens[mid_pos + 1 :])
                print(f"  MODEL INPUT:     {prefix_part} [GENERATE] {suffix_part}")
                print(f"  MODEL SHOULD SAY: {' '.join(tar_tokens)}")

    print(f"\n{'=' * 60}")
    print(f"Key insight: FIM teaches the model to FILL GAPS, not just append.")
    print(f"Copilot, CodeGemma, StarCoder all use this training format.")
    print(f"\nWithout FIM:  model only sees [before cursor]")
    print(f"With FIM:     model sees [before cursor] [after cursor]")
    print(f"              and generates the middle. Same model, better data.")
