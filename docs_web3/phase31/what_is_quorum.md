# What Is Quorum

## Why It Exists

If only a tiny fraction of token holders participate in governance, a malicious actor could pass harmful proposals with minimal support.
Quorum exists to ensure that decisions reflect broad community engagement.
Without it, the will of a narrow minority could override the silent majority.
Low-participation attacks could drain treasuries, force unwanted upgrades, or grant emergency powers to small factions.
Quorum forces proposal creators to actively campaign and build consensus.
They cannot rely on apathy to slide changes through unnoticed.
In essence, quorum separates legitimate collective decisions from stealth takeovers.
It requires visible evidence of community involvement before any binding action can occur.

## Definition

Quorum is the minimum number or percentage of eligible votes that must be cast for a proposal to be considered valid.
If quorum is not reached, the proposal fails automatically.
This failure happens regardless of the yes-to-no ratio among those who did vote.
The threshold is typically encoded directly into the governance smart contract.
It can only be changed through a successful proposal that itself meets the existing quorum.

## Real-Life Analogy

Imagine a union contract negotiation where the agreement only becomes legally binding if at least half the members cast ballots.
If only ten out of one hundred workers vote, even a unanimous ten-to-zero result cannot ratify the contract.
This rule forces organizers to engage the entire membership.
They must hold informational meetings and ensure broad understanding before any vote occurs.

The quorum requirement protects the silent majority from being bound by decisions they ignored.
It also prevents a small group of highly motivated insiders from making sweeping changes while the broader community sleeps.
Just as a union cannot claim worker consent without worker participation, a DAO cannot claim community mandate without community votes.
The mechanism ensures that apathy is not mistaken for assent.

## Tiny Numeric Example

A DAO has 10,000 eligible governance tokens, and the quorum requirement is set at 20%:

| Proposal | Total Votes Cast | Quorum Met? | Yes Votes | No Votes | Final Result |
|----------|-----------------|-------------|----------|----------|--------------|
| Alpha | 2,500 | Yes (25%) | 1,800 | 700 | Passes with 72% approval |
| Beta | 1,500 | No (15%) | 1,200 | 300 | Fails due to quorum |
| Gamma | 2,000 | Yes (20%) | 800 | 1,200 | Fails with 40% approval |
| Delta | 3,000 | Yes (30%) | 1,500 | 1,500 | Fails with 50% approval |

Proposal Beta fails despite 80% approval because too few participants voted.
The 1,200 yes votes represent a strong majority of voters, but they constitute only 12% of total eligible tokens.
Proposal Delta reaches quorum but still fails because it did not achieve a majority.
This shows that quorum and majority are independent requirements.
Both must be satisfied for a proposal to pass.
A well-designed governance system sets quorum high enough to ensure legitimacy but low enough to avoid gridlock.
Setting quorum at 50% may prevent any proposal from passing during market downturns when holders are inactive.
Setting quorum at 5% may allow well-coordinated attackers to pass harmful proposals with minimal resistance.
Many protocols dynamically adjust quorum based on historical participation rates.
This adaptive approach maintains security without freezing governance during low-engagement periods.
Community education about quorum importance is essential for healthy decentralized governance.
Voters must understand that abstaining still affects the system by making quorum harder to reach.

## Common Confusion

- Quorum is not the same as a majority.
  Quorum measures participation level, while majority measures the winner among voters.
- Reaching quorum does not guarantee passage.
  It merely allows the proposal to be decided by the vote tally that follows.
- Abstain votes typically count toward quorum.
  They demonstrate active participation even without taking a side on the issue.
- Quorum requirements are not universal across all DAOs.
  Some use 10%, others use 40%, depending on community risk tolerance and size.
- Quorum cannot be bypassed by splitting one proposal into many smaller proposals.
  Each proposal is evaluated independently against the threshold.
- High quorum is not always better governance.
  Overly strict requirements can create gridlock and prevent necessary upgrades.
- Quorum is not permanently fixed.
  Many DAOs allow governance votes to adjust the threshold as the community evolves.

## Key Properties
## Where It Appears in Our Code

Quorum validation logic is enforced in `src_web3/phase31/governance/src/lib.rs`.
The `execute_proposal` function checks total participation against the minimum threshold.
Only after this check passes can the proposal outcome be finalized.
This ensures that every executed decision reflects genuine community engagement.
