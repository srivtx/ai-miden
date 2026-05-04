## What Is APY?

**The Problem:**
DeFi platforms advertise returns in many different formats: daily
rates, weekly rates, total return over a lockup period, or multiplier
points.

Without a standardized annual metric, users cannot compare
opportunities fairly. A platform offering ten percent per month looks
better than one offering one hundred percent per year, even though they
are mathematically identical.

Users need a single normalized number that reflects the real annual
return, including the effect of compounding.

**Definition:**
APY stands for Annual Percentage Yield.
It represents the real rate of return earned on an investment over one
year, accounting for compound interest.

Unlike APR, which is a simple annual rate, APY assumes that rewards
are reinvested and therefore generates returns on the rewards
themselves. The more frequently compounding occurs, the larger the gap
between APR and APY.

**Real-life analogy:**
Imagine two gyms advertising membership costs.
Gym A says ten dollars per visit.
Gym B says two hundred forty dollars per year.

To compare them, you convert both to the same unit: dollars per year.
If you plan to visit three times per week, Gym A costs one thousand
five hundred sixty dollars per year, making Gym B the obvious choice.

APY is the financial equivalent of that normalization.
It converts every return rate into an annual figure so you can compare
a daily compounding yield farm, a monthly lending protocol, and a
quarterly dividend stock on equal footing.

**Tiny numeric example:**
A protocol offers a daily reward rate of 0.1%.

| Metric | Calculation | Result |
|--------|-------------|--------|
| Daily rate | Given | 0.1% |
| APR (simple) | 0.1% * 365 | 36.5% |
| APY (daily compounding) | (1 + 0.001)^365 - 1 | 44.0% |
| APY (weekly compounding) | (1 + 0.007)^52 - 1 | 43.3% |
| APY (monthly compounding) | (1 + 0.03)^12 - 1 | 42.6% |

The difference between APR and APY is 7.5 percentage points in this
example.
Over a ten thousand dollar investment, that gap equals seven hundred
fifty dollars in additional returns purely from compounding frequency.

**Common confusion:**
- **"APY and APR are the same thing."**
  No. APR is a simple annual rate without compounding.
  APY includes compounding and is therefore always equal to or higher
  than APR for the same base rate.

- **"APY is guaranteed for the whole year."**
  No. APY is typically calculated from current reward rates, which can
  change daily. If the reward pool shrinks or more users stake, the
  actual APY you receive will drop.

- **"Higher APY always means better investment."**
  No. Extremely high APYs often come with extreme risks: smart contract
  bugs, token inflation, impermanent loss, or rug pulls.
  A sustainable ten percent APY may be safer than a temporary one
  thousand percent APY.

- **"APY includes token price appreciation."**
  No. APY measures the growth in token quantity, not fiat value.
  If the token price drops fifty percent while you earn a twenty
  percent APY, your net return in dollars is still negative.

- **"Compounding happens automatically in all protocols."**
  No. Some protocols require manual claiming and restaking.
  If you do not actively compound, your effective return will match the
  APR, not the advertised APY.

- **"APY is calculated the same way by every platform."**
  No. Different platforms use different time windows, fee assumptions,
  and compounding frequencies. Always read the fine print to understand
  how the number is derived.

- **"You need a large stake for APY to matter."**
  No. APY is a percentage and applies equally to all stake sizes.
  However, fixed gas fees for claiming and restaking can eat into small
  stakes, making high-frequency compounding uneconomical.

**Where it appears in our code:**
`src_web3/phase18/staking/src/lib.rs` — The program calculates reward
accrual based on elapsed time and stake amount, which forms the basis
for APY estimation.

`src_web3/phase18/staking_api.ts` — The Express API computes and
displays both APR and APY so users can compare simple versus compounded
returns before staking.
