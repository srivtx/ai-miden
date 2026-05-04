# What Is a Perpetual Future

## The Problem:

Traditional futures contracts expire on a specific date, forcing traders to roll their positions into new contracts or take physical delivery of the underlying asset. This creates friction for speculators who simply want to bet on price direction without managing settlement logistics. In cryptocurrency markets, demand for simple leveraged exposure never stops, yet creating a new monthly contract every month fragments liquidity and confuses retail participants. A perpetual future solves this by removing the expiration date entirely, allowing a position to remain open indefinitely as long as the trader can maintain sufficient margin. This innovation transforms futures from a hedging instrument for commodity producers into a pure price speculation tool for digital assets.

## Definition:

A perpetual future is a derivative contract that tracks the price of an underlying asset without an expiration or settlement date. Traders can hold long or short positions indefinitely, paying or receiving periodic funding payments to keep the contract price anchored to the spot market. The contract is settled in cash or collateral rather than physical delivery, and leverage allows traders to control larger notional positions than their deposited margin would normally permit.

## How It Works (Step-by-Step):

1. A trader deposits collateral (margin) into a perpetual exchange and selects leverage. The notional position size equals Margin multiplied by Leverage.

2. The trader opens a long or short position at the current mark price. The mark price is an index-based estimate derived from spot exchange prices, not the last traded price on the perpetual platform itself.

3. Every funding interval (typically 1 to 8 hours), a funding payment is exchanged between longs and shorts. The payment is calculated as: Funding Payment = Position Size * Mark Price * Funding Rate. If the funding rate is positive, longs pay shorts; if negative, shorts pay longs.

4. The exchange computes unrealized profit and loss (uPnL) continuously. For a long position: uPnL = Position Size * (Mark Price - Entry Price). For a short position: uPnL = Position Size * (Entry Price - Mark Price). A positive uPnL means profit; a negative uPnL means loss.

5. The exchange monitors the margin ratio: Margin Ratio = (Initial Margin + uPnL - Cumulative Funding Paid) / Notional Value. If the mark price moves against the position such that the margin ratio falls below the maintenance margin requirement, the position is flagged for liquidation.

6. Upon liquidation, the exchange's liquidation engine closes the position automatically. The remaining margin after covering losses is returned to the trader; if losses exceed the margin, the insurance fund or a socialized loss mechanism covers the shortfall.

## Real-life analogy:

Imagine a rental agreement for an apartment that never ends and never requires you to buy the building. Every day, the landlord checks whether similar apartments are renting for more or less than your rate. If your rent is below market, you pay the landlord a small daily adjustment. If your rent is above market, the landlord pays you. This daily payment keeps your effective rent close to the true market price, even though the lease itself has no termination date. You can leave anytime by giving notice, but as long as you stay and keep paying the adjustment, the agreement continues forever.

The apartment is the underlying asset. The endless lease is the perpetual contract. The daily adjustment is the funding payment. The security deposit you gave the landlord is your margin. If apartment prices crash and your deposit no longer covers the risk, the landlord evicts you and keeps the deposit, which is liquidation.

## Tiny numeric example:

A trader opens a long perpetual position when ETH spot is $2,000.

| Field | Value |
|-------|-------|
| Position Size | 2 ETH |
| Entry Price | $2,000 |
| Leverage | 10x |
| Required Margin (1 / Leverage) | $400 (10%) |
| Maintenance Margin Requirement | 2.5% of notional |
| Perpetual Mark Price | $2,010 |
| Funding Interval | 8 hours |
| Funding Rate | 0.01% (positive, longs pay shorts) |

**Step 1: Initial unrealized PnL**
uPnL = Position Size * (Mark Price - Entry Price)
uPnL = 2 * ($2,010 - $2,000) = 2 * $10 = +$20
The position is in profit immediately because the mark price is above the entry price.

**Step 2: Funding payment after 8 hours**
Funding Payment = Position Size * Mark Price * Funding Rate
Funding Payment = 2 * $2,010 * 0.0001 = $0.402
The trader pays $0.402 to shorts.

**Step 3: Updated margin state after funding**
Remaining Margin = Initial Margin - Funding Payment + uPnL
Remaining Margin = $400 - $0.402 + $20 = $419.598

**Step 4: Price drops to $1,900**
New uPnL = 2 * ($1,900 - $2,000) = -$200
Remaining Margin = $400 - $0.402 - $200 = $199.598
Notional Value = 2 * $1,900 = $3,800
Margin Ratio = $199.598 / $3,800 = 5.25%
This is above the 2.5% maintenance requirement, so no liquidation occurs.

**Step 5: Price drops further to $1,840**
New uPnL = 2 * ($1,840 - $2,000) = -$320
Remaining Margin = $400 - $0.402 - $320 = $79.598
Notional Value = 2 * $1,840 = $3,680
Maintenance Margin Required = 2.5% * $3,680 = $92.00
Margin Ratio = $79.598 / $3,680 = 2.16%
Since 2.16% is below the 2.5% maintenance requirement, the position is liquidated.

**Step 6: Liquidation outcome**
The liquidation engine closes the 2 ETH position at $1,840. The $79.598 remaining margin is returned to the trader minus any liquidation fee. The $320 loss is absorbed by the counterparty and insurance fund. If the price had gapped below $1,800, the remaining margin would be negative and the insurance fund would cover the shortfall.

## Common confusion:

- A perpetual future is not the same as owning the asset. No. You have price exposure but no staking rights, airdrops, or governance tokens.
- Funding rate is not an interest rate on borrowed capital. No. It is a payment that rebalances the contract price toward the spot index.
- Perpetual exchanges are not necessarily decentralized. No. Many popular platforms operate off-chain order books with centralized matching engines.
- High leverage is not free money. No. A 10x position can be liquidated by a 10% move, which is common in crypto.
- Mark price is not the last traded price. No. It is an index-based estimate used to calculate unrealized PnL and avoid manipulation.
- Liquidation does not mean you lose the full margin instantly. No. Some protocols use partial liquidation or insurance funds to soften the blow.

## Key properties:

- No expiration date, enabling indefinite directional exposure
- Funding payments every 1 to 8 hours to align mark and index prices
- Leverage up to 50x or more on some platforms, magnifying both gains and losses
- Cash settlement in stablecoins or collateral tokens rather than physical delivery
- Liquidation engines that close positions before margin turns negative

## Where it appears in our code:

Perpetual market simulation logic is implemented in `src_web3/phase41/perpetual_api.ts`.
The API exposes endpoints to open positions, compute funding payments, and trigger liquidations based on mark price movements.
It tracks unrealized profit and loss using isolated margin mechanics so that each position stands on its own collateral.
