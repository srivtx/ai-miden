# What Is a Cliff

## Why It Exists

Startups and projects need a grace period to evaluate whether a new team member is a good fit before giving them ownership. Without a cliff, a contributor could join, receive tokens on day one, and leave immediately. The cliff creates a minimum service requirement: if the recipient leaves before the cliff date, they forfeit all unvested tokens. This simple mechanism dramatically reduces turnover risk and filters out short-term participants.

## Definition

A cliff is a period at the beginning of a vesting schedule during which no tokens unlock. Only after the cliff expires does the recipient begin to accrue vested tokens according to the schedule.

## Real-Life Analogy

Think of a trial period at a gym. You sign up for a year, but the deal says that if you cancel within the first three months, you lose your signup bonus. After three months, you earn a free personal training session every month for the rest of the year. The first three months are the cliff: they test your commitment before rewards begin.

## Tiny Numeric Example

An advisor receives a grant of 24,000 tokens vesting over 24 months with a 6-month cliff.

| Month | Cliff Status | Monthly Vested | Cumulative Vested | Forfeited if Leaves |
|-------|--------------|---------------:|------------------:|--------------------:|
| 1 | Inside | 0 | 0 | 24,000 |
| 3 | Inside | 0 | 0 | 24,000 |
| 6 | End of cliff | 0 | 0 | 24,000 |
| 7 | Passed | 1,000 | 1,000 | 23,000 |
| 12 | Passed | 1,000 | 6,000 | 18,000 |
| 18 | Passed | 1,000 | 12,000 | 12,000 |
| 24 | Passed | 1,000 | 24,000 | 0 |

At month five the advisor has earned nothing. At month seven they unlock their first 1,000 tokens. If they depart at month 10, they keep 4,000 tokens and forfeit 20,000.

## Common Confusion

- A cliff is not a lockup for all holders; it only affects the specific grant, not the entire token supply.
- Reaching the cliff does not release all tokens at once unless the schedule is designed that way; linear schedules release incrementally after the cliff.
- A cliff does not guarantee employment; it only determines token eligibility. Labor laws still govern actual employment contracts.
- The cliff date is usually measured from the grant date, not the wallet connection date or the first task completion date.
- Cliff forfeiture is not a penalty; it is the absence of earned ownership because the service requirement was not met.
- Some contracts include a "cliff acceleration" clause for acquisitions; this is not automatic and must be explicitly programmed.
- A 0-month cliff means tokens start vesting immediately; this is common for early founders but rare for later hires.

## Key Properties

## Where It Appears in Our Code

The cliff logic is central to `src_web3/phase37/vesting_api.ts`, where the claim endpoint checks whether the current time exceeds `startTime + cliffDuration` before calculating any vested amount.
