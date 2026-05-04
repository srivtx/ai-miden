use anchor_lang::prelude::*; // WHY: Anchor framework simplifies account validation, serialization, and instruction dispatch.
use anchor_lang::solana_program::hash::hash; // WHY: We use Solana's hash function to create deterministic market resolution IDs.

// WHY: Declare the program ID so the runtime and clients know which program this code represents.
declare_id!("OracleProgram1111111111111111111111111111111");

// WHY: The main module contains all instructions, accounts, and errors for the oracle resolution program.
#[program]
pub mod oracle_resolution {
    use super::*; // WHY: Bring outer scope imports and types into the program module for instruction definitions.

    // WHY: This instruction initializes the global oracle config, storing the trusted authority and dispute parameters.
    pub fn initialize(
        ctx: Context<Initialize>,
        trusted_oracle: Pubkey, // WHY: The trusted oracle is the only pubkey allowed to submit resolutions; storing it prevents unauthorized claims.
        dispute_period_seconds: i64, // WHY: A configurable dispute window allows different markets to have different risk tolerances.
    ) -> Result<()> {
        let oracle_state = &mut ctx.accounts.oracle_state; // WHY: Mutably borrow the singleton oracle state account to set its fields.
        oracle_state.authority = ctx.accounts.authority.key(); // WHY: Record the deployer as the admin who can update trusted oracles later.
        oracle_state.trusted_oracle = trusted_oracle; // WHY: Persist the trusted oracle so future resolutions can validate the signer against it.
        oracle_state.dispute_period_seconds = dispute_period_seconds; // WHY: Store the timelock duration so the contract can enforce it without external input.
        oracle_state.bump = ctx.bumps.oracle_state; // WHY: Store the PDA bump so future instructions can re-derive the oracle state address.
        Ok(()) // WHY: Return success to commit the initialization.
    }

    // WHY: This instruction allows the authority to update the trusted oracle pubkey in case of key rotation or compromise.
    pub fn update_trusted_oracle(
        ctx: Context<UpdateTrustedOracle>,
        new_trusted_oracle: Pubkey, // WHY: The new pubkey that will be allowed to sign resolutions.
    ) -> Result<()> {
        let oracle_state = &mut ctx.accounts.oracle_state; // WHY: Mutably borrow to update the trusted oracle field.
        // WHY: Only the original authority can rotate the oracle; this prevents a compromised oracle from appointing itself permanently.
        require!(
            ctx.accounts.authority.key() == oracle_state.authority,
            OracleError::Unauthorized
        );
        oracle_state.trusted_oracle = new_trusted_oracle; // WHY: Replace the old oracle with the new one atomically.
        Ok(()) // WHY: Return success to commit the update.
    }

    // WHY: This instruction accepts a signed resolution from the trusted oracle and begins the dispute period.
    pub fn resolve(
        ctx: Context<Resolve>,
        market_key: Pubkey, // WHY: The market being resolved so the oracle can record and log which market the attestation applies to.
        outcome: u8, // WHY: 0 = YES, 1 = NO; same encoding as the market program for consistency.
    ) -> Result<()> {
        let oracle_state = &ctx.accounts.oracle_state; // WHY: Immutably borrow to read trusted oracle and dispute settings.
        let resolution = &mut ctx.accounts.resolution; // WHY: Mutably borrow the resolution account to store the outcome and timestamps.

        // WHY: Verify that the transaction signer is the trusted oracle; this is the core security gate.
        require!(
            ctx.accounts.oracle_signer.key() == oracle_state.trusted_oracle,
            OracleError::InvalidOracleSigner
        );

        // WHY: Prevent re-resolution of the same market; once a resolution exists, it must go through dispute or finalization.
        require!(
            resolution.state == ResolutionState::None,
            OracleError::AlreadyResolved
        );

        // WHY: Record the market key so the resolution account is self-describing and auditable.
        resolution.market = market_key;
        // WHY: Record the reported outcome so the market program and clients can read it.
        resolution.outcome = outcome;
        // WHY: Record the current timestamp so the dispute window has a fixed starting point.
        resolution.resolved_at = Clock::get()?.unix_timestamp;
        // WHY: Compute the finalization timestamp by adding the configured dispute period.
        resolution.finalizes_at = resolution.resolved_at
            .checked_add(oracle_state.dispute_period_seconds)
            .unwrap();
        // WHY: Set the resolution state to Resolving so disputes can be filed during the window.
        resolution.state = ResolutionState::Resolving;
        // WHY: Store the bump so the resolution PDA can be re-derived by clients.
        resolution.bump = ctx.bumps.resolution;

        Ok(()) // WHY: Return success to commit the resolution and start the dispute clock.
    }

