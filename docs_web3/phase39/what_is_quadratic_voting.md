# What Is Quadratic Voting

## Why It Exists

Traditional voting systems give every voter one vote per issue, which treats weak preferences and strong preferences equally. A person who mildly supports a park renovation gets the same influence as someone who feels passionately about saving a hospital. This leads to outcomes that do not reflect the intensity of community desire. Quadratic voting fixes this by allowing voters to express strength of preference, but it charges them quadratically for additional votes so that no single person can dominate the outcome cheaply.

## Definition

Quadratic voting is a collective decision-making mechanism where voters purchase votes using a budget of voice credits. The cost of N votes on a single issue is N squared credits. This pricing makes it affordable to cast a few votes on many issues, but expensive to cast many votes on one issue, balancing intensity and breadth of preference.

## Real-Life Analogy

Imagine a town hall meeting where every resident receives 100 tokens. To vote on a new library, you can put in one token for one vote, four tokens for two votes, nine tokens for three votes, or sixteen tokens for four votes. A resident who cares deeply about the library can swing it, but at a steep cost. Another resident who cares equally about ten small issues can cast one vote on each and still influence the overall outcome. Quadratic voting is that town hall, but mathematically fair.

## Tiny Numeric Example

Three voters decide between two proposals: A and B. Each voter has 16 voice credits.

| Voter | Votes for A | Cost (credits) | Votes for B | Cost (credits) | Credits Spent |
|-------|------------:|---------------:|------------:|---------------:|--------------:|
| 1 | 4 | 16 | 0 | 0 | 16 |
| 2 | 1 | 1 | 2 | 4 | 5 |
| 3 | 1 | 1 | 3 | 9 | 10 |
| Total | 6 | 18 | 5 | 13 | 31 |

Proposal A wins with 6 total votes against B's 5, even though voter 1 spent all 16 credits on A. Voter 1's intensity was heard, but voters 2 and 3's combined moderate preferences still mattered. The quadratic cost prevented voter 1 from casting 16 votes and completely overriding everyone else.

## Common Confusion

- Quadratic voting is not "one person one vote"; it explicitly allows unequal influence, but prices it fairly.
- The square root of cost is not the number of votes; rather, the number of votes squared is the cost. Four votes cost sixteen credits.
- It does not eliminate majority rule; it refines it by incorporating preference intensity without allowing tyranny of the wealthiest.
- Voice credits are not money in most implementations; they are an equal budget distributed to participants.
- QV does not solve all governance problems; collusion, bribery, and low participation can still distort results.
- It requires a trusted mechanism to distribute voice credits; if credits are sold instead of given equally, the system reverts to plutocracy.
- The optimal outcome under QV maximizes the sum of utilities, but only if voters are truthful and independent.

## Key Properties

## Where It Appears in Our Code

The quadratic voting API in `src_web3/phase39/quadratic_voting_api.ts` implements an election where participants receive a fixed budget of voice credits, cast votes across multiple proposals, and the system tallies results using quadratic cost rules.
