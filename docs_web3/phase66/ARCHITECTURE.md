# Phase 66: Security & Auditing Architecture

This document outlines the step-by-step audit process for reviewing Solana/Anchor programs before deployment.

## Step 1: Review all CPI calls for program ID validation
**Why:** Cross-program invocations delegate execution to external code. If the destination program is not restricted to a known whitelist, an attacker can route protocol logic to a malicious contract that drains state or forges signatures. Every `invoke` and `invoke_signed` must be preceded by a hardcoded or state-backed program ID check.

## Step 2: Check closed account handling
**Why:** Closing an account by transferring its lamports does not erase its data or type discriminator. Without invalidating the discriminator (e.g., setting it to `CLOSED_ACCOUNT_DISCRIMINATOR` or using Anchor's `close = signer`), the account remains a valid input for other instructions. Attackers can pass "closed" accounts to instructions that trust the discriminator, leading to reuse exploits.

## Step 3: Verify PDA canonicalization (bump + seeds)
**Why:** Program Derived Addresses are deterministic only when derived from fixed seeds and the canonical bump. If a program accepts user-provided bumps or variable seed prefixes, an attacker can substitute an alternative PDA they control. Using Anchor's `seeds` and `bump` constraints ensures only the intended canonical address is accepted.

## Step 4: Audit account discriminator collisions
**Why:** Anchor uses an 8-byte discriminator to identify account types. If two account types share a discriminator, or if a closed account retains its original discriminator, deserialization can produce unexpected types. Review all `#[account]` structs and ensure the `CLOSED_ACCOUNT_DISCRIMINATOR` is used consistently for closed accounts.

## Step 5: Check for missing owner checks
**Why:** Any account provided in a transaction could be a fake account created by an attacker with arbitrary data. Solana's runtime does not verify ownership for read-only accounts. The program must explicitly check `account.owner == expected_program_id` for every account whose data it trusts, or rely on Anchor's typed `Account<'info, T>` wrapper which enforces ownership automatically.

## Step 6: Test with fuzzing and formal verification tools
**Why:** Manual audits miss edge cases. Fuzzing generates thousands of random inputs to trigger unexpected code paths. Formal verification mathematically proves properties like "no integer overflow" or "PDA derivation is always canonical." Combining both approaches catches bugs that human reviewers overlook and provides machine-checked guarantees for critical invariants.
