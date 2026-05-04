## What Is Liquidation?

**The Problem:**
When a borrower posts collateral and takes out a loan, the value of
that collateral can drop due to market volatility.

If the collateral becomes worth less than the loan, the lender is
exposed to loss.
There is no credit department to call the borrower and demand repayment.
The protocol needs an automatic, trustless mechanism to recover the
lender's funds before the collateral value falls below the debt value.

Without liquidation, the entire lending system becomes insolvent during
market downturns.

**Definition:**
Liquidation is the automatic sale of a borrower's collateral by the
smart contract to repay their debt when the collateral value falls
below a protocol-defined threshold.

A liquidator, who can be any user or bot, repays part or all of the
borrower's debt and receives the collateral at a discount as an
incentive.
The borrower keeps any remaining collateral after the liquidation, but
their position is partially or fully closed.

**Real-life analogy:**
Imagine you buy a house with a mortgage and the bank requires you to
maintain twenty percent equity.
If the housing market crashes and your equity drops to ten percent, the
bank does not send you a polite letter.
It forecloses and sells your house at auction.

A real estate investor buys the house for less than market value,
repays the bank, and keeps the difference as profit.
You receive any leftover cash after the sale and the bank's fees, but
you no longer own the house.

In DeFi, this happens instantly and automatically when a price oracle
reports that your collateral has dropped below the threshold.
There is no judge, no paperwork, and no delay.

**Tiny numeric example:**
Bob deposits 1 ETH worth two thousand USDC and borrows one thousand
USDC.
The liquidation threshold is one hundred twenty percent.

| ETH Price | Collateral Value | Debt | Collateral Ratio | Status |
|-----------|------------------|------|------------------|--------|
| $2,000    | $2,000           | $1,000| 200%            | Safe   |
| $1,500    | $1,500           | $1,000| 150%            | Safe   |
| $1,200    | $1,200           | $1,000| 120%            | Critical |
| $1,100    | $1,100           | $1,000| 110%            | Liquidated |

At one thousand one hundred dollars, the collateral ratio drops below
one hundred twenty percent.
A liquidator repays one thousand USDC of debt and receives one ETH
worth one thousand one hundred dollars.
The liquidator profits one hundred dollars minus fees.
Bob loses his ETH but owes nothing.
The protocol remains solvent.

**Common confusion:**
- **"Liquidation means you lose all your collateral."**
  No. Liquidation sells only enough collateral to repay the debt plus
  a penalty. Any remaining collateral is returned to the borrower.

- **"Liquidation is a penalty charged by the protocol."**
  No. Liquidation is a sale event.
  The penalty is a discount given to the liquidator as an incentive to
  monitor and act on unhealthy positions.
  The protocol itself does not keep the penalty in most designs.

- **"You can avoid liquidation by ignoring it."**
  No. Liquidation is automatic and permissionless.
  Anyone can trigger it once the threshold is crossed.
  The borrower has no ability to block it.

- **"Liquidation only happens during crashes."**
  It is most common during crashes, but it can happen during any price
decline, even small ones, if the borrower is highly leveraged.

- **"The liquidator is the protocol team."**
  No. Liquidators are independent bots or users who compete to execute
  liquidations for profit.
  The protocol does not run them.

- **"Liquidation price is the same as the collateral price."**
  No. Liquidation occurs at a discount.
  The liquidator pays the debt and receives collateral worth more than
  the debt repaid, creating their profit margin.

- **"If no one liquidates me, I keep my position."**
  Temporarily, yes.
  But as the price drops further, the position becomes more attractive
  to liquidators.
  Eventually, the protocol may use a reserve fund or emergency
  mechanism to force closure.

**Where it appears in our code:**
`src_web3/phase19/lending/src/lib.rs` — The program includes a
liquidation instruction that allows any user to repay debt and seize
collateral from positions below the health factor threshold.

`src_web3/phase19/lending_api.ts` — The Express API simulates
liquidations, calculates liquidator profit, and shows exactly how much
collateral is sold when a position becomes unhealthy.
