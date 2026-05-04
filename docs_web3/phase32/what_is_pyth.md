# What Is Pyth

## The Problem

Decentralized oracle networks traditionally rely on third-party node operators who are anonymous to the protocols they serve. These operators fetch data from public APIs and report it on-chain for a fee. The model works, but it introduces latency, because the node operator is an intermediary who must poll external sources and then submit a transaction. It also introduces trust assumptions, because the operator has no direct stake in the accuracy of the underlying market. A bribed or compromised node can report false data, and while staking and slashing exist, the deterrent is only as strong as the economic weight of the stake.

In high-frequency environments like Solana, where block times are roughly 400 milliseconds, these delays are unacceptable. A perpetual futures exchange cannot wait several seconds for a price update when leverage positions need continuous monitoring. Moreover, traditional models aggregate data that has already been processed by intermediaries, moving the protocol one step further from the original market makers who actually know the price. Pyth was designed to solve this by eliminating the middleman entirely and letting the trading venues themselves publish data directly to the blockchain.

Within the broader oracle landscape, Pyth occupies a distinct position. Chainlink pioneered decentralized third-party aggregation across many chains and remains the dominant general-purpose solution. Band Protocol and API3 offer similar multi-chain coverage with different economic models. Pyth differentiates itself by focusing on financial market data, sourcing from first-party publishers with real-world reputations, and optimizing for low-latency, high-frequency updates on Solana. It is not a universal oracle for weather or sports outcomes; it is a specialized financial data layer.

## Definition

Pyth is a decentralized oracle protocol built natively on Solana that aggregates high-frequency financial market data directly from first-party publishers, including institutional trading firms, centralized exchanges, and market makers. Each publisher submits a signed price update that includes the current price, a confidence interval representing the publisher's uncertainty, and a recent slot number. The Pyth on-chain program aggregates these contributions, removes outliers, and publishes a single aggregate price with a combined confidence interval that any Solana program can consume.

## How It Works (Step-by-Step)

1. **First-Party Publishers Submit Signed Price Updates.** Trading firms and exchanges that already maintain live order books generate price ticks internally. Instead of routing these through an intermediary node, they sign each update with their private key and submit it directly to the Pyth protocol. Each submission contains the asset pair, the price, a confidence interval, and the slot number at which the price was observed.

2. **The Pyth Protocol Collects Contributions per Slot.** Within each Solana slot, the protocol gathers all valid publisher submissions for a given price identifier. It verifies the cryptographic signature of each publisher to ensure the data originated from a registered and reputable source, not an impostor.

3. **Outlier Removal via Confidence Bands.** The protocol calculates an initial aggregate price, often a median, and constructs an acceptance band around it. Publishers whose prices fall outside this band, or whose confidence intervals are unreasonably wide, are excluded from the final calculation. This prevents a single malfunctioning trading engine or a deliberate spoofing attempt from distorting the result.

4. **Weighted Aggregation Produces the Final Price.** The remaining valid contributions are aggregated into a single price and a single confidence interval. The aggregation algorithm weights publishers by their historical accuracy and stake. The final confidence interval reflects the disagreement among the included publishers: tight agreement yields a narrow interval, while dispersed prices yield a wide one.

5. **On-Chain Account Update.** The aggregated result is written to a Solana account that acts as the permanent on-chain price feed for that asset pair. This account is updated atomically within the slot, meaning any transaction in the same or subsequent slot can reference the new price without needing an additional oracle transaction.

6. **Consumer Validation Before Action.** Smart contracts that read Pyth data must perform their own safety checks. They verify that the slot number is recent enough to avoid staleness, that the aggregate confidence interval is below a protocol-defined threshold, and that enough publishers contributed to reach a quorum. If any check fails, the contract should revert rather than act on unreliable data.

## Real-Life Analogy

Imagine a farmers market where prices are set not by a single auctioneer guessing values, but by the farmers themselves holding up signs showing what they currently charge. A market coordinator walks the aisles, reads every sign, removes obvious mistakes like a tomato priced at one hundred dollars, and announces the fair median. Because the farmers set the initial prices based on their own costs, the final announcement reflects ground truth rather than speculation.

## Tiny Numeric Example

