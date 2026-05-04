# What Is Jupiter?

## The Problem

Liquidity on Solana is fragmented across dozens of decentralized exchanges. Raydium, Orca, Phoenix, Lifinity, and many others each operate their own liquidity pools with different depths, fees, and pricing. If a user wants to swap one token for another, they must manually check each exchange to find the best price. A large trade might move the price significantly in a single pool, but that same trade could be split across multiple pools for a much better average price. Without an aggregator, users consistently overpay, slippage is higher than necessary, and the overall trading experience is slow and confusing. Small traders lack the tools to route optimally, and large traders cannot execute without causing excessive market impact.

## Definition

Jupiter is a decentralized liquidity aggregator on the Solana blockchain. It scans all major decentralized exchanges and automated market makers to find the most efficient route for any token swap. Instead of executing a trade against a single liquidity pool, Jupiter splits, batches, and sequences transactions across multiple pools and even multiple hops to deliver the best possible price to the user. It operates entirely through smart contracts and API endpoints, requiring no custody of user funds and no permission to access. Jupiter has become the most-used DeFi infrastructure on Solana, routing billions of dollars in monthly volume by acting as a meta-layer above individual DEXs.

## How It Works (6 Steps)

**Step 1: Scan DEXs.** Jupiter maintains a real-time index of all active liquidity pools across integrated DEXs on Solana. This includes constant product pools, stable pools, concentrated liquidity pools, and order book markets. The indexer listens to on-chain account changes and updates price curves, depths, and fees continuously.

**Step 2: Find Best Route.** When a user requests a quote, Jupiter's routing engine computes all viable paths between the input token and the output token. A path can be a direct swap (one hop) or an indirect swap (two or more hops through intermediate tokens). The engine evaluates each path using current pool depths, fees, and price impact.

**Step 3: Split Across Pools.** For large trades, Jupiter calculates the optimal way to split the input amount across multiple pools and routes. This is a constrained optimization problem: maximize output tokens subject to the available liquidity and fees in each pool. The result is a distribution of the trade across several execution paths.

**Step 4: Build Transaction.** Jupiter assembles the swap instructions into a single Solana transaction. This includes the routing instructions, token account creation if needed, and any intermediate swaps. The transaction is serialized and returned to the user or application for signing.

**Step 5: Execute.** The user signs the transaction with their private key and submits it to the Solana network. Jupiter does not hold the user's funds or signing authority. Execution happens atomically on-chain: either all swaps in the route succeed, or the entire transaction fails and no tokens move.

**Step 6: Settle.** After the transaction is confirmed, the output tokens are in the user's wallet. Jupiter's contracts ensure that intermediate tokens created during multi-hop routes are automatically converted or closed, leaving the user with only the intended output token and no dust.

## Real-life Analogy

Imagine you need to exchange $10,000 worth of Japanese yen for Euros. You could walk into a single currency exchange booth at the airport, but they might offer a terrible rate and not have enough Euros in the drawer. Instead, you use a smart currency broker app. The app checks every exchange booth in the city, finds that Booth A has the best rate for $3,000, Booth B has the best rate for $4,000, and Booth C has a slightly worse rate but unlimited supply for the remaining $3,000. It also discovers that converting yen to US dollars first, then dollars to Euros, yields an even better total. The app books all three transactions simultaneously, gives you a single receipt, and either all exchanges happen or none do. Jupiter is that broker, but for tokens on Solana.

## Tiny Numeric Example With Actual Jupiter Quote Response

Suppose you want to swap 1 SOL for USDC on devnet. You call the Jupiter quote API:

```
GET https://quote-api.jup.ag/v6/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=1000000000&slippageBps=50
```

A real response might look like this (simplified):

