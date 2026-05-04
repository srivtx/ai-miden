# What Is Account Validation?

## Why it exists (THE PROBLEM)

Solana programs receive arbitrary accounts from transaction signers.

If a program blindly trusts the accounts passed to it, attackers can substitute fake token accounts, impersonate authorities, or pass accounts owned by malicious programs that mimic expected interfaces.

This leads to theft, corruption, or complete protocol compromise.

Attackers specifically look for programs that skip validation because they are the easiest to exploit.

## Definition

Account validation is the process of verifying that every account passed to a program instruction is the correct type, has the expected owner, satisfies required constraints, and matches the intended relationship to other accounts in the transaction before any state changes occur.

## Real-life analogy

Imagine a nightclub where the bouncer only checks that someone has an ID, but does not verify the photo, expiration date, or whether the ID was issued by the state.

A teenager with a fake ID walks in.

A banned patron borrows a friend's ID.

A process server walks in with a police badge bought online.

Account validation is the bouncer properly scanning, cross-referencing, and verifying every credential.

The program must confirm that each account is authentic, current, and authorized for the specific action requested before letting the transaction proceed.

## Tiny numeric example

A lending program must validate four accounts for a deposit:

| Account | Required Owner | Required Constraint | Failure if Missing |
|---------|---------------|---------------------|--------------------|
| User wallet | System Program | Must be signer | Attacker deposits on behalf of others |
| Token account | Token Program | Must match mint | Fake token account drains vault |
| Vault | Program PDA | Must be derived correctly | Attacker substitutes personal account |
| Program config | Our Program | Must be initialized | Attacker passes uninitialized data |

Missing any single check allows a specific, well-defined exploit vector that attackers will find and exploit.

Comprehensive validation is the foundation of secure program design on Solana.

No program should ever trust an account simply because a client provided it.

## Common confusion

- "AccountInfo is enough."
  Raw AccountInfo has no validation whatsoever.
  Anchor accounts structs enforce constraints automatically at the framework level.

- "Validation is only about ownership."
  Validation also includes signership, mutability, relationships, seeds, initialization status, and discriminators.

- "If the client passes the wrong account, it is the user's fault."
  Programs are responsible for validating every account.
  Blaming users is not a security model.

- "PDA accounts do not need validation."
  PDAs especially need validation because anyone can derive addresses.
  Only the correct seeds prove legitimacy.

- "Validation slows down the program."
  Proper validation adds minimal compute cost compared to the catastrophic cost of an exploit draining a vault.

- "Once validated, an account stays safe."
  Account state can change between transactions.
  Re-validation may be needed in complex multi-step flows.

- "Anchor validates everything for me."
  Anchor helps enormously but developers must still specify the correct constraints in the derive macro.

## Where it appears in our code

- `src_web3/phase24/vulnerable_program.rs`
  Accepts raw AccountInfo without ownership, signer, or relationship checks, making it exploitable.

- `src_web3/phase24/secure_program.rs`
  Uses Anchor derive macros to enforce owner, signer, has_one, and seed constraints comprehensively.
