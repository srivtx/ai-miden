use anchor_lang::prelude::*; // WHY: Import Anchor core macros and types for BPF program development.
use anchor_spl::token::{self, Token, TokenAccount, Transfer}; // WHY: Import SPL token CPI helpers for staking and slashing token transfers.

declare_id!("Guard11111111111111111111111111111111111111"); // WHY: Hardcode the program ID so Anchor resolves accounts and CPIs deterministically.

#[program] // WHY: Mark the following module as the Anchor program entry point containing all instruction handlers.
pub mod guardian { // WHY: Define the guardian program module to isolate registry logic and generated code.
    use super::*; // WHY: Bring parent scope items into the module so we can use Anchor structs without fully qualifying paths.

    pub fn initialize_registry( // WHY: Define the setup instruction that creates the guardian registry.
        ctx: Context<InitializeRegistry>, // WHY: Receive validated accounts for the registry initialization.
        max_guardians: u16, // WHY: Accept the maximum number of guardians to preallocate vector capacity.
    ) -> Result<()> { // WHY: Return Anchor's Result so validation errors halt execution atomically.
        let registry = &mut ctx.accounts.registry; // WHY: Mutably borrow the registry account to store persistent configuration.
        registry.authority = ctx.accounts.authority.key(); // WHY: Record the deployer as the authority who can slash guardians later.
        registry.guardians = Vec::with_capacity(max_guardians as usize); // WHY: Preallocate vector capacity to avoid reallocations and bound account size.
        registry.bump = ctx.bumps.registry; // WHY: Store the PDA bump so the registry can sign CPIs during slashing.
        Ok(()) // WHY: Return success so the transaction commits the initialized registry to the ledger.
    } // WHY: Close the initialize_registry instruction scope.

    pub fn register_guardian( // WHY: Define the instruction that adds a new guardian to the registry.
        ctx: Context<RegisterGuardian>, // WHY: Receive validated accounts for the registration.
        ed25519_pubkey: [u8; 32], // WHY: Accept the guardian's Ed25519 public key for bridge signature verification.
    ) -> Result<()> { // WHY: Return Anchor's Result so validation errors halt execution atomically.
        let registry = &mut ctx.accounts.registry; // WHY: Mutably borrow the registry to append a new guardian entry.
        require!(registry.guardians.len() < registry.guardians.capacity(), ErrorCode::RegistryFull); // WHY: Reject registration if the preallocated capacity is exhausted.
        let guardian = GuardianInfo { // WHY: Construct a new guardian metadata struct.
            solana_pubkey: ctx.accounts.guardian_authority.key(), // WHY: Record the guardian's Solana wallet for staking and slashing.
            ed25519_pubkey, // WHY: Store the provided Ed25519 public key for the bridge to verify signatures.
            stake_amount: 0, // WHY: Initialize stake to zero so the guardian must explicitly deposit collateral.
            is_active: true, // WHY: Mark the guardian as active immediately so they can begin signing after staking.
        }; // WHY: Close the GuardianInfo struct initialization.
        registry.guardians.push(guardian); // WHY: Append the new guardian to the registry vector.
        Ok(()) // WHY: Return success after the guardian is registered.
    } // WHY: Close the register_guardian instruction scope.

