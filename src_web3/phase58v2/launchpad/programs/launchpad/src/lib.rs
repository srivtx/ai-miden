use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Mint, Transfer}; // WHY: Import SPL token primitives for real CPI transfers

declare_id!("LchPad111111111111111111111111111111111111"); // WHY: Program ID placeholder; Anchor replaces this on deploy

#[program] // WHY: Anchor macro that generates the program entrypoint and instruction router
pub mod launchpad {
    use super::*; // WHY: Bring parent module items into scope for instruction handlers

    // WHY: Initialize a new token sale project with tiered whitelist
    pub fn register_project(
        ctx: Context<RegisterProject>,
        token_mint: Pubkey,
        hard_cap: u64,
        soft_cap: u64,
        sale_start: i64,
        sale_end: i64,
    ) -> Result<()> {
        let project = &mut ctx.accounts.project; // WHY: Mutable reference to create the project account
        require!(sale_end > sale_start, LaunchpadError::InvalidTimeline); // WHY: Prevent backwards timelines
        require!(hard_cap > soft_cap, LaunchpadError::InvalidCap); // WHY: Hard cap must exceed soft cap
        project.admin = ctx.accounts.admin.key(); // WHY: Record admin for authorization checks
        project.token_mint = token_mint; // WHY: Record which token is being sold
        project.hard_cap = hard_cap; // WHY: Maximum raise limit
        project.soft_cap = soft_cap; // WHY: Minimum raise for success
        project.raised = 0; // WHY: Start with zero contributions
        project.sale_start = sale_start; // WHY: Record sale window start
        project.sale_end = sale_end; // WHY: Record sale window end
        project.finalized = false; // WHY: Not finalized until sale ends
        project.bump = ctx.bumps.project; // WHY: Store PDA bump for address regeneration
        msg!("Project registered: {}", project.key()); // WHY: Log for off-chain indexing
        Ok(()) // WHY: Anchor Result type for consistent error handling
    }

    // WHY: Define whitelist tiers with different prices and allocations
    pub fn set_tier(
        ctx: Context<SetTier>,
        tier_id: u8,
        price: u64,
        allocation: u64,
        whitelist: Option<Pubkey>,
    ) -> Result<()> {
        require!(
            ctx.accounts.admin.key() == ctx.accounts.project.admin,
            LaunchpadError::Unauthorized
        ); // WHY: Only project admin can configure tiers
        let tier = &mut ctx.accounts.tier; // WHY: Mutable reference to create tier account
        tier.project = ctx.accounts.project.key(); // WHY: Link tier to parent project
        tier.tier_id = tier_id; // WHY: Unique identifier within project
        tier.price = price; // WHY: Price per token in this tier
        tier.allocation = allocation; // WHY: Max tokens available in this tier
        tier.sold = 0; // WHY: Start with zero sales
        tier.whitelist = whitelist; // WHY: Optional whitelist mint for gated access
        tier.bump = ctx.bumps.tier; // WHY: Store PDA bump
        msg!("Tier {} set for project {}", tier_id, ctx.accounts.project.key()); // WHY: Log for transparency
        Ok(())
    }

    // WHY: User participates in sale by transferring payment tokens
    pub fn participate(
        ctx: Context<Participate>,
        amount: u64,
    ) -> Result<()> {
        let project = &ctx.accounts.project; // WHY: Read project config for validation
        let clock = Clock::get()?; // WHY: Get on-chain time for sale window check
        require!(
            clock.unix_timestamp >= project.sale_start && clock.unix_timestamp <= project.sale_end,
            LaunchpadError::SaleNotActive
        ); // WHY: Enforce sale window

        let tier = &mut ctx.accounts.tier; // WHY: Mutable reference to update tier sales
        require!(tier.sold + amount <= tier.allocation, LaunchpadError::TierAllocationExceeded); // WHY: Prevent overselling tier

        // WHY: Check whitelist if tier is gated
        if let Some(whitelist_mint) = tier.whitelist {
            require!(
                ctx.accounts.whitelist_token_account.mint == whitelist_mint,
                LaunchpadError::NotWhitelisted
            );
            require!(
                ctx.accounts.whitelist_token_account.amount > 0,
                LaunchpadError::NotWhitelisted
            ); // WHY: Must hold at least one whitelist token
        }

        let cost = amount.checked_mul(tier.price).ok_or(LaunchpadError::MathOverflow)?; // WHY: Calculate total cost with overflow protection

        // WHY: Transfer payment tokens from user to project vault via real CPI
        let cpi_accounts = Transfer {
            from: ctx.accounts.user_payment_account.to_account_info(), // WHY: Source of payment tokens
            to: ctx.accounts.project_vault.to_account_info(), // WHY: Destination is project vault PDA
            authority: ctx.accounts.user.to_account_info(), // WHY: User must sign for their token transfer
        };
        let cpi_ctx = CpiContext::new(ctx.accounts.token_program.to_account_info(), cpi_accounts); // WHY: Build CPI context with token program
        token::transfer(cpi_ctx, cost)?; // WHY: Execute real SPL transfer

        // WHY: Record participation
        let participation = &mut ctx.accounts.participation; // WHY: Mutable reference to create participation record
        participation.project = project.key(); // WHY: Link to project
        participation.user = ctx.accounts.user.key(); // WHY: Record participant
        participation.tier = tier.key(); // WHY: Record which tier
        participation.amount += amount; // WHY: Accumulate if user participates multiple times
        participation.cost += cost; // WHY: Track total cost
        participation.claimed = false; // WHY: Not yet claimed

        // WHY: Update project state
        let project_mut = &mut ctx.accounts.project; // WHY: Need mutable reference after immutable borrow ends
        project_mut.raised = project_mut.raised.checked_add(cost).ok_or(LaunchpadError::MathOverflow)?; // WHY: Track total raised safely
        tier.sold = tier.sold.checked_add(amount).ok_or(LaunchpadError::MathOverflow)?; // WHY: Track tier sales safely

        msg!("User {} bought {} tokens for {} lamports", ctx.accounts.user.key(), amount, cost); // WHY: Log for transparency
        Ok(())
    }

