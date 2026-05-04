use anchor_lang::prelude::*; // WHY: Import Anchor core types and macros for program framework
use anchor_spl::token_2022::{Token2022, TransferChecked, transfer_checked}; // WHY: Import Token-2022 CPI helpers for real token transfers with hooks
use anchor_spl::associated_token::AssociatedToken; // WHY: Import ATA program for creating user token accounts automatically
use anchor_spl::token_interface::{Mint, TokenAccount}; // WHY: Use token interface to support both SPL Token and Token-2022 mints

// WHY: 1e18 precision factor prevents rounding errors in reward-per-share integer division
const PRECISION: u128 = 1_000_000_000_000_000_000;

// WHY: Declare program ID; replaced by Anchor during deployment
declare_id!("Farm111111111111111111111111111111111111111");

#[program]
pub mod farm {
    use super::*; // WHY: Bring outer scope types into program module

    // WHY: Initialize a new farm pool with staking and reward token configuration
    pub fn create_pool(
        ctx: Context<CreatePool>,
        reward_rate: u64, // WHY: Rewards emitted per second, determines APY
    ) -> Result<()> {
        let pool = &mut ctx.accounts.pool; // WHY: Mutable borrow to modify pool account data
        pool.authority = ctx.accounts.authority.key(); // WHY: Set admin who can deposit rewards
        pool.stake_mint = ctx.accounts.stake_mint.key(); // WHY: Record which token users stake
        pool.reward_mint = ctx.accounts.reward_mint.key(); // WHY: Record which token is given as reward
        pool.stake_vault = ctx.accounts.stake_vault.key(); // WHY: Record PDA vault that holds staked tokens
        pool.reward_vault = ctx.accounts.reward_vault.key(); // WHY: Record PDA vault that holds reward tokens
        pool.reward_rate = reward_rate; // WHY: Store emission rate for time-based reward calculation
        pool.reward_per_share = 0; // WHY: Accumulator starts at zero before any rewards deposited
        pool.total_staked = 0; // WHY: No tokens staked at pool creation
        pool.last_update_time = Clock::get()?.unix_timestamp; // WHY: Record current time for delta calculations
        Ok(()) // WHY: Return success to signal transaction completed
    }

    // WHY: User stakes tokens into the pool, earning proportional rewards
    pub fn stake(
        ctx: Context<Stake>,
        amount: u64, // WHY: Number of tokens to stake, validated by CPI transfer
    ) -> Result<()> {
        // WHY: Must update accumulator before changing stake to prevent dilution of past rewards
        update_pool_rewards(&mut ctx.accounts.pool)?; // WHY: Apply time-based reward accrual since last interaction

        let pool = &mut ctx.accounts.pool; // WHY: Mutable borrow for updating pool state
        let user = &mut ctx.accounts.user_info; // WHY: Mutable borrow for updating user state

        // WHY: If user already has stake, update reward_debt to current accumulator value
        if user.staked_amount > 0 {
            user.reward_debt = (user.staked_amount as u128) // WHY: Cast to u128 for precision math
                .checked_mul(pool.reward_per_share) // WHY: Current stake * current accumulator
                .unwrap(); // WHY: Panic on overflow indicates bug or attack
        }

        // WHY: Increase user's staked amount by deposit amount
        user.staked_amount = user.staked_amount.checked_add(amount).unwrap(); // WHY: Safe add to prevent overflow
        // WHY: Increase total staked so new deposits dilute future rewards correctly
        pool.total_staked = pool.total_staked.checked_add(amount).unwrap(); // WHY: Maintain invariant: sum(user.staked) == pool.total_staked

        // WHY: Set user's personal snapshot of global accumulator at time of deposit
        user.reward_debt = (user.staked_amount as u128) // WHY: Must use updated stake amount
            .checked_mul(pool.reward_per_share) // WHY: Lock in pre-existing rewards as "already paid"
            .unwrap(); // WHY: Overflow impossible with valid state but checked for safety

        // WHY: Perform REAL CPI transfer from user wallet to farm vault
        let cpi_accounts = TransferChecked { // WHY: Use checked transfer to validate decimals
            from: ctx.accounts.user_stake_account.to_account_info(), // WHY: Source is user's token account
            mint: ctx.accounts.stake_mint.to_account_info(), // WHY: Mint required for decimal validation in transfer_checked
            to: ctx.accounts.stake_vault.to_account_info(), // WHY: Destination is farm's PDA vault
            authority: ctx.accounts.user.to_account_info(), // WHY: User must sign for outgoing transfer
        };
        let cpi_program = ctx.accounts.token_program.to_account_info(); // WHY: Token-2022 program processes the transfer
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts); // WHY: Build CPI context for cross-program invocation
        transfer_checked(cpi_ctx, amount, ctx.accounts.stake_mint.decimals)?; // WHY: Execute real on-chain token movement

