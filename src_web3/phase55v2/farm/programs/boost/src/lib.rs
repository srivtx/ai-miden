use anchor_lang::prelude::*; // WHY: Import Anchor core types and macros
use anchor_spl::token_2022::{Token2022, MintTo, mint_to}; // WHY: Token-2022 CPI for NFT minting
use anchor_spl::token_interface::{Mint, TokenAccount}; // WHY: Token interface for compatibility

// WHY: Declare program ID; replaced by Anchor during deployment
declare_id!("Boost11111111111111111111111111111111111111");

#[program]
pub mod boost {
    use super::*; // WHY: Bring outer scope into program module

    // WHY: Initialize the boost NFT mint with a fixed supply and multiplier metadata
    pub fn initialize_boost_mint(
        ctx: Context<InitializeBoostMint>,
        multiplier_bps: u16, // WHY: Basis points for reward multiplier (20000 = 2x)
    ) -> Result<()> {
        let boost_config = &mut ctx.accounts.boost_config; // WHY: Mutable borrow to store config
        boost_config.authority = ctx.accounts.authority.key(); // WHY: Only admin can mint boost NFTs
        boost_config.mint = ctx.accounts.boost_mint.key(); // WHY: Record which mint belongs to this boost program
        boost_config.multiplier_bps = multiplier_bps; // WHY: Store multiplier for verification during claims
        boost_config.total_minted = 0; // WHY: Track supply for potential mint limits
        Ok(()) // WHY: Config initialized successfully
    }

    // WHY: Mint a boost NFT to a user, increasing their reward rate
    pub fn mint_boost_nft(ctx: Context<MintBoostNft>) -> Result<()> {
        let boost_config = &mut ctx.accounts.boost_config; // WHY: Mutable borrow for supply tracking

        // WHY: Only the configured authority can mint boost NFTs
        require!(
            ctx.accounts.authority.key() == boost_config.authority,
            BoostError::Unauthorized // WHY: Prevent unauthorized minting that would break reward economics
        );

        // WHY: Increment total minted count for supply tracking
        boost_config.total_minted = boost_config.total_minted.checked_add(1).unwrap(); // WHY: Safe increment

        // WHY: Mint one NFT to user's associated token account via REAL CPI
        let cpi_accounts = MintTo { // WHY: SPL Token mint instruction
            mint: ctx.accounts.boost_mint.to_account_info(), // WHY: The boost NFT mint
            to: ctx.accounts.user_boost_account.to_account_info(), // WHY: User's ATA receiving the NFT
            authority: ctx.accounts.boost_mint.to_account_info(), // WHY: Mint authority is the mint itself (PDA)
        };
        let cpi_program = ctx.accounts.token_program.to_account_info(); // WHY: Token-2022 program
        let bump = ctx.bumps.boost_mint; // WHY: PDA bump for signing
        let seeds = &[ // WHY: PDA seeds for mint authority
            b"boost_mint".as_ref(), // WHY: Static seed
            boost_config.key().as_ref(), // WHY: Config-specific seed
            &[bump], // WHY: Bump seed
        ];
        let signer = &[&seeds[..]]; // WHY: PDA signer array
        let cpi_ctx = CpiContext::new_with_signer(cpi_program, cpi_accounts, signer); // WHY: PDA signs mint
        mint_to(cpi_ctx, 1)?; // WHY: Mint exactly 1 NFT (non-fungible)

        Ok(()) // WHY: User now holds a boost NFT
    }

    // WHY: Verify that a user holds a valid boost NFT and return multiplier
    pub fn verify_boost(ctx: Context<VerifyBoost>) -> Result<u16> {
        // WHY: Check that user actually owns tokens in this account
        require!(ctx.accounts.user_boost_account.amount > 0, BoostError::NoBoostNft); // WHY: Empty account means no boost

        // WHY: Verify the mint matches the authorized boost mint
        require!(
            ctx.accounts.user_boost_account.mint == ctx.accounts.boost_config.mint,
            BoostError::InvalidBoostMint // WHY: Prevent fake NFTs from other collections
        );

        // WHY: Return multiplier in basis points for farm program to apply
        Ok(ctx.accounts.boost_config.multiplier_bps) // WHY: 20000 bps = 2x multiplier
    }
}