    // WHY: This instruction allows anyone to challenge a resolution by posting a bond, triggering a review.
    pub fn dispute(
        ctx: Context<Dispute>,
        market_key: Pubkey, // WHY: The market being disputed so the contract can verify the correct resolution account.
    ) -> Result<()> {
        let resolution = &mut ctx.accounts.resolution; // WHY: Mutably borrow to transition state.
        let oracle_state = &ctx.accounts.oracle_state; // WHY: Immutably borrow to read dispute parameters.

        // WHY: Disputes are only allowed while the resolution is in the Resolving state.
        require!(
            resolution.state == ResolutionState::Resolving,
            OracleError::NotResolving
        );
        // WHY: Disputes are only allowed before the finalization timestamp expires.
        require!(
            Clock::get()?.unix_timestamp < resolution.finalizes_at,
            OracleError::DisputeWindowClosed
        );
        // WHY: Verify that the resolution being disputed matches the market key provided by the caller.
        require!(
            resolution.market == market_key,
            OracleError::MarketMismatch
        );

        // WHY: Transfer the dispute bond from the disputer to the resolution account so there is economic skin-in-the-game.
        let bond = 1_000_000_000u64; // WHY: A fixed 1 SOL bond discourages frivolous disputes; this could be parameterized in a production system.
        let ix = anchor_lang::solana_program::system_instruction::transfer(
            &ctx.accounts.disputer.key(), // WHY: Debit the disputer's lamport balance.
            &resolution.key(), // WHY: Credit the resolution account so the bond is held in escrow.
            bond,
        );
        anchor_lang::solana_program::program::invoke(
            &ix,
            &[
                ctx.accounts.disputer.to_account_info(), // WHY: The disputer must sign the transfer.
                resolution.to_account_info(), // WHY: The resolution account receives the bond.
                ctx.accounts.system_program.to_account_info(), // WHY: The system program executes the lamport transfer.
            ],
        )?;

        // WHY: Transition the state to Disputed so the market program knows not to finalize yet.
        resolution.state = ResolutionState::Disputed;
        // WHY: Record the disputer so the bond can be returned or slashed later by governance.
        resolution.disputer = Some(ctx.accounts.disputer.key());

        Ok(()) // WHY: Return success to commit the dispute.
    }

    // WHY: This instruction finalizes a resolution after the dispute period expires and no successful dispute occurred.
    pub fn finalize(
        ctx: Context<Finalize>,
        market_key: Pubkey, // WHY: The market being finalized so the instruction targets the correct resolution account.
    ) -> Result<()> {
        let resolution = &mut ctx.accounts.resolution; // WHY: Mutably borrow to transition state.

        // WHY: Finalization is only allowed if the resolution is still in the Resolving state (not Disputed).
        require!(
            resolution.state == ResolutionState::Resolving,
            OracleError::NotResolving
        );
        // WHY: Finalization is only allowed after the dispute window has fully elapsed.
        require!(
            Clock::get()?.unix_timestamp >= resolution.finalizes_at,
            OracleError::DisputeWindowOpen
        );
        // WHY: Verify that the resolution account matches the market key to prevent targeting the wrong market.
        require!(
            resolution.market == market_key,
            OracleError::MarketMismatch
        );

        // WHY: Transition the state to Finalized so the market program can allow claims.
        resolution.state = ResolutionState::Finalized;

        Ok(()) // WHY: Return success to commit the finalization.
    }

    // WHY: This instruction allows the authority to override a disputed resolution after manual review, resetting or finalizing it.
    pub fn override_resolution(
        ctx: Context<OverrideResolution>,
        new_outcome: u8, // WHY: The corrected outcome after review.
    ) -> Result<()> {
        let oracle_state = &ctx.accounts.oracle_state; // WHY: Read the authority to enforce admin-only access.
        let resolution = &mut ctx.accounts.resolution; // WHY: Mutably borrow to update the outcome and state.

        // WHY: Only the original authority can override resolutions; this is a governance safety valve.
        require!(
            ctx.accounts.authority.key() == oracle_state.authority,
            OracleError::Unauthorized
        );
        // WHY: Overrides only make sense on disputed resolutions; resolved or finalized markets should not be changed arbitrarily.
        require!(
            resolution.state == ResolutionState::Disputed,
            OracleError::NotDisputed
        );

        // WHY: Update the outcome to the corrected value so the market program can settle correctly.
        resolution.outcome = new_outcome;
        // WHY: Transition to Finalized immediately because the authority acts as the arbiter of the dispute.
        resolution.state = ResolutionState::Finalized;

        Ok(()) // WHY: Return success to commit the override.
    }
}

