# What Is PDA Canonicalization

## The Problem
An attacker can manipulate Program Derived Address (PDA) derivation by providing alternative seeds or non-canonical bumps, causing the program to operate on an unintended account that the attacker controls or has crafted for exploitation.

## Definition
PDA canonicalization is the requirement that a program must derive PDAs using fixed, program-controlled seeds and the canonical bump returned by `find_program_address`. Failing to enforce canonicalization allows attackers to pass PDAs derived from unexpected seed combinations.

## How It Works
1. Identify the CPI call: Locate where `create_program_address` or `find_program_address` is used.
2. Check program ID whitelist: Not applicable for PDA canonicalization; instead, verify the seeds array contains only program-controlled constants.
3. Validate account ownership: Ensure the PDA account is owned by the expected program.
4. Verify instruction data: Confirm that seed components passed as instruction arguments are restricted or validated.
5. Restrict permissions: Enforce that only the canonical bump from `find_program_address` is accepted.
6. Audit: Review all PDA derivations for attacker-controlled seed prefixes or missing bump validation.

## Real-life analogy
Imagine a postal service that delivers packages to addresses derived from a customer's name and apartment number. A malicious resident submits an alternative spelling of their name and a different valid apartment number, causing the package to be delivered to a unit they secretly control instead of the intended canonical address.

## Tiny numeric example with exploit payload
A vault PDA is expected at the canonical address derived from seeds `[b"vault", authority.key()]`. The program uses `create_program_address` with a user-provided bump of `254` and accepts the user's custom seed prefix. An attacker derives an alternative vault at seeds `[b"fake_vault", authority.key()]` with bump `255`, passes it to the withdrawal instruction, and drains funds because the program never enforced the canonical `b"vault"` prefix or the canonical bump.

## Common confusion
- "Any valid PDA derivation is safe because the address is still off-curve." No. The attacker can control alternative valid PDAs with different seeds.
- "Checking `derived == account.key` is sufficient PDA validation." No. This only proves the account is a valid PDA for some seeds, not the expected canonical seeds.
- "The bump parameter can be passed by the client without server-side validation." No. The program must verify the bump matches the canonical result from `find_program_address`.
- "Using `create_program_address` is equivalent to `find_program_address`." No. `create_program_address` accepts any valid bump, while `find_program_address` deterministically returns the canonical bump.
- "Seed prefixes do not need to be hardcoded in the program." No. Seed prefixes must be program-controlled constants to prevent alternative derivations.
- "Anchor's `seeds` constraint is optional for PDA accounts." No. Omitting it forces manual validation that is easy to implement incorrectly.

## Key properties
1. PDAs must be derived with `find_program_address` to obtain the canonical bump.
2. All seed components should be program-controlled constants or derived from known accounts, not raw user input.
3. The canonical bump must be validated against the account's actual bump.
4. Anchor's `seeds = [...], bump` constraint is the safest way to enforce canonicalization.
5. Non-canonical PDA vulnerabilities often enable account substitution attacks.