#[derive(Accounts)]
pub struct InitializeBoostMint<'info> {
    #[account(mut)] // WHY: Payer must be mutable
    pub authority: Signer<'info>, // WHY: Admin who configures boost program

    #[account(
        init, // WHY: Create config account
        payer = authority, // WHY: Admin pays rent
        space = 8 + BoostConfig::SIZE, // WHY: Discriminator + struct size
        seeds = [b"boost_config", authority.key().as_ref()], // WHY: PDA derived from authority
        bump // WHY: Valid bump
    )]
    pub boost_config: Account<'info, BoostConfig>, // WHY: Stores boost program configuration

    #[account(
        init, // WHY: Create NFT mint
        payer = authority, // WHY: Admin pays rent
        seeds = [b"boost_mint", boost_config.key().as_ref()], // WHY: PDA tied to config
        bump, // WHY: Valid bump
        mint::decimals = 0, // WHY: NFT has 0 decimals (indivisible)
        mint::authority = boost_mint, // WHY: PDA is its own mint authority
        mint::token_program = token_program, // WHY: Use Token-2022 program
    )]
    pub boost_mint: InterfaceAccount<'info, Mint>, // WHY: The NFT mint

    pub token_program: Interface<'info, Token2022>, // WHY: Token-2022 program
    pub system_program: Program<'info, System>, // WHY: For account creation
    pub rent: Sysvar<'info, Rent>, // WHY: Rent calculation
}

#[derive(Accounts)]
pub struct MintBoostNft<'info> {
    #[account(mut)] // WHY: Authority signs
    pub authority: Signer<'info>, // WHY: Must match config authority

    #[account(
        mut, // WHY: Config mutated for supply tracking
        seeds = [b"boost_config", boost_config.authority.as_ref()], // WHY: PDA from initialization
        bump // WHY: Valid bump
    )]
    pub boost_config: Account<'info, BoostConfig>, // WHY: Boost configuration

    #[account(
        mut, // WHY: Mint supply increases
        seeds = [b"boost_mint", boost_config.key().as_ref()], // WHY: PDA from initialization
        bump // WHY: Valid bump
    )]
    pub boost_mint: InterfaceAccount<'info, Mint>, // WHY: NFT mint

    /// CHECK: User account does not need validation beyond being a valid pubkey // WHY: We only need their address for ATA
    pub user: AccountInfo<'info>, // WHY: Recipient of NFT

    #[account(
        init_if_needed, // WHY: Create ATA if user doesn't have one
        payer = authority, // WHY: Admin pays for user's ATA creation
        associated_token::mint = boost_mint, // WHY: ATA for boost mint
        associated_token::authority = user, // WHY: User owns the ATA
        associated_token::token_program = token_program, // WHY: Token-2022 program
    )]
    pub user_boost_account: InterfaceAccount<'info, TokenAccount>, // WHY: User's NFT wallet

    pub token_program: Interface<'info, Token2022>, // WHY: Token-2022 program
    pub associated_token_program: Program<'info, AssociatedToken>, // WHY: For ATA creation
    pub system_program: Program<'info, System>, // WHY: For account creation
    pub rent: Sysvar<'info, Rent>, // WHY: Rent calculation
}

#[derive(Accounts)]
pub struct VerifyBoost<'info> {
    pub boost_config: Account<'info, BoostConfig>, // WHY: Config for multiplier and mint verification

    #[account(
        token::mint = boost_config.mint, // WHY: Must be account for the authorized boost mint
        token::token_program = token_program, // WHY: Token-2022 program
    )]
    pub user_boost_account: InterfaceAccount<'info, TokenAccount>, // WHY: User's NFT balance

    pub token_program: Interface<'info, Token2022>, // WHY: Token-2022 program
}

#[account]
pub struct BoostConfig {
    pub authority: Pubkey, // WHY: Admin who can mint
    pub mint: Pubkey, // WHY: Authorized boost NFT mint
    pub multiplier_bps: u16, // WHY: Reward multiplier in basis points
    pub total_minted: u64, // WHY: Supply tracking
}

impl BoostConfig {
    pub const SIZE: usize = 32 + 32 + 2 + 8; // WHY: Bytes for all fields
}

#[error_code]
pub enum BoostError {
    #[msg("Unauthorized")] // WHY: Clear error for debugging
    Unauthorized, // WHY: Non-authority tried to mint
    #[msg("No boost NFT")] // WHY: Clear error for debugging
    NoBoostNft, // WHY: User has no boost NFT in their account
    #[msg("Invalid boost mint")] // WHY: Clear error for debugging
    InvalidBoostMint, // WHY: NFT from wrong collection
}