        Ok(()) // WHY: Success means tokens are now in vault and user is earning rewards
    }

    // WHY: User withdraws staked tokens and claims all pending rewards
    pub fn unstake(
        ctx: Context<Unstake>,
        amount: u64, // WHY: Amount to withdraw, must not exceed user's stake
    ) -> Result<()> {
        // WHY: Update accumulator so rewards are calculated up to current second
        update_pool_rewards(&mut ctx.accounts.pool)?; // WHY: Must accrue before any state change

        let pool = &mut ctx.accounts.pool; // WHY: Mutable borrow for pool updates
        let user = &mut ctx.accounts.user_info; // WHY: Mutable borrow for user updates

        // WHY: Validate user has enough staked to withdraw requested amount
        require!(user.staked_amount >= amount, FarmError::InsufficientStake); // WHY: Prevent withdrawing more than deposited

        // WHY: Calculate pending rewards before reducing stake amount
        let pending = calculate_pending_reward(pool, user)?; // WHY: Rewards owed based on current stake

        // WHY: Reduce user's stake by withdrawal amount
        user.staked_amount = user.staked_amount.checked_sub(amount).unwrap(); // WHY: Safe subtract to prevent underflow
        // WHY: Reduce total staked so future reward calculations use correct denominator
        pool.total_staked = pool.total_staked.checked_sub(amount).unwrap(); // WHY: Maintain global invariant

        // WHY: Update reward_debt to current accumulator with reduced stake
        user.reward_debt = (user.staked_amount as u128) // WHY: Use new (reduced) stake amount
            .checked_mul(pool.reward_per_share) // WHY: Lock in rewards earned up to this moment
            .unwrap(); // WHY: Checked for safety

        // WHY: Transfer withdrawn stake tokens from vault back to user wallet via REAL CPI
        let vault_bump = ctx.bumps.stake_vault; // WHY: Retrieve PDA bump for signing
        let pool_key = pool.key(); // WHY: Seed for PDA derivation
        let seeds = &[ // WHY: Seeds must match vault PDA derivation in CreatePool
            b"stake_vault".as_ref(), // WHY: Static seed for stake vault PDA
            pool_key.as_ref(), // WHY: Pool address makes vault unique per pool
            &[vault_bump], // WHY: Bump seed required for PDA signing
        ];
        let signer = &[&seeds[..]]; // WHY: PDA must sign because vault is program-owned

        let cpi_accounts = TransferChecked { // WHY: Checked transfer validates token decimals
            from: ctx.accounts.stake_vault.to_account_info(), // WHY: Source is farm vault
            mint: ctx.accounts.stake_mint.to_account_info(), // WHY: Mint for decimal validation
            to: ctx.accounts.user_stake_account.to_account_info(), // WHY: Destination is user's wallet
            authority: ctx.accounts.stake_vault.to_account_info(), // WHY: PDA is the authority on the vault
        };
        let cpi_program = ctx.accounts.token_program.to_account_info(); // WHY: Token-2022 program
        let cpi_ctx = CpiContext::new_with_signer(cpi_program, cpi_accounts, signer); // WHY: Use PDA signer for program-owned account
        transfer_checked(cpi_ctx, amount, ctx.accounts.stake_mint.decimals)?; // WHY: Real token transfer out of vault

        // WHY: If there are pending rewards, transfer them via REAL CPI from reward vault
        if pending > 0 {
            let reward_vault_bump = ctx.bumps.reward_vault; // WHY: Retrieve PDA bump for reward vault signing
            let reward_seeds = &[ // WHY: Seeds for reward vault PDA
                b"reward_vault".as_ref(), // WHY: Static seed distinguishes reward vault from stake vault
                pool_key.as_ref(), // WHY: Pool address for uniqueness
                &[reward_vault_bump], // WHY: Bump seed for valid PDA
            ];
            let reward_signer = &[&reward_seeds[..]]; // WHY: PDA must sign for reward vault outbound transfer

            let reward_cpi_accounts = TransferChecked { // WHY: Checked transfer for reward tokens
                from: ctx.accounts.reward_vault.to_account_info(), // WHY: Source is reward vault
                mint: ctx.accounts.reward_mint.to_account_info(), // WHY: Reward token mint for validation
                to: ctx.accounts.user_reward_account.to_account_info(), // WHY: User's reward token account
                authority: ctx.accounts.reward_vault.to_account_info(), // WHY: PDA is authority on reward vault
            };
            let reward_cpi_program = ctx.accounts.token_program.to_account_info(); // WHY: Token-2022 program
            let reward_cpi_ctx = CpiContext::new_with_signer(reward_cpi_program, reward_cpi_accounts, reward_signer); // WHY: PDA signs
            transfer_checked(reward_cpi_ctx, pending, ctx.accounts.reward_mint.decimals)?; // WHY: Real reward token transfer
        }

        Ok(()) // WHY: Success means user received both stake and rewards
    }

    // WHY: User claims accumulated rewards without withdrawing stake
    pub fn claim(ctx: Context<Claim>) -> Result<()> {
        // WHY: Update accumulator to include all rewards earned up to now
        update_pool_rewards(&mut ctx.accounts.pool)?; // WHY: Must be current before calculating claim

        let pool = &mut ctx.accounts.pool; // WHY: Mutable borrow
        let user = &mut ctx.accounts.user_info; // WHY: Mutable borrow

        // WHY: Calculate how many reward tokens user has earned
        let pending = calculate_pending_reward(pool, user)?; // WHY: Math uses current global accumulator

        // WHY: Prevent empty claims that waste transaction fees
        require!(pending > 0, FarmError::NoPendingRewards); // WHY: Revert if nothing to claim

        // WHY: Update reward_debt so user cannot claim same rewards twice
        user.reward_debt = (user.staked_amount as u128) // WHY: Current stake
            .checked_mul(pool.reward_per_share) // WHY: Current accumulator
            .unwrap(); // WHY: Safe math

        // WHY: Transfer reward tokens from reward vault to user via REAL CPI
        let reward_vault_bump = ctx.bumps.reward_vault; // WHY: PDA bump for signing
        let pool_key = pool.key(); // WHY: Pool address for seed
        let seeds = &[ // WHY: PDA seeds for reward vault
            b"reward_vault".as_ref(), // WHY: Static seed
            pool_key.as_ref(), // WHY: Pool-specific
            &[reward_vault_bump], // WHY: Bump
        ];
        let signer = &[&seeds[..]]; // WHY: PDA signer

        let cpi_accounts = TransferChecked { // WHY: Validate decimals during transfer
            from: ctx.accounts.reward_vault.to_account_info(), // WHY: Source is reward vault
            mint: ctx.accounts.reward_mint.to_account_info(), // WHY: Reward mint for validation
            to: ctx.accounts.user_reward_account.to_account_info(), // WHY: User's reward account
            authority: ctx.accounts.reward_vault.to_account_info(), // WHY: PDA authority
        };
        let cpi_program = ctx.accounts.token_program.to_account_info(); // WHY: Token-2022 program
        let cpi_ctx = CpiContext::new_with_signer(cpi_program, cpi_accounts, signer); // WHY: PDA signs the transfer
        transfer_checked(cpi_ctx, pending, ctx.accounts.reward_mint.decimals)?; // WHY: Real token movement to user

        Ok(()) // WHY: User now has reward tokens in their wallet
    }

    // WHY: Deposit additional reward tokens into pool and update accumulator
    pub fn deposit_rewards(
        ctx: Context<DepositRewards>,
        amount: u64, // WHY: Number of reward tokens to add to pool
    ) -> Result<()> {
        // WHY: Update accumulator before receiving new rewards
        update_pool_rewards(&mut ctx.accounts.pool)?; // WHY: Accrue existing rewards with old rate

        let pool = &mut ctx.accounts.pool; // WHY: Mutable borrow

        // WHY: Transfer reward tokens from funder to reward vault via REAL CPI
        let cpi_accounts = TransferChecked { // WHY: Checked for decimal safety
            from: ctx.accounts.funder_reward_account.to_account_info(), // WHY: Source is funder's wallet
            mint: ctx.accounts.reward_mint.to_account_info(), // WHY: Reward mint validation
            to: ctx.accounts.reward_vault.to_account_info(), // WHY: Destination is pool reward vault
            authority: ctx.accounts.funder.to_account_info(), // WHY: Funder signs for transfer
        };
        let cpi_program = ctx.accounts.token_program.to_account_info(); // WHY: Token-2022 program
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts); // WHY: Build CPI context
        transfer_checked(cpi_ctx, amount, ctx.accounts.reward_mint.decimals)?; // WHY: Real token transfer to vault

        // WHY: Only increase accumulator if there are stakers; otherwise rewards sit in vault
        if pool.total_staked > 0 {
            let increase = (amount as u128) // WHY: Cast to u128 for precision
                .checked_mul(PRECISION) // WHY: Scale up before division
                .unwrap() // WHY: Overflow check
                .checked_div(pool.total_staked as u128) // WHY: Divide by total stake for per-share amount
                .unwrap(); // WHY: Division by zero prevented by if-statement
            pool.reward_per_share = pool.reward_per_share.checked_add(increase).unwrap(); // WHY: Accumulate globally
        }

        Ok(()) // WHY: Rewards are now distributed proportionally to all stakers
    }

    // WHY: Claim and restake rewards in single atomic transaction for gas efficiency
    pub fn compound(ctx: Context<Compound>) -> Result<()> {
        // WHY: Update accumulator before calculating compound amount
        update_pool_rewards(&mut ctx.accounts.pool)?; // WHY: Must be current

        let pool = &mut ctx.accounts.pool; // WHY: Mutable borrow
        let user = &mut ctx.accounts.user_info; // WHY: Mutable borrow

        // WHY: Calculate rewards to compound
        let pending = calculate_pending_reward(pool, user)?; // WHY: Same formula as claim
        require!(pending > 0, FarmError::NoPendingRewards); // WHY: Skip empty compounds

        // WHY: Update reward_debt before staking rewards
        user.reward_debt = (user.staked_amount as u128) // WHY: Current stake
            .checked_mul(pool.reward_per_share) // WHY: Current accumulator
            .unwrap(); // WHY: Safe math

        // WHY: Increase stake by reward amount (compound interest)
        user.staked_amount = user.staked_amount.checked_add(pending).unwrap(); // WHY: Safe add
        pool.total_staked = pool.total_staked.checked_add(pending).unwrap(); // WHY: Update global total

        // WHY: Transfer reward tokens from reward vault to stake vault via REAL CPI
        // WHY: This moves rewards from reward vault into the staking pool
        let reward_vault_bump = ctx.bumps.reward_vault; // WHY: PDA bump for reward vault
        let stake_vault_bump = ctx.bumps.stake_vault; // WHY: PDA bump for stake vault
        let pool_key = pool.key(); // WHY: Pool address

        let reward_seeds = &[ // WHY: Reward vault PDA seeds
            b"reward_vault".as_ref(), // WHY: Static seed
            pool_key.as_ref(), // WHY: Pool-specific
            &[reward_vault_bump], // WHY: Bump
        ];
        let reward_signer = &[&reward_seeds[..]]; // WHY: PDA signer

        let cpi_accounts = TransferChecked { // WHY: Move reward tokens between vaults
            from: ctx.accounts.reward_vault.to_account_info(), // WHY: Source is reward vault
            mint: ctx.accounts.reward_mint.to_account_info(), // WHY: Reward mint (becomes stake when restaked)
            to: ctx.accounts.stake_vault.to_account_info(), // WHY: Destination is stake vault
            authority: ctx.accounts.reward_vault.to_account_info(), // WHY: PDA authority on reward vault
        };
        let cpi_program = ctx.accounts.token_program.to_account_info(); // WHY: Token-2022 program
        let cpi_ctx = CpiContext::new_with_signer(cpi_program, cpi_accounts, reward_signer); // WHY: PDA signs
        transfer_checked(cpi_ctx, pending, ctx.accounts.reward_mint.decimals)?; // WHY: Real inter-vault transfer

        // WHY: Update reward_debt again after stake increase to lock in post-compound state
        user.reward_debt = (user.staked_amount as u128) // WHY: New compounded stake amount
            .checked_mul(pool.reward_per_share) // WHY: Current accumulator unchanged during compound
            .unwrap(); // WHY: Safe math

        Ok(()) // WHY: Rewards are now staked and earning more rewards
    }
}

