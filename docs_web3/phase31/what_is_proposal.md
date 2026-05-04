# What Is a Proposal

## Why It Exists

Decentralized communities generate endless ideas in forums and chat rooms.
Without a formal mechanism for suggesting changes, discussions decay into noise with no actionable outcomes.
A proposal system creates a structured pipeline where ideas are submitted, debated, voted upon, and executed.
This process follows predefined rules that prevent malicious actors from forcing sudden changes.
It ensures every modification receives community scrutiny.
An immutable audit trail of governance decisions is created automatically.
Without proposals, protocols would lack the procedural rigor necessary to manage treasuries, upgrade code, or adjust parameters safely.
The proposal acts as the formal interface between informal community sentiment and enforceable on-chain action.

## Definition

A proposal is a formal on-chain request to alter protocol parameters, spend treasury funds, or upgrade program code.
It progresses through a lifecycle of pending, active, succeeded, defeated, or executed states.
These states are governed entirely by smart contract logic.
Each state transition is automatic and transparent.
Anyone can verify why a proposal advanced or failed without trusting a central administrator.

## Real-Life Analogy

Picture a town hall meeting where residents submit written motions instead of shouting suggestions from the floor.
Each motion is placed in a locked glass box for exactly one week.
Every citizen can read the full text, ask questions, and discuss implications with neighbors.
After the review period, townspeople drop colored tokens into ballot slots marked yes and no.
If the yes tokens exceed the no tokens by the required margin, the motion automatically unlocks the town budget.
Road repair is scheduled without needing a mayor to sign anything.

The glass box, the waiting period, and the automatic unlocking are all encoded rules.
These rules prevent hasty decisions and hidden agendas.
Once a motion enters the box, it cannot be altered.
Voters decide on the exact text they reviewed.
If the motion fails, the tokens are returned and the record remains public for future reference.
This mirrors how blockchain proposals function.
There is formal submission, immutable text, structured debate, binding vote, and automatic execution.

## Tiny Numeric Example

A proposal lifecycle measured in block heights on Solana looks like this:

| Stage | Start Block | End Block | Duration | Action Required |
|-------|------------|-----------|----------|-----------------|
| Submitted | 1,000,000 | 1,000,000 | 0 blocks | Pay deposit |
| Review | 1,000,001 | 1,050,800 | 50,800 blocks | Community debate |
| Voting | 1,050,801 | 1,152,400 | 101,600 blocks | Token holders vote |
| Queued | 1,152,401 | 1,253,000 | 100,600 blocks | Timelock delay |
| Execution | 1,253,001 | N/A | Immediate | Automatic if passed |

A proposal to send 5,000 USDC to a contractor for security audits passes with 60% approval.
It executes automatically once the timelock expires.
If the same proposal had received only 30% approval, it would transition to the defeated state.
The deposit would then be refunded to the proposer.

## Common Confusion

- A proposal is not immediately executable upon submission.
  It must pass through mandatory review and voting periods that allow community deliberation.
- Submitting a proposal is rarely free.
  Most DAOs require a refundable deposit to prevent spam and ensure serious proposals.
- A passed proposal is not guaranteed to execute successfully.
  The target smart contract may reject the instruction due to logic constraints.
- Proposals are not editable after submission.
  Any typo or mistake requires cancellation and resubmission with a new deposit.
- Off-chain forum discussion does not count as voting.
  Only on-chain token votes recorded in smart contracts affect the outcome.
- A proposal quorum is not the same as a majority.
  Quorum is the minimum participation threshold, while majority determines the winner.
- Failed proposals do not disappear from history.
  They remain permanently on-chain as immutable records of governance attempts.

## Key Properties
## Where It Appears in Our Code

Proposal creation and lifecycle management are implemented in `src_web3/phase31/governance/src/lib.rs`.
The `create_proposal` and `execute_proposal` instruction handlers enforce stage transitions.
They also validate state changes according to the governance rules.
The TypeScript API in `src_web3/phase31/governance_api.ts` exposes endpoints for creating proposals and tracking their status.
This allows front-end applications to interact with the on-chain governance system without handling raw transaction bytes directly.
Developers can use these endpoints to build dashboards that display proposal timelines and vote tallies in real time.
