## What Is Vesting?

**The Problem:**
If a blockchain project gives all tokens to investors, team members, or
advisors on day one, those recipients can immediately sell everything
on the open market.

This creates massive sell pressure, crashes the token price, and
destroys confidence in the project.
Early backers need assurance that insiders cannot dump their
allocations instantly.

At the same time, long-term contributors need a predictable schedule
that guarantees their tokens will arrive if they continue building.
There must be a mechanism that staggers token releases over time,
aligning the incentives of recipients with the long-term health of the
protocol.

**Definition:**
Vesting is a schedule that gradually unlocks tokens or assets over time,
rather than releasing them all at once.

It typically includes a cliff, which is an initial period during which
no tokens are released, followed by periodic unlocks.
Vesting is used for team allocations, investor stakes, airdrops, and
employee compensation.

The schedule is enforced by a smart contract that checks the current
time against predefined milestones and only transfers tokens when the
conditions are met.

**Real-life analogy:**
Imagine a construction loan from a bank.
The bank does not hand the builder five hundred thousand dollars on the
first day.

Instead, the loan agreement specifies milestones: one hundred thousand
dollars when the foundation is complete, one hundred thousand dollars
when the framing is done, one hundred thousand dollars when the roof is
on, and so on.

The builder only receives each payment after an inspector verifies the
milestone.
If the builder abandons the project, the remaining funds stay with the
bank.

Vesting works identically: the smart contract is the bank, the
milestones are dates, and the inspector is the Clock sysvar.
Recipients only get paid when time proves they have stuck around.

**Tiny numeric example:**
An employee receives a grant of ten thousand tokens with a one-year
cliff and quarterly vesting thereafter.

| Date       | Time Elapsed | Milestone | Cumulative Unlocked | Remaining Locked |
|------------|--------------|-----------|---------------------|------------------|
| Start      | 0 months     | Grant     | 0                   | 10,000           |
| Month 6    | 6 months     | Cliff     | 0                   | 10,000           |
| Month 12   | 12 months    | 25%       | 2,500               | 7,500            |
| Month 15   | 15 months    | 37.5%     | 3,750               | 6,250            |
| Month 18   | 18 months    | 50%       | 5,000               | 5,000            |
| Month 24   | 24 months    | 75%       | 7,500               | 2,500            |
| Month 36   | 36 months    | 100%      | 10,000              | 0                |

Until month twelve, the employee cannot withdraw anything.
After the cliff, twenty-five percent unlocks, followed by additional
six-point-two-five percent every quarter.
If the employee leaves at month ten, they receive zero tokens.

**Common confusion:**
- **"Vesting means you cannot sell tokens until the end."**
  No. Vesting releases tokens gradually.
  After each milestone, the unlocked portion is fully liquid and can
  be sold or transferred.

- **"Vesting is only for employee compensation."**
  No. Vesting is used for investor allocations, airdrops, treasury
  releases, and protocol rewards.
  Any situation that benefits from staggered releases can use vesting.

- **"The cliff is a penalty."**
  No. The cliff is simply a waiting period.
  It ensures that short-term participants do not receive a
  disproportionate share before they have contributed meaningfully.

- **"Vesting schedules are reversible by the admin."**
  In some protocols, yes, but in trustless designs, the schedule is
  immutable once set.
  The smart contract enforces the dates regardless of admin
  preferences.

- **"Unvested tokens do not exist."**
  No. They usually exist in a smart contract vault, but they are
  locked.
  The total supply includes them, which means inflation is front-loaded
  even though liquidity is back-loaded.

- **"You can skip vesting by transferring the locked tokens."**
  No. Locked tokens are held by the vesting contract, not the
  recipient's wallet.
  The recipient only gains custody as tokens unlock.

- **"Vesting guarantees the token price will be stable."**
  No. Vesting reduces sudden sell pressure, but it does not control
  market demand, external news, or macro trends.
  It is one tool among many for token management.

**Where it appears in our code:**
`src_web3/phase20/timelock/src/lib.rs` — The program implements a
vesting schedule by checking elapsed time against milestones and
releasing proportional token amounts.

`src_web3/phase20/timelock_api.ts` — The Express API creates vesting
schedules, calculates unlocked amounts based on current time, and
allows claiming only the vested portion.
