# What Is a Recurring Payment

## The Problem

Businesses need stable cash flow to pay employees, buy inventory, and plan growth. Consumers prefer spreading costs over time rather than paying large lump sums. Recurring payments bridge this gap by breaking a total obligation into smaller, scheduled installments. On a blockchain, recurring payments are implemented with smart contracts that hold funds and release them according to a calendar, removing the need for trust in a centralized billing system.

## Definition

A recurring payment is a repeated transfer of funds from a payer to a payee according to a predetermined schedule. In Web3, the schedule and amounts are encoded in a smart contract, and the transfers are executed automatically when conditions are met.

## How It Works (Step-by-Step)

1. **Fund the escrow.** The payer deposits a lump sum into a smart contract escrow account that is owned by the recurring payment program. These tokens are now locked and earmarked for future disbursements.
2. **Define the schedule.** The contract stores the payment interval (e.g., 7 days), the amount per interval (e.g., 2 SOL), and either a maximum number of payments or an end date.
3. **Trigger the claim.** When an interval has elapsed, the payee (or an authorized keeper) calls the contract's claim function. The contract does not push funds automatically; an on-chain transaction is required.
4. **Validate conditions.** The contract checks the current timestamp or slot against the last payment time, verifies that the escrow still holds enough funds, and confirms the schedule has not reached its cap.
5. **Release the installment.** If all conditions pass, the contract transfers exactly the scheduled amount from escrow to the payee's wallet and updates the last claim timestamp.
6. **Pause or renew.** If the escrow runs out of funds or the payment cap is reached, the contract halts further claims. The payer can optionally add more funds to renew the schedule.

## Real-Life Analogy

Think of a newspaper delivery. Every morning the paper arrives at your door, and once a month the delivery service collects payment for the bundle. You do not sign a receipt each morning; the agreement is that delivery continues until you call to cancel. A smart contract recurring payment is the same: tokens are "delivered" to the merchant on a schedule, and the agreement runs until one party terminates it.

## Tiny Numeric Example

A supporter sets up weekly recurring tips of 2 SOL to a content creator, funding the escrow with 10 SOL upfront:

| Week | Supporter Escrow | Creator Claimed | Remaining in Escrow | Transaction Cost |
|------|-----------------:|----------------:|--------------------:|-----------------:|
| 1 | 10 SOL | 2 SOL | 8 SOL | 0.000005 SOL |
| 2 | 8 SOL | 2 SOL | 6 SOL | 0.000005 SOL |
| 3 | 6 SOL | 2 SOL | 4 SOL | 0.000005 SOL |
| 4 | 4 SOL | 2 SOL | 2 SOL | 0.000005 SOL |
| 5 | 2 SOL | 2 SOL | 0 SOL | 0.000005 SOL |
| 6 | 0 SOL | 0 SOL | 0 SOL | 0 SOL (insufficient funds, schedule paused) |

After five weeks the creator has received the full 10 SOL. On week 6 the claim fails because the escrow is empty. The supporter must deposit additional funds to resume the schedule. The creator cannot withdraw the full 10 SOL at once; only the current 2 SOL installment is released per valid claim.

## Common Confusion

- No, recurring payments are not standing orders enforced by a bank; there is no central authority, only code.
- No, missing a payment interval does not create debt; the contract simply skips the release if funds are unavailable.
- No, a recurring payment contract is not a savings account; the funds are earmarked for the payee and typically cannot be redirected.
- No, the payer cannot claw back released funds unless the contract explicitly includes a refund mechanism.
- No, gas fees are paid by whoever triggers the claim, which may be the payee rather than the payer.
- No, recurring does not mean infinite; contracts usually specify an end date or a total cap.

## Key Properties

- Funds are locked in escrow before any payments begin.
- Payments execute automatically on a fixed schedule when triggered.
- The payee can only claim the current scheduled installment, not the full balance.
- Intervals are enforced by on-chain timestamps or slot-based checks.
- The stream halts automatically when escrow is depleted or the cap is reached.

## Where It Appears in Our Code

The recurring payment logic is embedded in `src_web3/phase36/subscription_api.ts` under the claim endpoint, which checks elapsed time since the last claim and computes the exact amount that may be transferred.
