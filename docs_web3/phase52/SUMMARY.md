# Phase 52: Complete Lending Protocol — Summary

## Overview

This phase builds a complete decentralized lending protocol from scratch. Students implement a Solana-based system where users deposit collateral, borrow assets, accrue interest dynamically, repay debt, withdraw collateral, and face automated liquidation when their health factor drops below 1. The project includes two on-chain programs, an Express API, and a standalone liquidation bot service.

## Architecture Diagram

```
+-----------------------------------------------------------------------+
|                           User / Frontend                             |
+----------------------------------+------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                     Express API (Port 3056)                           |
|  POST /deposit | POST /borrow | POST /repay | POST /withdraw         |
|  POST /liquidate | GET /health-factor/:user | GET /market-stats      |
+----------------------------------+------------------------------------+
                                   |
                    +--------------+--------------+
                    |                             |
                    v                             v
+---------------------------+      +-----------------------------+
|   Lending Program         |      |   Interest Oracle Program   |
|   (src_web3/phase52/      |      |   (src_web3/phase52/        |
|    lending/src/lib.rs)    |      |    interest_oracle/src/     |
|                           |      |    lib.rs)                  |
|  - Deposit collateral     |      |                             |
|  - Borrow against collat. |      |  - Store asset prices       |
|  - Repay debt             |      |  - Update prices            |
|  - Withdraw collateral    |      |                             |
|  - Liquidate positions    |      |                             |
|  - Track utilization      |      |                             |
|  - Accrue interest        |      |                             |
+---------------------------+      +-----------------------------+
                    |                             |
                    +--------------+--------------+
                                   |
                                   v
+---------------------------+      +-----------------------------+
|   Liquidator Service      |      |   Solana RPC / Validator    |
|   (src_web3/phase52/      |      |                             |
|    liquidator.ts)         |      |  - Confirms transactions    |
|                           |      |  - Stores on-chain state    |
|  - Polls all positions    |      |                             |
|  - Computes health factor |      |                             |
|  - Triggers liquidation   |      |                             |
|    when HF < 1.0          |      |                             |
+---------------------------+      +-----------------------------+
```

## File Map

```
ai-miden/
├── docs_web3/
│   └── phase52/
│       ├── SUMMARY.md                          <- This file
│       ├── ARCHITECTURE.md                     <- Step-by-step build guide
│       ├── what_is_collateral_pool.md          <- Collateral pool concept
│       ├── what_is_interest_rate_model.md      <- Interest rate math
│       └── what_is_liquidation_bot.md          <- Liquidation bot concept
└── src_web3/
    └── phase52/
        ├── lending/
        │   ├── Cargo.toml                      <- Solana program dependencies
        │   └── src/
        │       └── lib.rs                      <- Lending program entrypoint
        ├── interest_oracle/
        │   ├── Cargo.toml                      <- Oracle dependencies
        │   └── src/
        │       └── lib.rs                      <- Price oracle program
        ├── lending_api.ts                      <- Express REST API
        ├── liquidator.ts                       <- Liquidation bot service
        └── deploy.sh                           <- Build and deploy script
```

## Learning Outcomes

- Design on-chain accounts for collateral tracking and debt ledgers.
- Implement deposit, borrow, repay, withdraw, and liquidation instructions.
- Build an algorithmic interest rate model tied to pool utilization.
- Compute and monitor borrower health factors using oracle prices.
- Create an automated liquidation service that protects protocol solvency.
- Connect on-chain programs to an off-chain API and a standalone bot.

## Technology Stack

- **On-chain**: Rust, Solana `solana-program` crate, custom account serialization
- **Off-chain**: TypeScript, Node.js, Express, `@solana/web3.js`
- **Deployment**: Solana CLI, shell scripts