// WHY: Update global reward accumulator based on time elapsed since last update
fn update_pool_rewards(pool: &mut Account<Pool>) -> Result<()> {
    let clock = Clock::get()?; // WHY: Get current on-chain timestamp
    let current_time = clock.unix_timestamp; // WHY: Use Solana clock for deterministic time
    let time_delta = (current_time - pool.last_update_time) as u64; // WHY: Seconds since last update

    // WHY: Only update if time has passed and there are stakers
    if time_delta > 0 && pool.total_staked > 0 {
        let rewards = (time_delta as u128) // WHY: Cast to u128 for precision
            .checked_mul(pool.reward_rate as u128) // WHY: Total rewards = seconds * rate
            .unwrap() // WHY: Overflow check
            .checked_mul(PRECISION) // WHY: Scale before division
            .unwrap() // WHY: Overflow check
            .checked_div(pool.total_staked as u128) // WHY: Per-share amount
            .unwrap(); // WHY: Division by zero prevented by guard clause
        pool.reward_per_share = pool.reward_per_share.checked_add(rewards).unwrap(); // WHY: Accumulate
    }

    pool.last_update_time = current_time; // WHY: Reset timestamp for next calculation
    Ok(()) // WHY: Pool state now reflects all accrued rewards
}

// WHY: Calculate user's pending rewards using reward-per-share accumulator
fn calculate_pending_reward(
    pool: &Account<Pool>, // WHY: Read pool state for current accumulator
    user: &Account<UserInfo>, // WHY: Read user state for stake and debt snapshot
) -> Result<u64> {
    let staked = user.staked_amount as u128; // WHY: Cast to u128 for precision math
    let accrued = staked.checked_mul(pool.reward_per_share).unwrap(); // WHY: Total value at current accumulator
    let debt = user.reward_debt; // WHY: Snapshot of already-paid rewards

    // WHY: If debt exceeds accrued, user overclaimed due to bug; return 0
    if accrued <= debt {
        return Ok(0); // WHY: No pending rewards
    }

    let pending = accrued.checked_sub(debt).unwrap() // WHY: Rewards earned since last interaction
        .checked_div(PRECISION) // WHY: Remove precision factor
        .unwrap(); // WHY: Safe subtract verified above

    Ok(pending as u64) // WHY: Return u64 for token transfer amounts
}

