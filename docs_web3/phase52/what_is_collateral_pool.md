# Collateral Pool

## The Problem

In a lending protocol, borrowers must prove they can repay loans even if asset prices move against them. Without a secure holding area for borrower assets, lenders have no guarantee of recovery. A Collateral Pool solves this by locking borrower deposits and making them available for liquidation if the borrower becomes insolvent.

## Definition

A Collateral Pool is an on-chain account or smart contract structure that holds assets deposited by borrowers to secure their debt. The pool tracks each user's collateral balance, enforces over-collateralization rules, and releases collateral only after debt is fully repaid or during a permitted liquidation.

## How It Works

1. **User opens a lending position**: The borrower identifies the asset they want to deposit and the asset they want to borrow.
2. **Deposit is transferred into the pool**: The user's tokens move from their wallet into the protocol-controlled collateral pool account.
3. **Pool records the deposit**: The protocol updates an internal ledger mapping the user to their collateral balance and assigns a collateral factor.
4. **Borrowing is enabled**: Based on the deposited collateral value and the collateral factor, the protocol calculates the maximum borrow amount and allows the user to withdraw loan tokens.
5. **Value is monitored**: The protocol continuously checks collateral value against borrowed value using oracle price feeds.
6. **Liquidation or release**: If the health factor drops below 1, anyone can liquidate the position and claim collateral at a discount. If the user repays, the pool releases the collateral back to the user.

## Real-life Analogy

Think of a pawn shop. You hand over a watch worth 1,000 dollars and the shop gives you a 500 dollar loan. The watch sits in a locked display case. If you repay the loan plus interest, you get the watch back. If you do not return, the shop sells the watch to recover the loan. The locked display case is the collateral pool.

## Tiny Numeric Example with Liquidation Math

Alice deposits 10 ETH as collateral when ETH is priced at 2,000 dollars per ETH.

- Collateral value: 10 ETH * 2,000 dollars = 20,000 dollars
- Collateral factor: 75 percent
- Maximum borrow: 20,000 dollars * 0.75 = 15,000 dollars
- Alice borrows 12,000 USDC

Initial health factor:
- Health factor = (Collateral value * Collateral factor) / Borrowed value
- Health factor = (20,000 * 0.75) / 12,000 = 15,000 / 12,000 = 1.25

ETH price drops to 1,500 dollars:
- New collateral value: 10 * 1,500 = 15,000 dollars
- New health factor: (15,000 * 0.75) / 12,000 = 11,250 / 12,000 = 0.9375

Because health factor is below 1.0, the position is underwater.

Liquidation math:
- Liquidator repays 50 percent of the debt: 6,000 USDC
- Liquidation bonus: 10 percent
- Collateral seized: (6,000 * 1.10) / 1,500 = 6,600 / 1,500 = 4.4 ETH
- Alice keeps: 10 - 4.4 = 5.6 ETH
- Alice still owes: 6,000 USDC

## Common Confusion

- No, the collateral pool does not lend out the collateral tokens to other users.
- No, collateral is not returned instantly when borrowed funds are repaid; the protocol must verify full repayment first.
- No, a collateral factor of 75 percent does not mean you can borrow 100 percent of your deposit.
- No, the collateral pool does not guarantee the original dollar value of your deposit.
- No, liquidation does not return any surplus to the borrower before all debt is cleared.
- No, different assets do not share the same collateral factor.

## Key Properties

1. **Segregation**: Each user's collateral is accounted for separately within the shared pool.
2. **Over-collateralization**: Borrowers must deposit more value than they borrow.
3. **Non-rehypothecation**: The pool holds collateral; it does not redeploy it into yield strategies unless explicitly designed to.
4. **Programmable release**: Collateral is only released upon repayment or liquidation.
5. **Transparency**: All balances and rules are visible on-chain.

## Where It Appears

Collateral pools appear in Aave, Compound, Solend, MakerDAO vaults, and every major decentralized lending market.
