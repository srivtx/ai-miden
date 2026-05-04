## What Is Collateral?

**The Problem:**
In traditional finance, lenders rely on credit scores, employment
history, and legal contracts to ensure repayment.

In decentralized finance, borrowers are anonymous.
There is no court to sue a defaulting borrower and no credit bureau to
track their history.
Lenders need a guarantee that they will be repaid even if the borrower
disappears.
Without collateral, trustless lending would be impossible because there
would be no way to recover losses.

**Definition:**
Collateral is an asset deposited by a borrower into a smart contract to
secure a loan. The collateral must be worth more than the loan value,
typically by a significant margin.

If the borrower fails to maintain sufficient collateral value, the smart
contract automatically sells the collateral to repay the lender.
The borrower retains ownership of the collateral until liquidation
occurs, but they cannot withdraw it while a loan is active unless they
first repay the debt.

**Real-life analogy:**
Imagine you want to borrow five hundred dollars from a friend, but you
live in different countries and there is no legal system to enforce the
loan.

Your friend asks you to leave your laptop, worth one thousand dollars,
in a locked safe that neither of you can open alone.
You receive the five hundred dollars.
If you repay on time, the safe opens and you get your laptop back.
If you disappear, your friend can open the safe, sell the laptop, and
recover their five hundred dollars plus a penalty for the trouble.

The laptop is your collateral.
It exists to eliminate trust by giving the lender a recoverable asset
that is worth more than the loan itself.

**Tiny numeric example:**
ETH is priced at two thousand USDC.
The protocol has a seventy-five percent loan-to-value ratio.

| Collateral (ETH) | Collateral Value | Max LTV | Max Borrow (USDC) | Safety Buffer |
|------------------|------------------|---------|-------------------|---------------|
| 1.0              | $2,000           | 75%     | $1,500            | $500          |
| 2.5              | $5,000           | 75%     | $3,750            | $1,250        |
| 0.5              | $1,000           | 75%     | $750              | $250          |

The safety buffer is the dollar value of collateral that cannot be
borrowed against.
It protects the lender from normal market volatility.
If the collateral value drops, this buffer shrinks, and the borrower
must either add more collateral or repay part of the loan.

**Common confusion:**
- **"Collateral is a fee you pay to borrow."**
  No. Collateral is still your asset.
  You can recover it by repaying the loan.
  A fee is spent and gone forever.
  Collateral is locked, not spent.

- **"You can withdraw collateral at any time."**
  No. As long as you have an active loan, your collateral is locked.
  You can only withdraw excess collateral that is not needed to secure
  your debt.

- **"The protocol owns your collateral."**
  No. The smart contract holds it in escrow.
  You retain the right to reclaim it upon repayment.
  Ownership does not transfer unless liquidation occurs.

- **"Any token can be used as collateral."**
  No. Protocols only accept assets with reliable price oracles,
  sufficient liquidity, and low volatility risk.
  New or illiquid tokens are usually not accepted.

- **"Collateral value is measured when you deposit and never changes."**
  No. The protocol constantly updates collateral value using price
  oracles. A drop in collateral value can trigger liquidation even if
  you borrowed safely at the time of deposit.

- **"You must deposit the same token you want to borrow."**
  No. You typically deposit a volatile asset like ETH and borrow a
  stable asset like USDC.
  This allows you to access liquidity without selling your long-term
  holdings.

- **"Collateral eliminates all lender risk."**
  No. If collateral drops in price faster than the protocol can
  liquidate it, or if the oracle provides bad data, lenders can still
  suffer losses.
  Collateral reduces but does not eliminate risk.

**Where it appears in our code:**
`src_web3/phase19/lending/src/lib.rs` — The program verifies that
deposited collateral meets minimum requirements and tracks its value
relative to borrowed amounts.

`src_web3/phase19/lending_api.ts` — The Express API calculates maximum
borrow capacity, collateral ratios, and health factors based on
deposited assets.