// WHY: Define the account validation struct for initializing the oracle state.
#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(mut)]
    pub authority: Signer<'info>, // WHY: The deployer signs and pays for the oracle state account.

    #[account(
        init,
        payer = authority, // WHY: The authority pays rent for the oracle state account.
        space = 8 + OracleState::LEN, // WHY: 8 bytes for Anchor discriminator plus the serialized state.
        seeds = [b"oracle_state"], // WHY: Use a fixed seed so there is exactly one global oracle state per program deployment.
        bump // WHY: Anchor computes the canonical bump for the PDA.
    )]
    pub oracle_state: Account<'info, OracleState>, // WHY: This singleton account stores global oracle configuration.

    pub system_program: Program<'info, System>, // WHY: Required for account creation (init).
}

// WHY: Define the account validation struct for updating the trusted oracle.
#[derive(Accounts)]
pub struct UpdateTrustedOracle<'info> {
    pub authority: Signer<'info>, // WHY: Only the current authority can sign this instruction.

    #[account(mut, seeds = [b"oracle_state"], bump = oracle_state.bump)] // WHY: Re-derive the oracle state PDA to ensure it is the legitimate config account.
    pub oracle_state: Account<'info, OracleState>, // WHY: Mutably borrowed to update the trusted oracle field.
}

// WHY: Define the account validation struct for submitting a resolution.
#[derive(Accounts)]
#[instruction(market_key: Pubkey, outcome: u8)] // WHY: Include instruction args so the init seeds can reference the market key for unique PDA derivation.
pub struct Resolve<'info> {
    #[account(mut)]
    pub oracle_signer: Signer<'info>, // WHY: The trusted oracle must sign to prove the attestation is authentic.

    #[account(
        seeds = [b"oracle_state"], // WHY: Re-derive the global oracle state to read trusted_oracle and dispute settings.
        bump = oracle_state.bump
    )]
    pub oracle_state: Account<'info, OracleState>, // WHY: Read-only to validate the signer and read dispute parameters.

    #[account(
        init,
        payer = oracle_signer, // WHY: The oracle pays rent for the resolution account; this prevents spam by requiring economic cost.
        space = 8 + Resolution::LEN, // WHY: 8 bytes for discriminator plus serialized resolution data.
        seeds = [b"resolution", market_key.as_ref()], // WHY: Derive the resolution PDA from the market key so every market has exactly one resolution account.
        bump // WHY: Anchor computes the canonical bump.
    )]
    pub resolution: Account<'info, Resolution>, // WHY: This account stores the resolution outcome and dispute state for a specific market.

    pub system_program: Program<'info, System>, // WHY: Required for account creation (init).
}

// WHY: Define the account validation struct for disputing a resolution.
#[derive(Accounts)]
#[instruction(market_key: Pubkey)] // WHY: Include market_key so the instruction can verify it matches the resolution account.
pub struct Dispute<'info> {
    #[account(mut)]
    pub disputer: Signer<'info>, // WHY: The disputer signs and pays the bond.

    #[account(
        seeds = [b"oracle_state"], // WHY: Re-derive the oracle state to read dispute settings.
        bump = oracle_state.bump
    )]
    pub oracle_state: Account<'info, OracleState>, // WHY: Read-only to access dispute_period_seconds.

    #[account(
        mut,
        seeds = [b"resolution", market_key.as_ref()], // WHY: Re-derive the resolution PDA to ensure it matches the market being disputed.
        bump = resolution.bump
    )]
    pub resolution: Account<'info, Resolution>, // WHY: Mutably borrowed to transition state and record the disputer.

    pub system_program: Program<'info, System>, // WHY: Required for the lamport transfer of the dispute bond.
}

// WHY: Define the account validation struct for finalizing a resolution.
#[derive(Accounts)]
#[instruction(market_key: Pubkey)] // WHY: Include market_key to verify the resolution account.
pub struct Finalize<'info> {
    #[account(mut)]
    pub caller: Signer<'info>, // WHY: Anybody can call finalize after the dispute window; permissionless finalization ensures markets do not get stuck.

    #[account(
        mut,
        seeds = [b"resolution", market_key.as_ref()], // WHY: Re-derive the resolution PDA.
        bump = resolution.bump
    )]
    pub resolution: Account<'info, Resolution>, // WHY: Mutably borrowed to transition state to Finalized.
}

