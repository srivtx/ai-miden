# What Is Treasury Management?

## The Problem

A decentralized organization needs to hold and spend collective funds, but if a single person controls the wallet, the organization is not truly decentralized. Members need a way to pool resources and spend them only after collective approval, with protections against theft, abuse, and unilateral action.

## Definition

Treasury management is the practice of holding, tracking, and releasing a DAO's shared assets through programmatic rules. It combines multi-signature authorization, spending limits, and on-chain execution so that funds move only when the community has explicitly approved the destination, amount, and purpose.

## How It Works (6 Steps)

1. **Pool funds.** Members deposit tokens or assets into a treasury account that the DAO program controls. This creates a shared balance visible on-chain.

2. **Set spending limits.** The DAO defines maximum amounts that can be moved in a single transaction, per day, or per proposal category. This prevents any one large withdrawal from draining the treasury.

3. **Require multi-sig approval.** Before any release, a configurable number of signers must approve. This is often the same as the proposal vote threshold, but it can be a separate security layer.

4. **Link to proposals.** Withdrawals are not standalone transactions. They are attached to proposals that pass through the governance cycle, ensuring the community votes on the purpose and amount.

5. **Execute after timelock.** Even after a proposal passes, there is a mandatory delay before the treasury releases funds. This gives members time to review the outcome and exit if they disagree.

6. **Log every movement.** All deposits, approvals, and withdrawals are recorded on-chain. Anyone can audit the full history of treasury activity without trusting a central bookkeeper.

## Real-life Analogy

Imagine a community center funded by neighborhood dues. The center's bank account requires three board members to sign any check over $1,000. A proposal to repaint the walls must be approved at a town hall meeting, and the check can only be written three days after the vote. No single person can walk away with the money, and every expense traces back to a public decision.

## Tiny Numeric Example with Proposal Thresholds

A DAO has 100 members and a treasury of 50,000 USDC.

- Proposal threshold: 10 members must co-sign to create a spending proposal.
- Quorum: 40 votes required for a valid result.
- Pass threshold: 60% of votes must be in favor.
- Spending limit: 5,000 USDC per proposal.
- Multi-sig requirement: 3 of 5 treasury signers.
- Timelock: 2 days after passing.

A member proposes a 4,000 USDC marketing grant. 45 members vote, 30 in favor (66%). After the 2-day delay, 3 treasury signers confirm, and the 4,000 USDC is released. A later proposal for 6,000 USDC is automatically rejected because it exceeds the 5,000 USDC spending limit.

## Common Confusion

- Does the treasury need a separate wallet from the DAO? No. The treasury is an account owned by the DAO program, not a standalone wallet, though it may hold many types of tokens.

- Can the treasury manager override a vote? No. The treasury program only executes what the governance program instructs after a proposal passes.

- Is the treasury only for tokens? No. It can hold NFTs, LP positions, or any asset the program is configured to manage.

- Are spending limits fixed forever? No. The DAO can vote to update limits, but that change itself is a proposal subject to the same rules.

- Does multi-sig mean every member must sign? No. Multi-sig refers to a smaller set of appointed signers or the proposal outcome, not a requirement for every single member.

- Can funds be recovered if sent to the wrong address? No. Blockchain transactions are irreversible. The timelock exists precisely to catch errors before execution.

## Key Properties (5)

1. **Transparency.** Every balance and transaction is on-chain and verifiable.

2. **Collective control.** No single actor can move funds without community approval.

3. **Rate limiting.** Spending limits prevent rapid or excessive withdrawals.

4. **Time delay.** The timelock adds a safety window for review and response.

5. **Programmatic enforcement.** Rules are code, not policy documents. Violations are impossible by construction.

## Where It Appears

Treasury management appears in every major DAO, including MakerDAO's protocol surplus buffer, Uniswap's grants program, Gitcoin's matching pool, and any community-governed project that holds more than a trivial amount of assets. It is the financial backbone of on-chain governance.
