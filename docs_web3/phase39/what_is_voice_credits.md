# What Are Voice Credits

## Why It Exists

If a voting system allowed unlimited votes, wealthy or malicious actors could buy outcomes. If it allowed only one vote per person, important but minority-supported initiatives would lose. Voice credits are the currency of quadratic voting that solves this tension. They give every participant equal initial influence while allowing them to allocate that influence according to how much they care. The fixed budget ensures fairness; the quadratic pricing ensures moderation.

## Definition

Voice credits are a finite, non-transferable budget assigned to each voter in a quadratic voting system. Voters spend credits to purchase votes on proposals, with the cost of each additional vote on the same proposal increasing quadratically.

## Real-Life Analogy

Think of a parent giving each child ten dollars to donate to school clubs. One child might give one dollar to ten clubs. Another might give four dollars to one club they love, which counts as two votes under the club's rules. The parent ensures no child has more than ten dollars total, so influence is capped, but the children decide how to spread or concentrate their support. Voice credits are those ten dollars, but digitized and enforced by a smart contract.

## Tiny Numeric Example

A DAO gives every member 25 voice credits for a governance round.

| Member | Proposal X Votes | Cost for X | Proposal Y Votes | Cost for Y | Credits Left |
|--------|-----------------:|-----------:|-----------------:|-----------:|-------------:|
| Alice | 3 | 9 | 2 | 4 | 12 |
| Bob | 1 | 1 | 4 | 16 | 8 |
| Carol | 2 | 4 | 2 | 4 | 17 |

Alice expresses moderate support for both proposals. Bob concentrates heavily on Y. Carol spreads evenly. The credit budget forces hard choices and prevents any member from overwhelming a single proposal.

## Common Confusion

- Voice credits are not cryptocurrency tokens in most designs; they are accounting units that cannot be traded or transferred.
- Leftover credits do not carry over by default; each round usually distributes a fresh budget to prevent hoarding.
- Spending all credits on one proposal is allowed but expensive; four votes cost sixteen credits, leaving nothing for other issues.
- Voice credits do not represent money; even if a user is wealthy in ETH, they still receive the same credit budget as everyone else.
- Distributing credits requires identity verification; without it, a single person could create many wallets and claim multiple budgets.
- Credits are not votes; they are the resource used to buy votes. One vote costs one credit, two votes cost four credits.
- The budget size is arbitrary but important; too small and no one can express strong preferences, too large and collusion becomes profitable.

## Key Properties

## Where It Appears in Our Code

Voice credits are modeled in `src_web3/phase39/quadratic_voting_api.ts` where the `/register` endpoint assigns a fixed budget to each voter and the `/vote` endpoint deducts the quadratic cost from that budget.
