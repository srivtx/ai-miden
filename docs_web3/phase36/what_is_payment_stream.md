# What Is a Payment Stream

## The Problem

Not all work is delivered in discrete chunks. A freelancer who codes for forty hours, a consultant who advises over a quarter, or a farmer who grows crops across a season all provide continuous value. Lump-sum payments misalign incentives because the worker might be paid before delivering, or the client might delay payment after receiving value. Payment streams solve this by releasing money continuously in proportion to elapsed time, creating a fair and transparent exchange.

## Definition

A payment stream is a smart contract that holds a lump sum and releases it to a recipient at a constant rate over a defined period. Instead of waiting for the end of the month, the recipient can claim accrued funds at any moment, and the sender can cancel the stream to stop future accrual.

## How It Works (Step-by-Step)

1. **Initialize the stream.** The sender deposits the total lump sum into the stream contract and specifies the recipient, start timestamp, end timestamp, and total amount. The contract calculates the stream rate as `total_amount / (end_time - start_time)`.
2. **Accrual begins.** As each second or slot passes, the contract computes the accrued amount as `rate * elapsed_time`. This value increases continuously; it is not tied to fixed calendar intervals.
3. **Claim accrued funds.** The recipient submits a claim transaction at any time. The contract transfers the difference between total accrued and previously claimed amounts, then updates the recipient's claimed balance.
4. **Cancel the stream.** The sender can cancel at any point before the end time. The contract transfers any remaining accrued but unclaimed funds to the recipient and returns the unaccrued balance to the sender.
5. **Natural termination.** Once the end timestamp is reached, the full amount has accrued. The recipient claims the final portion, and the stream closes automatically because there are no remaining funds.
6. **Audit the state.** Anyone can query the contract to see the start time, rate, total claimed, and remaining balance, ensuring full transparency for both parties.

## Real-Life Analogy

Picture an hourglass filled with sand that represents money. The sand falls at a steady rate into a bottom chamber that the worker controls. Every grain that falls is earned. If the employer turns the hourglass upside down, the flow stops and the remaining sand in the top chamber returns to them. The worker never holds sand they have not earned, and the employer never loses sand for work not yet done.

## Tiny Numeric Example

A designer and a client agree on a payment stream of 3,000 USDC over 30 days at 100 USDC per day:

| Day | Stream Rate (USDC/day) | Accrued Total | Claimed by Designer | Remaining in Stream |
|-----|-----------------------:|--------------:|--------------------:|--------------------:|
| 5 | 100 | 500 | 0 | 3,000 |
| 10 | 100 | 1,000 | 1,000 | 2,000 |
| 15 | 100 | 1,500 | 1,000 | 1,500 |
| 20 | 100 | 2,000 | 2,000 | 1,000 |
| 25 | 100 | 2,500 | 2,000 | 500 |
| 30 | 100 | 3,000 | 3,000 | 0 |

At day 10 the designer claims 1,000 USDC. At day 20 the designer claims another 1,000 USDC. By day 30 the designer claims the final 1,000 USDC and the stream closes. If the client cancels at day 12, the designer keeps 1,200 USDC (already accrued) and the remaining 1,800 USDC returns to the client.

## Common Confusion

- No, a payment stream is not interest-bearing; the rate is fixed by agreement, not by market forces.
- No, claiming early does not speed up the stream; it simply transfers what has already accrued.
- No, streams are not loans; the sender owns the funds until they accrue, and the recipient has no obligation to repay.
- No, the recipient does not automatically receive funds; they must submit a claim transaction, which costs gas.
- No, a stream cannot change direction; the flow is one-way from sender to recipient unless a separate reverse stream is created.
- No, canceling a stream is not a breach of contract if the contract allows it; the terms are encoded in code, not in a court-enforceable document.

## Key Properties

- Funds are locked in the contract upfront and released continuously over time.
- The recipient can claim accrued funds at any point without waiting for the full term.
- The sender retains the right to cancel and recover unaccrued funds.
- Accrual is calculated linearly based on elapsed time, not discrete intervals.
- The contract terminates automatically when the full amount has been claimed or the end time passes.

## Where It Appears in Our Code

The payment stream simulation lives in `src_web3/phase36/subscription_api.ts`, where the `/create-stream` endpoint initializes a stream, `/claim` computes accrued value based on elapsed blocks, and `/cancel` returns unaccrued funds to the sender.
