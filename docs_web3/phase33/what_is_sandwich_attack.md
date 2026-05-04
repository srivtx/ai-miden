# What Is a Sandwich Attack

**The Problem:**

When a large trade is visible before execution, attackers can place two coordinated transactions around it to artificially inflate and then deflate the price, pocketing the difference. A sandwich attack combines front running and back running into a single exploitation that guarantees profit at the trader's expense. This predatory behavior degrades liquidity and drives users away from decentralized markets.

**Definition:**

A sandwich attack is a two-step MEV strategy where an attacker places a buy order immediately before a victim's large trade and a sell order immediately after it. The attacker's first transaction pushes the price up, the victim buys at the inflated price, and the attacker's second transaction sells back the same tokens into the now higher market.

**How It Works (Step-by-Step):**

1. **Identification:** The attacker monitors pending transactions and identifies a large swap that will move the pool price meaningfully.
2. **Front-run buy:** The attacker submits a buy transaction with higher priority fees to be placed immediately before the victim's swap.
3. **Price inflation:** The attacker's purchase reduces the pool's reserve of the target token, raising its price according to the constant-product formula.
4. **Victim execution:** The victim's swap executes at the worse price, receiving fewer tokens than they would have at the true market rate.
5. **Back-run sell:** The attacker submits a sell transaction immediately after the victim's swap, selling exactly the tokens they bought in step 2.
6. **Profit capture:** The attacker receives more quote tokens than they spent, while the victim absorbs the loss as excess slippage.

**Real-life analogy:**

Picture an art auction where a collector plans to bid one million dollars on a painting. A manipulator bids nine hundred thousand dollars just before the collector, driving the perceived value up. The collector then bids one million as planned. Immediately after, the manipulator sells the exact same painting they just bought to the collector for one million dollars. The collector overpaid because the manipulator manufactured temporary demand and then sold back what they had purchased.

**Tiny numeric example:**

A victim swaps USDC for ETH in a constant-product pool with 1,000 ETH and 1,000,000 USDC. The invariant k = 1,000,000,000.

| Step | Action | ETH in Pool | USDC in Pool | ETH Price (USDC/ETH) |
|------|--------|-------------|--------------|----------------------|
| Start | Initial | 1,000 | 1,000,000 | 1,000.00 |
| Attacker buy | Buy 10 ETH | 990 | 1,010,101.01 | 1,020.30 |
| Victim buy | Buy 50 ETH | 940 | 1,063,829.79 | 1,131.73 |
| Attacker sell | Sell 10 ETH | 950 | 1,052,631.58 | 1,108.03 |

Exact math preserving k = 1,000,000,000 at every step:
- Attacker buys 10 ETH: pays 1,000,000,000 / (1,000 - 10) - 1,000,000 = 10,101.01 USDC. Pool becomes 990 ETH and 1,010,101.01 USDC.
- Victim buys 50 ETH: pays 1,000,000,000 / (990 - 50) - 1,010,101.01 = 53,728.78 USDC. Pool becomes 940 ETH and 1,063,829.79 USDC.
- Attacker sells 10 ETH: receives 1,063,829.79 - 1,000,000,000 / (940 + 10) = 11,198.21 USDC. Pool becomes 950 ETH and 1,052,631.58 USDC.

Attacker profit: 11,198.21 - 10,101.01 = 1,097.20 USDC.
Victim extra cost: 53,728.78 - (1,000,000,000 / 950 - 1,000,000) = 53,728.78 - 52,631.58 = 1,097.20 USDC.

**Common confusion:**

- A sandwich attack is not the same as normal market volatility. It is a deliberate, coordinated manipulation by a single actor. No.
- The victim's trade does not need to be huge. Even moderate trades in shallow pools can be profitably sandwiched. No.
- Sandwich attacks are not risk-free. If the victim cancels or another trader intervenes, the attacker may be left holding inventory at a loss. No.
- Slippage tolerance does not prevent sandwiching. It merely limits the maximum damage but still allows extraction up to that limit. No.
- Private mempools do not eliminate the risk. They shift the trust model to the mempool operator. No.
- Sandwich attacks are not limited to AMMs. Any on-chain market with visible order flow is a potential target. No.

**Key properties:**

- The attacker holds the asset only for the duration of a single block.
- Profit is bounded by the victim's slippage tolerance setting.
- The attack requires three transactions ordered precisely in the same block.
- It harms liquidity providers indirectly by generating toxic flow and deterring organic traders.

**Where it appears in our code:**

Sandwich protection is enforced in `src_web3/phase33/protected_swap/src/lib.rs`, where the program validates that the output amount meets the user's minimum expectation and rejects transactions that exceed slippage bounds.
