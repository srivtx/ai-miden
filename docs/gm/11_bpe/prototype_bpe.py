"""
Minimal BPE (Byte-Pair Encoding) Tokenizer

The algorithm:
  Step 1: Represent text as bytes (0-255), one token per byte
  Step 2: Count how many times each adjacent pair appears
  Step 3: Merge the most frequent pair into a NEW token
  Step 4: Repeat (2)-(3) until vocab_size is reached

Encoding: apply the learned merges greedily to new text
Decoding: map each token ID back to its byte sequence

Key property: NO <unk> tokens. Every possible input can be encoded
because it falls back to the byte level (0-255). If the text has
a character the model never trained on, it's encoded as individual
bytes. No special slot needed.

This is what GPT-2/3/4, Llama, Mistral use (via SentencePiece).
Our word-level tokenizer in cortexcode_torch.py has this exact bug:
vocab capped at 4096 → anything beyond gets <unk>. BPE fixes it.

Complexity: O(text_length * vocab_size) for training, O(text_length) for encoding.
"""


def count_pairs(ids):
    """Count adjacent pair frequencies. O(n) for n tokens."""
    counts = {}
    for a, b in zip(ids, ids[1:]):
        counts[(a, b)] = counts.get((a, b), 0) + 1
    return counts


def merge_once(ids, pair, new_id):
    """Replace all occurrences of (a, b) with new_id. O(n)."""
    result = []
    i = 0
    while i < len(ids):
        if i < len(ids) - 1 and ids[i] == pair[0] and ids[i + 1] == pair[1]:
            result.append(new_id)
            i += 2
        else:
            result.append(ids[i])
            i += 1
    return result


