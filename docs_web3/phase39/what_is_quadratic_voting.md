# What Is Quadratic Voting

**The Problem:**

Traditional voting systems give every voter one vote per issue, which treats weak preferences and strong preferences equally. A person who mildly supports a park renovation gets the same influence as someone who feels passionately about saving a hospital. This leads to outcomes that do not reflect the intensity of community desire. Quadratic voting fixes this by allowing voters to express strength of preference, but it charges them quadratically for additional votes so that no single person can dominate the outcome cheaply.

**Definition:**

Quadratic voting is a collective decision-making mechanism where voters purchase votes using a budget of voice credits. The cost of N votes on a single issue is N squared credits. This pricing makes it affordable to cast a few votes on many issues, but expensive to cast many votes on one issue, balancing intensity and breadth of preference.

**How It Works (Step-by-Step):**

1. **Receive budget.** The system distributes an equal, fixed budget of voice credits to every verified voter before the voting round begins.
2. **Choose proposals.** Each voter reviews the available proposals and decides which issues they care about and how many votes they want to cast on each.
3. **Calculate quadratic cost.** For each proposal, the system computes the credit cost as the square of the requested votes. Three votes on one proposal costs nine credits, not three.
4. **Submit votes.** The voter locks in their allocations. The system checks that the total credit cost across all proposals does not exceed the voter's budget.
5. **Tally results.** After voting closes, the system sums the vote counts for each proposal. The proposal with the highest total vote count wins, reflecting both the number of supporters and the intensity of their preferences.

**Real-life analogy:**

Imagine a town hall meeting where every resident receives 100 tokens. To vote on a new library, you can put in one token for one vote, four tokens for two votes, nine tokens for three votes, or sixteen tokens for four votes. A resident who cares deeply about the library can swing it, but at a steep cost. Another resident who cares equally about ten small issues can cast one vote on each and still influence the overall outcome. Quadratic voting is that town hall, but mathematically fair.

**Tiny numeric example:**

Three voters decide between two proposals: A and B. Each voter has 16 voice credits.

| Voter | Votes for A | Cost (credits) | Votes for B | Cost (credits) | Credits Spent |
|-------|------------:|---------------:|------------:|---------------:|--------------:|
| 1 | 4 | 16 | 0 | 0 | 16 |
| 2 | 1 | 1 | 2 | 4 | 5 |
| 3 | 1 | 1 | 3 | 9 | 10 |
| Total | 6 | 18 | 5 | 13 | 31 |

Proposal A wins with 6 total votes against B's 5, even though voter 1 spent all 16 credits on A. Voter 1's intensity was heard, but voters 2 and 3's combined moderate preferences still mattered. The quadratic cost prevented voter 1 from casting 16 votes and completely overriding everyone else.

**Common confusion:**

- No, quadratic voting is not "one person one vote"; it explicitly allows unequal influence, but prices it fairly.
- No, the square root of cost is not the number of votes; rather, the number of votes squared is the cost. Four votes cost sixteen credits.
- No, it does not eliminate majority rule; it refines it by incorporating preference intensity without allowing tyranny of the wealthiest.
- No, voice credits are not money in most implementations; they are an equal budget distributed to participants.
- No, QV does not solve all governance problems; collusion, bribery, and low participation can still distort results.
- No, the optimal outcome under QV does not occur automatically; it maximizes the sum of utilities only if voters are truthful and independent.

**Key properties:**

- The marginal cost of each additional vote increases linearly, while the total cost increases quadratically.
- Every participant begins with identical influence, preventing plutocratic outcomes.
- Expressing strong preference on a single issue requires sacrificing influence on all other issues.
- The mechanism incentivizes truthful revelation of preference intensity under ideal conditions.
- Outcomes approximate the socially optimal allocation when voters act independently.

**Where it appears in our code:**

The quadratic voting API in `src_web3/phase39/quadratic_voting_api.ts` implements an election where participants receive a fixed budget of voice credits, cast votes across multiple proposals, and the system tallies results using quadratic cost rules.
