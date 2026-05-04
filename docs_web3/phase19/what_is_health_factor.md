## What Is a Health Factor?

**The Problem:**
Borrowers in a lending protocol need a simple, standardized way to
understand how close they are to liquidation.

Comparing raw collateral and debt values is confusing because different
assets have different prices, liquidation thresholds, and volatility
profiles.
A single normalized number that works across all collateral types allows
borrowers to monitor their risk at a glance and gives liquidators a
clear trigger for action.

**Definition:**
Health Factor is a normalized ratio that measures the safety of a loan
by comparing the liquidation-adjusted value of collateral to the total
debt.

It is typically calculated as the sum of each collateral asset
multiplied by its liquidation threshold, divided by the total debt
value.
A Health Factor above one means the position is safe.
A Health Factor below one means the position is eligible for
liquidation.

**Real-life analogy:**
Imagine a fuel gauge in a car.
Instead of showing liters remaining, it shows a percentage from zero to
one hundred.
At fifty percent, you know you are halfway to empty.
At twenty percent, you know you should find a gas station soon.
At five percent, you are in critical danger of stalling.

Health factor works the same way: it abstracts away the complex details
of tank size, fuel efficiency, and distance to destination and gives you
one number that tells you how safe you are.

Above one point five is comfortable.
Between one point two and one point five is caution.
Below one point zero means the engine stops immediately.

**Tiny numeric example:**
Alice deposits two ETH worth four thousand USDC as collateral.
The liquidation threshold for ETH is eighty percent.
She borrows two thousand five hundred USDC.

| ETH Price | Collateral Value | Liquidation Threshold | Adjusted Collateral | Debt | Health Factor |
|-----------|------------------|-----------------------|---------------------|------|---------------|
| $2,000    | $4,000           | 80%                   | $3,200              | $2,500| 1.28          |
| $1,800    | $3,600           | 80%                   | $2,880              | $2,500| 1.15          |
| $1,600    | $3,200           | 80%                   | $2,560              | $2,500| 1.02          |
| $1,562.50 | $3,125           | 80%                   | $2,500              | $2,500| 1.00          |
| $1,500    | $3,000           | 80%                   | $2,400              | $2,500| 0.96          |

At one thousand five hundred dollars per ETH, the health factor drops
below one and liquidation is triggered.
The formula makes it easy to see exactly when the position becomes
unsafe without manually comparing complex numbers.

**Common confusion:**
- **"Health factor is the same as collateral ratio."**
  No. Collateral ratio is collateral divided by debt.
  Health factor applies liquidation thresholds to each asset, making it
  a more accurate measure of liquidation risk.

- **"Health factor above one means you cannot lose money."**
  No. It only means you are not currently liquidatable.
  The market can move against you instantly, and you can still suffer
  losses from price drops.

- **"All assets have the same liquidation threshold."**
  No. Stable assets like USDC might have ninety percent thresholds,
  while volatile assets like altcoins might have fifty percent.
  Health factor accounts for these differences.

- **"Health factor is calculated once and stays the same."**
  No. It is recalculated continuously based on live oracle prices.
  A position can go from safe to liquidatable within a single block.

- **"You can increase health factor by borrowing more."**
  No. Borrowing more increases debt, which decreases health factor.
  To increase it, you must deposit more collateral or repay part of
  the loan.

- **"Health factor protects you from liquidation."**
  No. It is only a measurement.
  It does not prevent liquidation.
  It warns you that liquidation is approaching so you can take action.

- **"Health factor is universal across all protocols."**
  No. Different protocols use different formulas, threshold values, and
  asset weights.
  A health factor of one point two in Protocol A may represent a
  different risk level than one point two in Protocol B.

**Where it appears in our code:**
`src_web3/phase19/lending/src/lib.rs` — The program calculates health
factor on every borrow and liquidation check by multiplying collateral
values by their thresholds and dividing by total debt.

`src_web3/phase19/lending_api.ts` — The Express API displays real-time
health factors, color-codes risk levels, and triggers liquidation alerts
when the value drops below one.
