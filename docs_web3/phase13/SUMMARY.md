Phase 13: Token Vault Program Recap
===================================

This phase covered secure, programmable token custody using vault patterns.

What we learned
---------------
- **Token Vault Program** is a program that holds user tokens in PDA-owned
  accounts and enforces custom rules before allowing withdrawals. It protects
  assets beyond simple wallet ownership.
- **Vault** is the abstraction of accounts, state, and rules that together
  form a secure storage unit. It typically includes a state account, a PDA,
  and one or more token accounts.
- **Authority** is the designated signer that a program trusts for privileged
  operations. Authority checks are the gatekeepers of program security.

Why it matters
--------------
Most DeFi protocols are vaults at their core. Lending pools vault user deposits.
Yield farms vault LP tokens. Launchpads vault raised funds. Understanding how
to build a secure vault with proper authority checks, PDA derivation, and
state management is foundational to building any protocol that holds user funds.

Code we built
-------------
- `src_web3/phase13/vault/src/lib.rs` — Rust program implementing deposit,
  time-locked withdrawal, and authority-gated configuration changes.
- `src_web3/phase13/vault/Cargo.toml` — Dependencies for the vault program.
- `src_web3/phase13/vault_api.ts` — TypeScript Express API for depositing
  into vaults, querying vault state, and withdrawing after conditions are met.

Key patterns
------------
- Derive vault PDAs deterministically from user-specific seeds so users can
  always find their vault address.
- Store vault rules in a separate state account so the program can read and
  enforce them before any token movement.
- Always verify the authority signer before processing admin instructions.
- Use CPI to the SPL Token program for actual transfers; never manipulate
  token balances manually.
- Keep vault state and token balances in sync by validating the token account
  balance against the state record during withdrawals.
