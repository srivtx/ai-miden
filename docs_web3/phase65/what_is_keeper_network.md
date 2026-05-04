# What Is a Keeper Network?

## The Problem

On-chain smart contracts cannot trigger themselves. A program sitting on Solana has no internal clock, no daemon, and no ability to wake up and say "liquidate this position now." If a trader becomes underwater, the blockchain itself will never spontaneously execute a liquidation. Someone must poke the contract. Without that external poke, bad debt accumulates, solvency breaks, and the exchange collapses.

## Definition

A keeper network is a decentralized fleet of off-chain bots that continuously monitor on-chain state, detect protocol-defined trigger conditions (like an underwater margin account), and submit transactions to execute the required action (usually liquidation or settlement). Keepers are not employed by the protocol; they are independent, profit-seeking operators who earn fees for keeping the system healthy.

## How It Works

1. **Monitor positions.** Each keeper maintains a WebSocket or RPC subscription to every margin account in the protocol, tracking collateral, perp exposure, and oracle prices in real time.
2. **Detect underwater.** The keeper computes the margin ratio for every user: `(total collateral) / (position notional * maintenance margin requirement)`. If the ratio drops below 1.0, the account is liquidatable.
3. **Calculate reward.** Drift offers a liquidation incentive: the keeper earns a percentage of the liquidated collateral as a fee. The keeper simulates the transaction to confirm the exact profit before spending gas.
4. **Submit liquidation.** The keeper builds and signs a `liquidatePerp` or `liquidateSpot` transaction using the Drift SDK and broadcasts it to the Solana network.
5. **Collect fee.** If the transaction lands first, the protocol transfers the liquidation reward into the keeper's wallet. If another keeper was faster, this keeper pays gas and earns nothing.
6. **Repeat.** The keeper loops indefinitely, polling or streaming account updates every 400 ms.

## Real-life Analogy

Imagine a parking garage where cars are towed the moment they overstay. The garage owner does not employ tow-truck drivers. Instead, any independent tow company can watch the garage, identify expired cars, and tow them. The first truck to arrive keeps the impound fee. The garage stays clear, and the tow companies compete for profit. The garage cannot tow itself; it relies on external watchers.

## Tiny Numeric Example

Alice has $10,000 in USDC collateral and a 5x leveraged SOL-PERP long with $50,000 notional. Maintenance margin requirement is 5%.

- Maintenance requirement: $50,000 * 5% = $2,500
- Margin ratio: $10,000 / $2,500 = 4.0 (safe)

SOL drops 15%. Her position notional is now $42,500. Her collateral drops to $2,500 (unrealized loss of $7,500).

- New margin ratio: $2,500 / ($42,500 * 5%) = $2,500 / $2,125 = 1.18 (still above 1.0, but close)

SOL drops another 3%. Notional is $41,225. Collateral is $1,775.

- New margin ratio: $1,775 / ($41,225 * 5%) = $1,775 / $2,061 = 0.86 (underwater)

A keeper detects this. Drift offers a 2.5% liquidation fee on the liquidated notional. The keeper liquidates the full position.

- Liquidation fee: $41,225 * 2.5% = $1,030.62
- Keeper pays ~$0.02 in Solana transaction fees.
- Keeper profit: ~$1,030.60.
- Alice's remaining collateral: $1,775 - $1,030.62 = $744.38 returned to her.

## Common Confusion

- Are keepers employees of the protocol?
  - No. They are independent, permissionless operators. Anyone with a bot and SOL for gas can run a keeper.

- Do keepers need special permissions or whitelisting?
  - No. Liquidation functions are public instructions on the Drift program. No signer restrictions exist beyond the standard transaction requirements.

- Can a keeper steal user funds?
  - No. The protocol enforces strict liquidation math. The keeper only receives the protocol-defined fee; they cannot arbitrarily confiscate collateral.

- Is there only one keeper?
  - No. Thousands of bots compete globally. The winner is determined by latency, priority fees, and RPC location.

- Do keepers work for free?
  - No. They are purely economically motivated. If liquidation profitability drops below gas costs, they stop monitoring.

- Are keepers unique to Drift?
  - No. Every major DeFi protocol (Aave, dYdX, Mango) relies on keeper-like bots for liquidations, oracle updates, or order matching.

## Key Properties

1. **Permissionless entry.** No KYC, no registration, no staking requirement to start monitoring.
2. **Winner-takes-all competition.** Only the first transaction to land earns the reward; the rest burn gas.
3. **Economic liveness guarantee.** If the protocol is profitable to liquidate, rational actors will appear to do the work.
4. **No protocol custody.** Keepers never hold user funds; they only trigger state transitions the smart contract already allows.
5. **Latency-critical.** Success depends on sub-second RPC streaming, optimized transaction building, and aggressive priority-fee bidding.
