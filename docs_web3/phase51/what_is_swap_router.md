# What Is a Swap Router?

## The Problem

A single liquidity pool rarely offers the best price for every trade, especially in fragmented DeFi ecosystems where the same token exists across dozens of pools with different depths and fee tiers. If you want to swap Token A for Token C, there might not even be a direct pool. You would have to manually find a path like A -> B -> C, compare it against other paths like A -> D -> C, estimate fees and slippage for each, and then manually execute a series of transactions. For a human, this is slow, error-prone, and almost guarantees a suboptimal result.

## Definition

A swap router is an intermediary smart contract or off-chain service that finds the most efficient path for a token swap across multiple liquidity pools. It splits the trade across routes, aggregates prices, and executes the entire sequence atomically so the trader receives the maximum possible output for their input.

## How It Works (6 Steps)

1. **Receive the Request**: The trader specifies an input token, an output token, and either an exact input amount or an exact output amount they desire.
2. **Discover Pools**: The router queries all known liquidity pools that contain the input token, the output token, or viable intermediary tokens.
3. **Build Candidate Paths**: It constructs possible routes. For example, a direct pool A->C, or indirect paths like A->B->C and A->D->E->C.
4. **Simulate and Compare**: The router simulates the expected output for each path using current pool reserves and fee structures. It accounts for price impact at each hop.
5. **Select the Best Path**: It chooses the route or combination of routes that yields the highest output for the user, sometimes splitting a large trade across multiple paths to minimize slippage.
6. **Execute Atomically**: The router executes all swaps in a single transaction. If any step fails, the entire transaction reverts, ensuring the trader does not end up stuck with an unwanted intermediary token.

## Real-life Analogy

Imagine you are in New York and you want to fly to Tokyo. There is no direct flight available today. A travel router is like a master travel agent who checks every airline, every hub city, and every connection. They might find that flying New York -> London -> Tokyo is cheaper than New York -> Los Angeles -> Tokyo, even though London seems out of the way. They book all the tickets at once, and if the London connection is cancelled, the entire booking is void and you get a full refund.

## Tiny Numeric Example

- You want to swap 1,000 Token A for Token C.
- **Direct pool A->C**: 1,000 A gives you 800 C after slippage and a 0.3% fee.
- **Path A->B->C**:
  - Pool A->B: 1,000 A gives 950 B.
  - Pool B->C: 950 B gives 902 C.
- The router selects A->B->C because it yields 902 C versus 800 C.
- If you had tried to do this manually via A->C, you would have lost 102 C.
- The router executes both swaps in one transaction, so you never hold Token B yourself.

## Common Confusion

- **No.** A router is not a liquidity pool. It does not hold tokens; it only directs your trade through pools that do.
- **No.** It does not guarantee the best price forever. It guarantees the best price at the exact moment the transaction is simulated and submitted. Prices can change in the next block.
- **No.** It is not a centralized black box. Many routers are open-source smart contracts, and their pathfinding logic is transparent.
- **No.** It does not increase gas fees infinitely. While multi-hop trades cost more gas than single hops, the output improvement usually far outweighs the extra cost.
- **No.** It does not require you to own intermediary tokens. The router handles the entire sequence; your wallet only sees the final output token.
- **No.** A router is not only for Ethereum. Every major DeFi ecosystem, including Solana, uses routing to aggregate fragmented liquidity.

## Key Properties

1. **Pathfinding**: Uses graph algorithms to explore token pairs as edges in a graph, finding the most favorable traversal.
2. **Atomic Execution**: All hops succeed or the entire transaction fails, protecting the trader from partial execution.
3. **Slippage Protection**: The router enforces a minimum output amount, reverting if market movement makes the trade unfavorable.
4. **Split Routing**: Large trades can be divided across multiple parallel paths to minimize price impact in any single pool.
5. **Aggregator Role**: It can route through any type of liquidity, including AMMs, order books, and even private market makers.

## Where It Appears

- Uniswap Universal Router
- 1inch Aggregation Protocol
- Paraswap
- Jupiter on Solana
- CowSwap (which uses solvers that act as advanced routers)
