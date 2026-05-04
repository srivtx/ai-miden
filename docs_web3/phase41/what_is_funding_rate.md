# What Is a Funding Rate

## Why It Exists

If a perpetual future had no mechanism to tether its price to the spot market, the contract could drift arbitrarily far from the underlying asset. Traders might push the perpetual premium to 20% above spot during a frenzy, creating a broken derivative that no longer reflects reality. A funding rate exists to apply economic pressure that continuously pulls the perpetual price back toward the spot index. When the perpetual trades above spot, longs pay shorts. When it trades below, shorts pay longs. This payment creates a cost for the majority side and an incentive for the minority side, restoring balance without any centralized intervention or forced settlement.

## Definition

A funding rate is a periodic payment exchanged between long and short holders of a perpetual futures contract. The rate is positive when the perpetual trades at a premium to the spot index, meaning longs pay shorts. It is negative when the perpetual trades at a discount, meaning shorts pay longs. The payment occurs every funding interval, typically every 1, 4, or 8 hours, and is proportional to the notional position size.

## Real-Life Analogy

Imagine a seesaw in a playground that represents the price of an asset. The middle pivot is the spot price. When too many children pile onto the long side, that side dips down and the other side rises. The funding rate is like a parent who hands out small treats to the children on the high side and takes treats away from the children on the low side. The heavier side gradually becomes less appealing because its participants keep losing treats, while the lighter side attracts more children because they gain treats. Over time, the seesaw returns to a balanced position near the middle pivot, even though no one forced the children to move.

The children are traders. The treats are funding payments. The parent is the protocol's automatic rebalancing mechanism. The middle pivot is the spot index price.

## Tiny Numeric Example

Consider a BTC perpetual market with the following state:

| Metric | Value |
|--------|-------|
| Spot Index Price | $30,000 |
| Perpetual Mark Price | $30,300 |
| Premium | $300 (1.0%) |
| Funding Interval | 8 hours |
| Position Size | 1 BTC |

The positive premium indicates heavy long interest. The funding rate is calculated as a fraction of the premium, say 0.05% for this interval. The long holder pays 1 * $30,300 * 0.0005 = $15.15 to the short holder every 8 hours. Over one month (90 intervals), this accumulates to $1,363.50. If the spot price stays flat at $30,000, the long holder loses money purely from funding, while the short holder earns it. This cost discourages new longs from entering and encourages arbitrageurs to short the perpetual while buying spot, driving the premium back toward zero.

## Common Confusion

- Funding rate is not an interest rate paid to the exchange.
  It is a peer-to-peer payment between traders with opposite positions.
- A high funding rate does not guarantee that the price will fall.
  It only indicates that longs are aggressive, and they are willing to pay to maintain exposure.
- Negative funding does not mean the market is crashing.
  It means shorts are dominant and must pay longs to keep their positions.
- Funding is not charged on your entire account balance.
  It is applied only to the notional size of your open perpetual position.
- The exchange does not keep funding payments.
  On decentralized protocols, the payments flow directly between contract counterparties.
- Funding intervals are not always 8 hours.
  Some protocols use 1-hour or even continuous funding to react faster to premium deviations.
- Funding rate calculations are not standardized across exchanges.
  Each platform uses its own formula based on index constituents and premium averaging windows.
- You cannot avoid funding by closing right before the interval.
  Most protocols use a time-weighted position snapshot to prevent this gaming.

## Key Properties

- Premium-based formula derived from the difference between mark and index prices
- Interval-based payments that create carry costs for directional exposure
- Auto-balancing mechanism that reduces the need for external arbitrageurs
- Transparent on-chain calculation that anyone can verify before holding overnight

## Where It Appears in Our Code

Funding rate logic is implemented in `src_web3/phase41/perpetual_api.ts`.
The API calculates the premium between a simulated mark price and an index price.
It applies the funding payment to open positions at regular intervals and adjusts margin balances accordingly.
This ensures that simulated perpetual prices do not diverge unrealistically from the spot market.