// WHY: Define the account validation struct for overriding a disputed resolution.
#[derive(Accounts)]
pub struct OverrideResolution<'info> {
    pub authority: Signer<'info>, // WHY: Only the admin authority can override.

    #[account(
        seeds = [b"oracle_state"], // WHY: Re-derive the oracle state to validate the authority.
        bump = oracle_state.bump
    )]
    pub oracle_state: Account<'info, OracleState>, // WHY: Read-only to check the stored authority.

    #[account(mut)] // WHY: Mutably borrowed to update the outcome and state.
    pub resolution: Account<'info, Resolution>, // WHY: The specific resolution being overridden.
}

// WHY: The OracleState account is a singleton storing global configuration for the oracle program.
#[account]
pub struct OracleState {
    pub authority: Pubkey, // WHY: The admin who can rotate trusted oracles and override disputes.
    pub trusted_oracle: Pubkey, // WHY: The only pubkey allowed to submit resolution attestations.
    pub dispute_period_seconds: i64, // WHY: How long participants have to challenge a resolution before it finalizes.
    pub bump: u8, // WHY: PDA bump for re-deriving the oracle state address.
}

// WHY: Implement a helper to compute the serialized size for rent calculation.
impl OracleState {
    pub const LEN: usize = 32 // authority
        + 32 // trusted_oracle
        + 8 // dispute_period_seconds
        + 1; // bump
}

// WHY: The Resolution account stores the outcome and dispute lifecycle for a single market.
#[account]
pub struct Resolution {
    pub market: Pubkey, // WHY: Identifies which market this resolution belongs to.
    pub outcome: u8, // WHY: The winning outcome index (0 = YES, 1 = NO).
    pub resolved_at: i64, // WHY: Unix timestamp when the oracle submitted the resolution.
    pub finalizes_at: i64, // WHY: Unix timestamp when the dispute window closes and finalization is allowed.
    pub state: ResolutionState, // WHY: Tracks whether the resolution is pending, disputed, or finalized.
    pub disputer: Option<Pubkey>, // WHY: Records who filed the dispute so the bond can be returned or slashed later.
    pub bump: u8, // WHY: PDA bump for re-deriving the resolution address.
}

// WHY: Implement a helper to compute the serialized size for rent calculation.
impl Resolution {
    pub const LEN: usize = 32 // market
        + 1 // outcome
        + 8 // resolved_at
        + 8 // finalizes_at
        + 1 // state
        + 1 + 32 // Option<Pubkey>: 1 byte discriminant + 32 bytes pubkey
        + 1; // bump
}

// WHY: Define the resolution state machine to enforce valid lifecycle transitions and prevent premature finalization.
#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Eq)]
pub enum ResolutionState {
    None,      // WHY: No resolution has been submitted yet; this is the default state for newly created resolution accounts.
    Resolving, // WHY: The oracle has submitted an outcome and the dispute window is open.
    Disputed,  // WHY: Someone has posted a bond to challenge the resolution; finalization is blocked pending review.
    Finalized, // WHY: The dispute window closed without a challenge, or an authority override settled the dispute; the market can now pay out.
}

// WHY: Define custom errors so clients can distinguish failure modes without parsing transaction logs.
#[error_code]
pub enum OracleError {
    #[msg("Unauthorized")]
    Unauthorized, // WHY: Prevents non-authorities from performing admin actions.
    #[msg("Invalid oracle signer")]
    InvalidOracleSigner, // WHY: Prevents unauthorized pubkeys from submitting resolutions.
    #[msg("Already resolved")]
    AlreadyResolved, // WHY: Prevents double-resolution of the same market.
    #[msg("Not resolving")]
    NotResolving, // WHY: Prevents disputing or finalizing a market that has no active resolution.
    #[msg("Dispute window closed")]
    DisputeWindowClosed, // WHY: Prevents late disputes that would delay finalization indefinitely.
    #[msg("Dispute window still open")]
    DisputeWindowOpen, // WHY: Prevents early finalization before participants have a chance to challenge.
    #[msg("Market mismatch")]
    MarketMismatch, // WHY: Prevents targeting the wrong resolution account.
    #[msg("Not disputed")]
    NotDisputed, // WHY: Prevents overriding resolutions that are not under active dispute.
}
