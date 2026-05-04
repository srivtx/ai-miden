# What Is a Sandwich Attack

## Why It Exists

When a large trade is visible before execution, attackers can place two transactions around it to artificially inflate and then deflate the price, pocketing the difference. A sandwich attack combines front running and back running into a single coordinated exploitation that guarantees profit at the trader's expense. This predatory behavior degrades liquidity and drives users away from decentralized markets.

## Definition

A sandwich attack is a two-step MEV strategy where an attacker places a buy order immediately before a victim's large trade and a sell order immediately after it. The attacker's first transaction pushes the price up, the victim buys at the inflated price, and the attacker's second transaction sells back into the now higher market.

## Real-Life Analogy

Picture an art auction where a collector plans to bid one million dollars on a painting. A manipulator bids nine hundred thousand just before the collector, driving the perceived value up. The collector then bids one million as planned. Immediately after, the manipulator withdraws their bid and sells a replica they already owned to the collector for one million. The collector overpaid because the manipulator manufactured temporary demand.

## Tiny Numeric Example

A victim swaps 100,000 USDC for ETH in a constant product pool with 1,000 ETH and 2,000,000 USDC:

| Step | Action | ETH in Pool | USDC in Pool | ETH Price |
|------|--------|-------------|--------------|-----------|
| Start | Initial | 1,000 | 2,000,000 | $2,000 |
| Attacker buy | Buy 5 ETH | 995 | 2,010,050 | $2,020.15 |
| Victim buy | Buy 49.26 ETH | 945.74 | 2,110,050 | $2,121.32 |
| Attacker sell | Sell 5 ETH | 950.74 | 2,089,000 | $2,097.24 |

The attacker profits approximately 21,050 USDC while the victim receives fewer ETH than expected at the true market price.

## Common Confusion

- A sandwich attack is not the same as volatility; it is a deliberate, coordinated manipulation by a single actor.
- The victim's trade does not need to be huge; even moderate trades in shallow pools can be profitably sandwiched.
- Sandwich attacks are not risk-free for attackers; if the victim cancels or another trader intervenes, the attacker may lose money.
- Slippage tolerance does not prevent sandwiching; it merely limits the maximum damage but still allows extraction up to that limit.
- Private mempools do not eliminate the risk; they shift the trust model to the mempool operator.
- Sandwich attacks are not limited to AMMs; any on-chain market with visible order flow is a potential target.
- Users cannot detect a sandwich in real time because the three transactions appear in a single block simultaneously.

## Key Properties
## Where It Appears in Our Code

Sandwich protection is enforced in `src_web3/phase33/protected_swap/src/lib.rs`, where the program validates that the output amount meets the user's minimum expectation and rejects transactions that exceed slippage bounds.
