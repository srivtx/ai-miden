# What Is Linear Vesting

## Why It Exists

Not all contributions are front-loaded. A developer who works steadily for a year provides value every month, not just on the first day. Linear vesting matches token unlocks to this steady contribution by releasing an equal portion of the grant at regular intervals. This prevents large sudden unlocks that could crash a token price, and it gives recipients a predictable, fair reward for ongoing participation.

## Definition

Linear vesting is a pattern where tokens unlock in equal increments over a fixed total duration. The amount vested at any time is proportional to the elapsed time since the start date, creating a straight-line graph of unlocked tokens versus time.

## Real-Life Analogy

Imagine a construction worker paid by the hour. Every hour on the clock earns a fixed wage, and at the end of the week the total is paid out. There is no lump sum at the start and no giant bonus at the end; compensation grows smoothly with effort. Linear vesting is the blockchain version of an hourly wage, except the "hours" are blocks or calendar days and the "wage" is a share of a token grant.

## Tiny Numeric Example

A contributor is granted 10,000 tokens with linear vesting over 10 months and no cliff.

| Month | Elapsed Fraction | Vested Tokens | Cumulative Vested | Unvested Remaining |
|-------|-----------------:|--------------:|------------------:|-------------------:|
| 1 | 0.10 | 1,000 | 1,000 | 9,000 |
| 2 | 0.20 | 1,000 | 2,000 | 8,000 |
| 3 | 0.30 | 1,000 | 3,000 | 7,000 |
| 5 | 0.50 | 1,000 | 5,000 | 5,000 |
| 7 | 0.70 | 1,000 | 7,000 | 3,000 |
| 10 | 1.00 | 1,000 | 10,000 | 0 |

At month 4.5 the contributor has vested 4,500 tokens because vesting is proportional to elapsed time. The contract may allow claiming at any moment, not just at month boundaries.

## Common Confusion

- Linear vesting is not interest; the total grant is fixed from the start, and time only determines when portions become transferable.
- It does not mean tokens are streamed continuously in micro-increments; most contracts calculate on demand when a claim is submitted.
- Linear vesting with a cliff is still linear after the cliff; the line simply starts at zero until the cliff passes.
- Claiming early does not increase the rate; it merely transfers whatever has vested up to that point.
- Linear is not always the best choice; some projects use stepped vesting (quarterly or yearly lumps) for administrative simplicity.
- The slope of the line is total grant divided by total duration, but contracts must handle integer division carefully to avoid rounding errors.
- Fully vested tokens are not automatically sent to the recipient; the recipient must still call the claim function.

## Key Properties

## Where It Appears in Our Code

Linear vesting is implemented in `src_web3/phase37/vesting_api.ts` under the calculateVestedAmount helper, which multiplies the total grant by the ratio of elapsed time to total duration.
