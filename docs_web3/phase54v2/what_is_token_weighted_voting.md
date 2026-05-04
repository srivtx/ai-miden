# What Is Token-Weighted Voting

## The Problem

One-person-one-vote works for nation states, but not for capital-backed protocols. A user with one token and a user with one million tokens have different economic stakes. If both get one vote, the small holder can vote for outcomes that harm the large holder, creating misaligned incentives. Phase 54 used lamport-weighted voting, which is native SOL balance. This is wrong for DAOs because SOL is volatile, easily borrowed, and not representative of protocol ownership. Phase 54v2 uses SPL token balance voting, where votes are weighted by holdings of a specific governance token.

## Definition

Token-weighted voting is a governance mechanism where a voter's influence is proportional to their balance of a designated SPL token at a specific block height or snapshot. The protocol checks the voter's token account, reads the amount field, and adds that amount to the proposal's vote tally. This aligns voting power with economic stake in the protocol.

## How It Works (6 Steps)

1. **Mint Governance Token** — The protocol creates an SPL token mint. This token is distributed to stakeholders, liquidity providers, or contributors.
2. **Take Snapshot** — Before voting begins, the protocol records the current token balances or sets a checkpoint. Some protocols take a merkle snapshot; others read on-chain balances in real time.
3. **Verify Token Account** — When a user votes, the program receives the user's token account as an account in the instruction. Anchor validates the account's mint and owner.
4. **Read Balance** — The program reads the `amount` field from the validated token account.
5. **Apply Weight** — The program adds the balance to `votes_for` or `votes_against`. A user with 500,000 tokens adds 500,000 to the tally.
6. **Enforce Deadline** — After the voting period ends, no further votes are accepted. The final tally determines execution eligibility.

## Real-Life Analogy

Token-weighted voting is like shareholder voting in a public company. If you own 100 shares of stock, you get 100 votes. If you own 10,000 shares, you get 10,000 votes. The board does not ask how many people you represent. They ask how many shares you own. Your influence matches your financial exposure to the company's success or failure.

## Tiny Numeric Example

```rust
use anchor_lang::prelude::*;
use anchor_spl::token::{TokenAccount, Mint};

declare_id!("Vote333333333333333333333333333333333333333");

#[program]
pub mod voting {
    use super::*;
    
    pub fn cast_vote(
        ctx: Context<CastVote>,
        vote_for: bool,
    ) -> Result<()> {
        let proposal = &mut ctx.accounts.proposal;
        let voter_token_account = &ctx.accounts.voter_token_account;
        let voter_record = &mut ctx.accounts.voter_record;
        
        require!(
            !proposal.has_voted.contains(&ctx.accounts.voter.key()),
            ErrorCode::AlreadyVoted
        );
        
        let weight = voter_token_account.amount;
        require!(weight > 0, ErrorCode::NoTokens);
        
        if vote_for {
            proposal.votes_for = proposal.votes_for.checked_add(weight).unwrap();
        } else {
            proposal.votes_against = proposal.votes_against.checked_add(weight).unwrap();
        }
        
        voter_record.weight = weight;
        voter_record.vote_for = vote_for;
        proposal.has_voted.push(ctx.accounts.voter.key());
        
        Ok(())
    }
}

#[derive(Accounts)]
pub struct CastVote<'info> {
    #[account(mut)]
    pub voter: Signer<'info>,
    
    #[account(
        mut,
        constraint = proposal.deadline > Clock::get()?.unix_timestamp
    )]
    pub proposal: Account<'info, Proposal>,
    
    #[account(
        constraint = voter_token_account.owner == voter.key(),
        constraint = voter_token_account.mint == governance_mint.key(),
    )]
    pub voter_token_account: Account<'info, TokenAccount>,
    
    pub governance_mint: Account<'info, Mint>,
    
    #[account(
        init_if_needed,
        payer = voter,
        space = 8 + 32 + 8 + 1,
        seeds = [b"vote", proposal.key().as_ref(), voter.key().as_ref()],
        bump
    )]
    pub voter_record: Account<'info, VoterRecord>,
    
    pub system_program: Program<'info, System>,
}

#[account]
pub struct Proposal {
    pub creator: Pubkey,
    pub description: String,
    pub quorum: u64,
    pub votes_for: u64,
    pub votes_against: u64,
    pub deadline: i64,
    pub executed: bool,
    pub has_voted: Vec<Pubkey>,
}

#[account]
pub struct VoterRecord {
    pub voter: Pubkey,
    pub weight: u64,
    pub vote_for: bool,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Already voted on this proposal")]
    AlreadyVoted,
    #[msg("No governance tokens held")]
    NoTokens,
}
```

In this example, `voter_token_account.amount` is the voting weight. Anchor validates that the token account is owned by the voter and matches the governance mint. A user with 250,000 governance tokens adds 250,000 to the tally. The `init_if_needed` attribute creates the voter record only on the first vote, saving rent. The `checked_add` prevents overflow, a common vulnerability in token-weighted systems.

## Common Confusion

- **Is token-weighted voting the same as proof of stake?** No. Proof of stake secures the blockchain. Token-weighted voting governs a protocol. They use different tokens and different rules.
- **Can I vote with borrowed tokens?** No. If the snapshot is taken before you borrow, the borrowed tokens do not count. Real protocols use snapshots or escrow to prevent flash loan attacks.
- **Does a large holder always win?** No. If the quorum requires more than the large holder owns, smaller holders can combine to reach quorum.
- **Are NFTs used for voting?** No. This example uses fungible SPL tokens. Some protocols use NFTs, but that is a different mechanism.
- **Can I split my tokens across wallets to vote twice?** No. Each wallet's token account is checked, but the sum still equals your total balance. You gain no advantage.
- **Is one token one vote mandatory?** No. Some protocols use quadratic voting, where votes cost the square of tokens. Token-weighted is linear by default.

## Key Properties

1. **Economic Alignment** — Voters with more tokens have more to lose or gain from the outcome. This reduces frivolous or malicious proposals.
2. **On-Chain Verifiability** — Anyone can verify that a vote weight matches a token balance at a specific mint. No off-chain oracle is required.
3. **Flash Loan Resistance** — Snapshots or escrow periods prevent attackers from borrowing tokens, voting, and repaying in the same transaction.
4. **Delegation Support** — Token holders can delegate voting power to representatives without transferring token ownership.
5. **Composable Tallying** — Vote tallies are stored on-chain in proposal accounts. Other programs can read these values and trigger conditional logic.
