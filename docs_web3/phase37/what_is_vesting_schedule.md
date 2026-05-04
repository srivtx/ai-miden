# What Is a Vesting Schedule

## Why It Exists

When a startup hires an engineer or a blockchain project allocates tokens to a team, giving the full reward on day one creates misaligned incentives. The recipient could quit immediately, dump the tokens on the market, or abandon the project. A vesting schedule locks tokens and releases them over time, ensuring that recipients earn their allocation through continued contribution. This protects investors, stabilizes token price, and aligns long-term interests between teams and communities.

## Definition

A vesting schedule is a timeline that defines when and how locked tokens become transferable. It specifies a start date, a total duration, a release pattern (such as linear or stepped), and optional conditions like a cliff period before any tokens unlock.

## Real-Life Analogy

Imagine a pension plan at a company. You are told that for every year you work, you gain the right to a portion of your retirement fund. If you leave before five years, you receive nothing. After five years, you keep what you have earned, and each additional year adds more. A token vesting schedule is the same principle: tokens are your pension, time worked is the vesting period, and the company is the smart contract holding the funds.

## Tiny Numeric Example

A team member is granted 12,000 tokens with a 12-month vesting schedule and a 3-month cliff.

| Month | Vested Tokens | Cumulative Vested | Unlocked? | Notes |
|-------|--------------:|------------------:|:---------:|-------|
| 1 | 0 | 0 | No | Before cliff |
| 2 | 0 | 0 | No | Before cliff |
| 3 | 0 | 0 | No | End of cliff, but no linear share yet |
| 4 | 1,000 | 1,000 | Yes | First monthly installment after cliff |
| 6 | 1,000 | 3,000 | Yes | Accumulating monthly |
| 9 | 1,000 | 6,000 | Yes | Halfway through |
| 12 | 1,000 | 12,000 | Yes | Fully vested |

The cliff ensures the contributor stays for at least three months. After that, tokens unlock monthly at a steady rate.

## Common Confusion

- Vesting is not a salary; it is a delayed grant that converts into ownership over time.
- Tokens do not appear in the recipient's wallet automatically; the recipient must submit a claim transaction to the vesting contract.
- A fully vested grant does not mean all tokens are sold; it means they are transferable, but the holder may keep them.
- Vesting schedules are not reversible; once tokens vest, they belong to the recipient and cannot be clawed back by the contract owner unless explicitly programmed.
- Accelerated vesting is not standard; special conditions like acquisition or milestone achievement must be written into the contract.
- Vesting does not prevent price drops; it only delays selling pressure by spreading unlocks over time.
- Multiple grants can overlap; a contributor may have one grant vesting monthly and another with a different cliff, managed by separate contracts or accounts.

## Key Properties

## Where It Appears in Our Code

The vesting API in `src_web3/phase37/vesting_api.ts` implements a complete vesting schedule with cliff detection, linear accrual, and a claim endpoint that computes exactly how many tokens have become unlocked at the current time.