    pub fn stake( // WHY: Define the instruction that allows a guardian to deposit economic collateral.
        ctx: Context<Stake>, // WHY: Receive validated accounts for the staking operation.
        amount: u64, // WHY: Accept the quantity of tokens the guardian wants to lock.
        guardian_index: u16, // WHY: Accept the index of the guardian in the registry to credit the stake.
    ) -> Result<()> { // WHY: Return Anchor's Result so validation errors halt execution atomically.
        require!(guardian_index < ctx.accounts.registry.guardians.len() as u16, ErrorCode::InvalidIndex); // WHY: Reject if the index is out of bounds to prevent panics.
        let guardian = &mut ctx.accounts.registry.guardians[guardian_index as usize]; // WHY: Mutably borrow the specific guardian entry to update its stake.
        require!(guardian.solana_pubkey == ctx.accounts.staker.key(), ErrorCode::Unauthorized); // WHY: Enforce that only the guardian themselves can stake on their own record.
        let cpi_accounts = Transfer { // WHY: Build the SPL Transfer instruction accounts to move tokens into the stake vault.
            from: ctx.accounts.staker_token_account.to_account_info(), // WHY: Debit the guardian's token account.
            to: ctx.accounts.stake_vault.to_account_info(), // WHY: Credit the programmatic stake vault.
            authority: ctx.accounts.staker.to_account_info(), // WHY: The guardian must sign because they own the source tokens.
        }; // WHY: Close the Transfer struct initialization.
        let cpi_program = ctx.accounts.token_program.to_account_info(); // WHY: Reference the SPL Token program to execute the transfer CPI.
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts); // WHY: Wrap the program and accounts into a CPI context.
        token::transfer(cpi_ctx, amount)?; // WHY: Execute the CPI transfer, locking the guardian's collateral.
        guardian.stake_amount += amount; // WHY: Credit the guardian's on-chain stake record so the bridge recognizes their economic weight.
        Ok(()) // WHY: Return success after the stake is recorded.
    } // WHY: Close the stake instruction scope.

    pub fn slash( // WHY: Define the instruction that penalizes a malicious guardian by seizing their stake.
        ctx: Context<Slash>, // WHY: Receive validated accounts for the slashing operation.
        guardian_index: u16, // WHY: Accept the index of the guardian to be slashed.
        amount: u64, // WHY: Accept the quantity of tokens to seize from the guardian's stake.
    ) -> Result<()> { // WHY: Return Anchor's Result so validation errors halt execution atomically.
        require!(ctx.accounts.authority.key() == ctx.accounts.registry.authority, ErrorCode::Unauthorized); // WHY: Enforce that only the registry authority can trigger slashing.
        require!(guardian_index < ctx.accounts.registry.guardians.len() as u16, ErrorCode::InvalidIndex); // WHY: Reject if the index is out of bounds to prevent panics.
        let guardian = &mut ctx.accounts.registry.guardians[guardian_index as usize]; // WHY: Mutably borrow the specific guardian entry to deduct stake.
        let slash_amount = std::cmp::min(amount, guardian.stake_amount); // WHY: Cap the slash at the guardian's current stake to avoid underflow.
        guardian.stake_amount -= slash_amount; // WHY: Deduct the slashed amount from the guardian's recorded stake.
        if guardian.stake_amount == 0 { // WHY: Check if the guardian's stake has been fully depleted.
            guardian.is_active = false; // WHY: Deactivate the guardian so they can no longer sign bridge operations.
        } // WHY: Close the deactivation check.
        let bump = ctx.accounts.registry.bump; // WHY: Load the registry PDA bump to authorize the vault transfer via PDA signing.
        let seeds = &[b"guardian_registry".as_ref(), &[bump]]; // WHY: Construct the PDA seed array that matches the registry account derivation.
        let signer = &[&seeds[..]]; // WHY: Wrap the seeds into the signer format expected by Anchor's CPI with_signer helper.
        let cpi_accounts = Transfer { // WHY: Build the SPL Transfer instruction accounts to move slashed tokens out of the stake vault.
            from: ctx.accounts.stake_vault.to_account_info(), // WHY: Debit the stake vault holding the guardian's collateral.
            to: ctx.accounts.destination_token_account.to_account_info(), // WHY: Credit the destination account, which could be a treasury or burn address.
            authority: ctx.accounts.registry.to_account_info(), // WHY: The registry PDA is the stake vault authority, so it must sign.
        }; // WHY: Close the Transfer struct initialization.
        let cpi_program = ctx.accounts.token_program.to_account_info(); // WHY: Reference the SPL Token program to execute the transfer CPI.
        let cpi_ctx = CpiContext::new_with_signer(cpi_program, cpi_accounts, signer); // WHY: Create a CPI context that automatically appends the PDA signer seeds.
        token::transfer(cpi_ctx, slash_amount)?; // WHY: Execute the CPI transfer, completing the economic penalty.
        Ok(()) // WHY: Return success after the guardian is slashed and funds are moved.
    } // WHY: Close the slash instruction scope.
} // WHY: Close the guardian program module.

