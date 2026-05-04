# Phase 66: Advanced Security & Auditing -- Summary

This phase covers the vulnerability patterns that drain real protocols in production. Students learned to identify, exploit, and remediate critical Solana/Anchor bugs.

## Top 10 Vulnerability Checklist

1. **Arbitrary CPI** -- Validate every cross-program invocation target against a hardcoded whitelist.
2. **Closed Account Reuse** -- Invalidate the account discriminator or use Anchor's `close = signer` constraint.
3. **PDA Canonicalization** -- Derive addresses with `find_program_address` and enforce the canonical bump via constraints.
4. **Missing Owner Checks** -- Verify every account passed to the program is owned by the expected program ID.
5. **Signer Authorization** -- Require a signer for every state-changing instruction and validate the signer's role.
6. **Integer Overflow** -- Use `checked_add`, `checked_sub`, and `checked_mul` for all arithmetic.
7. **Account Discriminator Collision** -- Ensure distinct account types have unique discriminators and handle closed states.
8. **Rent Exemption** -- Confirm all initialized accounts hold enough lamports to be rent-exempt.
9. **Reentrancy** -- Structure instructions to prevent recursive calls that manipulate intermediate state.
10. **Seed Authority Confusion** -- Hardcode seed prefixes and validate all PDA seeds against expected canonical values.

## Key Takeaway
Security is not a feature added at the end; it is a property of every line. Always assume user input is malicious, every account is adversarial, and every CPI destination is a potential attacker until proven otherwise.
