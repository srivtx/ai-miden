use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Mint, Transfer}; // WHY: Import SPL token primitives for real CPI transfers

declare_id!("Vest222222222222222222222222222222222222222"); // WHY: Program ID placeholder

#[program] // WHY: Anchor macro for program entrypoint
pub mod vesting {
    use super::*; // WHY: Bring parent scope items into instruction handlers

    // WHY: Create a vesting schedule for a user's token allocation
    pub fn create_schedule(
        ctx: Context<CreateSchedule>,
        total_amount: u64,
        cliff_duration: i64,
        vesting_duration: i64,
    ) -> Result<()> {
        require!(vesting_duration > cliff_duration, VestingError::InvalidDuration); // WHY: Vesting must exceed cliff
        let schedule = &mut ctx.accounts.schedule; // WHY: Mutable reference to initialize schedule
        schedule.beneficiary = ctx.accounts.beneficiary.key(); // WHY: Record who receives vested tokens
        schedule.total_amount = total_amount; // WHY: Total tokens to vest
        schedule.cliff_duration = cliff_duration; // WHY: Waiting period before any unlock
        schedule.vesting_duration = vesting_duration; // WHY: Total vesting period
        schedule.claimed_amount = 0; // WHY: Start with zero claimed
        schedule.start_time = Clock::get()?.unix_timestamp; // WHY: Vesting starts now
        schedule.bump = ctx.bumps.schedule; // WHY: Store PDA bump
        schedule.revoked = false; // WHY: Not revoked initially
        msg!("Vesting schedule created for {}", schedule.beneficiary); // WHY: Log for indexing
        Ok(())
    }

    // WHY: User claims vested tokens based on elapsed time
    pub fn claim_vested(ctx: Context<ClaimVested>) -> Result<()> {
        let schedule = &mut ctx.accounts.schedule; // WHY: Mutable reference to update claimed amount
        require!(!schedule.revoked, VestingError::ScheduleRevoked); // WHY: Cannot claim revoked schedule

        let clock = Clock::get()?; // WHY: Get current time for vesting calculation
        let elapsed = clock.unix_timestamp - schedule.start_time; // WHY: Time since vesting started

        // WHY: Calculate vested amount based on elapsed time
        let vested = if elapsed < schedule.cliff_duration {
            0 // WHY: Before cliff, nothing is vested
        } else if elapsed >= schedule.vesting_duration {
            schedule.total_amount // WHY: After full duration, everything is vested
        } else {
            // WHY: Linear interpolation between cliff and full vesting
            let vesting_elapsed = elapsed - schedule.cliff_duration; // WHY: Time since cliff ended
            let vesting_total = schedule.vesting_duration - schedule.cliff_duration; // WHY: Total vesting period after cliff
            let vested_amount = (schedule.total_amount as u128)
                .checked_mul(vesting_elapsed as u128)
                .ok_or(VestingError::MathOverflow)?
                .checked_div(vesting_total as u128)
                .ok_or(VestingError::MathOverflow)? as u64; // WHY: Use u128 for intermediate to prevent overflow
            vested_amount
        };

        let claimable = vested.saturating_sub(schedule.claimed_amount); // WHY: Only claim what hasn't been claimed yet
        require!(claimable > 0, VestingError::NothingToClaim); // WHY: Revert if nothing to claim

        // WHY: Transfer vested tokens from vault to beneficiary via real CPI
        let cpi_accounts = Transfer {
            from: ctx.accounts.vault.to_account_info(), // WHY: Source is vesting vault
            to: ctx.accounts.beneficiary_token_account.to_account_info(), // WHY: Destination is beneficiary's token account
            authority: ctx.accounts.vault_authority.to_account_info(), // WHY: PDA authority signs
        };
        let project_key = ctx.accounts.project.key(); // WHY: Need project key for PDA seeds
        let beneficiary_key = schedule.beneficiary.key(); // WHY: Need beneficiary key for PDA seeds
        let seeds = &[b"vesting_vault", project_key.as_ref(), beneficiary_key.as_ref(), &[ctx.bumps.vault_authority]]; // WHY: PDA seeds for vault authority
        let signer = &[&seeds[..]]; // WHY: Signer seeds array
        let cpi_ctx = CpiContext::new_with_signer(
            ctx.accounts.token_program.to_account_info(),
            cpi_accounts,
            signer,
        ); // WHY: Build CPI context with PDA signer
        token::transfer(cpi_ctx, claimable)?; // WHY: Execute real SPL transfer

        schedule.claimed_amount = schedule.claimed_amount.checked_add(claimable).ok_or(VestingError::MathOverflow)?; // WHY: Update claimed amount safely
        msg!("Claimed {} tokens, total claimed: {}", claimable, schedule.claimed_amount); // WHY: Log for transparency
        Ok(())
    }

