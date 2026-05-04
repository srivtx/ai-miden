# What Is Route Optimization?

## The Problem

In a decentralized exchange ecosystem, the same two tokens can often be traded through many different paths. A direct swap from Token A to Token B might use one pool with shallow liquidity and high fees. An indirect swap from Token A to Token C to Token B might use two pools with deep liquidity and low fees, yielding a better total output. A split swap might send half the amount through the direct route and half through the indirect route. Without automated route optimization, users are forced to guess which path is best, and they consistently leave money on the table. Manual route selection is especially broken for large trades, where a single pool cannot absorb the order without massive price impact.

## Definition

Route optimization is the computational process of finding the token swap path that maximizes the output amount (or minimizes the input amount) for a given trade, subject to constraints such as slippage tolerance, available liquidity, and DEX fees. It treats the entire Solana DEX landscape as a weighted graph where nodes are tokens and edges are liquidity pools. The optimization engine searches this graph for the most efficient sequence of edges, which may include direct edges, multi-edge paths, and parallel edge bundles where a trade is split across multiple pools simultaneously.

## How It Works (6 Steps)

**Step 1: Build the Liquidity Graph.** The optimizer constructs a directed graph where each node represents a token mint address and each directed edge represents a tradable pair on an integrated DEX. Each edge is weighted with current reserves, fee rates, and price curves. Stable pools, concentrated liquidity pools, and constant product pools each contribute edges with different mathematical properties.

**Step 2: Enumerate Candidate Paths.** For a given input token and output token, the engine generates all viable paths up to a maximum hop count (typically three hops). A path is a sequence of edges connecting the input node to the output node. The engine prunes paths that contain cycles or pass through tokens with negligible liquidity.

**Step 3: Calculate Output for Each Path.** For each candidate path, the engine simulates the trade amount through each hop. It applies the exact pricing formula of each pool type. For constant product pools, it uses the constant product formula x * y = k. For concentrated liquidity pools, it uses tick-based pricing. The simulation subtracts fees at each hop and computes the final output.

**Step 4: Evaluate Split Combinations.** The engine considers splitting the input amount across multiple paths. For example, 40% through Path A and 60% through Path B. It uses iterative methods or convex optimization to find the allocation that maximizes total output. This step is critical for large trades where no single path has enough depth.

**Step 5: Rank and Filter Results.** All candidate solutions are ranked by total output amount. The engine filters out any solution where the price impact exceeds a threshold or where the minimum output falls below the user's slippage tolerance. The top-ranked valid solution is selected as the optimal route.

**Step 6: Serialize Route Plan.** The selected route is converted into a structured plan with exact amounts, pool addresses, and DEX program IDs. This plan becomes the input for transaction building. Each step in the plan specifies which AMM to call, with which input token, and how much.

## Real-life Analogy

Imagine you need to ship 1,000 packages from New York to Los Angeles. You could send all 1,000 through a single trucking company that operates a direct route, but their trucks are small and charge a premium for oversized loads. Alternatively, you could send 400 packages by train to Chicago and then by truck to Los Angeles, 350 packages by plane to Denver and then by truck, and 250 packages directly by a different trucking company with larger vehicles. A logistics optimizer software evaluates fuel costs, capacity limits, transfer fees at each hub, and travel time. It discovers that the three-way split is $5,000 cheaper than the direct route alone. Route optimization for token swaps is identical: it finds the cheapest way to move value from one token to another by combining available channels intelligently.

## Tiny Numeric Example With Actual Jupiter Quote Response

Suppose you want to swap 100 USDC for BONK. You request a quote from Jupiter:

```
GET https://quote-api.jup.ag/v6/quote?inputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&outputMint=DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263&amount=100000000&slippageBps=100
```

A possible optimized response:

