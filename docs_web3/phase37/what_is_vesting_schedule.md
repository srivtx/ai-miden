# What Is a Vesting Schedule

## The Problem

When a startup hires an engineer or a blockchain project allocates tokens to a team, giving the full reward on day one creates misaligned incentives. The recipient could quit immediately, dump the tokens on the market, or abandon the project. A vesting schedule locks tokens and releases them over time, ensuring that recipients earn their allocation through continued contribution. This protects investors, stabilizes token price, and aligns long-term interests between teams and communities.

## Definition

A vesting schedule is a timeline that defines when and how locked tokens become transferable. It specifies a start date, a total duration, a release pattern (such as linear or stepped), and optional conditions like a cliff period before any tokens unlock.

## How It Works (Step-by-Step)

1. A total token grant is agreed upon, for example 12,000 tokens, and a vesting duration is chosen, for example 12 months.
2. A cliff period is set, for example 3 months, during which no tokens are unlocked to ensure minimum commitment.
3. The monthly unlock rate is calculated by dividing the total grant by the total duration: 12,000 / 12 = 1,000 tokens per month.
4. During the cliff, tokens accrue in the background but remain locked. At the end of month 3, the accrued 3,000 tokens unlock all at once, and the schedule continues.
5. After the cliff, the recipient can claim 1,000 additional tokens at the end of each subsequent month.
6. The smart contract records the start timestamp and allows the recipient to submit a claim transaction at any time to transfer the currently vested balance to their wallet.

## Real-life analogy

Imagine a pension plan at a company. You are told that for every year you work, you gain the right to a portion of your retirement fund. If you leave before five years, you receive nothing. After five years, you keep what you have earned, and each additional year adds more. A token vesting schedule is the same principle: tokens are your pension, time worked is the vesting period, and the company is the smart contract holding the funds.

## Tiny numeric example

A team member is granted 12,000 tokens with a 12-month vesting schedule and a 3-month cliff.

**Calculation:** 12,000 tokens / 12 months = 1,000 tokens per month.

| Month | Monthly Vested | Cumulative Vested | Unlocked? | Notes |
|-------|---------------:|------------------:|:---------:|-------|
| 1 | 0 | 0 | No | Before cliff |
| 2 | 0 | 0 | No | Before cliff |
| 3 | 3,000 | 3,000 | Yes | Cliff ends; accrued tokens unlock |
| 4 | 1,000 | 4,000 | Yes | Ongoing monthly vesting |
| 5 | 1,000 | 5,000 | Yes | Ongoing monthly vesting |
| 6 | 1,000 | 6,000 | Yes | Halfway point reached |
| 7 | 1,000 | 7,000 | Yes | Ongoing monthly vesting |
| 8 | 1,000 | 8,000 | Yes | Ongoing monthly vesting |
| 9 | 1,000 | 9,000 | Yes | Ongoing monthly vesting |
| 10 | 1,000 | 10,000 | Yes | Ongoing monthly vesting |
| 11 | 1,000 | 11,000 | Yes | Ongoing monthly vesting |
| 12 | 1,000 | 12,000 | Yes | Fully vested |

The cliff ensures the contributor stays for at least three months. After the cliff passes, tokens unlock monthly at a steady rate until the full grant is vested.

## Common confusion

- No, vesting is not a salary; it is a delayed grant that converts into ownership over time.
- No, tokens do not appear in the recipient's wallet automatically; the recipient must submit a claim transaction to the vesting contract.
- No, a fully vested grant does not mean all tokens are sold; it means they are transferable, but the holder may keep them.
- No, vesting schedules are not reversible; once tokens vest, they belong to the recipient and cannot be clawed back by the contract owner unless explicitly programmed.
- No, accelerated vesting is not standard; special conditions like acquisition or milestone achievement must be written into the contract.
- No, vesting does not prevent price drops; it only delays selling pressure by spreading unlocks over time.

## Key properties

- Time-locked release: tokens remain non-transferable until specific dates or elapsed periods are reached.
- Cliff protection: a minimum service period must pass before any portion of the grant becomes claimable.
- Programmable pattern: schedules can be linear, stepped, milestone-based, or hybrid to match project needs.
- Immutable terms: the timeline and conditions are encoded in the smart contract and cannot be altered unilaterally.
- Claim-based distribution: recipients must actively submit a transaction to move vested tokens to their own wallet.

## Where it appears in our code

The vesting API in `src_web3/phase37/vesting_api.ts` implements a complete vesting schedule with cliff detection, linear accrual, and a claim endpoint that computes exactly how many tokens have become unlocked at the current time.