    // WHY: User claims purchased tokens after sale ends
    pub fn claim(ctx: Context<Claim>) -> Result<()> {
        let project = &ctx.accounts.project; // WHY: Read project state
        let clock = Clock::get()?; // WHY: Get current time
        require!(clock.unix_timestamp > project.sale_end, LaunchpadError::SaleNotEnded); // WHY: Cannot claim during sale
        require!(project.raised >= project.soft_cap, LaunchpadError::SoftCapNotMet); // WHY: Refund if soft cap missed

        let participation = &mut ctx.accounts.participation; // WHY: Mutable reference to mark claimed
        require!(!participation.claimed, LaunchpadError::AlreadyClaimed); // WHY: Prevent double claim

        // WHY: Transfer sale tokens from project token vault to user
        let cpi_accounts = Transfer {
            from: ctx.accounts.project_token_vault.to_account_info(), // WHY: Source is project's token vault
            to: ctx.accounts.user_token_account.to_account_info(), // WHY: Destination is user's token account
            authority: ctx.accounts.project_vault_authority.to_account_info(), // WHY: PDA authority signs
        };
        let seeds = &[b"vault", project.key().as_ref(), &[ctx.bumps.project_vault_authority]]; // WHY: PDA seeds for signing
        let signer = &[&seeds[..]]; // WHY: Signer seeds array for CPI
        let cpi_ctx = CpiContext::new_with_signer(
            ctx.accounts.token_program.to_account_info(),
            cpi_accounts,
            signer,
        ); // WHY: Build CPI context with PDA signer
        token::transfer(cpi_ctx, participation.amount)?; // WHY: Execute real SPL transfer of purchased tokens

        participation.claimed = true; // WHY: Mark as claimed
        msg!("User {} claimed {} tokens", ctx.accounts.user.key(), participation.amount); // WHY: Log for indexing
        Ok(())
    }

    // WHY: Refund if soft cap not met
    pub fn refund(ctx: Context<Refund>) -> Result<()> {
        let project = &ctx.accounts.project; // WHY: Read project state
        let clock = Clock::get()?; // WHY: Get current time
        require!(clock.unix_timestamp > project.sale_end, LaunchpadError::SaleNotEnded); // WHY: Must wait for sale end
        require!(project.raised < project.soft_cap, LaunchpadError::SoftCapMet); // WHY: Only refund if failed

        let participation = &mut ctx.accounts.participation; // WHY: Mutable reference
        require!(!participation.refunded, LaunchpadError::AlreadyRefunded); // WHY: Prevent double refund

        // WHY: Return payment tokens to user
        let cpi_accounts = Transfer {
            from: ctx.accounts.project_vault.to_account_info(), // WHY: Source is project payment vault
            to: ctx.accounts.user_payment_account.to_account_info(), // WHY: Destination is user's payment account
            authority: ctx.accounts.project_vault_authority.to_account_info(), // WHY: PDA authority signs
        };
        let seeds = &[b"vault", project.key().as_ref(), &[ctx.bumps.project_vault_authority]]; // WHY: PDA seeds
        let signer = &[&seeds[..]]; // WHY: Signer seeds
        let cpi_ctx = CpiContext::new_with_signer(
            ctx.accounts.token_program.to_account_info(),
            cpi_accounts,
            signer,
        ); // WHY: CPI with PDA signer
        token::transfer(cpi_ctx, participation.cost)?; // WHY: Return exact amount paid

        participation.refunded = true; // WHY: Mark as refunded
        msg!("User {} refunded {} lamports", ctx.accounts.user.key(), participation.cost); // WHY: Log for transparency
        Ok(())
    }