Four publishers submit SOL/USD prices for slot 150,000,100:

| Publisher | Price | Confidence |
|-----------|-------|------------|
| Publisher A | $24.55 | $0.05 |
| Publisher B | $24.60 | $0.03 |
| Publisher C | $24.58 | $0.04 |
| Publisher D | $25.80 | $0.50 |

Step 1: Compute the initial median of all prices. Sorted: $24.55, $24.58, $24.60, $25.80. The median is the average of the two middle values: ($24.58 + $24.60) / 2 = **$24.59**.

Step 2: Define an acceptance band. A common rule is the median plus or minus twice the median confidence. The median confidence of the two middle publishers is ($0.04 + $0.03) / 2 = $0.035. The band is $24.59 ± (2 × $0.035) = $24.59 ± $0.07, which gives a range of **$24.52 to $24.66**.

Step 3: Publisher D reports $25.80, which falls outside the acceptance band, so it is excluded as an outlier. Publisher D's own confidence of $0.50 is also far wider than the others, reinforcing the suspicion of stale or erroneous data.

Step 4: Aggregate the three remaining publishers. The new median of $24.55, $24.58, $24.60 is **$24.58**. The aggregate confidence is derived from the spread of these included prices: ($24.60 - $24.55) / 2 = **$0.025**.

Step 5: The on-chain Pyth account for SOL/USD is updated to price = $24.58, confidence = $0.025, slot = 150,000,100, with three contributing publishers.

A lending protocol reading this account checks that the slot is within the last 300 slots, that the confidence of $0.025 is below its maximum allowed threshold of $0.10, and that at least three publishers contributed. All checks pass, so it proceeds with collateral valuation.

## Common Confusion

- Pyth is a single company running centralized servers that publishes prices. No. It is a protocol where many independent first-party publishers participate, and the on-chain program performs aggregation without centralized control.

- Pyth prices are delayed or batched for convenience like traditional oracle networks. No. They stream at high frequency, often slot-by-slot, to match the low-latency demands of institutional trading and perpetual exchanges.

- Using Pyth eliminates all smart contract risk, so developers do not need additional checks. No. Developers must still validate confidence intervals, staleness, and publisher quorum in their own programs. Pyth delivers the data; the contract must judge whether it is safe to use.

- Pyth publishers are anonymous node operators who can be replaced without consequence. No. They are known trading firms and exchanges whose real-world reputations and business relationships are at stake, which creates a stronger alignment than anonymous staking alone.

- Pyth data on other chains through Wormhole is a copy that is less secure than the Solana-native feed. No. While Solana is the primary source, the cross-chain relay mechanism preserves the same aggregate price and confidence. The security model differs by bridge design, not by the underlying Pyth aggregation.

- Confidence intervals are optional decorations that can be safely ignored in production code. No. They represent real disagreement among publishers, and contracts should reject prices with confidence wider than a protocol-defined threshold to avoid acting during chaotic market conditions.

## Key Properties

- **First-Party Data Provenance:** Prices originate directly from the trading venues and market makers that create the markets, eliminating intermediary latency and reducing the attack surface introduced by third-party nodes.

- **Confidence-Aware Aggregation:** Each publisher submits both a price and a confidence interval, allowing the protocol to weight contributions by certainty and to quantify market disagreement in the final output.

- **Slot-Aligned Freshness:** Because Pyth is native to Solana, price updates are tied to slot numbers rather than wall-clock time, giving consuming programs a precise, verifiable measure of data age within the high-speed ledger.

- **Economic and Reputational Security:** Publishers are known entities with commercial incentives to report accurately. Their reputations and future participation rights depend on reliable behavior, supplementing pure staking mechanisms with real-world accountability.

- **Cross-Chain Availability via Wormhole:** While aggregated on Solana, Pyth prices are relayed to other blockchains, allowing Ethereum, Aptos, and other ecosystems to consume the same low-latency financial data without maintaining separate oracle networks.

## Where It Appears in Our Code

Pyth-style account structures and aggregation logic are demonstrated in `src_web3/phase32/oracle/src/lib.rs` and queried via the Express API in `src_web3/phase32/price_feed_api.ts`.
