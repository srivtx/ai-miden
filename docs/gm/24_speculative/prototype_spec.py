"""
Minimal Speculative Decoding.

The problem: Autoregressive generation is sequential — token N can't be
generated until token N-1 is done. Each token = one full model forward.

Speculative decoding: Use a SMALL draft model to generate K tokens fast,
then use the LARGE target model to verify in ONE forward pass. Accept/reject
each token based on probability agreement. On average, accept ~2-3 tokens
per cycle, giving 2-3x speedup.

  draft_model: small, fast (10M params, 1ms per token)
  target_model: large, accurate (100M params, 10ms per token)

  Without speculation: 10ms per token.
  With speculation: draft generates 5 tokens in 5ms, target verifies in 10ms.
  Accept 3 of 5. Net: 15ms for 3 tokens = 5ms per token = 2x speedup.
"""

import torch
import torch.nn.functional as F


def speculative_generate(
    draft_model, target_model, prefix, max_new_tokens=20, draft_len=4, temperature=1.0
):
    """
    Generate tokens using speculative decoding.

    draft_model: returns (next_token_id, logits) for a single token
    target_model: returns (probabilities) for a full sequence
                  (used for verification, not generation)

    Returns: list of generated token ids
    """
    generated = list(prefix)
    while len(generated) - len(prefix) < max_new_tokens:
        # Phase 1: Draft K tokens with the small model
        draft_tokens = []
        draft_probs = []
        current = list(generated)

        for _ in range(draft_len):
            token_id, probs = draft_model.step(current, temperature)
            draft_tokens.append(token_id)
            draft_probs.append(probs[token_id].item())
            current.append(token_id)

        # Phase 2: Verify all K tokens with the large model in ONE pass
        # target_model.verify returns probabilities for each position
        target_seq = list(generated) + draft_tokens
        target_probs_all = target_model.verify(target_seq)

        # Compare draft probs vs target probs, accept/reject
        accepted = 0
        for k in range(draft_len):
            draft_p = draft_probs[k]
            target_p = target_probs_all[len(generated) + k][
                draft_tokens[k]
            ].item()

            # Acceptance criterion: with probability min(1, target/draft)
            # Simplification: always accept
            # Real specdec: sample with probability min(1, target_p/draft_p)
            if target_p > 0:
                generated.append(draft_tokens[k])
                accepted += 1
            else:
                break  # Reject: stop here, target model will generate from this position

        if accepted == 0:
            # If all rejected, fall back to target model generating one token
            token_id, _ = target_model.step(list(generated), temperature)
            generated.append(token_id)

    return generated


# =============================================================================
# Demo: mock models
# =============================================================================


class MockModel:
    """A mock model that always returns the same token ids."""

    def __init__(self, name, delay_ms=1.0):
        self.name = name
        self.delay_ms = delay_ms
        self.counter = 0

    def step(self, sequence, temperature=1.0):
        # Simulate compute delay
        torch.ones(1)  # dummy computation for delay simulation
        self.counter += 1
        # Return a deterministic next token
        return 42 + len(sequence), torch.softmax(torch.randn(100), dim=0)

    def verify(self, sequence):
        """Return probabilities for each position."""
        return [torch.softmax(torch.randn(100), dim=0) for _ in sequence]


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Speculative Decoding Demo")
    print("=" * 60)

    # Mock models
    draft = MockModel("draft (small, 1ms)")
    target = MockModel("target (large, 10ms)")

    print("\n  Without speculation:")
    print("    Token 1: target model forward (10ms)")
    print("    Token 2: target model forward (10ms)")
    print("    Token 3: target model forward (10ms)")
    print("    Total: 30ms for 3 tokens")
    print(f"\n  With speculation (draft_len=4):")
    print("    Draft generates 4 tokens with small model (4ms)")
    print("    Target verifies 4 tokens in one pass (10ms)")
    print("    Accepts 2-3 of 4 tokens")
    print("    Total: 14ms for ~3 tokens = 2x speedup")

    # How the acceptance works
    print(f"\n{'=' * 60}")
    print("Acceptance criteria:")
    print("  For each draft token k:")
    print("    p_draft = draft_model.prob(token_k | context + drafts[:k])")
    print("    p_target = target_model.prob(token_k | context + drafts[:k])")
    print("    r = random(0,1)")
    print("    Accept if r < min(1, p_target / p_draft)")
    print("    This ensures the output distribution matches target_model exactly.")
    print("\n  Intuition: if draft and target agree, p_target/p_draft ~= 1")
    print("    -> always accept. If they disagree (draft was wrong),")
    print("    -> reject and fall back to target for that position.")

    total_draft_toks = draft_len  # 4
    verify_time = 10  # ms
    accept_rate = 0.6  # typical
    accepted = int(total_draft_toks * accept_rate)
    total_time = total_draft_toks * 1 + verify_time  # ms
    time_per_tok = total_time / max(1, accepted)

    print(f"\n  Example numbers (draft_len={draft_len}):")
    print(f"    Draft time: {total_draft_toks} tokens × 1ms = {total_draft_toks}ms")
    print(f"    Verify time: {verify_time}ms")
    print(f"    Accepted: {accepted}/{total_draft_toks} tokens")
    print(f"    Time per token: {total_time}ms / {accepted} = {time_per_tok:.1f}ms")
    print(f"    Baseline: 10ms per token (target only)")
    print(f"    Speedup: {10/time_per_tok:.1f}x")

    print(f"\nKey insight: The draft model generates TOKENS fast but may be wrong.")
    print(f"The target model verifies the DRAFT fast (one forward for K tokens)")
    print(f"and only takes over when the draft is wrong. Most models agree 60-80%")
    print(f"of the time. The output distribution is identical to target-only.")
