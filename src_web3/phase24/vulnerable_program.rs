use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount};

// This file intentionally demonstrates vulnerable patterns for educational comparison.
// DO NOT USE THIS CODE IN PRODUCTION.

declare_id!("Vuln4444444444444444444444444444444444444444");

#[program]
pub mod vulnerable_program {
    use super::*;

    // VULNERABLE: This withdraw function transfers tokens before updating state.
    // An attacker could trigger a cross-program invocation that reenters withdraw
    // before the balance is reduced, draining the vault.
    pub fn withdraw(ctx: Context<VulnerableWithdraw>, amount: u64) -> Result<()> {
        // No signer check on the owner means anyone can pass any token account.
        // This allows attackers to withdraw from accounts they do not own.

        // VULNERABLE: No validation that the vault account is owned by this program.
        // An attacker could pass their own account as the vault and steal funds.

        // VULNERABLE: Transfer happens before state update, enabling reentrancy.
        let cpi_accounts = token::Transfer {
            from: ctx.accounts.vault.to_account_info(),
            to: ctx.accounts.user_token_account.to_account_info(),
            authority: ctx.accounts.vault_authority.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);
        token::transfer(cpi_ctx, amount)?;

        // VULNERABLE: State update happens after the external transfer call.
        // If the recipient is a malicious program, it can reenter before this line.
        let user = &mut ctx.accounts.user;
        user.balance = user.balance - amount; // Also vulnerable to underflow.

        Ok(())
    }

    // VULNERABLE: This deposit function uses unchecked arithmetic.
    // Overflow could silently wrap a user's balance to zero or a tiny number.
    pub fn deposit(ctx: Context<VulnerableDeposit>, amount: u64) -> Result<()> {
        // No signer check means anyone can credit any user account.
        let user = &mut ctx.accounts.user;
        // VULNERABLE: Standard addition wraps on overflow in release builds.
        user.balance = user.balance + amount;
        Ok(())
    }
}

#[derive(Accounts)]
pub struct VulnerableWithdraw<'info> {
    // VULNERABLE: This is not marked as a Signer, so the transaction submitter
    // does not need to own this account to trigger a withdrawal.
    pub user: Account<'info, User>,

    // VULNERABLE: No ownership constraint means any token account can be passed.
    pub vault: Account<'info, TokenAccount>,

    // VULNERABLE: No validation that this authority actually owns the vault.
    pub vault_authority: AccountInfo<'info>,

    // VULNERABLE: No constraint linking user_token_account to the user.
    pub user_token_account: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct VulnerableDeposit<'info> {
    // VULNERABLE: Not a Signer, so attackers can manipulate other users' balances.
    #[account(mut)]
    pub user: Account<'info, User>,

    pub system_program: Program<'info, System>,
}

#[account]
pub struct User {
    pub balance: u64,
}