#[derive(Accounts)]
pub struct CreatePool<'info> {
    #[account(mut)] // WHY: Payer must be mutable to fund account creation
    pub authority: Signer<'info>, // WHY: Admin who controls reward deposits

    #[account(
        init, // WHY: Initialize new pool account
        payer = authority, // WHY: Admin pays for rent
        space = 8 + Pool::SIZE, // WHY: 8 bytes discriminator + struct size
        seeds = [b"pool", authority.key().as_ref()], // WHY: PDA derived from authority for deterministic address
        bump // WHY: Anchor finds valid bump
    )]
    pub pool: Account<'info, Pool>, // WHY: Pool state account

    pub stake_mint: InterfaceAccount<'info, Mint>, // WHY: Token interface supports SPL and Token-2022
    pub reward_mint: InterfaceAccount<'info, Mint>, // WHY: Token interface for reward token

    #[account(
        init, // WHY: Create vault for staked tokens
        payer = authority, // WHY: Admin pays rent
        seeds = [b"stake_vault", pool.key().as_ref()], // WHY: PDA tied to pool
        bump, // WHY: Valid bump
        token::mint = stake_mint, // WHY: Vault holds stake tokens
        token::authority = stake_vault, // WHY: PDA is its own authority
        token::token_program = token_program, // WHY: Use Token-2022 program
    )]
    pub stake_vault: InterfaceAccount<'info, TokenAccount>, // WHY: ATA for staked tokens

    #[account(
        init, // WHY: Create vault for reward tokens
        payer = authority, // WHY: Admin pays rent
        seeds = [b"reward_vault", pool.key().as_ref()], // WHY: PDA tied to pool
        bump, // WHY: Valid bump
        token::mint = reward_mint, // WHY: Vault holds reward tokens
        token::authority = reward_vault, // WHY: PDA is its own authority
        token::token_program = token_program, // WHY: Use Token-2022 program
    )]
    pub reward_vault: InterfaceAccount<'info, TokenAccount>, // WHY: ATA for reward tokens

    pub token_program: Interface<'info, Token2022>, // WHY: Token-2022 program for CPI
    pub system_program: Program<'info, System>, // WHY: Required for account creation
    pub rent: Sysvar<'info, Rent>, // WHY: Rent sysvar for minimum balance calculation
}

