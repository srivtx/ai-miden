## What Is Slippage?

**The Problem:**
When a trader places an order on an AMM, they see the current price
displayed by the pool ratio. However, by the time their transaction
executes, their own trade has altered the pool's reserves.

The larger the trade relative to the pool's depth, the worse the final
price becomes compared to the initial quoted price. Traders need to
understand and protect themselves against this hidden cost, which can
turn a profitable arbitrage into an instant loss.

Slippage is the invisible tax that large traders pay for moving the
market against themselves.

**Definition:**
Slippage is the percentage difference between the expected price of a
trade and the actual average price received after execution.

It is caused entirely by the trade itself moving the pool ratio along
the pricing curve. Slippage is not a fee paid to anyone; it is a
market impact cost inherent to trading in pools with finite liquidity.

The more liquidity a pool has, the less slippage a given trade will
cause.

**Real-life analogy:**
Imagine you are buying apples at a roadside stand that has a flexible
pricing rule. The first apple costs one dollar. But the stand owner
believes in dynamic pricing: every apple you buy raises the price of
the next apple by a few cents because the stand's inventory shrinks.

If you buy one apple, you pay one dollar. If you buy one hundred
apples, the last apple might cost two dollars, and your average price
is one fifty.

The slippage is the fifty cents per apple you lost because your own
bulk purchase moved the market against you. In an AMM, there is no
owner setting prices, but the math does exactly the same thing
automatically.

**Tiny numeric example:**
Pool contains 10,000 Token A and 10,000 Token B.
The spot price is exactly 1.0.

| Amount A Swapped | B Received | Expected B | Slippage Cost | Slippage % |
|------------------|------------|------------|---------------|------------|
| 10               | 9.99       | 10.00      | 0.01          | 0.1%       |
| 100              | 99.01      | 100.00     | 0.99          | 1.0%       |
| 500              | 476.19     | 500.00     | 23.81         | 4.8%       |
| 1,000            | 909.09     | 1,000.00   | 90.91         | 9.1%       |
| 5,000            | 3,333.33   | 5,000.00   | 1,666.67      | 33.3%      |

A trade of five thousand A against a ten thousand A pool causes
thirty-three percent slippage. The trader receives only three thousand
three hundred thirty-three B instead of the five thousand they might
have expected.

This is why traders often split large orders across multiple pools or
use time-weighted average price strategies to minimize market impact.

**Common confusion:**
- **"Slippage is a hidden fee charged by the protocol."**
  No. Slippage is not sent to validators, developers, or liquidity
  providers. It is simply the worse price you receive because your trade
  changed the pool ratio. Fees are separate and usually much smaller
  than slippage on large trades.

- **"Slippage only happens when the market is volatile."**
  No. Slippage happens on every trade, even in completely flat markets.
  It is purely a function of trade size relative to pool depth.
  A one-million-dollar trade in a small pool will suffer massive
  slippage even if the external market has not moved at all.

- **"Setting a low slippage tolerance prevents slippage."**
  No. Setting a low slippage tolerance only causes your transaction to
  revert if the slippage exceeds your threshold. It does not reduce the
  actual slippage. To reduce slippage, you must either trade a smaller
  amount or use a deeper pool.

- **"Slippage and price impact are different things."**
  In AMM terminology, they are essentially the same concept.
  Price impact is the absolute price change, while slippage is usually
  expressed as a percentage. Both measure how much your own trade moves
  the market.

- **"All pools have the same slippage for the same trade size."**
  No. Slippage depends entirely on the ratio of trade size to pool
  depth. A five-thousand-dollar trade in a one-million-dollar pool has
  negligible slippage, but the same trade in a ten-thousand-dollar pool
  is devastating.

- **"Front-running causes slippage."**
  Front-running is a separate problem where bots see your transaction
  and trade before you to profit from your price movement.
  While front-running worsens your outcome, slippage exists even in a
  world with no front-running because of the mathematical curve.

- **"Stablecoin pools have no slippage."**
  They have less slippage near parity thanks to specialized curves, but
  large trades still cause slippage. A stableswap pool is not a flat
  line; it is just flatter near the one-to-one ratio.

**Where it appears in our code:**
`src_web3/phase16/amm/src/lib.rs` — The swap instruction calculates the
new reserves and inherently produces slippage as a side effect of
enforcing the constant product formula.

`src_web3/phase16/amm_api.ts` — The calculateSwap function explicitly
computes priceImpact as a percentage, and the swap endpoint returns
slippage data to the trader before execution.
