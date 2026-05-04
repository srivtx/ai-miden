# What Is a Payment Stream

## Why It Exists

Not all work is delivered in discrete chunks. A freelancer who codes for forty hours, a consultant who advises over a quarter, or a farmer who grows crops across a season all provide continuous value. Lump-sum payments misalign incentives because the worker might be paid before delivering, or the client might delay payment after receiving value. Payment streams solve this by releasing money continuously in proportion to elapsed time, creating a fair and transparent exchange.

## Definition

A payment stream is a smart contract that holds a lump sum and releases it to a recipient at a constant rate over a defined period. Instead of waiting for the end of the month, the recipient can claim accrued funds at any moment, and the sender can cancel the stream to stop future accrual.

## Real-Life Analogy

Picture an hourglass filled with sand that represents money. The sand falls at a steady rate into a bottom chamber that the worker controls. Every grain that falls is earned. If the employer turns the hourglass upside down, the flow stops and the remaining sand in the top chamber returns to them. The worker never holds sand they have not earned, and the employer never loses sand for work not yet done.

## Tiny Numeric Example

A designer and a client agree on a payment stream of 3,000 USDC over 30 days.

| Day | Stream Rate (USDC/day) | Accrued to Designer | Claimable Now | Returned on Cancel |
|-----|-----------------------:|--------------------:|--------------:|-------------------:|
| 5 | 100 | 500 | 500 | 2,500 |
| 10 | 100 | 1,000 | 1,000 | 2,000 |
| 15 | 100 | 1,500 | 1,500 | 1,500 |
| 20 | 100 | 2,000 | 2,000 | 1,000 |
| 25 | 100 | 2,500 | 2,500 | 500 |
| 30 | 100 | 3,000 | 3,000 | 0 |

At day 12 the designer claims 1,200 USDC. The stream continues and by day 30 the full 3,000 USDC has been transferred. If the client cancels at day 18, the designer keeps 1,800 USDC and the remaining 1,200 USDC returns to the client.

## Common Confusion

- A payment stream is not interest-bearing; the rate is fixed by agreement, not by market forces.
- Claiming early does not speed up the stream; it simply transfers what has already accrued.
- Streams are not loans; the sender owns the funds until they accrue, and the recipient has no obligation to repay.
- The recipient does not automatically receive funds; they must submit a claim transaction, which costs gas.
- A stream cannot change direction; the flow is one-way from sender to recipient unless a separate reverse stream is created.
- Streams are not divisible by default; if the sender wants to pay two workers, they need two separate streams.
- Canceling a stream is not a breach of contract if the contract allows it; the terms are encoded in code, not in a court-enforceable document.

## Key Properties

## Where It Appears in Our Code

The payment stream simulation lives in `src_web3/phase36/subscription_api.ts`, where the `/create-stream` endpoint initializes a stream, `/claim` computes accrued value based on elapsed blocks, and `/cancel` returns unaccrued funds to the sender.