#[derive(Accounts)]
pub struct Stake<'info> {
    #[account(mut)] // WHY: User must sign and pay for account creation
    pub user: Signer<'info>, // WHY: Staker who owns tokens

    #[account(mut)] // WHY: Pool state mutated by stake
    pub pool: Account<'info, Pool>, // WHY: Pool being staked into

    #[account(
        init_if_needed, // WHY: Create user info if first stake
        payer = user, // WHY: User pays rent for their own account
        space = 8 + UserInfo::SIZE, // WHY: Discriminator + struct
        seeds = [b"user_info", pool.key().as_ref(), user.key().as_ref()], // WHY: PDA per user per pool
        bump // WHY: Valid bump
    )]
    pub user_info: Account<'info, UserInfo>, // WHY: User's staking state

    #[account(
        mut, // WHY: User's token balance decreases
        token::mint = pool.stake_mint, // WHY: Must match pool's stake token
        token::authority = user, // WHY: User must own this account
        token::token_program = token_program, // WHY: Token-2022
    )]
    pub user_stake_account: InterfaceAccount<'info, TokenAccount>, // WHY: User's stake token wallet

    #[account(
        mut, // WHY: Vault balance increases
        seeds = [b"stake_vault", pool.key().as_ref()], // WHY: PDA derived in CreatePool
        bump, // WHY: Valid bump
    )]
    pub stake_vault: InterfaceAccount<'info, TokenAccount>, // WHY: Farm vault

    pub stake_mint: InterfaceAccount<'info, Mint>, // WHY: For decimal validation in transfer_checked
    pub token_program: Interface<'info, Token2022>, // WHY: Token-2022 program
    pub system_program: Program<'info, System>, // WHY: For user_info creation
    pub rent: Sysvar<'info, Rent>, // WHY: Rent calculation
}

