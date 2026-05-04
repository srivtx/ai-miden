# Architecture: Building the Lending Protocol from Scratch

This document walks through every step of building the complete lending protocol. Each step explains why the design choice was made.

---

## Step 1: Design Collateral and Borrow Accounts

**What we do**: Define the on-chain account structures. We create a `MarketAccount` to hold global pool state, a `UserPosition` account for each borrower, and an `OracleAccount` to store asset prices.

**Why**: Solana accounts are the only persistent storage. We need a global account to track total deposits, total borrows, and interest rate parameters so the protocol can compute utilization. We need per-user accounts because every borrower has a unique collateral balance, borrowed balance, and interest index snapshot. Separating global and per-user state prevents account size bloat and allows concurrent access to different user positions. The oracle account is separate so price updates do not require modifying lending state directly, which reduces recompilation risk and follows the single-responsibility principle.

---

## Step 2: Implement Deposit and Borrow

**What we do**: Write instructions that transfer tokens from the user into a protocol-associated token account, update the user's collateral balance, and allow borrowing up to a collateral-factor limit.

**Why**: Deposit is the entry point of the protocol. Without a secure token transfer into a program-controlled account, the protocol cannot guarantee collateral availability during liquidation. Borrow must check the user's total collateral value against their total borrowed value using the collateral factor. This over-collateralization rule is the core security guarantee that protects lenders. We implement borrow immediately after deposit because the two actions form the basic lending loop that every user expects.

---

## Step 3: Build Interest Accrual

**What we do**: Add a function that calculates the current borrow rate from utilization, accrues interest to total borrows, and updates the user's borrowed balance based on the time elapsed since their last interaction.

**Why**: Interest is how lenders earn yield and how the protocol sustains itself. Without dynamic interest, the pool cannot respond to supply and demand imbalances. We use a piecewise linear model so rates rise slowly in normal conditions and spike during high utilization to discourage bank runs. Accrual must happen on every state-changing instruction because Solana programs do not run cron jobs. By updating interest inside deposit, borrow, repay, and withdraw, we guarantee that balances are always current without an external scheduler.

---

## Step 4: Add Health Factor Checks

**What we do**: Compute a health factor for each user by dividing their weighted collateral value by their borrowed value. Enforce that a user cannot withdraw collateral or borrow more if the action would drop their health factor below 1.

**Why**: The health factor is the single metric that determines whether a position is safe. A value above 1 means collateral covers debt. A value below 1 means the position is underwater. Checking health factor before withdraw and borrow prevents users from deliberately or accidentally creating instant bad debt. We add this after interest accrual because interest itself can push a position underwater, and we want the most up-to-date borrowed balance before making safety checks.

---

## Step 5: Create Liquidation Flow

**What we do**: Implement a permissionless liquidation instruction. Anyone can repay a portion of an underwater borrower's debt and seize a larger portion of their collateral, receiving a liquidation bonus.

**Why**: Liquidation is the safety valve of the protocol. Without it, bad debt would accumulate and eventually socialize losses to lenders. Making it permissionless ensures there is no single point of failure and creates a competitive market of liquidators who act quickly for profit. The bonus incentivizes liquidators to cover gas costs and price risk. We implement liquidation after health factor checks because liquidation is the consequence of a failed health check.

---

## Step 6: Build Liquidation Bot Service

**What we do**: Create a standalone TypeScript service that polls all user positions, fetches current prices from the oracle, computes health factors off-chain, and submits liquidation transactions when health factor is below 1.

**Why**: A protocol is only as safe as its liquidation speed. Relying on humans to watch prices and click buttons is unreliable. A bot operates 24/7 and reacts in seconds. We build it off-chain because complex polling loops and transaction retry logic are expensive and slow inside a smart contract. The bot also demonstrates how off-chain infrastructure interfaces with on-chain programs, which is a critical skill for protocol developers.

---

## Step 7: Test End-to-End

**What we do**: Deploy the programs to a local validator or devnet, seed the oracle with prices, run the API, perform deposit and borrow transactions through the API, drop the collateral price to trigger liquidation, and verify the bot successfully liquidates the position.

**Why**: Testing in isolation proves that individual instructions work, but only an end-to-end test proves the system is safe under real market conditions. Price drops, interest accrual, and bot competition are emergent behaviors that appear only when all components run together. This step validates that the architecture choices in Steps 1 through 6 actually protect lender funds and allow the protocol to operate autonomously.
