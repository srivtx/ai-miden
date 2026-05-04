# Phase 54v2 Summary

## Overview

Phase 54v2 is a complete rewrite of Phase 54 (DAO) using Anchor v0.30+ and Squads v4 patterns. The goal is to show students the difference between raw Rust governance and modern production tooling. Raw Rust teaches fundamentals. Anchor teaches how real protocols are built today. This project implements a full governance system with token-weighted voting, treasury multisig integration, timelock execution, and a TypeScript API that constructs real Solana transactions.

## Architecture Diagram

```
+-------------------------------------------------------------+
|                        Client Layer                          |
|  +-------------------+  +-------------------------------+  |
|  |   Express API     |  |   Anchor TypeScript Client    |  |
|  |   Port 3063       |  |   @coral-xyz/anchor           |  |
|  +-------------------+  +-------------------------------+  |
|            |                          |                     |
|            v                          v                     |
|  POST /proposal              Real Transaction Construction  |
|  POST /vote                    (IDL + Provider + Program)   |
|  POST /delegate                                             |
|  POST /execute                                              |
|  GET  /proposals                                            |
|  GET  /proposal/:id                                         |
|  GET  /treasury/balance                                     |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                     On-Chain Programs                        |
|  +-------------------------+  +-------------------------+   |
|  |   Governance Program    |  |   Treasury Program      |   |
|  |   Anchor v0.30+         |  |   Squads v4 Pattern     |   |
|  |                         |  |                         |   |
|  |   - Initialize          |  |   - Request Withdrawal  |   |
|  |   - Create Proposal     |  |   - Approve Withdrawal  |   |
|  |   - Vote (SPL balance)  |  |   - Execute Withdrawal  |   |
|  |   - Delegate            |  |   - Member Management   |   |
|  |   - Execute             |  |                         |   |
|  |   - Timelock            |  |                         |   |
|  +-------------------------+  +-------------------------+   |
|            |                              |                 |
|            v                              v                 |
|  +-------------------------+  +-------------------------+   |
|  |   Proposal PDAs         |  |   Treasury Vault PDA    |   |
|  |   Voter Record PDAs     |  |   Withdrawal Proposals  |   |
|  |   Governance State      |  |   Member Registry       |   |
|  +-------------------------+  +-------------------------+   |
+-------------------------------------------------------------+
```

## What Changed from Phase 54

| Aspect | Phase 54 (Raw Rust) | Phase 54v2 (Anchor + Squads) |
|--------|---------------------|------------------------------|
| Language | Pure Rust, manual serialization | Rust with Anchor macros |
| Account Validation | Manual checks in every function | Declarative `#[account(...)]` constraints |
| Client | Raw web3.js with manual buffers | `@coral-xyz/anchor` typed client |
| IDL | None. Hand-written serializers | Auto-generated JSON IDL |
| Voting Weight | Lamports (native SOL) | SPL token balance (proper governance token) |
| Treasury | Single signer transfer | Multisig threshold pattern (Squads v4) |
| PDAs | Manual address derivation | Anchor `seeds` and `bump` attributes |
| Error Handling | Custom error enums, manual | `#[error_code]` with automatic propagation |
| Testing | Unit tests with mocks | Integration tests on devnet with real programs |
| Code Volume | ~800 lines for basic logic | ~400 lines with more features |

## Why Changed

1. **Industry Standard** — Every major Solana protocol uses Anchor or a similar framework. Students must learn what employers expect.
2. **Security** — Anchor constraints eliminate an entire class of account validation bugs that have caused real exploits.
3. **Velocity** — Anchor reduces development time by 50-70%. This allows teams to focus on business logic rather than boilerplate.
4. **Composability** — The Anchor IDL makes it trivial for other teams to integrate with your program. This is how DeFi protocols compose.
5. **Real Treasury Security** — Using a Squads multisig pattern for treasury is the industry standard for securing protocol funds. Single-key treasuries are considered reckless.

## How Changed

1. **Framework Migration** — The raw Rust entrypoint and manual Borsh serialization were replaced with `#[program]` and `#[derive(Accounts)]`.
2. **Constraint-Based Validation** — Every manual `if account.owner != expected` check was replaced with a declarative attribute constraint.
3. **Token Standard Upgrade** — Voting weight was changed from reading `account.lamports` to reading `token_account.amount` via `anchor_spl::token::TokenAccount`.
4. **Multisig Integration** — Treasury execution was restructured to require threshold approvals stored in a dedicated treasury account, mirroring Squads v4 architecture.
5. **IDL-Driven Client** — The TypeScript API was rebuilt around the Anchor IDL. Transaction construction uses `program.methods` instead of hand-built instruction buffers.
6. **Deployment Pipeline** — Added `deploy.sh` with Anchor build, program keypair management, and devnet deployment steps.

## Files in This Phase

```
docs_web3/phase54v2/
  what_is_anchor_governance.md
  what_is_squads_multisig.md
  what_is_token_weighted_voting.md
  SUMMARY.md
  ARCHITECTURE.md

src_web3/phase54v2/
  governance/
    Anchor.toml
    Cargo.toml
    programs/
      governance/
        src/
          lib.rs
      treasury/
        src/
          lib.rs
  dao_api.ts
  deploy.sh
```