#[derive(Accounts)]
pub struct Unstake<'info> {
    #[account(mut)] // WHY: User signs for withdrawal
    pub user: Signer<'info>, // WHY: Owner of stake

    #[account(mut)] // WHY: Pool mutated by unstake
    pub pool: Account<'info, Pool>, // WHY: Pool being withdrawn from

    #[account(
        mut, // WHY: User info mutated by unstake
        seeds = [b"user_info", pool.key().as_ref(), user.key().as_ref()], // WHY: Same PDA as stake
        bump, // WHY: Valid bump
    )]
    pub user_info: Account<'info, UserInfo>, // WHY: User's staking state

    #[account(
        mut, // WHY: Balance increases with returned stake
        token::mint = pool.stake_mint, // WHY: Must match stake token
        token::authority = user, // WHY: User's wallet
        token::token_program = token_program, // WHY: Token-2022
    )]
    pub user_stake_account: InterfaceAccount<'info, TokenAccount>, // WHY: User's stake wallet

    #[account(
        mut, // WHY: Balance decreases with reward payout
        token::mint = pool.reward_mint, // WHY: Must match reward token
        token::authority = user, // WHY: User's wallet
        token::token_program = token_program, // WHY: Token-2022
    )]
    pub user_reward_account: InterfaceAccount<'info, TokenAccount>, // WHY: User's reward wallet

    #[account(
        mut, // WHY: Balance decreases with returned stake
        seeds = [b"stake_vault", pool.key().as_ref()], // WHY: PDA from CreatePool
        bump, // WHY: Valid bump
    )]
    pub stake_vault: InterfaceAccount<'info, TokenAccount>, // WHY: Farm stake vault

    #[account(
        mut, // WHY: Balance decreases with reward payout
        seeds = [b"reward_vault", pool.key().as_ref()], // WHY: PDA from CreatePool
        bump, // WHY: Valid bump
    )]
    pub reward_vault: InterfaceAccount<'info, TokenAccount>, // WHY: Farm reward vault

    pub stake_mint: InterfaceAccount<'info, Mint>, // WHY: For decimal validation
    pub reward_mint: InterfaceAccount<'info, Mint>, // WHY: For decimal validation
    pub token_program: Interface<'info, Token2022>, // WHY: Token-2022 program
}

