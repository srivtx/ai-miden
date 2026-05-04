# What Is Leverage

## Why It Exists

Financial markets have participants with strong convictions but limited capital. A trader who believes an asset will double in price may only have one thousand dollars to deploy. Without leverage, the maximum gain is one thousand dollars, which may not justify the research and risk involved. Leverage exists to amplify exposure, allowing a trader to control a much larger position than their cash balance would normally permit. This magnifies both profits and losses, turning small price movements into significant outcomes. In decentralized finance, leverage is implemented through margin systems and overcollateralized loans, enabling on-chain speculation without traditional broker relationships.

## Definition

Leverage is the use of borrowed capital or margin to increase the potential return of an investment. It is expressed as a multiple, such as 2x, 5x, or 10x, indicating how many times larger the position is compared to the trader's own capital. A 5x leveraged position means the trader contributes 20% of the notional value and borrows or implicitly controls the remaining 80%. The borrowed portion is secured by the trader's collateral, which can be seized if the position moves against them beyond a predefined threshold.

## Real-Life Analogy

Imagine you want to buy a house worth $500,000 but you only have $100,000 in savings. A bank lends you the remaining $400,000, and you use the house itself as collateral. If the house rises to $600,000, your equity becomes $200,000, which is a 100% return on your $100,000 investment even though the asset only rose 20%. However, if the house falls to $400,000, your equity is wiped out completely. The bank does not care about your opinion; it will foreclose and sell the house to recover its loan. This is leverage in property investment, and the same logic applies to digital assets.

The house is the leveraged asset. Your savings are the margin. The bank loan is the borrowed notional. Foreclosure is liquidation.

## Tiny Numeric Example

A trader has $1,000 and opens a 10x long position on SOL:

| Metric | Value |
|--------|-------|
| Trader Capital | $1,000 |
| Leverage | 10x |
| Total Position Size | $10,000 |
| SOL Entry Price | $20 |
| SOL Quantity | 500 SOL |
| Liquidation Price | $18.10 (roughly 9.5% below entry) |

If SOL rises to $22, the position is worth $11,000. After repaying the borrowed $9,000, the trader has $2,000, a 100% gain on the original $1,000. If SOL falls to $18, the position is worth $9,000. The trader's equity is now $0, and the position is liquidated before it goes negative. A mere 10% price drop erased 100% of the trader's capital. The liquidation price is slightly above the theoretical 10% threshold to account for fees, slippage, and a maintenance margin buffer.

## Common Confusion

- Leverage is not free money.
  It amplifies losses just as aggressively as it amplifies gains.
- Higher leverage does not mean higher probability of profit.
  It means higher sensitivity to price volatility and faster liquidation.
- Isolated margin is not the same as cross margin.
  Isolated margin limits liquidation to one position, while cross margin uses your entire account as collateral.
- Liquidation price is not the breakeven price.
  It is the price at which your collateral no longer covers the borrowed notional.
- Maintenance margin is not your initial deposit.
  It is the minimum equity ratio you must maintain to avoid liquidation.
- Leverage on decentralized platforms is not unlimited.
  Protocols cap leverage to protect lenders and prevent cascading liquidations.
- Using leverage does not make you a sophisticated trader.
  It makes you a trader with higher risk exposure, which requires stricter risk management.
- Funding fees on leveraged positions are not interest on the borrowed amount.
  They are payments to balance the perpetual price, though they act similarly to a carrying cost.

## Key Properties

- Multiplier effect on both gains and losses relative to price movement
- Collateral requirement that secures the borrowed or controlled notional
- Liquidation threshold that closes the position before insolvency
- Margin modes (isolated vs cross) that control how collateral is allocated across positions

## Where It Appears in Our Code

Leverage and margin logic is implemented in `src_web3/phase41/perpetual_api.ts`.
The API accepts a leverage parameter when opening a position and computes the required initial margin.
It tracks the liquidation price in real time and simulates forced closure when the mark price crosses the threshold.
This demonstrates how collateral, notional size, and price volatility interact in leveraged trading.
