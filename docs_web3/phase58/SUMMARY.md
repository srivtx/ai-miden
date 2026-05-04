# Phase 58 Summary: Token Launchpad With Tiered Sales, Vesting, and Refunds

## Project Overview

Phase 58 teaches how to build a complete decentralized token launchpad from scratch. A token launchpad is a platform that allows blockchain projects to raise capital by selling tokens to the public in a structured, fair, and transparent manner. This phase combines multiple advanced concepts into a single cohesive system: tiered whitelisting for price discrimination, vesting schedules for long-term alignment, cliff and unlock periods for controlled token release, and refund mechanisms for capital safety. By the end of this phase, you will understand how these components interact to create a trustless fundraising environment that protects both project creators and participant investors.

## ASCII Architecture Diagram

```
+------------------------------------------------------------------+
|                        PHASE 58 LAUNCHPAD                        |
+------------------------------------------------------------------+
|                                                                  |
|  +-------------------+        +-------------------+             |
|  |   Admin Panel     |        |  Public Frontend  |             |
|  |  (TypeScript API) |        |  (TypeScript API) |             |
|  +---------+---------+        +---------+---------+             |
|            |                            |                       |
|            v                            v                       |
|  +-------------------+        +-------------------+             |
|  |  Register Project |        |  Apply for Tier   |             |
|  |  Set Caps & Dates |        |  Contribute Funds |             |
|  |  Approve Whitelist|        |  Claim Refund     |             |
|  +---------+---------+        +---------+---------+             |
|            |                            |                       |
+------------+----------------------------+-----------------------+
             |                            |
             v                            v
+------------------------------------------------------------------+
|                     SOLANA SMART CONTRACT                        |
|                                                                  |
|  +----------------------------------------------------------+   |
|  |                   PROJECT REGISTRY                         |   |
|  |  - Token Mint Address                                    |   |
|  |  - Soft Cap, Hard Cap, Sale Timeline                     |   |
|  |  - Admin Authority                                       |   |
|  +---------------------------+------------------------------+   |
|                              |                                   |
|  +---------------------------v------------------------------+   |
|  |                   TIERED WHITELIST                       |   |
|  |  - Tier 1: Early Adopters (0.40 USDC, 2,000 max)       |   |
|  |  - Tier 2: Community      (0.45 USDC, 1,500 max)       |   |
|  |  - Tier 3: Public         (0.50 USDC, 1,000 max)       |   |
|  |  - Wallet -> Tier Mapping                                |   |
|  +---------------------------+------------------------------+   |
|                              |                                   |
|  +---------------------------v------------------------------+   |
|  |                   TOKEN SALE CONTRACT                    |   |
|  |  - Accept Payments (USDC / SOL / ETH)                    |   |
|  |  - Verify Whitelist Tier                                 |   |
|  |  - Enforce Per-Wallet Allocation Limits                  |   |
|  |  - Track Total Raised vs Hard Cap                        |   |
|  +---------------------------+------------------------------+   |
|                              |                                   |
|  +---------------------------v------------------------------+   |
|  |                   VESTING SCHEDULE                       |   |
|  |  - Linear or Step-Based Release                          |   |
|  |  - Total Vesting Duration                                |   |
|  |  - Tokens Per Interval Calculation                       |   |
|  +---------------------------+------------------------------+   |
|                              |                                   |
|  +---------------------------v------------------------------+   |
|  |                   CLIFF AND UNLOCK                       |   |
|  |  - Cliff Period: No tokens released                      |   |
|  |  - Unlock Start: Vesting begins                          |   |
|  |  - Claim Function: Release eligible tokens               |   |
|  +---------------------------+------------------------------+   |
|                              |                                   |
|  +---------------------------v------------------------------+   |
|  |                   REFUND MECHANISM                       |   |
|  |  - Compare Total Raised vs Soft Cap at Finalization      |   |
|  |  - If Failed: Enable Refund Function                     |   |
|  |  - If Success: Disable Refunds, Enable Withdrawals       |   |
|  +----------------------------------------------------------+   |
|                                                                  |
+------------------------------------------------------------------+
             |                            |
             v                            v
+------------------------------------------------------------------+
|                     DATA STORES (ACCOUNTS)                       |
|                                                                  |
|  ProjectAccount  WhitelistEntry  Contribution  VestingSchedule   |
|                                                                  |
+------------------------------------------------------------------+
```

## File Map

```
docs_web3/phase58/
├── ARCHITECTURE.md              Step-by-step build instructions from scratch
├── SUMMARY.md                   This file - project overview and connections
├── what_is_token_launchpad.md   Core concept: decentralized fundraising platform
├── what_is_tiered_sale.md       Core concept: whitelist tiers with different prices
└── what_is_refund_mechanism.md  Core concept: capital protection via soft cap

src_web3/phase58/
├── token_launchpad/
│   ├── Cargo.toml               Rust dependencies and BPF build config
│   └── src/
│       └── lib.rs               On-chain Solana program (Rust)
└── launchpad_api.ts             TypeScript Express API wrapping contract calls
```

## Phase Connections

Phase 58 builds directly upon the foundational Web3 concepts taught in earlier phases. Understanding these connections helps place the launchpad in the broader curriculum context.

- **Phase 1-5:** Introduced Solana programming model, accounts, and basic transaction signing. The launchpad uses these primitives for every participant interaction.
- **Phase 6-10:** Covered token creation, minting, and transfers. The launchpad sells tokens that were created and minted using these exact techniques.
- **Phase 11-20:** Taught smart contract security, access control, and error handling. The tiered whitelist and admin controls in this phase apply those security patterns at scale.
- **Phase 21-35:** Explored decentralized finance primitives such as escrow, vaults, and automated market makers. The refund mechanism is an escrow pattern, and the sale contract itself is a specialized vault.
- **Phase 36-57:** Built decentralized autonomous organization tooling, governance, and treasury management. Many real-world launchpads are governed by DAOs, and the skills from those phases apply to managing launchpad treasuries.

## What You Will Learn

1. How to design a multi-tier whitelist system that rewards early community members with better pricing while maintaining fairness.
2. How to build a token sale smart contract that accepts payments, validates participation rules, and enforces hard caps.
3. How to integrate vesting schedules so that tokens are released gradually rather than dumped immediately after purchase.
4. How to implement cliff periods that delay the start of vesting, protecting the project from early sell pressure.
5. How to create a refund mechanism that returns participant funds if the project fails to meet its minimum funding goal.
6. How to structure admin controls that allow necessary oversight without creating centralization risks.
7. How to test a full sale flow from project registration through contribution, finalization, vesting claims, and refund scenarios.

## Quick Start

To explore the launchpad code for this phase:

```bash
# Build the Rust program
cd src_web3/phase58/token_launchpad && cargo build-bpf

# Start the TypeScript API (runs on port 3018)
cd src_web3 && npx ts-node phase58/launchpad_api.ts
```

Then interact with the API endpoints for project registration, tier whitelisting, contributions, finalization, and claims.
