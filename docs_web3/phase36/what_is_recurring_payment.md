# What Is a Recurring Payment

## Why It Exists

Businesses need stable cash flow to pay employees, buy inventory, and plan growth. Consumers prefer spreading costs over time rather than paying large lump sums. Recurring payments bridge this gap by breaking a total obligation into smaller, scheduled installments. On a blockchain, recurring payments are implemented with smart contracts that hold funds and release them according to a calendar, removing the need for trust in a centralized billing system.

## Definition

A recurring payment is a repeated transfer of funds from a payer to a payee according to a predetermined schedule. In Web3, the schedule and amounts are encoded in a smart contract, and the transfers are executed automatically when conditions are met.

## Real-Life Analogy

Think of a newspaper delivery. Every morning the paper arrives at your door, and once a month the delivery service collects payment for the bundle. You do not sign a receipt each morning; the agreement is that delivery continues until you call to cancel. A smart contract recurring payment is the same: tokens are "delivered" to the merchant on a schedule, and the agreement runs until one party terminates it.

## Tiny Numeric Example

A content creator sets up weekly recurring tips of 2 SOL from a supporter.

| Week | Supporter Escrow | Creator Claimed | Remaining in Escrow | Transaction Cost |
|------|-----------------:|----------------:|--------------------:|-----------------:|
| 1 | 20 SOL | 2 SOL | 18 SOL | 0.000005 SOL |
| 2 | 18 SOL | 2 SOL | 16 SOL | 0.000005 SOL |
| 3 | 16 SOL | 2 SOL | 14 SOL | 0.000005 SOL |
| 4 | 14 SOL | 2 SOL | 12 SOL | 0.000005 SOL |
| 5 | 12 SOL | 0 SOL | 12 SOL | 0 SOL (insufficient for next claim) |

After four weeks the supporter added more funds, extending the schedule. The creator only receives what the contract releases; they cannot withdraw the full 20 SOL at once.

## Common Confusion

- Recurring payments are not standing orders in a bank; there is no central authority enforcing them, only code.
- Missing a payment interval does not create debt; the contract simply skips the release if funds are unavailable.
- A recurring payment contract is not a savings account; the funds are earmarked for the payee and typically cannot be redirected.
- The payer cannot claw back released funds unless the contract explicitly includes a refund mechanism.
- Gas fees are paid by whoever triggers the claim, which may be the payee, not the payer.
- Recurring does not mean infinite; contracts usually specify an end date or a total cap.
- Changing the amount mid-schedule requires deploying a new contract or an upgrade transaction; it is not as flexible as editing a bank transfer online.

## Key Properties

## Where It Appears in Our Code

The recurring payment logic is embedded in `src_web3/phase36/subscription_api.ts` under the claim endpoint, which checks elapsed time since the last claim and computes the exact amount that may be transferred.
