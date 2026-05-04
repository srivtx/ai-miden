# What Is Cross Collateral?

## The Problem

In isolated margin systems, every position is backed by a single collateral asset. If a trader wants to go long ETH-PERP with USDC but also hold SOL as a hedge, the SOL sits idle. Capital efficiency is terrible. Worse, if the trader's only collateral is a volatile asset, a dip in that asset's price simultaneously erodes both their position value and their collateral value, accelerating liquidation.

## Definition

Cross collateral is a margin model that allows a trader to deposit multiple different assets into a single unified margin account. All assets jointly back all positions. The protocol values each asset according to its oracle price and a haircut (margin weight), then sums them into a total effective collateral figure against which all open positions are measured.

## How It Works

1. **Monitor positions.** The protocol tracks every asset in every user's margin basket, updating prices via the oracle network every 400 ms.
2. **Detect underwater.** The margin engine calculates total weighted collateral: for each asset, `(deposited amount * oracle price * asset margin weight)`. If the sum divided by total position maintenance requirement falls below 1.0, the account is liquidatable.
3. **Calculate reward.** The liquidation reward is computed against the total position notional, exactly as in isolated margin. The presence of multiple collateral types does not change the liquidation fee percentage.
4. **Submit liquidation.** A keeper initiates liquidation. The protocol first attempts to repay bad debt by seizing the most liquid collateral asset (usually USDC). If insufficient, it moves down the collateral priority list.
5. **Collect fee.** The keeper receives their fee. The remaining mixed collateral, if any, is returned to the user. Because multiple assets back the position, the user often retains more residual value than in an isolated system.
6. **Repeat.** The cycle runs continuously. Cross-collateral accounts are monitored alongside isolated accounts in the same keeper loop.

## Real-life Analogy

Imagine applying for a business loan. The bank accepts your house, your stock portfolio, and your car as combined collateral. If your business struggles, the bank does not care which asset it seizes first; it cares about the total value. Your diversified backing makes you safer than someone who pledges only one volatile asset. The bank monitors the total package, not individual items in isolation.

## Tiny Numeric Example

Charlie deposits into a cross-collateral margin account:

- 5,000 USDC (weight: 1.0)
- 20 SOL at $100 each = $2,000 (weight: 0.9)
- 0.05 BTC at $60,000 each = $3,000 (weight: 0.95)

Total weighted collateral:

- USDC: $5,000 * 1.0 = $5,000
- SOL: $2,000 * 0.9 = $1,800
- BTC: $3,000 * 0.95 = $2,850
- Total = $9,650

Charlie opens a 3x ETH-PERP long. Notional = $28,950. Maintenance requirement = 5%.

- Maintenance required: $28,950 * 5% = $1,447.50
- Margin ratio: $9,650 / $1,447.50 = 6.67 (safe)

ETH drops 20%. Unrealized loss = $5,790. Weighted collateral still $9,650 (assets unchanged).

- New margin ratio: ($9,650 - $5,790) / $1,447.50 = $3,860 / $1,447.50 = 2.67 (still safe)

ETH drops another 30% from entry. Total unrealized loss = $9,525.

- New margin ratio: ($9,650 - $9,525) / $1,447.50 = $125 / $1,447.50 = 0.086 (underwater)

A keeper liquidates. The protocol seizes USDC first, then SOL, then BTC. The keeper earns 2.5% of notional = $723.75. Charlie's remaining mixed collateral (~$125) is returned. Without cross collateral, if Charlie had used only SOL as collateral, the SOL price drop would have liquidated him far earlier.

## Common Confusion

- Does cross collateral mean I can use any token?
  - No. Only tokens explicitly whitelisted and assigned margin weights by the protocol governance can be used as collateral.

- Are all collateral assets treated equally?
  - No. Each asset has a margin weight (haircut). USDC is usually 1.0; volatile altcoins may be 0.6 or lower.

- Can I withdraw one collateral asset while positions are open?
  - No. Withdrawals are only permitted if the post-withdrawal total weighted collateral still satisfies the initial margin requirement for all open positions.

- Does cross collateral eliminate liquidation risk?
  - No. It improves capital efficiency and diversifies collateral price risk, but if total weighted collateral falls below maintenance, liquidation still occurs.

- Is cross collateral the same as portfolio margin?
  - No. Portfolio margin offsets correlated positions. Cross collateral simply pools multiple assets as backing; it does not reduce margin requirements based on correlation.

- Can a keeper choose which collateral to seize?
  - No. The protocol defines a fixed seizure priority (typically USDC first, then stablecoins, then volatile assets by liquidity).

## Key Properties

1. **Unified risk layer.** All assets and all positions share one margin ratio, simplifying risk management.
2. **Weighted valuation.** Each collateral asset is haircut based on volatility and liquidity, preventing overvaluation of risky tokens.
3. **Capital efficiency.** Traders do not need to convert holdings to a single base asset, reducing swap costs and tax events.
4. **Fixed seizure priority.** The protocol, not the keeper or user, determines which assets are liquidated first.
5. **Governance-controlled whitelist.** New collateral assets require DAO approval, ensuring only sufficiently liquid and oracled tokens enter the pool.
