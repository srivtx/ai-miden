# What Is Linear Vesting

## The Problem

Not all contributions are front-loaded. A developer who works steadily for a year provides value every month, not just on the first day. Linear vesting matches token unlocks to this steady contribution by releasing an equal portion of the grant at regular intervals. This prevents large sudden unlocks that could crash a token price, and it gives recipients a predictable, fair reward for ongoing participation.

## Definition

Linear vesting is a pattern where tokens unlock in equal increments over a fixed total duration. The amount vested at any time is proportional to the elapsed time since the start date, creating a straight-line graph of unlocked tokens versus time.

## How It Works (Step-by-Step)

1. A total grant is fixed, for example 10,000 tokens, and a total duration is chosen, for example 10 months.
2. The contract calculates the vesting rate by dividing the total grant by the total duration: 10,000 / 10 = 1,000 tokens per month.
3. At any moment, the contract computes the vested amount with the formula: `vested = total * (elapsed / duration)`. For example, after 4.5 months, vested = 10,000 * (4.5 / 10) = 4,500 tokens.
4. The recipient can submit a claim transaction at any time. The contract evaluates the elapsed time, applies the formula, and transfers only the tokens that have not been claimed before.
5. If there is no cliff, vesting begins immediately on day one. If a cliff exists, the formula returns zero until the cliff period passes, then resumes the same proportional calculation.
6. When elapsed time equals total duration, the formula yields the full grant and the schedule is complete.

## Real-life analogy

Picture a large water tank with a capacity of 10,000 liters and a pipe that drips exactly 1,000 liters every month. There are no sudden floods and no dry spells; the water level rises by the same amount each month. At any day you can measure the level and know precisely how much water is inside. Linear vesting is that steady drip: tokens flow out of the contract at a constant rate, and the recipient can draw from the pool at any time.

## Tiny numeric example

A contributor is granted 10,000 tokens with linear vesting over 10 months and no cliff.

**Formula:** vested = total * (elapsed / duration)  
**Monthly rate:** 10,000 / 10 = 1,000 tokens per month.

| Month | Elapsed Fraction | Vested This Month | Cumulative Vested | Unvested Remaining |
|-------|-----------------:|------------------:|------------------:|-------------------:|
| 1 | 0.10 | 1,000 | 1,000 | 9,000 |
| 2 | 0.20 | 1,000 | 2,000 | 8,000 |
| 3 | 0.30 | 1,000 | 3,000 | 7,000 |
| 4 | 0.40 | 1,000 | 4,000 | 6,000 |
| 5 | 0.50 | 1,000 | 5,000 | 5,000 |
| 6 | 0.60 | 1,000 | 6,000 | 4,000 |
| 7 | 0.70 | 1,000 | 7,000 | 3,000 |
| 8 | 0.80 | 1,000 | 8,000 | 2,000 |
| 9 | 0.90 | 1,000 | 9,000 | 1,000 |
| 10 | 1.00 | 1,000 | 10,000 | 0 |

At month 4.5 the contributor has vested 4,500 tokens because vesting is proportional to elapsed time. The contract may allow claiming at any moment, not just at month boundaries.

## Common confusion

- No, linear vesting is not interest; the total grant is fixed from the start, and time only determines when portions become transferable.
- No, it does not mean tokens are streamed continuously in micro-increments; most contracts calculate on demand when a claim is submitted.
- No, linear vesting with a cliff is not a different formula after the cliff; the same proportional calculation resumes once the cliff passes.
- No, claiming early does not increase the rate; it merely transfers whatever has vested up to that point.
- No, linear is not always the best choice; some projects use stepped vesting (quarterly or yearly lumps) for administrative simplicity.
- No, fully vested tokens are not automatically sent to the recipient; the recipient must still call the claim function.

## Key properties

- Constant release rate: the same fraction of the total grant unlocks in each equal time period.
- Proportional to elapsed time: the vested amount at any timestamp equals total multiplied by elapsed time divided by duration.
- No mandatory cliff: linear vesting can run with or without an initial cliff period.
- Continuously calculable: the contract can compute the exact vested amount at any instant without iterating past events.
- Predictable supply impact: unlocks are evenly spaced, reducing sudden market pressure and giving recipients a steady reward.

## Where it appears in our code

Linear vesting is implemented in `src_web3/phase37/vesting_api.ts` under the `calculateVestedAmount` helper, which multiplies the total grant by the ratio of elapsed time to total duration.