    // WHY: Admin withdraws raised funds after successful sale
    pub fn admin_withdraw(ctx: Context<AdminWithdraw>) -> Result<()> {
        let project = &ctx.accounts.project; // WHY: Read project state
        require!(project.raised >= project.soft_cap, LaunchpadError::SoftCapNotMet); // WHY: Only if successful

        let cpi_accounts = Transfer {
            from: ctx.accounts.project_vault.to_account_info(), // WHY: Source is project vault
            to: ctx.accounts.admin_payment_account.to_account_info(), // WHY: Destination is admin's account
            authority: ctx.accounts.project_vault_authority.to_account_info(), // WHY: PDA authority
        };
        let seeds = &[b"vault", project.key().as_ref(), &[ctx.bumps.project_vault_authority]]; // WHY: PDA seeds
        let signer = &[&seeds[..]]; // WHY: Signer seeds
        let cpi_ctx = CpiContext::new_with_signer(
            ctx.accounts.token_program.to_account_info(),
            cpi_accounts,
            signer,
        ); // WHY: CPI with PDA signer
        token::transfer(cpi_ctx, project.raised)?; // WHY: Transfer all raised funds

        msg!("Admin withdrew {} lamports", project.raised); // WHY: Log for transparency
        Ok(())
    }
}

#[derive(Accounts)] // WHY: Anchor macro that validates accounts and generates deserialization
pub struct RegisterProject<'info> {
    #[account(init, payer = admin, space = 8 + Project::SIZE, seeds = [b"project", admin.key().as_ref()], bump)]
    pub project: Account<'info, Project>, // WHY: PDA for project account, initialized here
    #[account(mut)] // WHY: Admin pays for account creation
    pub admin: Signer<'info>, // WHY: Must be a signer to authorize project creation
    pub system_program: Program<'info, System>, // WHY: Required for account creation
}

#[derive(Accounts)]
pub struct SetTier<'info> {
    #[account(mut, has_one = admin)] // WHY: Ensure project.admin matches the admin signer
    pub project: Account<'info, Project>,
    #[account(init, payer = admin, space = 8 + Tier::SIZE, seeds = [b"tier", project.key().as_ref(), &[tier_id]], bump)]
    pub tier: Account<'info, Tier>, // WHY: PDA for tier account
    #[account(mut)]
    pub admin: Signer<'info>,
    pub system_program: Program<'info, System>,
    /// CHECK: tier_id passed as instruction data // WHY: Anchor requires explicit check notes for unchecked accounts
    pub tier_id: u8,
}

#[derive(Accounts)]
pub struct Participate<'info> {
    #[account(mut)] // WHY: Project state updated (raised amount)
    pub project: Account<'info, Project>,
    #[account(mut)] // WHY: Tier state updated (sold amount)
    pub tier: Account<'info, Tier>,
    #[account(init_if_needed, payer = user, space = 8 + Participation::SIZE, seeds = [b"participation", project.key().as_ref(), user.key().as_ref()], bump)]
    pub participation: Account<'info, Participation>, // WHY: PDA for user participation record
    #[account(mut)] // WHY: User pays for account creation and signs token transfer
    pub user: Signer<'info>,
    #[account(mut, constraint = user_payment_account.owner == user.key())] // WHY: Ensure user owns payment account
    pub user_payment_account: Account<'info, TokenAccount>,
    #[account(mut, seeds = [b"vault", project.key().as_ref()], bump)] // WHY: Project vault PDA
    pub project_vault: Account<'info, TokenAccount>,
    #[account(mut, constraint = whitelist_token_account.owner == user.key())] // WHY: Optional whitelist check
    pub whitelist_token_account: Account<'info, TokenAccount>,
    pub token_program: Program<'info, Token>, // WHY: SPL Token program for CPI
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Claim<'info> {
    #[account(mut)] // WHY: Participation marked as claimed
    pub project: Account<'info, Project>,
    #[account(mut, constraint = participation.user == user.key())] // WHY: Only owner can claim
    pub participation: Account<'info, Participation>,
    pub user: Signer<'info>, // WHY: User must sign
    #[account(mut, seeds = [b"vault", project.key().as_ref()], bump)] // WHY: Project vault PDA
    pub project_token_vault: Account<'info, TokenAccount>,
    #[account(mut)] // WHY: User receives tokens
    pub user_token_account: Account<'info, TokenAccount>,
    /// CHECK: PDA authority for vault // WHY: PDA does not implement AccountDeserialize
    #[account(seeds = [b"vault", project.key().as_ref()], bump)]
    pub project_vault_authority: AccountInfo<'info>,
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct Refund<'info> {
    #[account(mut)] // WHY: Project state checked
    pub project: Account<'info, Project>,
    #[account(mut, constraint = participation.user == user.key())] // WHY: Only owner can refund
    pub participation: Account<'info, Participation>,
    pub user: Signer<'info>,
    #[account(mut, seeds = [b"vault", project.key().as_ref()], bump)] // WHY: Project vault PDA
    pub project_vault: Account<'info, TokenAccount>,
    #[account(mut)] // WHY: User receives refund
    pub user_payment_account: Account<'info, TokenAccount>,
    /// CHECK: PDA authority // WHY: PDA used for signing CPI
    #[account(seeds = [b"vault", project.key().as_ref()], bump)]
    pub project_vault_authority: AccountInfo<'info>,
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct AdminWithdraw<'info> {
    #[account(has_one = admin)] // WHY: Only project admin can withdraw
    pub project: Account<'info, Project>,
    pub admin: Signer<'info>, // WHY: Admin must sign
    #[account(mut, seeds = [b"vault", project.key().as_ref()], bump)] // WHY: Project vault PDA
    pub project_vault: Account<'info, TokenAccount>,
    #[account(mut)] // WHY: Admin receives funds
    pub admin_payment_account: Account<'info, TokenAccount>,
    /// CHECK: PDA authority // WHY: PDA used for signing CPI
    #[account(seeds = [b"vault", project.key().as_ref()], bump)]
    pub project_vault_authority: AccountInfo<'info>,
    pub token_program: Program<'info, Token>,
}

