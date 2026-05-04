## What Is Impermanent Loss?

**The Problem:**
When you deposit two tokens into a liquidity pool, the automated market
maker formula forces the pool to maintain a specific ratio of those
tokens.

If the market price of one token rises significantly compared to the
other, arbitrageurs will trade against the pool until its internal
price matches the external market.

This process leaves the pool holding more of the depreciating asset
and less of the appreciating one than if you had simply held the
tokens in your wallet.

The loss is called impermanent because it reverses if prices return to
their original ratio, but in practice prices rarely revert perfectly.

**Definition:**
Impermanent loss is the opportunity cost experienced by liquidity
providers when the price ratio of the pooled assets changes compared
to simply holding the assets outside the pool.

It is the difference in value between holding tokens in a wallet
versus holding them in a liquidity pool, assuming no fee income.
The loss is realized when the provider withdraws their liquidity at
the new price ratio.

**Real-life analogy:**
Imagine you and a friend each put five hundred dollars cash and five
hundred dollars worth of gold into a shared safe.
You agree that the safe must always hold equal dollar value of cash
and gold.

If gold doubles in price, the safe automatically rebalances by selling
some gold for cash to maintain the fifty-fifty split.
When you later open the safe, you have more cash but less gold than
you started with.

If you had simply kept your original five hundred dollars cash and
five hundred dollars worth of gold in separate drawers at home, you
would now have fifteen hundred dollars total.
But because the safe rebalanced, you have less.

The difference is your impermanent loss.
The safe earned a small fee every time someone peeked inside, but if
that fee was smaller than your loss, you would have been better off
not participating.

**Tiny numeric example:**
You deposit 1 ETH and 1,000 USDC when ETH is priced at $1,000.
Total value: $2,000.

| Scenario | ETH Price | Pool ETH | Pool USDC | Pool Value | Hold Value | Impermanent Loss |
|----------|-----------|----------|-----------|------------|------------|------------------|
| Start    | $1,000    | 1.000    | 1,000     | $2,000     | $2,000     | $0               |
| ETH +25% | $1,250    | 0.894    | 1,118     | $2,236     | $2,250     | $14              |
| ETH +50% | $1,500    | 0.816    | 1,225     | $2,449     | $2,500     | $51              |
| ETH +100%| $2,000    | 0.707    | 1,414     | $2,828     | $3,000     | $172             |
| ETH +400%| $5,000    | 0.447    | 2,236     | $4,472     | $6,000     | $1,528           |

At a one hundred percent price increase, holding would be worth three
thousand dollars, but the pool is worth only two thousand eight
hundred twenty-eight dollars.

The one hundred seventy-two dollar gap is impermanent loss.
If the pool earned two hundred dollars in fees during this period,
the provider still comes out ahead.
If it earned only one hundred dollars, the provider lost money
relative to holding.

**Common confusion:**
- **"Impermanent loss means you lost tokens."**
  No. You may actually have more total dollar value than you started
  with. Impermanent loss is relative to the hypothetical value of
  holding, not an absolute loss of principal.

- **"The loss is truly impermanent and always recovers."**
  No. The name is misleading. If prices never return to the original
  ratio, the loss becomes permanent.
  It is only "impermanent" in the mathematical sense that it would
  vanish if prices reverted.

- **"Fees always compensate for impermanent loss."**
  No. In volatile markets or during strong directional trends,
  impermanent loss can far exceed fee income.
  Providers must carefully choose pools where expected volume
  justifies the risk.

- **"Impermanent loss only happens in two-token pools."**
  No. Any pool where the AMM rebalances assets based on price ratios
  exposes providers to this effect.
  Multi-token pools and weighted pools also experience it, though the
  math is more complex.

- **"Stablecoin pools have no impermanent loss."**
  They have much less because the prices are pegged, but depegs can
  cause significant losses.
  If one stablecoin drops to ninety cents, the pool accumulates the
  broken stablecoin and sheds the healthy one.

- **"You can avoid impermanent loss by choosing the right pool."**
  You can minimize it by choosing correlated assets or very deep pools,
  but you cannot eliminate it entirely in any standard AMM without
  giving up fees or using exotic derivatives.

- **"Impermanent loss is a bug in the AMM design."**
  No. It is an inherent mathematical property of any system that
  maintains a constant ratio or product.
  It is the price liquidity providers pay for earning passive fees.

**Where it appears in our code:**
`src_web3/phase17/liquidity_pool/src/lib.rs` — The withdrawal
instruction calculates the current reserve ratio, demonstrating how
providers receive a rebalanced mix of tokens.

`src_web3/phase17/liquidity_api.ts` — The API includes an impermanent
loss calculator that compares pool value versus hold value at current
prices.
