# What Is a Perpetual Future

## Why It Exists

Traditional futures contracts expire on a specific date, forcing traders to roll their positions into new contracts or take physical delivery of the underlying asset. This creates friction for speculators who simply want to bet on price direction without managing settlement logistics. In the cryptocurrency markets, the demand for simple leveraged exposure never stops, yet creating a new monthly contract every month fragments liquidity and confuses retail participants. A perpetual future solves this by removing the expiration date entirely, allowing a position to remain open indefinitely as long as the trader can maintain sufficient margin. This innovation transforms futures from a hedging instrument for commodity producers into a pure price speculation tool for digital assets.

## Definition

A perpetual future is a derivative contract that tracks the price of an underlying asset without an expiration or settlement date. Traders can hold long or short positions indefinitely, paying or receiving periodic funding payments to keep the contract price anchored to the spot market. The contract is settled in cash or collateral rather than physical delivery, and leverage allows traders to control larger notional positions than their deposited margin would normally permit.

## Real-Life Analogy

Imagine a rental agreement for an apartment that never ends and never requires you to buy the building. Every day, the landlord checks whether similar apartments are renting for more or less than your rate. If your rent is below market, you pay the landlord a small daily adjustment. If your rent is above market, the landlord pays you. This daily payment keeps your effective rent close to the true market price, even though the lease itself has no termination date. You can leave anytime by giving notice, but as long as you stay and keep paying the adjustment, the agreement continues forever.

The apartment is the underlying asset. The endless lease is the perpetual contract. The daily adjustment is the funding payment. The security deposit you gave the landlord is your margin. If apartment prices crash and your deposit no longer covers the risk, the landlord evicts you and keeps the deposit, which is liquidation.

## Tiny Numeric Example

A trader opens a long perpetual position when ETH spot is $2,000:

| Field | Value |
|-------|-------|
| Position Size | 2 ETH |
| Entry Price | $2,000 |
| Leverage | 5x |
| Required Margin | $800 (20%) |
| Perpetual Mark Price | $2,010 |
| Funding Interval | 8 hours |
| Funding Rate | 0.01% (positive, longs pay shorts) |

The position is underwater immediately because the mark price is higher than entry. After 8 hours, the funding payment occurs. The trader pays 2 * $2,010 * 0.0001 = $0.402 to shorts. If the spot price drops to $1,900 and mark follows, the position has an unrealized loss of 2 * ($1,900 - $2,000) = -$200. With only $800 margin, the position is 25% down. A further drop to $1,840 triggers liquidation because the remaining margin cannot cover the loss.

## Common Confusion

- A perpetual future is not the same as owning the asset.
  You have price exposure but no staking rights, airdrops, or governance tokens.
- Funding rate is not an interest rate on borrowed capital.
  It is a payment that rebalances the contract price toward the spot index.
- Perpetual exchanges are not necessarily decentralized.
  Many popular platforms operate off-chain order books with centralized matching engines.
- High leverage is not free money.
  A 10x position can be liquidated by a 10% move, which is common in crypto.
- Mark price is not the last traded price.
  It is an index-based estimate used to calculate unrealized PnL and avoid manipulation.
- Liquidation does not mean you lose the full margin instantly.
  Some protocols use partial liquidation or insurance funds to soften the blow.
- Holding a perpetual long forever is not costless.
  You pay funding every interval, which can accumulate to exceed the spot gain.
- Decentralized perpetual protocols do not eliminate counterparty risk.
  Smart contract bugs and oracle failures can still cause losses.

## Key Properties

- No expiration date, enabling indefinite directional exposure
- Funding payments every 1 to 8 hours to align mark and index prices
- Leverage up to 50x or more on some platforms, magnifying both gains and losses
- Cash settlement in stablecoins or collateral tokens rather than physical delivery
- Liquidation engines that close positions before margin turns negative

## Where It Appears in Our Code

Perpetual market simulation logic is implemented in `src_web3/phase41/perpetual_api.ts`.
The API exposes endpoints to open positions, compute funding payments, and trigger liquidations based on mark price movements.
It tracks unrealized profit and loss using isolated margin mechanics so that each position stands on its own collateral.
