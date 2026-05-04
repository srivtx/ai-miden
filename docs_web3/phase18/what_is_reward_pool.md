## What Is a Reward Pool?

**The Problem:**
Staking incentives must come from a sustainable source.
If a protocol promises rewards but has no treasury, no fee revenue,
and no emission schedule, the rewards are either a Ponzi scheme or a
temporary marketing gimmick.

Users need confidence that the reward stream is funded, predictable,
and fairly distributed. Without a transparent reward pool, stakers
cannot estimate their real yield or trust the protocol's long-term
viability.

**Definition:**
A reward pool is a dedicated treasury of tokens, usually held in a
smart contract, that is used to pay staking rewards over time
according to predefined rules.

The pool is funded by protocol emissions, transaction fees, or external
contributions. Rewards are distributed algorithmically based on stake
size, duration, and sometimes additional criteria such as lockup length
or governance participation.

**Real-life analogy:**
Imagine a company that sets aside ten percent of its quarterly profits
into a locked bonus fund. The fund is transparent: employees can see
the balance on a public dashboard.

At the end of each quarter, the fund is distributed to employees who
have worked the full period, with larger bonuses going to those who
worked more hours. If the company has a bad quarter, the fund is
smaller, and bonuses shrink accordingly.

If the company has a great quarter, the fund grows, and everyone
benefits. The key is that the money already exists before it is
promised.

A reward pool in DeFi works identically: it is a visible, pre-funded
reservoir that pays out algorithmically based on verifiable
contributions.

**Tiny numeric example:**
A protocol allocates 1,000,000 reward tokens for one year of staking
incentives.

| Total Staked | Reward Pool | Duration | Rate per Token per Second | Your Stake | Your Daily Reward |
|--------------|-------------|----------|---------------------------|------------|-------------------|
| 100,000      | 1,000,000   | 1 year   | 0.000000317               | 10,000     | 273.97 tokens     |
| 500,000      | 1,000,000   | 1 year   | 0.0000000634              | 10,000     | 54.79 tokens      |
| 1,000,000    | 1,000,000   | 1 year   | 0.0000000317              | 10,000     | 27.40 tokens      |
| 2,000,000    | 1,000,000   | 1 year   | 0.00000001585             | 10,000     | 13.70 tokens      |

As more tokens are staked, the same reward pool is divided among more
participants, so the rate per token decreases.
This is why early stakers often earn higher yields.

**Common confusion:**
- **"The reward pool is infinite."**
  No. Nearly all reward pools have a fixed budget.
  Once the tokens are distributed, rewards stop unless the treasury is
  replenished through fees or new emissions.

- **"Reward pools are funded by new investors."**
  In legitimate protocols, reward pools are funded by protocol revenue,
  token emissions, or treasury allocations.
  If the only source of rewards is new deposits, the model is
  unsustainable.

- **"A bigger reward pool always means higher APY."**
  No. APY depends on the ratio of rewards to total staked amount.
  A massive pool with billions staked may pay less than a small pool
  with few stakers.

- **"Reward pools pay out in the same token you staked."**
  Not necessarily. Many protocols pay rewards in a governance token
  or a partner token, not the original staked asset.
  This creates exposure to a second asset's price volatility.

- **"Once a reward pool is created, the rules never change."**
  Protocol governance can vote to alter emission schedules, add new
  pools, or redirect funding. The current rules are not necessarily
  permanent.

- **"Unclaimed rewards stay in the pool forever."**
  Most protocols have claim deadlines or auto-compound mechanisms.
  Unclaimed rewards may be reclaimed by the treasury or redistributed
  after a certain period.

- **"Reward pool APY is guaranteed."**
  APY is an estimate based on current parameters.
  If total staked amount changes or the reward pool is depleted, the
  actual yield will differ from the projection.

**Where it appears in our code:**
`src_web3/phase18/staking/src/lib.rs` — The on-chain program tracks a
reward pool balance and decrements it as stakers claim their earned
rewards.

`src_web3/phase18/staking_api.ts` — The Express API models a finite
reward pool and recalculates per-token reward rates whenever new stakes
enter the system.