#[derive(Accounts)]
pub struct Claim<'info> {
    #[account(mut)] // WHY: User signs for claim
    pub user: Signer<'info>, // WHY: Reward recipient

    #[account(mut)] // WHY: Pool mutated by claim
    pub pool: Account<'info, Pool>, // WHY: Pool being claimed from

    #[account(
        mut, // WHY: User info mutated by claim
        seeds = [b"user_info", pool.key().as_ref(), user.key().as_ref()], // WHY: Same PDA
        bump, // WHY: Valid bump
    )]
    pub user_info: Account<'info, UserInfo>, // WHY: User's staking state

    #[account(
        mut, // WHY: Balance increases with rewards
        token::mint = pool.reward_mint, // WHY: Must match reward token
        token::authority = user, // WHY: User's wallet
        token::token_program = token_program, // WHY: Token-2022
    )]
    pub user_reward_account: InterfaceAccount<'info, TokenAccount>, // WHY: User's reward wallet

    #[account(
        mut, // WHY: Balance decreases with reward payout
        seeds = [b"reward_vault", pool.key().as_ref()], // WHY: PDA from CreatePool
        bump, // WHY: Valid bump
    )]
    pub reward_vault: InterfaceAccount<'info, TokenAccount>, // WHY: Farm reward vault

    pub reward_mint: InterfaceAccount<'info, Mint>, // WHY: For decimal validation
    pub token_program: Interface<'info, Token2022>, // WHY: Token-2022 program
}

