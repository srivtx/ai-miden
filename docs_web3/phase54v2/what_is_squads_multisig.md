# What Is Squads Multisig

## The Problem

A DAO treasury holds millions or billions of dollars in tokens. If a single private key controls the treasury, one phishing attack or one rogue employee can drain everything. Traditional multisig wallets exist, but they are generic. They do not understand governance proposals, voting periods, or protocol-specific execution logic. Phase 54 used a basic transfer function. Phase 54v2 uses Squads, a protocol-level multisig designed for Solana treasuries.

## Definition

Squads is a multisig protocol built on Solana. Version 4 (Squads v4) provides on-chain multisig accounts, transaction proposals, member voting, and execution. It is not just a wallet. It is a program that other programs can integrate with. Over $10 billion in assets are secured by Squads multisigs across the Solana ecosystem.

## How It Works (6 Steps)

1. **Create Multisig** — A team initializes a Squads multisig with a list of member public keys and a threshold (e.g., 3 of 5).
2. **Create Vault** — Squads creates a program-derived address that acts as the treasury vault. This vault is controlled only by the multisig program.
3. **Propose Transaction** — Any member proposes a transaction, such as transferring USDC to a contractor or calling a custom program instruction.
4. **Vote on Transaction** — Members vote yes or no. Votes are recorded on-chain in the Squads program.
5. **Reach Threshold** — Once the number of yes votes meets the threshold, the transaction becomes executable.
6. **Execute Transaction** — Any member (or a permissionless cranker) executes the transaction. The Squads program validates the threshold, then makes the CPI call or token transfer.

## Real-Life Analogy

A corporate bank account with signatories is like Squads. Imagine a nonprofit with five board members. The bylaws say three signatures are required to write a check. Any board member can write a check, but the bank only honors it after seeing three valid signatures. Squads is the bank and the bylards combined, but on-chain and automated.

## Tiny Numeric Example

```rust
use anchor_lang::prelude::*;
use squads_multisig_program::state::Multisig;

declare_id!("Tre222222222222222222222222222222222222222");

#[program]
pub mod treasury {
    use super::*;
    
    pub fn request_withdrawal(
        ctx: Context<RequestWithdrawal>,
        amount: u64,
    ) -> Result<()> {
        let treasury = &mut ctx.accounts.treasury;
        let proposal = &mut ctx.accounts.proposal;
        
        require!(
            amount <= treasury.balance,
            ErrorCode::InsufficientFunds
        );
        
        proposal.amount = amount;
        proposal.approvals = 0;
        proposal.threshold = treasury.threshold;
        proposal.executed = false;
        
        Ok(())
    }
}

#[derive(Accounts)]
pub struct RequestWithdrawal<'info> {
    #[account(mut)]
    pub proposer: Signer<'info>,
    
    #[account(
        mut,
        constraint = treasury.members.contains(&proposer.key())
    )]
    pub treasury: Account<'info, Treasury>,
    
    #[account(
        init,
        payer = proposer,
        space = 8 + 32 + 8 + 8 + 8 + 1,
        seeds = [b"withdrawal", treasury.key().as_ref(), &treasury.proposal_count.to_le_bytes()],
        bump
    )]
    pub proposal: Account<'info, WithdrawalProposal>,
    
    pub system_program: Program<'info, System>,
}

#[account]
pub struct Treasury {
    pub members: Vec<Pubkey>,
    pub threshold: u8,
    pub balance: u64,
    pub proposal_count: u64,
}

#[account]
pub struct WithdrawalProposal {
    pub treasury: Pubkey,
    pub amount: u64,
    pub approvals: u8,
    pub threshold: u8,
    pub executed: bool,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Insufficient treasury balance")]
    InsufficientFunds,
}
```

In this simplified pattern, the treasury stores a member list and threshold. The `constraint = treasury.members.contains(&proposer.key())` ensures only members can propose. The proposal PDA is seeded with the treasury key and a nonce, guaranteeing uniqueness. In a full Squads integration, the member check and threshold logic would be delegated to the Squads program via CPI, but this example shows the core pattern: on-chain threshold logic with deterministic proposal addresses.

## Common Confusion

- **Is Squads just a wallet?** No. It is a protocol. Other programs can invoke Squads instructions via CPI.
- **Does Squads custody my funds?** No. Your funds sit in a PDA controlled by the Squads program, not by Squads Labs the company.
- **Can I recover a lost key?** No. If you lose your private key and no other members will vote to replace you, access is permanently reduced.
- **Is Squads free?** No. There are small transaction fees for creating multisigs and executing transactions, paid in SOL for rent and compute.
- **Can one member block execution?** No. A member voting no does not veto. Only failing to reach the yes threshold blocks execution.
- **Does Squads support time locks?** No. Squads v4 itself does not enforce time locks, but you can wrap Squads execution in a timelock program.

## Key Properties

1. **Threshold-Based Security** — Funds move only after M of N members approve. No single point of failure.
2. **On-Chain Transparency** — Every proposal, vote, and execution is recorded on Solana. Anyone can audit the history.
3. **Program Composability** — Other Anchor programs can create Squads proposals and vaults via CPI, making multisig a building block.
4. **Permissionless Execution** — Once threshold is met, anyone can trigger execution. You do not need a specific member online at the exact moment.
5. **Deterministic Vaults** — Treasury addresses are derived from the multisig address and seed constants. You can predict vault addresses before creation.