#[derive(Accounts)] // WHY: Tell Anchor to generate account validation code for the InitializeRegistry instruction.
pub struct InitializeRegistry<'info> { // WHY: Define the account constraints required to initialize the guardian registry.
    #[account(mut)] // WHY: Mark the authority as mutable because it pays for account creation rent.
    pub authority: Signer<'info>, // WHY: Require a signer who will become the registry authority.
    #[account( // WHY: Open the registry account definition with init and PDA constraints.
        init, // WHY: Create the registry account on the first call and fail if it already exists.
        payer = authority, // WHY: Charge rent lamports from the authority for the new account.
        space = 8 + GuardianRegistry::MAX_SIZE, // WHY: Allocate enough bytes for the account discriminator and maximum guardian entries.
        seeds = [b"guardian_registry"], // WHY: Derive the registry PDA from a static seed so it has a deterministic address.
        bump // WHY: Let Anchor find and store the canonical bump for this PDA.
    )] // WHY: Close the registry account attributes.
    pub registry: Account<'info, GuardianRegistry>, // WHY: Declare the typed registry account that persists guardian data.
    pub system_program: Program<'info, System>, // WHY: Reference the System program because init accounts require system-level allocation.
} // WHY: Close the InitializeRegistry accounts struct.

#[derive(Accounts)] // WHY: Tell Anchor to generate account validation code for the RegisterGuardian instruction.
pub struct RegisterGuardian<'info> { // WHY: Define the account constraints required to register a new guardian.
    #[account(mut)] // WHY: Mark the guardian authority as mutable in case future upgrades require account mutation.
    pub guardian_authority: Signer<'info>, // WHY: Require the guardian themselves to sign the registration.
    #[account(mut)] // WHY: Mark the registry as mutable because a new guardian entry will be appended.
    pub registry: Account<'info, GuardianRegistry>, // WHY: Access the registry to push the new guardian metadata.
} // WHY: Close the RegisterGuardian accounts struct.

#[derive(Accounts)] // WHY: Tell Anchor to generate account validation code for the Stake instruction.
pub struct Stake<'info> { // WHY: Define the account constraints required for a guardian to deposit stake.
    #[account(mut)] // WHY: Mark the staker as mutable because they pay for any potential account creation.
    pub staker: Signer<'info>, // WHY: Require the guardian to sign the token transfer.
    #[account(mut)] // WHY: Mark the registry as mutable because the guardian's stake amount will be updated.
    pub registry: Account<'info, GuardianRegistry>, // WHY: Access the registry to credit the guardian's stake.
    #[account(mut)] // WHY: Mark the staker token account as mutable because its balance will decrease.
    pub staker_token_account: Account<'info, TokenAccount>, // WHY: Declare the guardian's token account as the transfer source.
    #[account( // WHY: Open the stake_vault constraints.
        mut, // WHY: Mark the vault as mutable because its balance will increase.
        seeds = [b"stake_vault", registry.key().as_ref()], // WHY: Derive the stake vault PDA from a static seed plus the registry key for uniqueness.
        bump // WHY: Let Anchor validate the canonical bump for the stake vault PDA.
    )] // WHY: Close the stake_vault constraints.
    pub stake_vault: Account<'info, TokenAccount>, // WHY: Declare the programmatic vault that holds all guardian collateral.
    pub token_program: Program<'info, Token>, // WHY: Reference the SPL Token program for the transfer CPI.
} // WHY: Close the Stake accounts struct.