```json
{
  "inputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "inAmount": "100000000",
  "outputMint": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
  "outAmount": "892345678901234567",
  "otherAmountThreshold": "883452321882922281",
  "swapMode": "ExactIn",
  "slippageBps": 100,
  "platformFee": null,
  "priceImpactPct": "0.0523",
  "routePlan": [
    {
      "swapInfo": {
        "ammKey": "58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYo2Y",
        "label": "Orca",
        "inputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "outputMint": "So11111111111111111111111111111111111111112",
        "inAmount": "60000000",
        "outAmount": "420000000",
        "feeAmount": "120000",
        "feeMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
      },
      "percent": 60
    },
    {
      "swapInfo": {
        "ammKey": "7qbRF6Y22GuEmGNYQCmX9j4CdDYCPDT8FGV4Rvw1jHtA",
        "label": "Raydium",
        "inputMint": "So11111111111111111111111111111111111111112",
        "outputMint": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        "inAmount": "420000000",
        "outAmount": "535407407340740740",
        "feeAmount": "420000",
        "feeMint": "So11111111111111111111111111111111111111112"
      },
      "percent": 60
    },
    {
      "swapInfo": {
        "ammKey": "HcoJqG325TT9zL99R6gGt8kJ3Q3h63VtW6YyYqyF1MRn",
        "label": "Raydium",
        "inputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "outputMint": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        "inAmount": "40000000",
        "outAmount": "356938271560493827",
        "feeAmount": "80000",
        "feeMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
      },
      "percent": 40
    }
  ],
  "contextSlot": 245678912,
  "timeTaken": 0.008234
}
```

**Interpretation:**
- Input: 100,000,000 base units = 100 USDC.
- Output: 892,345,678,901,234,567 base units of BONK.
- Route: 60% of USDC goes through Orca (USDC -> SOL), then Raydium (SOL -> BONK). 40% of USDC goes directly through Raydium (USDC -> BONK).
- This split route achieves a better price than either path alone because the direct USDC->BONK pool has shallow liquidity for the full 100 USDC, but the SOL-intermediated path is deeper.

## Common Confusion (6 Bullets With "No.")

- **Is route optimization just finding the DEX with the lowest fee?** No. Fee rates are only one variable. The optimizer also considers pool depth, price impact, token decimals, and the mathematical pricing curve of each pool. A low-fee pool with shallow liquidity can easily deliver a worse total output than a high-fee pool with deep liquidity.

- **Does a longer route with more hops always mean a better price?** No. Each additional hop introduces another set of fees and price impact. The optimizer evaluates all hop counts and often finds that a direct route is optimal for small trades. More hops help only when they access significantly deeper liquidity.

- **Is the optimal route the same for every trade size?** No. The best route depends on the input amount. A route that works well for 10 USDC may be terrible for 10,000 USDC because large trades exhaust shallow pools. Jupiter computes a custom route for every specific amount.

- **Does route optimization happen on-chain during transaction execution?** No. The optimization computation happens off-chain in Jupiter's routing engine. The on-chain transaction simply executes the precomputed route plan. This is necessary because the optimization problem is too complex to solve within Solana's compute unit limits.

- **Is the optimized route always a single path, or can it split?** No. The route can and often does split across multiple paths. Jupiter's engine supports arbitrary splits to maximize output. A trade might be divided among three or more pools in precise proportions calculated by the optimizer.

- **Does route optimization guarantee the best possible price in the entire market?** No. The optimizer can only consider the DEXs and pools that Jupiter has integrated. If a better price exists on a non-integrated DEX or an over-the-counter desk, Jupiter will not find it. The guarantee is limited to the indexed liquidity graph.

## Key Properties (5)

1. **Graph-Based Search.** Route optimization treats the token ecosystem as a mathematical graph. This abstraction allows the engine to apply well-known graph algorithms and optimization techniques to a problem that would otherwise be intractable.

2. **Amount-Dependent Solutions.** The optimal route is not a static property of two tokens. It is a function of the trade amount. The engine recompute the solution for every quote because changing the amount changes price impact and pool utilization.

3. **Multi-Hop and Split Support.** The engine supports both multi-hop paths and split allocations. This dual capability dramatically expands the search space and enables solutions that no single-pool or single-path approach could achieve.

4. **Off-Chain Computation.** The heavy optimization work is done off-chain to respect Solana's compute budget. Only the lightweight execution of the precomputed route happens on-chain. This separation of optimization and execution is a critical architectural choice.

5. **Deterministic Simulation.** The engine simulates each candidate route using the exact mathematical formulas of the underlying pools. It does not use approximations or heuristics for the core pricing. This ensures that the quoted output matches the expected on-chain output as closely as possible.
