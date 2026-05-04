## What Is the Constant Product Formula?

**The Problem:**
If an automated market maker simply quoted a fixed price, traders would
drain the entire pool by buying the underpriced asset until nothing
remained. A fixed price cannot adapt to changing supply and demand.

The protocol needs a pricing rule that automatically adjusts as
reserves shift, making large trades progressively more expensive while
guaranteeing the pool never fully empties. Without such a rule, the
exchange would be insolvent within minutes of going live.

The constant product formula was invented to create a self-regulating
market where prices float freely but the pool always retains some
inventory.

**Definition:**
The constant product formula is the mathematical rule x times y equals k,
where x is the reserve of one token, y is the reserve of the other token,
and k is a fixed number that does not change during swaps.

When a trader deposits dx of token x, the pool must release dy of token
y such that the new reserves still multiply to k. This creates a
hyperbolic pricing curve where the marginal price approaches infinity
as either reserve approaches zero, mathematically preventing the pool
from ever running dry.

The formula ensures that every trade is possible but becomes
increasingly expensive as it depletes one side of the pool.

**Real-life analogy:**
Imagine a seesaw in a playground that has a magical constraint:
the product of the weight on the left side and the weight on the right
side must always equal exactly ten thousand pounds squared.

If both sides hold one hundred pounds, the seesaw is balanced.
When you remove ten pounds from the right side, the left side must
instantly adjust to compensate, but not by simple subtraction.
Instead, the left side must now hold one hundred and eleven pounds
to keep the product at ten thousand.

The more weight you remove from one side, the more disproportionately
heavy the other side becomes. Eventually, removing even a tiny amount
from the nearly empty side would require an impossibly large weight on
the other side. This is why the pool never empties: the math makes
the last drop infinitely expensive.

**Tiny numeric example:**
Pool contains 100 Token A and 1,000 Token B.
The constant product k equals 100,000.

| dx (A In) | New A Reserve | New B Reserve | dy (B Out) | Price After |
|-----------|---------------|---------------|------------|-------------|
| 1         | 101           | 990.10        | 9.90       | 9.80        |
| 5         | 105           | 952.38        | 47.62      | 9.07        |
| 10        | 110           | 909.09        | 90.91      | 8.26        |
| 25        | 125           | 800.00        | 200.00     | 6.40        |
| 50        | 150           | 666.67        | 333.33     | 4.44        |

Notice that doubling the trade size more than doubles the output
difference. The first one A yields 9.90 B, but the next four A yield
only 37.72 B. This non-linearity is the core protection mechanism of
the formula. It ensures that no single trader can acquire the entire
reserve without paying an exponentially increasing price.

**Common confusion:**
- **"The constant k never changes."**
  Not exactly. k only stays constant during pure swaps.
  When liquidity providers add or remove funds, k increases or decreases
  because both x and y change simultaneously.
  The formula is only constant during the actual trade execution.

- **"The formula guarantees a fair price."**
  No. The formula guarantees mathematical consistency, not market
  fairness. If the pool price diverges from the external market,
  arbitrageurs will trade until the prices realign, often at the
  expense of the pool's liquidity providers. The formula is blind to
  external reality.

- **"You can derive the price by dividing the reserves."**
  The spot price is y divided by x, but the actual execution price for
  a trade is worse than the spot price because the trade moves the
  reserves along the curve. The execution price is the average over
  the interval, not the instantaneous rate at the start.

- **"The formula works for any number of tokens."**
  The classic x times y equals k only handles two tokens.
  Multi-token pools require more complex formulas, such as those used
  by Balancer, which generalize the concept to weighted pools with
  multiple assets.

- **"Constant product means the price is stable."**
  The opposite is true. The constant product formula is specifically
  designed to allow prices to float freely.
  Stable pools use different curves that keep prices near parity for
  assets like stablecoins.

- **"k is the total value of the pool."**
  No. k has no direct dollar meaning. It is simply the mathematical
  product of the two reserves. A pool with k equals one million could
  hold one penny and ten million dollars, or one thousand dollars and
  one thousand dollars. k is a scalar, not a valuation.

- **"Adding liquidity does not change the price."**
  Correct, but with an important caveat. If you add liquidity at the
  current ratio, the price stays the same. If you add imbalanced
  liquidity, the formula effectively treats part of your deposit as a
  swap, changing the price and causing a loss to existing providers.

**Where it appears in our code:**
`src_web3/phase16/amm/src/lib.rs` — The Rust program enforces x times y
equals k inside the swap instruction by recalculating reserves and
verifying the product remains constant.

`src_web3/phase16/amm_api.ts` — The Express API uses the same formula in
the calculateSwap helper to compute output amounts, price impact, and
fees before executing trades.
