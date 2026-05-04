# What Is Pyth

## Why It Exists

First-party oracle solutions often rely on anonymous third-party node operators who can be bribed or compromised. Pyth addresses this by using data from the trading venues and market makers themselves, who already know the true prices because they create the markets. This first-party model reduces latency, increases accuracy, and aligns incentives because the data providers have reputations and businesses to protect.

## Definition

Pyth is a decentralized oracle network on Solana that aggregates high-frequency financial market data directly from institutional traders, exchanges, and market makers. It publishes price updates on-chain with confidence intervals and multi-source attestations.

## Real-Life Analogy

Imagine a farmers market where prices are set not by a single auctioneer guessing values, but by the farmers themselves holding up signs showing what they currently charge. A market coordinator walks the aisles, reads every sign, removes obvious mistakes like a tomato priced at one hundred dollars, and announces the fair median. Because the farmers set the initial prices based on their own costs, the final announcement reflects ground truth rather than speculation.

## Tiny Numeric Example

A Pyth price update for SOL/USD contains multiple publisher contributions:

| Publisher | Price | Confidence | Slot |
|-----------|-------|------------|------|
| Publisher A | $24.55 | $0.05 | 150,000,100 |
| Publisher B | $24.60 | $0.03 | 150,000,100 |
| Publisher C | $24.58 | $0.04 | 150,000,100 |
| Aggregate | $24.58 | $0.04 | 150,000,100 |

The on-chain program reads the aggregate row and checks that the slot is recent enough.

## Common Confusion

- Pyth is not a single company running servers; it is a protocol where many independent publishers participate.
- Pyth prices are not delayed for convenience; they stream at high frequency to match institutional trading standards.
- Using Pyth does not eliminate smart contract risk; developers must still validate confidence and staleness.
- Pyth publishers are not anonymous; they are known trading firms whose real-world reputation is at stake.
- Pyth data exists on multiple chains through Wormhole; Solana-native Pyth is the primary source, not a copy.
- Confidence intervals are not optional decorations; contracts should reject prices with confidence wider than a threshold.
- Pyth is not free at scale; consuming programs may need to pay update fees or reward publishers.

## Key Properties
## Where It Appears in Our Code

Pyth-style account structures and aggregation logic are demonstrated in `src_web3/phase32/oracle/src/lib.rs` and queried via the Express API in `src_web3/phase32/price_feed_api.ts`.