    // WHY: Admin can revoke schedule in case of breach or termination
    pub fn emergency_revoke(ctx: Context<EmergencyRevoke>) -> Result<()> {
        let schedule = &mut ctx.accounts.schedule; // WHY: Mutable reference to revoke
        require!(!schedule.revoked, VestingError::AlreadyRevoked); // WHY: Prevent double revoke
        schedule.revoked = true; // WHY: Mark as revoked
        msg!("Schedule revoked for {}", schedule.beneficiary); // WHY: Log for transparency
        Ok(())
    }
}

#[derive(Accounts)] // WHY: Anchor macro for account validation
pub struct CreateSchedule<'info> {
    #[account(init, payer = admin, space = 8 + VestingSchedule::SIZE, seeds = [b"schedule", project.key().as_ref(), beneficiary.key().as_ref()], bump)]
    pub schedule: Account<'info, VestingSchedule>, // WHY: PDA for vesting schedule
    #[account(mut)] // WHY: Admin pays for account creation
    pub admin: Signer<'info>, // WHY: Admin must sign
    /// CHECK: Project key used as seed // WHY: Raw pubkey used for PDA derivation
    pub project: AccountInfo<'info>,
    /// CHECK: Beneficiary pubkey used as seed // WHY: Raw pubkey used for PDA derivation
    pub beneficiary: AccountInfo<'info>,
    pub system_program: Program<'info, System>, // WHY: Required for account creation
}

#[derive(Accounts)]
pub struct ClaimVested<'info> {
    #[account(mut, constraint = schedule.beneficiary == beneficiary.key())] // WHY: Only beneficiary can claim
    pub schedule: Account<'info, VestingSchedule>,
    #[account(mut)] // WHY: Beneficiary signs and pays for tx
    pub beneficiary: Signer<'info>,
    #[account(mut, seeds = [b"vesting_vault", project.key().as_ref(), beneficiary.key().as_ref()], bump)] // WHY: Vault PDA
    pub vault: Account<'info, TokenAccount>,
    #[account(mut)] // WHY: Beneficiary receives tokens
    pub beneficiary_token_account: Account<'info, TokenAccount>,
    /// CHECK: PDA authority // WHY: PDA used for signing CPI
    #[account(seeds = [b"vesting_vault", project.key().as_ref(), beneficiary.key().as_ref()], bump)]
    pub vault_authority: AccountInfo<'info>,
    /// CHECK: Project key for seeds // WHY: Raw pubkey for PDA derivation
    pub project: AccountInfo<'info>,
    pub token_program: Program<'info, Token>, // WHY: SPL Token program for CPI
}

#[derive(Accounts)]
pub struct EmergencyRevoke<'info> {
    #[account(mut)] // WHY: Schedule state updated
    pub schedule: Account<'info, VestingSchedule>,
    pub admin: Signer<'info>, // WHY: Admin must sign
}

#[account] // WHY: Anchor macro for account serialization
pub struct VestingSchedule {
    pub beneficiary: Pubkey, // WHY: Who receives vested tokens
    pub total_amount: u64, // WHY: Total tokens to vest
    pub cliff_duration: i64, // WHY: Cliff period in seconds
    pub vesting_duration: i64, // WHY: Total vesting period in seconds
    pub claimed_amount: u64, // WHY: Tokens already claimed
    pub start_time: i64, // WHY: When vesting started
    pub bump: u8, // WHY: PDA bump
    pub revoked: bool, // WHY: Whether schedule is revoked
}

impl VestingSchedule {
    pub const SIZE: usize = 32 + 8 + 8 + 8 + 8 + 8 + 1 + 1; // WHY: Discriminator + all fields
}

#[error_code] // WHY: Anchor typed errors
pub enum VestingError {
    #[msg("Invalid duration: vesting must exceed cliff")]
    InvalidDuration, // WHY: Typed error for bad parameters
    #[msg("Schedule revoked")]
    ScheduleRevoked, // WHY: Typed error for revoked schedule
    #[msg("Math overflow")]
    MathOverflow, // WHY: Typed error for arithmetic overflow
    #[msg("Nothing to claim")]
    NothingToClaim, // WHY: Typed error for empty claim
    #[msg("Already revoked")]
    AlreadyRevoked, // WHY: Typed error for double revoke
}