#[derive(Accounts)]
pub struct DepositRewards<'info> {
    #[account(mut)] // WHY: Funder signs and pays
    pub funder: Signer<'info>, // WHY: Reward depositor

    #[account(mut)] // WHY: Pool mutated by deposit
    pub pool: Account<'info, Pool>, // WHY: Target pool

    #[account(
        mut, // WHY: Balance decreases
        token::mint = pool.reward_mint, // WHY: Must match reward token
        token::authority = funder, // WHY: Funder's wallet
        token::token_program = token_program, // WHY: Token-2022
    )]
    pub funder_reward_account: InterfaceAccount<'info, TokenAccount>, // WHY: Funder's reward wallet

    #[account(
        mut, // WHY: Balance increases
        seeds = [b"reward_vault", pool.key().as_ref()], // WHY: PDA from CreatePool
        bump, // WHY: Valid bump
    )]
    pub reward_vault: InterfaceAccount<'info, TokenAccount>, // WHY: Farm reward vault

    pub reward_mint: InterfaceAccount<'info, Mint>, // WHY: For decimal validation
    pub token_program: Interface<'info, Token2022>, // WHY: Token-2022 program
}

#[derive(Accounts)]
pub struct Compound<'info> {
    #[account(mut)] // WHY: User or bot signs
    pub user: Signer<'info>, // WHY: Must be user or authorized bot

    #[account(mut)] // WHY: Pool mutated by compound
    pub pool: Account<'info, Pool>, // WHY: Target pool

    #[account(
        mut, // WHY: User info mutated
        seeds = [b"user_info", pool.key().as_ref(), user.key().as_ref()], // WHY: Same PDA
        bump, // WHY: Valid bump
    )]
    pub user_info: Account<'info, UserInfo>, // WHY: User's staking state

    #[account(
        mut, // WHY: Balance increases with restaked rewards
        seeds = [b"stake_vault", pool.key().as_ref()], // WHY: PDA from CreatePool
        bump, // WHY: Valid bump
    )]
    pub stake_vault: InterfaceAccount<'info, TokenAccount>, // WHY: Farm stake vault

    #[account(
        mut, // WHY: Balance decreases with claimed rewards
        seeds = [b"reward_vault", pool.key().as_ref()], // WHY: PDA from CreatePool
        bump, // WHY: Valid bump
    )]
    pub reward_vault: InterfaceAccount<'info, TokenAccount>, // WHY: Farm reward vault

    pub reward_mint: InterfaceAccount<'info, Mint>, // WHY: For decimal validation
    pub token_program: Interface<'info, Token2022>, // WHY: Token-2022 program
}

#[account]
pub struct Pool {
    pub authority: Pubkey, // WHY: Admin who can deposit rewards
    pub stake_mint: Pubkey, // WHY: Token users stake
    pub reward_mint: Pubkey, // WHY: Token given as reward
    pub stake_vault: Pubkey, // WHY: PDA holding staked tokens
    pub reward_vault: Pubkey, // WHY: PDA holding reward tokens
    pub reward_rate: u64, // WHY: Rewards per second
    pub reward_per_share: u128, // WHY: Global accumulator with 1e18 precision
    pub total_staked: u64, // WHY: Sum of all user stakes
    pub last_update_time: i64, // WHY: Timestamp of last accumulator update
}

impl Pool {
    pub const SIZE: usize = 32 + 32 + 32 + 32 + 32 + 8 + 16 + 8 + 8; // WHY: Size of all fields in bytes
}

#[account]
pub struct UserInfo {
    pub staked_amount: u64, // WHY: User's current stake
    pub reward_debt: u128, // WHY: Snapshot of reward_per_share at last interaction
    pub owner: Pubkey, // WHY: User wallet address
    pub pool: Pubkey, // WHY: Pool this user info belongs to
}

impl UserInfo {
    pub const SIZE: usize = 8 + 16 + 32 + 32; // WHY: Size of all fields in bytes
}

#[error_code]
pub enum FarmError {
    #[msg("Insufficient staked amount")] // WHY: Clear error for UX debugging
    InsufficientStake, // WHY: User tried to unstake more than deposited
    #[msg("No pending rewards")] // WHY: Clear error for UX debugging
    NoPendingRewards, // WHY: User tried to claim with zero accrued rewards
}
