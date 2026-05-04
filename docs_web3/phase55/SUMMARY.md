# Phase 55: Complete Yield Farm — Project Overview

## What You Are Building

A production-quality yield farming protocol with multi-pool support, NFT-based reward boosting, and an auto-compounding service layer. This project demonstrates how to architect complex DeFi incentive systems on Solana, combining on-chain programs with off-chain automation.

## Architecture Diagram

```
+------------------------------------------------------------------+
|                        USER INTERFACE                            |
|                    (Wallet, Web App, CLI)                        |
+----------------------------+-------------------------------------+
                             |
                             v
+----------------------------+-------------------------------------+
|                     EXPRESS API (port 3059)                      |
|  /pool/create  /stake  /unstake  /claim  /compound  /boost/apply |
+------------+---------------+---------------+---------------------+
             |               |               |
             v               v               v
+------------+-------+ +-----+------+ +------+--------+
|   FARM PROGRAM     | |   DEX      | | BOOST PROGRAM |
|  (src/lib.rs)      | |  (swap)    | | (src/lib.rs)  |
|  - create_pool     | |            | | - mint_boost  |
|  - stake / unstake | |            | | - validate    |
|  - claim rewards   | |            | | - multiplier  |
|  - reward-per-share| |            | |               |
+--------+-----------+ +------------+ +---------------+
         |
         v
+-------------------+
|  COMPOUNDER       |
|  (compounder.ts)  |
|  - monitor loop   |
|  - harvest        |
|  - reinvest       |
+-------------------+
```

## File Map

```
ai-miden/
├── docs_web3/phase55/
│   ├── what_is_yield_farm.md          # Educational doc: yield farming mechanics
│   ├── what_is_boost_nft.md           # Educational doc: NFT reward multipliers
│   ├── what_is_compounding_strategy.md# Educational doc: auto-compounding math
│   ├── SUMMARY.md                     # This file: overview and architecture
│   └── ARCHITECTURE.md                # Step-by-step build instructions
│
├── src_web3/phase55/
│   ├── farm/
│   │   ├── Cargo.toml                 # Solana program dependencies
│   │   └── src/lib.rs                 # Main farm program: pools, staking, rewards
│   ├── boost/
│   │   ├── Cargo.toml                 # Solana program dependencies
│   │   └── src/lib.rs                 # Boost NFT program: mint, validate, multiply
│   ├── farm_api.ts                    # Express API: HTTP routes to chain
│   ├── compounder.ts                  # Standalone service: auto-compound loop
│   └── deploy.sh                      # Build and deploy both programs
```

## Component Responsibilities

### Farm Program
The core on-chain logic. It owns pool state, tracks reward-per-share accumulators, accepts stakes and unstakes, and calculates exact reward amounts. It is the source of truth for all farming data.

### Boost Program
A companion program that mints boost NFTs and exposes a validation instruction. The farm program CPI-calls or references the boost program to verify NFT ownership and apply multipliers during reward calculation.

### Express API
An off-chain adapter layer that translates HTTP requests into Solana transactions. It handles RPC communication, transaction signing simulation, and error formatting. The API makes the protocol accessible to web frontends.

### Compounder Service
A background Node.js process that watches opted-in users, triggers claims when profitable, swaps reward tokens for staking tokens, and restakes. It turns APR into APY without user intervention.

## Key Design Decisions

1. **Reward-per-share accumulator**: We use a global u128 accumulator to track rewards. This avoids O(n) iteration over users and scales to millions of stakers.

2. **Separate boost program**: Isolating NFT logic prevents farm program bloat and allows boost NFTs to be reused by other protocols.

3. **Off-chain compounder**: On-chain auto-compounding is complex and expensive. A trusted off-chain service with user permission is simpler and more flexible.

4. **Multi-pool support**: Each pool is an independent account with its own reward token, staking token, and emission schedule. This supports arbitrary incentive programs.

## Learning Outcomes

After completing this phase, you will understand:
- How to implement reward-per-share accounting in Rust on Solana
- How to design cross-program invocations between a farm and an NFT program
- How to structure an Express API that interacts with Solana RPC
- How to build a background service that automates blockchain transactions
- The mathematical relationship between APR, APY, and compounding frequency
