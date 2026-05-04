use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount};

// This file demonstrates secure patterns that fix the vulnerabilities shown in vulnerable_program.rs.
// Use these patterns as a reference for production Solana programs.

declare_id!("Secure444444444444444444444444444444444444444");

#[program]
pub mod secure_program {
    use super::*;

    // SECURE: This withdraw function updates state before any external transfer.
    // It also enforces signer checks and validates all accounts.
    pub fn withdraw(ctx: Context<SecureWithdraw>, amount: u64) -> Result<()> {
        // Verify the amount is positive to prevent zero-value spam attacks.
        require!(amount > 0, ErrorCode::AmountMustBeGreaterThanZero);

        // SECURE: Ensure the user has sufficient balance before proceeding.
        require!(
            ctx.accounts.user.balance >= amount,
            ErrorCode::InsufficientBalance
        );

        // SECURE: Update state before the external token transfer to prevent reentrancy.
        let user = &mut ctx.accounts.user;
        user.balance = user.balance.checked_sub(amount).ok_or(ErrorCode::Underflow)?;

        // SECURE: Transfer tokens only after the internal balance is reduced.
        // Even if the recipient reenters, the balance check will fail.
        let cpi_accounts = token::Transfer {
            from: ctx.accounts.vault.to_account_info(),
            to: ctx.accounts.user_token_account.to_account_info(),
            authority: ctx.accounts.vault_authority.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        // Use the PDA seeds to authorize the transfer from the program vault.
        let seeds = &[b"vault", &[ctx.bumps.vault_authority]];
        let signer = &[&seeds[..]];
        let cpi_ctx = CpiContext::new_with_signer(cpi_program, cpi_accounts, signer);
        token::transfer(cpi_ctx, amount)?;

        Ok(())
    }

    // SECURE: This deposit function uses checked arithmetic to prevent overflow.
    pub fn deposit(ctx: Context<SecureDeposit>, amount: u64) -> Result<()> {
        // Verify the amount is positive to prevent zero-value deposits.
        require!(amount > 0, ErrorCode::AmountMustBeGreaterThanZero);

        let user = &mut ctx.accounts.user;
        // SECURE: checked_add returns None on overflow, which we convert to an error.
        user.balance = user.balance.checked_add(amount).ok_or(ErrorCode::Overflow)?;
        Ok(())
    }
}

#[derive(Accounts)]
pub struct SecureWithdraw<'info> {
    // SECURE: The owner must sign to prove they authorize this withdrawal.
    #[account(mut)]
    pub owner: Signer<'info>,

    // SECURE: The user account is linked to the owner via a constraint.
    #[account(mut, has_one = owner)]
    pub user: Account<'info, User>,

    // SECURE: The vault must be owned by the token program to prevent fake accounts.
    #[account(mut, token::authority = vault_authority)]
    pub vault: Account<'info, TokenAccount>,

    // SECURE: The vault authority is a PDA derived from this program.
    #[account(seeds = [b"vault"], bump)]
    pub vault_authority: AccountInfo<'info>,

    // SECURE: The destination token account must be owned by the signing owner.
    #[account(token::authority = owner)]
    pub user_token_account: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct SecureDeposit<'info> {
    // SECURE: The depositor must sign to prevent unauthorized balance manipulation.
    #[account(mut)]
    pub depositor: Signer<'info>,

    // SECURE: The user account is linked to the depositor via a constraint.
    #[account(mut, has_one = depositor @ ErrorCode::Unauthorized)]
    pub user: Account<'info, User>,

    pub system_program: Program<'info, System>,
}

#[account]
pub struct User {
    pub owner: Pubkey, // SECURE: Track the authorized owner to enforce access control.
    pub balance: u64,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Amount must be greater than zero")]
    AmountMustBeGreaterThanZero,
    #[msg("Insufficient balance")]
    InsufficientBalance,
    #[msg("Arithmetic underflow")]
    Underflow,
    #[msg("Arithmetic overflow")]
    Overflow,
    #[msg("Unauthorized")]
    Unauthorized,
}