```json
{
  "inputMint": "So11111111111111111111111111111111111111112",
  "inAmount": "1000000000",
  "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "outAmount": "14283560000",
  "otherAmountThreshold": "14276424280",
  "swapMode": "ExactIn",
  "slippageBps": 50,
  "platformFee": null,
  "priceImpactPct": "0.003456",
  "routePlan": [
    {
      "swapInfo": {
        "ammKey": "HcoJqG325TT9zL99R6gGt8kJ3Q3h63VtW6YyYqyF1MRn",
        "label": "Raydium",
        "inputMint": "So11111111111111111111111111111111111111112",
        "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "inAmount": "1000000000",
        "outAmount": "14283560000",
        "feeAmount": "250000",
        "feeMint": "So11111111111111111111111111111111111111112"
      },
      "percent": 100
    }
  ],
  "contextSlot": 245678901,
  "timeTaken": 0.004512
}
```

**Interpretation:**
- Input: 1,000,000,000 lamports = 1.0 SOL.
- Output: 14,283,560,000 base units = 14,283.56 USDC (since USDC has 6 decimals).
- Slippage protection: the minimum acceptable output is 14,276.42 USDC.
- Price impact: 0.3456%.
- Route: 100% routed through a single Raydium pool in this case.
- For a larger trade, the routePlan might contain multiple entries with different AMMs and percentages.

## Common Confusion (6 Bullets With "No.")

- **Is Jupiter a decentralized exchange where trades execute on its own order book?** No. Jupiter does not maintain its own liquidity pools or order books. It is purely an aggregator that routes trades through existing DEXs such as Raydium, Orca, and Phoenix. It adds a layer of intelligence above DEXs but does not replace them.

- **Does Jupiter hold user funds in a central wallet to execute trades?** No. Jupiter never takes custody of user tokens. The user's wallet signs a transaction that executes directly on Solana. Jupiter only provides the transaction instructions. The private key never leaves the user's device.

- **Is the price quoted by Jupiter guaranteed to be the exact price received?** No. The quote is computed at a specific slot and is valid for a short window. If pool states change between quoting and execution, the actual output may differ. That is why Jupiter includes slippage protection and a minimum output threshold.

- **Does Jupiter charge additional fees on top of the underlying DEX fees?** No. Jupiter does not add its own swap fees for basic usage. The user pays only the fees charged by the individual DEXs in the route. Some integrations may add a platform fee, but that is opt-in and transparent.

- **Can Jupiter only route between popular tokens like SOL and USDC?** No. Jupiter can route between any two SPL tokens that have at least one path of liquidity through integrated DEXs. Even obscure or newly launched tokens can be swapped if there is a viable route, though the price impact may be high.

- **Is a single-hop route always better than a multi-hop route?** No. Multi-hop routes often produce better output amounts because they access deeper liquidity or more favorable pricing through intermediate tokens. Jupiter's optimization engine evaluates all possibilities, and the best route is frequently a multi-hop path.

## Key Properties (5)

1. **Optimal Routing.** Jupiter solves a combinatorial optimization problem across all available liquidity pools. It evaluates direct routes, multi-hop routes, and split routes to find the execution path that maximizes the output for a given input. This is its core value proposition and the reason it outperforms manual DEX selection.

2. **Atomic Execution.** All swaps in a Jupiter route are bundled into a single Solana transaction. This guarantees atomicity: either every intermediate swap succeeds and the user receives the final output, or the entire transaction fails and no state changes occur. Users are never left holding unexpected intermediate tokens.

3. **Permissionless Access.** Anyone can query Jupiter's quote API or smart contracts without registration, API keys for basic usage, or whitelisting. This open access aligns with the decentralized ethos of DeFi and enables any wallet or application to integrate swapping functionality.

4. **Real-time Liquidity Indexing.** Jupiter continuously indexes on-chain liquidity states. It does not rely on cached or stale data for routing. When a pool's reserves change, the indexer updates the routing graph within seconds, ensuring that quotes reflect actual market conditions.

5. **Slippage and MEV Protection.** Jupiter enforces user-specified slippage tolerances by embedding a minimum output amount into the transaction. If market movement exceeds this threshold before confirmation, the transaction reverts. Additionally, by bundling complex routes into single transactions, Jupiter reduces the attack surface for sandwich attacks and front-running.
