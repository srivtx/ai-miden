# What Is a Price Feed

## The Problem

Smart contracts cannot observe markets on their own. They need an external signal that tells them what one asset is worth relative to another. The naive solution is to let a contract query a single exchange API, but this reintroduces centralization and creates a fatal vulnerability. If that exchange suffers a flash crash, gets hacked, or simply goes offline for maintenance, the contract acts on corrupted data. In a lending protocol, a single bad price can trigger mass liquidations of healthy positions or allow underwater borrowers to escape unscathed. Both outcomes destroy lender capital and erode trust in the entire system.

The problem intensifies at scale. A protocol handling billions of dollars in collateral cannot afford even a few seconds of stale pricing during volatile markets. Yet pushing data on-chain costs transaction fees, so updating every block is economically impractical. There is a constant tension between freshness and cost, between precision and gas efficiency. Without a standardized, robust mechanism for delivering market data, DeFi protocols are forced to build bespoke data pipelines that are expensive to maintain, difficult to audit, and prone to failure under load.

## Definition

A price feed is a structured, time-stamped stream of asset prices delivered to a blockchain by an oracle network. Each update contains the aggregated price of a trading pair, a confidence interval that quantifies the spread between sources, a timestamp or slot number indicating when the data was collected, and cryptographic proof that the value passed through a validated aggregation process. The feed triggers updates either on a fixed schedule or when the market price deviates beyond a predetermined threshold from the last published value.

## How It Works (Step-by-Step)

1. **Data Sources Report Raw Trade Prices.** Independent market venues such as centralized exchanges, decentralized AMM pools, and over-the-counter desks each publish their own last-traded price for a given asset pair. Because order books differ in depth, liquidity, and geographic location, these raw prices naturally diverge by small amounts.

2. **Oracle Nodes Collect and Timestamp Reports.** Nodes in the oracle network fetch these raw values from multiple sources simultaneously. Each node records the exact time or blockchain slot when the sample was taken and performs basic sanity checks, such as verifying that the price is positive and that the source responded within an acceptable window.

3. **Outlier Detection Removes Anomalous Values.** The network compares all collected prices and discards values that deviate significantly from the statistical cluster. A common method is to calculate the median and reject any source whose price differs by more than a fixed percentage, such as one or two percent. This step neutralizes flash crashes, exchange outages, and deliberate manipulation attempts on thin markets.

4. **Aggregation Computes the Final Price.** The remaining valid prices are sorted, and the median is selected as the final value. The median is preferred over the mean because it is robust: a single extreme value cannot skew the result. Some feeds use a confidence-weighted average if sources have known reliability scores.

5. **Cryptographic Signing Bundles the Result.** The aggregated price, the confidence interval, the timestamp, and the identity of the aggregating nodes are packaged into a signed payload. The signature proves that the data passed through the network's validation rules and was not altered in transit.

6. **On-Chain Delivery with Deviation or Time Triggers.** The signed update is transmitted to the blockchain. Feeds typically do not push every block; instead, they publish when the price moves beyond a deviation threshold, such as 0.5 percent, or when a maximum time interval, such as one hour, has elapsed. This balances freshness with transaction cost.

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

Five exchanges report the price of BTC in USD at the same timestamp:

| Source | Reported Price | Distance from Median | Included |
|--------|---------------|---------------------|----------|
| Exchange A | $30,020 | $5 | Yes |
| Exchange B | $30,050 | $25 | Yes |
| Exchange C | $30,015 | $10 | Yes |
| Exchange D | $31,200 | $1,175 | No (outlier, exceeds 1% threshold) |
| Exchange E | $30,025 | $0 | Yes |

Step 1: Sort the included prices: $30,015, $30,020, $30,025, $30,050.
Step 2: The median of four values is the average of the second and third: ($30,020 + $30,025) / 2 = **$30,022.50**.
Step 3: The confidence interval is half the spread of included sources: ($30,050 - $30,015) / 2 = **$17.50**.

The on-chain feed publishes BTC = $30,022.50 ± $17.50. A lending protocol reading this value knows that Exchange D was discarded and that the remaining four sources agreed within roughly 0.12 percent, which is narrow enough to trust for liquidation decisions.

## Common Confusion

- A price feed is the same as a single exchange ticker displayed on a website. No. It aggregates many independent sources and discards outliers before publishing, which removes the single-point bias of any one venue.

- Price feeds update on every single block without exception. No. They push updates only when deviation thresholds or time limits are crossed to manage transaction costs and network load.

- The published price is guaranteed to match exactly what users see on any specific exchange like Coinbase. No. It reflects a broader market median that may differ slightly from any individual venue due to timing and liquidity differences.

- Confidence intervals are just errors or mistakes in the data. No. They represent the natural spread between legitimate sources and help smart contracts judge whether the market is orderly enough to act upon.

- Using a stale price feed for a few minutes is harmless because prices do not move that fast. No. Outdated data can cause incorrect liquidations, unfair swap rates, and bad debt that harms protocol solvency.

- Price feeds can predict future prices based on historical patterns. No. They only report historical and current market snapshots. Any predictive value would require an entirely different statistical model.

## Key Properties

- **Multi-Source Aggregation:** The final price is derived from many independent market venues, not one, which dilutes the influence of any single compromised source.

- **Median Robustness:** Using the median instead of the mean ensures that extreme values, whether from flash crashes or manipulation, cannot pull the reported price in their direction.

- **Bounded Staleness:** Deviation and time triggers guarantee that the on-chain price never drifts too far from reality, even during periods of low volatility.

- **Cryptographic Integrity:** Each update carries a signature that smart contracts verify to confirm the data was processed by the legitimate oracle network and not forged.

- **Confidence Quantification:** The confidence interval gives consuming contracts a numeric measure of market disagreement, allowing them to pause operations when spreads are too wide.

## Where It Appears in Our Code

Price feed parsing and validation are handled in `src_web3/phase32/oracle/src/lib.rs`.
The `consume_price` instruction reads the feed account and extracts the current price and confidence.
It validates that the confidence interval is within acceptable bounds before allowing the value to be used.
The TypeScript API in `src_web3/phase32/price_feed_api.ts` exposes endpoints for querying and validating feeds.
