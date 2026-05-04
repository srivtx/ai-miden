# Phase 58v2: Real Launchpad with Jupiter + Anchor — Summary

## Project Overview

Phase 58v2 is a production-grade token sale launchpad built on Solana using the Anchor framework and Jupiter liquidity aggregation. Unlike Phase 58, which used an in-memory Express mock, Phase 58v2 deploys real smart contracts to Solana devnet (and mainnet). It handles project registration, tiered whitelists, capped participation, Jupiter-powered payment routing, vesting with cliff and linear unlock, proportional refunds, and admin withdrawals.

## Architecture Diagram

```
                    User Wallet (Phantom / Solflare)
                           |
                           | Sign Transaction
                           v
               +---------------------------+
               |   Express API (Port 3066) |
               |   src_web3/phase58v2/     |
               |   launchpad_api.ts        |
               +---------------------------+
                           |
          +----------------+----------------+
          |                                 |
          v                                 v
+--------------------------------+   +------------------+
| Jupiter Quote / Swap API       |   | Anchor Provider  |
| quote-api.jup.ag/v6            |   | RPC Connection   |
+--------------------------------+   +------------------+
                                              |
                          +-------------------+-------------------+
                          |                                       |
                          v                                       v
          +---------------------------+            +---------------------------+
          | Launchpad Program         |            | Vesting Program           |
          | programs/launchpad/src/   |            | programs/vesting/src/     |
          | lib.rs                    |            | lib.rs                    |
          +---------------------------+            +---------------------------+
                          |                                       |
                          +-------------------+-------------------+
                                              |
                                              v
                                   +--------------------+
                                   | SPL Token Program  |
                                   | Token Transfers    |
                                   +--------------------+
                                              |
                                              v
                                   +--------------------+
                                   | On-Chain Accounts  |
                                   | Project, Treasury, |
                                   | User, Vesting      |
                                   +--------------------+
```

## Comparison to Phase 58

### What Changed

| Component | Phase 58 (Mock) | Phase 58v2 (Real) |
|-----------|-----------------|-------------------|
| Smart Contract | None. Logic lived in Express memory. | Anchor program deployed to Solana devnet. |
| Data Storage | JavaScript objects in RAM. Lost on restart. | Solana accounts on-chain. Permanent and auditable. |
| Token Transfers | Console.log("Transferred tokens"). No real SPL calls. | Real SPL Token program CPI invocations. |
| Payment Routing | Assumed user paid in USDC. No swap logic. | Jupiter API integration for any-to-USDC swaps. |
| Vesting | Timestamps stored in memory. No enforcement. | On-chain vesting program with cliff and linear unlock. |
| Refunds | Marked status in memory. No real token returns. | SPL transfer refunds back to user wallets. |
| Admin Withdraw | Marked status in memory. | Authority-signed CPI transfer from treasury. |
| Testing | Unit tests against mock data. | End-to-end tests on devnet with real transactions. |

### Why Changed

1. **Security**: In-memory mocks cannot be audited. Real programs have account ownership checks, signer validation, and immutable logic enforced by the Solana runtime.

2. **Trustlessness**: Users do not need to trust the API server. The smart contract enforces all rules. Even if the API goes down, users can interact directly with the program.

3. **Composability**: Real on-chain programs can be called by other programs and wallets. A mock API cannot be composed into DeFi protocols.

4. **Real Economics**: Only real SPL transfers create actual value flow. Mock transfers teach syntax but not the economic reality of transaction fees, slippage, and account rent.

5. **Production Readiness**: Phase 58 taught concepts. Phase 58v2 teaches deployment, devnet testing, RPC management, and mainnet migration paths.

### How Changed

1. **Anchor Framework**: Replaced raw JavaScript logic with Rust programs using Anchor macros for account validation and CPI.

2. **Jupiter API**: Added HTTP calls to `quote-api.jup.ag/v6` for swap quotes and transaction building. The API server now constructs real swap transactions alongside launchpad instructions.

3. **SPL Token CPIs**: Replaced mock transfers with `anchor_spl::token::transfer` calls, requiring associated token accounts and proper account validation.

4. **Separate Vesting Program**: Split vesting into its own program for modularity. The launchpad program calls the vesting program via CPI to create and unlock vesting schedules.

5. **Devnet Deployment**: Added `deploy.sh` to build Anchor programs and deploy to devnet. The API connects to devnet RPC by default.

6. **Real Transaction Submission**: The API uses `@solana/web3.js` to construct, sign, and send transactions to the Solana network, then polls for confirmation.

## Files Overview

| File | Purpose |
|------|---------|
| `docs_web3/phase58v2/what_is_jupiter_routing.md` | Explains Jupiter swap routing for launchpad payments. |
| `docs_web3/phase58v2/what_is_anchor_launchpad.md` | Explains how Anchor simplifies launchpad program development. |
| `docs_web3/phase58v2/what_is_fair_sale_mechanics.md` | Explains anti-whale and fair distribution mechanics. |
| `docs_web3/phase58v2/SUMMARY.md` | This file. Project overview and comparison. |
| `docs_web3/phase58v2/ARCHITECTURE.md` | Step-by-step build guide with WHY for each step. |
| `src_web3/phase58v2/launchpad/Anchor.toml` | Anchor workspace configuration. |
| `src_web3/phase58v2/launchpad/Cargo.toml` | Rust workspace dependencies. |
| `src_web3/phase58v2/launchpad/programs/launchpad/src/lib.rs` | Main launchpad program. |
| `src_web3/phase58v2/launchpad/programs/vesting/src/lib.rs` | Vesting program with cliff and linear unlock. |
| `src_web3/phase58v2/launchpad_api.ts` | Express API using Anchor and Jupiter. |
| `src_web3/phase58v2/deploy.sh` | Build and deploy script. |