#[derive(Accounts)] // WHY: Tell Anchor to generate account validation code for the Slash instruction.
pub struct Slash<'info> { // WHY: Define the account constraints required to penalize a guardian.
    pub authority: Signer<'info>, // WHY: Require the registry authority to sign the slashing operation.
    #[account(mut)] // WHY: Mark the registry as mutable because the guardian's stake and active status will be updated.
    pub registry: Account<'info, GuardianRegistry>, // WHY: Access the registry to deduct the guardian's stake.
    #[account(mut)] // WHY: Mark the stake vault as mutable because its balance will decrease.
    pub stake_vault: Account<'info, TokenAccount>, // WHY: Declare the vault holding the slashed guardian's collateral.
    #[account(mut)] // WHY: Mark the destination account as mutable because its balance will increase.
    pub destination_token_account: Account<'info, TokenAccount>, // WHY: Declare the account that receives the slashed funds.
    pub token_program: Program<'info, Token>, // WHY: Reference the SPL Token program for the transfer CPI.
} // WHY: Close the Slash accounts struct.

#[account] // WHY: Mark this struct as an Anchor account so it can be deserialized from raw account data.
pub struct GuardianRegistry { // WHY: Define the persistent guardian registry stored in a single PDA.
    pub authority: Pubkey, // WHY: Store the registry authority who can trigger slashing.
    pub guardians: Vec<GuardianInfo>, // WHY: Store the list of guardians dynamically up to a fixed maximum capacity.
    pub bump: u8, // WHY: Store the PDA bump so the registry can sign CPIs during slashing.
} // WHY: Close the GuardianRegistry definition.

impl GuardianRegistry { // WHY: Open an implementation block for registry constants.
    pub const MAX_GUARDIANS: usize = 50; // WHY: Cap the guardian count at 50 to bound account size and loop gas.
    pub const MAX_SIZE: usize = 32 + 4 + (Self::MAX_GUARDIANS * GuardianInfo::SIZE) + 1; // WHY: Precompute the maximum account size for init space allocation.
} // WHY: Close the GuardianRegistry implementation.

#[derive(Clone, AnchorSerialize, AnchorDeserialize)] // WHY: Derive Borsh serialization traits so GuardianInfo can be stored inside a Vec in an Anchor account.
pub struct GuardianInfo { // WHY: Define a single guardian's metadata.
    pub solana_pubkey: Pubkey, // WHY: Store the guardian's Solana wallet for staking and slashing.
    pub ed25519_pubkey: [u8; 32], // WHY: Store the guardian's Ed25519 public key for bridge signature verification.
    pub stake_amount: u64, // WHY: Track how many tokens the guardian has locked as economic collateral.
    pub is_active: bool, // WHY: Flag whether the guardian is eligible to sign; false after slashing.
} // WHY: Close the GuardianInfo definition.

impl GuardianInfo { // WHY: Open an implementation block for guardian size constants.
    pub const SIZE: usize = 32 + 32 + 8 + 1; // WHY: Sum the byte sizes of all fields for precise account space calculation.
} // WHY: Close the GuardianInfo implementation.

#[error_code] // WHY: Tell Anchor to generate a typed error enum for instruction failures.
pub enum ErrorCode { // WHY: Define all revert reasons so clients can debug failed transactions.
    #[msg("Registry is full")] // WHY: Provide a human-readable revert message when guardian capacity is reached.
    RegistryFull, // WHY: Define the error variant for exhausted guardian capacity.
    #[msg("Invalid guardian index")] // WHY: Provide a human-readable revert message when an index is out of bounds.
    InvalidIndex, // WHY: Define the error variant for out-of-range guardian indices.
    #[msg("Unauthorized")] // WHY: Provide a human-readable revert message when the signer lacks permission.
    Unauthorized, // WHY: Define the error variant for permission violations.
} // WHY: Close the ErrorCode enum.
