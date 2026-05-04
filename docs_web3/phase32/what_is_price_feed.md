# What Is a Price Feed

## Why It Exists

Decentralized applications that lend, borrow, or swap assets must know the relative value of tokens.
Without this knowledge, a lending protocol could allow a borrower to withdraw far more than their collateral is worth.
A price feed aggregates market data and delivers it on-chain so smart contracts can make value-based decisions automatically.
It provides the continuous updates necessary for liquidations, margin calls, and fair exchange rates.
Without reliable price feeds, DeFi protocols would collapse under the weight of inaccurate valuations.

## Definition

A price feed is a structured stream of asset prices published by an oracle network at regular intervals.
Each update includes the price, a confidence interval, a timestamp, and a cryptographic proof of authenticity.
The feed may trigger on significant market movements or on a fixed time schedule.
Smart contracts consume this stream to maintain accurate internal accounting of asset values.

## Real-Life Analogy

Picture an airport departures board that updates every thirty seconds.
Behind the scenes, radar stations, airline computers, and ground crew radios feed data to a central system.
The board does not guess where planes are.
It displays the latest verified position from multiple independent sources.

Pilots and passengers trust the board because multiple independent sources agree.
The timestamp tells them whether the information is current or stale.
If one radar station reports a plane at the wrong gate, the system compares it with others and discards the anomaly.
This is exactly how a decentralized price feed operates.
Multiple exchanges report prices, and the feed publishes the aggregated result with a confidence score.

## Tiny Numeric Example

A lending protocol uses a price feed to monitor collateral value:

| Time | BTC Price | User Collateral | Borrowed | Health Factor | Action |
|------|-----------|-----------------|----------|---------------|--------|
| 12:00 | $30,000 | 1 BTC ($30K) | $20K USDC | 1.50 | None |
| 12:15 | $28,500 | 1 BTC ($28.5K) | $20K USDC | 1.425 | Warning |
| 12:30 | $25,000 | 1 BTC ($25K) | $20K USDC | 1.25 | Liquidation eligible |
| 12:45 | $22,000 | 1 BTC ($22K) | $20K USDC | 1.10 | Liquidation triggered |

When the health factor drops below 1.10, the protocol automatically allows liquidation.
The price feed updates every fifteen minutes in this example.
If the feed were delayed by an hour, the protocol might miss the liquidation window entirely.
This would leave the protocol undercollateralized and expose lenders to losses.

## Common Confusion

- A price feed is not the same as a single exchange ticker.
  It aggregates many sources to reduce single-point bias.
- Price feeds do not update every block.
  They push updates only when deviation thresholds or time limits are crossed.
- The published price is not guaranteed to match what users see on Coinbase.
  It reflects a broader market average.
- Confidence intervals are not errors.
  They represent the spread between sources and help contracts judge reliability.
- Stale price feeds are not harmless.
  Using outdated data can cause incorrect liquidations or unfair swaps.
- Price feeds cannot predict prices.
  They only report historical and current market snapshots.
- Not all tokens have price feeds.
  Exotic or low-volume assets may lack sufficient source data for aggregation.

## Key Properties
## Where It Appears in Our Code

Price feed parsing and validation are handled in `src_web3/phase32/oracle/src/lib.rs`.
The `consume_price` instruction reads the feed account and extracts the current price and confidence.
It validates that the confidence interval is within acceptable bounds before allowing the value to be used.
The TypeScript API in `src_web3/phase32/price_feed_api.ts` exposes endpoints for querying and validating feeds.