class BPETokenizer:
    """
    Byte-Pair Encoding tokenizer.

    Train on raw text. Encode/decode with O(n) complexity.
    No <unk> tokens. Vocabulary is learned from data.
    """

    def __init__(self, vocab_size=4096):
        self.vocab_size = vocab_size
        # Merge table: (token_a, token_b) -> new_token_id
        self.merges = {}
        # Reverse vocab: token_id -> byte sequence
        self.byte_vocab = {}

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(self, text, verbose=False):
        """Learn merge rules from text. Returns self for chaining."""

        # Phase 1: convert to bytes, then to integer sequence
        # Every byte is its own token (0-255 = 256 base tokens)
        ids = list(text.encode("utf-8"))
        num_merges = self.vocab_size - 256
        if num_merges < 0:
            raise ValueError(f"vocab_size must be >= 256, got {self.vocab_size}")

        # Phase 2: iteratively merge most frequent pair
        for step in range(num_merges):
            stats = count_pairs(ids)
            if not stats:
                break

            # Pick the pair with highest frequency
            # (ties broken arbitrarily by Python dict iteration order)
            best_pair = max(stats, key=stats.get)
            new_id = 256 + step

            ids = merge_once(ids, best_pair, new_id)
            self.merges[best_pair] = new_id

            if verbose and (step < 5 or step % 500 == 0):
                freq = stats[best_pair]
                print(f"  merge {step+1}/{num_merges}: {best_pair} -> {new_id} "
                      f"  (freq={freq})")

        # Phase 3: build reverse vocabulary for decoding
        # Base: each byte maps to itself
        self.byte_vocab = {i: bytes([i]) for i in range(256)}
        # Merged tokens: concatenate byte sequences of children
        for (a, b), new_id in self.merges.items():
            self.byte_vocab[new_id] = self.byte_vocab[a] + self.byte_vocab[b]

        if verbose:
            encoded = self.encode(text)
            ratio = len(text) / len(encoded) if encoded else 1
            print(f"  Final: {len(ids)} bytes, {len(encoded)} tokens "
                  f"  (compression: {ratio:.1f}x)")

        return self

    # ------------------------------------------------------------------
    # Encoding (text -> token IDs)
    # ------------------------------------------------------------------

    def encode(self, text):
        """Convert text to token IDs using learned merges."""
        ids = list(text.encode("utf-8"))
        if len(ids) < 2:
            return ids

        # Greedy: at each step, find the earliest-fused pair we know,
        # merge it, repeat. This is a simplification of the real BPE
        # algorithm, which processes in priority order.
        #
        # The real algorithm (used in GPT-2) applies merges in a
        # fixed priority order (the order they were learned).
        # This naive implementation re-scans after each merge
        # (quadratic worst-case) but is correct and simple.
        while True:
            stats = count_pairs(ids)
            if not stats:
                break
            # Find the pair with the SMALLEST merge index
            # (earliest-learned merges have priority)
            pair = min(stats, key=lambda p: self.merges.get(p, float("inf")))
            if pair not in self.merges:
                break
            ids = merge_once(ids, pair, self.merges[pair])

        return ids

    # ------------------------------------------------------------------
    # Decoding (token IDs -> text)
    # ------------------------------------------------------------------

    def decode(self, ids):
        """Convert token IDs back to text."""
        byte_parts = []
        for idx in ids:
            if idx in self.byte_vocab:
                byte_parts.append(self.byte_vocab[idx])
            else:
                # Unknown ID: fall back to its byte value
                # (shouldn't happen if trained properly)
                byte_parts.append(bytes([idx & 0xFF]))
        return b"".join(byte_parts).decode("utf-8", errors="replace")

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self):
        """Serialize to a JSON-compatible dict for saving."""
        return {
            "vocab_size": self.vocab_size,
            "merges": {f"{a},{b}": new_id for (a, b), new_id in self.merges.items()},
        }

    def from_dict(self, d):
        """Restore from a dict."""
        self.vocab_size = d["vocab_size"]
        self.merges = {}
        self.byte_vocab = {i: bytes([i]) for i in range(256)}
        for k, new_id in d["merges"].items():
            a, b = map(int, k.split(","))
            self.merges[(a, b)] = new_id
            self.byte_vocab[new_id] = self.byte_vocab[a] + self.byte_vocab[b]
        return self


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("BPE Tokenizer Demo")
    print("=" * 60)

    # 1. Train on a small sample of Python code
    sample = (
        "def add(a, b):\n    return a + b\n\n"
        "def multiply(x, y):\n    return x * y\n\n"
        "class Calculator:\n"
        "    def __init__(self):\n        self.result = 0\n"
        "    def compute(self, a, b, op):\n"
        "        if op == 'add':\n            return a + b\n"
        "        return a * b\n"
    ) * 10  # repeat for frequency

    print(f"\nTraining text: {len(sample)} chars")
    print(sample[:100] + "...\n")

    tokenizer = BPETokenizer(vocab_size=512).train(sample, verbose=True)

    # 2. Encode/decode round-trip
    test_text = "def subtract(a, b):\n    return a - b"
    encoded = tokenizer.encode(test_text)
    decoded = tokenizer.decode(encoded)

    print(f"\n{'=' * 60}")
    print("Round-trip test:")
    print(f"  Input:   {test_text!r}")
    print(f"  Encoded: {encoded}")
    print(f"  Decoded: {decoded!r}")
    print(f"  Match:   {test_text == decoded}")
    print(f"  Compression: {len(test_text)} chars -> {len(encoded)} tokens "
          f"({len(test_text)/len(encoded):.1f}x)")

    # 3. Show what some tokens represent
    print(f"\n{'=' * 60}")
    print("Vocabulary samples:")
    for tid in list(tokenizer.byte_vocab.keys())[:10] + [400, 450, 500, 511]:
        if tid in tokenizer.byte_vocab:
            val = tokenizer.byte_vocab[tid]
            print(f"  {tid:4d}: {val!r}")

    print(
        "\nKey insight: there is no <unk> token. Unknown characters "
        "are encoded as their UTF-8 byte sequence. The tokenizer is "
        "lossless for any input."
    )