#[account] // WHY: Anchor macro for account serialization
pub struct Project {
    pub admin: Pubkey, // WHY: Admin authority
    pub token_mint: Pubkey, // WHY: Token being sold
    pub hard_cap: u64, // WHY: Max raise
    pub soft_cap: u64, // WHY: Min raise for success
    pub raised: u64, // WHY: Current raise amount
    pub sale_start: i64, // WHY: Sale start timestamp
    pub sale_end: i64, // WHY: Sale end timestamp
    pub finalized: bool, // WHY: Whether sale is finalized
    pub bump: u8, // WHY: PDA bump
}

impl Project {
    pub const SIZE: usize = 32 + 32 + 8 + 8 + 8 + 8 + 8 + 1 + 1; // WHY: Discriminator + fields size
}

#[account]
pub struct Tier {
    pub project: Pubkey, // WHY: Parent project
    pub tier_id: u8, // WHY: Tier identifier
    pub price: u64, // WHY: Price per token
    pub allocation: u64, // WHY: Max tokens
    pub sold: u64, // WHY: Tokens sold
    pub whitelist: Option<Pubkey>, // WHY: Optional whitelist mint
    pub bump: u8, // WHY: PDA bump
}

impl Tier {
    pub const SIZE: usize = 32 + 1 + 8 + 8 + 8 + (1 + 32) + 1; // WHY: Discriminator + fields size
}

#[account]
pub struct Participation {
    pub project: Pubkey, // WHY: Parent project
    pub user: Pubkey, // WHY: Participant
    pub tier: Pubkey, // WHY: Tier purchased
    pub amount: u64, // WHY: Tokens purchased
    pub cost: u64, // WHY: Total cost paid
    pub claimed: bool, // WHY: Whether tokens claimed
    pub refunded: bool, // WHY: Whether refunded
}

impl Participation {
    pub const SIZE: usize = 32 + 32 + 32 + 8 + 8 + 1 + 1; // WHY: Discriminator + fields size
}

#[error_code] // WHY: Anchor macro for typed errors
pub enum LaunchpadError {
    #[msg("Invalid timeline: sale end must be after start")]
    InvalidTimeline, // WHY: Typed error for timeline validation
    #[msg("Invalid cap: hard cap must exceed soft cap")]
    InvalidCap, // WHY: Typed error for cap validation
    #[msg("Unauthorized")]
    Unauthorized, // WHY: Typed error for auth failures
    #[msg("Sale is not active")]
    SaleNotActive, // WHY: Typed error for out-of-window purchases
    #[msg("Tier allocation exceeded")]
    TierAllocationExceeded, // WHY: Typed error for overselling
    #[msg("Not whitelisted")]
    NotWhitelisted, // WHY: Typed error for whitelist failures
    #[msg("Math overflow")]
    MathOverflow, // WHY: Typed error for arithmetic overflow
    #[msg("Sale has not ended")]
    SaleNotEnded, // WHY: Typed error for premature claim/refund
    #[msg("Soft cap not met")]
    SoftCapNotMet, // WHY: Typed error when trying to claim with failed raise
    #[msg("Soft cap was met")]
    SoftCapMet, // WHY: Typed error when trying to refund successful raise
    #[msg("Already claimed")]
    AlreadyClaimed, // WHY: Typed error for double claim
    #[msg("Already refunded")]
    AlreadyRefunded, // WHY: Typed error for double refund
}
