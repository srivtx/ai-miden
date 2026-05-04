# Phase 57: Complete Prediction Market — Summary

## Overview

In this phase, students build a fully functional prediction market from scratch on Solana. The system consists of two on-chain programs (market and oracle) and an off-chain Express API that serves as the user-facing interface. The market program manages market creation, share minting, AMM-based trading, liquidity provision, and automated settlement. The oracle program governs trusted resolution, dispute windows, and finalization. Together they form a complete Web3 application that demonstrates real-world DeFi mechanics.

## Architecture Diagram

```text
+-----------------------------------------------------------+
|                        CLIENT                             |
|              (Web App / CLI / Postman)                    |
+---------------------------+-------------------------------+
                            |
                            | HTTP
                            v
+-----------------------------------------------------------+
|                 EXPRESS API (port 3061)                   |
|  /market/create  /market/buy  /market/sell               |
|  /market/resolve /market/claim                            |
|  /liquidity/add  /liquidity/remove                       |
|  /markets        /market/:id                             |
+---------------------------+-------------------------------+
                            |
                            | Solana JSON-RPC / Anchor
                            v
+---------------------------+-------------------------------+
|              MARKET PROGRAM (Solana BPF)                  |
|  - Create market (YES/NO outcomes)                        |
|  - Mint outcome shares                                    |
|  - Constant-product AMM for pricing                       |
|  - Buy / sell shares                                      |
|  - Provide / remove liquidity                             |
|  - Claim winnings after resolution                        |
+---------------------------+-------------------------------+
                            |
                            | CPI (Cross-Program Invocation)
                            v
+---------------------------+-------------------------------+
|              ORACLE PROGRAM (Solana BPF)                  |
|  - Store trusted oracle pubkeys                           |
|  - Accept signed resolution attestations                  |
|  - Enforce expiration / prevent early resolution          |
|  - Dispute period with bond                               |
|  - Finalize outcome                                       |
+---------------------------+-------------------------------+
```

## File Map

```text
ai-miden/
├── docs_web3/
│   └── phase57/
│       ├── what_is_prediction_market.md          # Concept doc: definition, mechanics, example
│       ├── what_is_oracle_resolution.md          # Concept doc: oracle role, dispute, finalization
│       ├── what_is_liquidity_provision_pm.md     # Concept doc: AMM LP mechanics, impermanent loss
│       ├── SUMMARY.md                            # This file: overview and architecture
│       └── ARCHITECTURE.md                       # Step-by-step build guide with rationale
└── src_web3/
    └── phase57/
        ├── market/
        │   ├── Cargo.toml                        # Solana program dependencies
        │   └── src/
        │       └── lib.rs                        # Market program: create, trade, settle, LP
        ├── oracle/
        │   ├── Cargo.toml                        # Solana program dependencies
        │   └── src/
        │       └── lib.rs                        # Oracle program: resolution, dispute, finalize
        ├── market_api.ts                         # Express API: REST routes for all operations
        └── deploy.sh                             # Build and deploy script
```

## Learning Objectives

1. Understand how prediction markets aggregate information through peer-to-peer trading.
2. Implement a constant-product AMM for pricing binary outcome shares.
3. Design an oracle resolution flow with economic security (dispute bonds, trusted signers).
4. Build a complete full-stack Web3 application with on-chain programs and an off-chain API.
5. Practice secure Solana program development using Anchor patterns, account validation, and CPI.

## Prerequisites

- Rust and Solana CLI installed.
- Anchor framework familiarity.
- TypeScript and Node.js for the API layer.
- Understanding of SPL tokens and token accounts.
- Basic knowledge of AMM math (constant product x * y = k).

## How to Run

1. Start a local Solana validator or use Devnet.
2. Run `deploy.sh` to build and deploy both programs.
3. Start the API with `ts-node market_api.ts`.
4. Use curl or a frontend to interact with the endpoints on port 3061.
