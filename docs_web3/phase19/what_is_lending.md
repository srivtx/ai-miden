## What Is a Lending Protocol?

**The Problem:**
Traditional banking connects savers with borrowers through a
centralized institution that holds deposits, assesses creditworthiness,
and manages defaults.

In decentralized finance, there is no bank, no credit score, and no
legal system to enforce loan contracts across borders.
Crypto holders want to earn yield on idle assets without selling them,
while other users want liquidity to trade or leverage positions without
losing exposure to their holdings.

There must be a trustless system that allows deposits, borrowing, and
repayment without human intermediaries.

**Definition:**
A lending protocol is a decentralized system of smart contracts that
allows users to deposit assets to earn interest, while other users
borrow those assets by posting collateral worth more than the loan.

All terms, interest rates, and liquidation rules are encoded in the
smart contract and enforced automatically by the blockchain.
There are no credit checks because every loan is overcollateralized,
meaning the borrower must lock up more value than they receive.

**Real-life analogy:**
Imagine a pawn shop that operates entirely by robot.
You walk in with a gold watch worth two thousand dollars.
The robot instantly appraises it, offers you a loan of one thousand
dollars, and locks the watch in a vault.

You receive the cash and walk out.
There is no paperwork, no credit check, and no human judgment.
The robot charges interest every hour.

If the price of gold drops and your watch is now worth only one
thousand one hundred dollars, the robot instantly sells the watch to
repay your loan.

If gold rises and you repay the loan plus interest, the robot returns
your watch.
This pawn shop never sleeps, never discriminates, and never makes
exceptions.
A DeFi lending protocol is that robot shop running on the blockchain.

**Tiny numeric example:**
Alice deposits 10,000 USDC.
Bob deposits 1 ETH worth 2,000 USDC and borrows 1,000 USDC.

| Participant | Collateral | Borrowed | Interest Rate | LTV | Liquidation Price |
|-------------|------------|----------|---------------|-----|-------------------|
| Alice       | 10,000 USDC| 0        | 5% supply APY | N/A | N/A               |
| Bob         | 1 ETH ($2k)| 1,000 USDC| 8% borrow APY | 50% | $1,250 ETH        |

Alice earns five percent on her deposit.
Bob pays eight percent on his loan.
The three percent spread funds the protocol treasury and liquidation
incentives.
If ETH drops to one thousand two hundred fifty dollars, Bob's position
becomes eligible for liquidation.

**Common confusion:**
- **"Lending protocols work like a bank savings account."**
  No. Banks use fractional reserves and credit scoring.
  Lending protocols require overcollateralization and have no credit
  checks. Your deposit is not insured by any government.

- **"You can borrow without putting up collateral."**
  In standard DeFi lending, no.
  Every loan is overcollateralized because there is no identity or
  legal recourse. Undercollateralized lending exists in niche protocols
  but requires additional trust mechanisms.

- **"The protocol keeps the interest spread as profit."**
  Some protocols do, but many distribute fees to governance token
  holders or use them to subsidize rewards.
  The business model varies by protocol.

- **"Depositors cannot lose money."**
  Yes, they can. Smart contract bugs, oracle failures, and extreme
  market crashes can all lead to losses.
  Deposits are not risk-free.

- **"Interest rates are fixed forever."**
  No. Most lending protocols use algorithmic interest rate models that
  adjust based on supply and demand.
  High utilization leads to high borrow rates.

- **"You can only borrow the same asset you deposit."**
  No. You typically deposit one asset as collateral and borrow a
  different asset. For example, deposit ETH and borrow stablecoins.

- **"Liquidation means you lose everything."**
  No. Liquidation only sells enough collateral to repay the loan plus
  a penalty. The borrower keeps any remaining collateral after the sale.

**Where it appears in our code:**
`src_web3/phase19/lending/src/lib.rs` — Solana program that handles
depositing collateral, borrowing against it, repaying loans, and
executing liquidations.

`src_web3/phase19/lending_api.ts` — TypeScript Express API simulating
lending markets with dynamic interest rates, health factors, and
liquidation triggers.
