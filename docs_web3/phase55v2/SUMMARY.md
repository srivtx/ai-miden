# Phase 55v2: Real Yield Farm with Token-2022 + Anchor

## Overview

Phase 55v2 is a complete rewrite of the Phase 55 yield farm using modern Solana production tooling. While Phase 55 demonstrated yield farm concepts with raw Rust and stubbed reward transfers, Phase 55v2 implements a fully functional yield farm using the Anchor framework, Token-2022 extensions, and real SPL token transfers via Cross-Program Invocation (CPI). This project is designed to teach the difference between educational prototypes and production-grade decentralized finance protocols.

## Architecture Diagram

```
User Wallet
    |
    | stake(USDC)
    v
+-----------------------------------+
|         Express API (3064)        |
|  /pool/create  /stake  /unstake   |
|  /claim  /compound  /rewards/:user|
+-----------------------------------+
    |
    | Construct Anchor transactions
    v
+-----------------------------------+
|      Anchor Program (Farm)        |
|  - create_pool                    |
|  - stake (real CPI transfer IN)   |
|  - unstake (real CPI transfer OUT)|
|  - claim (real CPI reward transfer)
|  - compound                       |
|  - reward-per-share accumulator   |
+-----------------------------------+
    |
    | CPI calls
    v
+-----------------------------------+
|      Token-2022 Program           |
|  - Transfer with hooks            |
|  - Reward token distribution      |
+-----------------------------------+
    |
    v
Farm Vault (staked tokens)
Reward Vault (reward tokens)

+-----------------------------------+
|      Boost NFT Program            |
|  - Mint boost NFTs                |
|  - Apply reward multiplier        |
|  - Verified on stake/claim        |
+-----------------------------------+

+-----------------------------------+
|      Auto-Compound Bot            |
|  - Monitor pools every N seconds  |
|  - Filter by threshold            |
|  - Build & submit compound txs    |
|  - Deduct performance fee         |
+-----------------------------------+
```

## What Changed from Phase 55

Phase 55 used raw Rust with `solana_program` directly, manually deserializing accounts and constructing instructions byte-by-byte. Phase 55v2 uses Anchor, which generates IDLs, provides declarative account validation, and handles serialization automatically.

Phase 55 stubbed all token transfers. When a user staked, the program incremented a counter but never moved tokens. When a user claimed rewards, the program printed a message but no reward tokens changed hands. Phase 55v2 performs real CPI calls to the SPL Token and Token-2022 programs. Every stake, unstake, and claim instruction results in actual token movement on-chain.

Phase 55 had no reward-per-share accumulator. It used a naive per-user reward map that would run out of compute with more than a few users. Phase 55v2 implements the Synthetix-style reward-per-share pattern with u128 precision, enabling unlimited user scaling at constant compute cost.

Phase 55 had no automated compounding. Users were expected to manually claim and restake. Phase 55v2 includes a standalone auto-compounding service that monitors pools, filters by economic threshold, and submits compound transactions automatically.

Phase 55 had no NFT integration. Phase 55v2 includes a Boost NFT program where holding an NFT increases a user's reward rate through an on-chain multiplier verified during every claim.

## Why It Changed

Raw Rust is error-prone. Manual account deserialization, unchecked ownership validation, and hand-rolled instruction builders are the leading causes of smart contract exploits on Solana. Anchor eliminates an entire class of bugs by enforcing account constraints at the framework level.

Stubbed transfers create a false sense of security. Students who only see logs claiming "transferred 100 tokens" without actual token movement do not learn the mechanics of Cross-Program Invocation, PDA signing, or token account management. Real CPI transfers force students to understand Solana's account model deeply.

Naive reward maps do not scale. Teaching a pattern that fails at 10 users creates bad architectural instincts. The reward-per-share accumulator is the industry standard used by Synthetix, PancakeSwap, and every major yield farm because it is the only pattern that scales to millions of users.

Manual compounding is unrealistic. No production protocol expects users to log in daily to claim and restake. Auto-compounders are a standard service layer in DeFi, and understanding their design teaches students about off-chain infrastructure, economic thresholds, and transaction retry logic.

## How It Changed

The project is organized into two programs (`farm` and `boost`) under a single Anchor workspace. The `farm` program handles pool creation, staking, unstaking, claiming, and compounding. The `boost` program handles NFT minting and multiplier application.

The Express API (`farm_api.ts`) acts as a middleware layer between user interfaces and the blockchain. It does not hold private keys or custody funds. It constructs unsigned transactions, which users sign with their wallets, except for auto-compound transactions where the bot uses a protocol-funded payer.

Token-2022 is used for reward tokens to demonstrate transfer hooks. While the core farm logic works with standard SPL tokens for staking, the reward distribution layer uses Token-2022 to show how modern token extensions enable programmable behavior on every transfer.

The auto-compounder (`compounder.ts`) is a standalone Node.js service. It connects to the network via WebSocket for account change notifications and uses a configurable polling interval as a fallback. It uses the Anchor IDL to build instructions dynamically, ensuring it stays in sync with program upgrades.

## File Structure

```
docs_web3/phase55v2/
  what_is_token_2022_rewards.md
  what_is_reward_per_share.md
  what_is_auto_compound_bot.md
  SUMMARY.md
  ARCHITECTURE.md

src_web3/phase55v2/
  farm/
    Anchor.toml
    Cargo.toml
    programs/
      farm/
        src/lib.rs
      boost/
        src/lib.rs
  farm_api.ts
  compounder.ts
  deploy.sh
```

## Learning Outcomes

After completing Phase 55v2, students will understand:

1. How to build Solana programs with Anchor instead of raw Rust
2. How to perform real token transfers via CPI to SPL Token and Token-2022 programs
3. How reward-per-share accumulators enable O(1) scaling for yield farms
4. How transfer hooks in Token-2022 enable programmable token behavior
5. How off-chain services like auto-compounders interact with on-chain programs
6. How to design multi-program architectures where NFTs modify DeFi protocol behavior
7. How to test and deploy Anchor programs to devnet with reproducible build scripts
