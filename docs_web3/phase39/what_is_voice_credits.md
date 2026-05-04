# What Are Voice Credits

**The Problem:**

If a voting system allowed unlimited votes, wealthy or malicious actors could buy outcomes. If it allowed only one vote per person, important but minority-supported initiatives would lose. Voice credits are the currency of quadratic voting that solves this tension. They give every participant equal initial influence while allowing them to allocate that influence according to how much they care. The fixed budget ensures fairness; the quadratic pricing ensures moderation.

**Definition:**

Voice credits are a finite, non-transferable budget assigned to each voter in a quadratic voting system. Voters spend credits to purchase votes on proposals, with the cost of each additional vote on the same proposal increasing quadratically.

**How It Works (Step-by-Step):**

1. **Allocate credits.** The system distributes an identical, fixed budget of voice credits to every verified voter at the start of a governance round.
2. **Select proposals and vote counts.** A voter chooses which proposals to support and how many votes to cast on each. Choosing more votes on one proposal means fewer resources remain for others.
3. **Apply the quadratic cost formula.** The system calculates the credit cost for each proposal as `cost = votes^2`. One vote costs 1 credit, two votes cost 4 credits, three votes cost 9 credits, and four votes cost 16 credits.
4. **Deduct from budget.** The system subtracts the total quadratic cost across all proposals from the voter's credit budget. If the total exceeds the budget, the transaction is rejected.
5. **Record votes.** Once the budget check passes, the system registers the vote counts for each chosen proposal.
6. **Finalize spending.** Spent credits are consumed and cannot be recovered or reallocated during the same round. Leftover credits typically expire when the round ends.

**Real-life analogy:**

Think of a parent giving each child ten dollars to donate to school clubs. One child might give one dollar to ten clubs. Another might give four dollars to one club they love, which counts as two votes under the club's rules. The parent ensures no child has more than ten dollars total, so influence is capped, but the children decide how to spread or concentrate their support. Voice credits are those ten dollars, but digitized and enforced by a smart contract.

**Tiny numeric example:**

A DAO gives every member 25 voice credits for a governance round.

| Member | Proposal X Votes | Cost for X | Proposal Y Votes | Cost for Y | Credits Left |
|--------|-----------------:|-----------:|-----------------:|-----------:|-------------:|
| Alice | 3 | 9 | 2 | 4 | 12 |
| Bob | 1 | 1 | 4 | 16 | 8 |
| Carol | 2 | 4 | 2 | 4 | 17 |

Alice expresses moderate support for both proposals. Bob concentrates heavily on Y. Carol spreads evenly. The credit budget forces hard choices and prevents any member from overwhelming a single proposal.

**Common confusion:**

- No, voice credits are not cryptocurrency tokens in most designs; they are accounting units that cannot be traded or transferred.
- No, leftover credits do not carry over by default; each round usually distributes a fresh budget to prevent hoarding.
- No, spending all credits on one proposal is not efficient; four votes cost sixteen credits, leaving nothing for other issues.
- No, voice credits do not represent money; even if a user is wealthy in ETH, they still receive the same credit budget as everyone else.
- No, credits are not votes; they are the resource used to buy votes. One vote costs one credit, two votes cost four credits.
- No, the budget size is not irrelevant; too small and no one can express strong preferences, too large and collusion becomes profitable.

**Key properties:**

- Non-transferable by design, preventing market-based influence buying.
- Quadratic pricing imposes a real trade-off between intensity and breadth of preference.
- Equal initial distribution is essential for fairness and anti-plutocracy.
- Credits are consumed upon use and typically expire at the end of a voting round.
- The budget constraint forces voters to reveal their true relative priorities.

**Where it appears in our code:**

Voice credits are modeled in `src_web3/phase39/quadratic_voting_api.ts` where the `/register` endpoint assigns a fixed budget to each voter and the `/vote` endpoint deducts the quadratic cost from that budget.
