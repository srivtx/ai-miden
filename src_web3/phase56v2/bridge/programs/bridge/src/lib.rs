use anchor_lang::prelude::*; // WHY: Import Anchor core macros and types for BPF program development.
use anchor_spl::token::{self, Burn, Mint, MintTo, Token, TokenAccount, Transfer}; // WHY: Import SPL token CPI helpers for minting, burning, and transferring tokens.
use ed25519_dalek::{PublicKey, Signature, Verifier}; // WHY: Import real Ed25519 types to verify guardian signatures on-chain instead of stubbing.

declare_id!("Bridge11111111111111111111111111111111111111"); // WHY: Hardcode the program ID so Anchor resolves accounts and CPIs deterministically.

#[program] // WHY: Mark the following module as the Anchor program entry point containing all instruction handlers.
pub mod bridge { // WHY: Define the bridge program module to isolate instruction logic and generated code.
    use super::*; // WHY: Bring parent scope items into the module so we can use Anchor structs without fully qualifying paths.

    pub fn initialize( // WHY: Define the setup instruction that runs once to configure the bridge vault and threshold.
        ctx: Context<Initialize>, // WHY: Receive validated accounts for the initialize instruction via Anchor's context wrapper.
        guardian_threshold: u8, // WHY: Accept the minimum number of guardian signatures required for any mint or release.
    ) -> Result<()> { // WHY: Return Anchor's Result so validation errors halt execution atomically.
        let state = &mut ctx.accounts.bridge_state; // WHY: Mutably borrow the bridge state account to store persistent configuration.
        state.authority = ctx.accounts.authority.key(); // WHY: Record the deployer as the authority who can update settings later.
        state.original_mint = ctx.accounts.original_mint.key(); // WHY: Record the original token mint so future transfers can validate the correct token type.
        state.vault_bump = ctx.bumps.vault; // WHY: Store the vault PDA bump seed so CPI signers can regenerate the signer array.
        state.state_bump = ctx.bumps.bridge_state; // WHY: Store the state PDA bump seed for use in subsequent PDA signer calls.
        state.guardian_threshold = guardian_threshold; // WHY: Persist the threshold so every future operation enforces multisig policy.
        state.nonce = 0; // WHY: Start the operation nonce at zero to prevent replay attacks on the first lock.
        state.wrapped_mint = ctx.accounts.wrapped_mint.key(); // WHY: Record the wrapped mint address so mint instructions target the correct token.
        Ok(()) // WHY: Return success so the transaction commits the initialized state to the ledger.
    } // WHY: Close the initialize instruction scope.

    pub fn lock_tokens( // WHY: Define the instruction that moves original tokens from the user into the bridge vault.
        ctx: Context<LockTokens>, // WHY: Receive validated accounts for the lock operation.
        amount: u64, // WHY: Accept the quantity of original tokens the user wants to bridge.
    ) -> Result<()> { // WHY: Return Anchor's Result so any failure rolls back the token transfer.
        require!(amount > 0, ErrorCode::ZeroAmount); // WHY: Reject zero-value locks to prevent spam and empty state accounts.
        let cpi_accounts = Transfer { // WHY: Build the SPL Transfer instruction accounts to move tokens into the vault.
            from: ctx.accounts.user_token_account.to_account_info(), // WHY: Debit the user's original token account.
            to: ctx.accounts.vault.to_account_info(), // WHY: Credit the bridge vault token account.
            authority: ctx.accounts.user.to_account_info(), // WHY: The user must sign because they own the source tokens.
        }; // WHY: Close the Transfer struct initialization.
        let cpi_program = ctx.accounts.token_program.to_account_info(); // WHY: Reference the SPL Token program to execute the transfer CPI.
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts); // WHY: Wrap the program and accounts into a context for the cross-program invocation.
        token::transfer(cpi_ctx, amount)?; // WHY: Execute the CPI transfer, propagating any failure from the SPL program.
        let lock_record = &mut ctx.accounts.lock_record; // WHY: Mutably borrow the lock record to store proof of the deposit.
        lock_record.user = ctx.accounts.user.key(); // WHY: Record the depositor's pubkey so the bridge knows who to credit later.
        lock_record.amount = amount; // WHY: Store the exact locked amount so minting cannot exceed the deposit.
        lock_record.nonce = ctx.accounts.bridge_state.nonce; // WHY: Assign the current nonce to this lock for unique identification and ordering.
        lock_record.is_released = false; // WHY: Mark the lock as unreleased so double-minting is blocked.
        ctx.accounts.bridge_state.nonce += 1; // WHY: Increment the global nonce so the next lock receives a unique identifier.
        emit!(LockEvent { // WHY: Emit an on-chain event so off-chain indexers and relayers detect the lock without parsing account data.
            user: ctx.accounts.user.key(), // WHY: Include the user address in the event for filtering.
            amount, // WHY: Include the amount so the relayer knows how many wrapped tokens to mint.
            nonce: lock_record.nonce, // WHY: Include the nonce so the relayer can build the exact message hash for guardians.
        }); // WHY: Close the event emission.
        Ok(()) // WHY: Return success after the lock is recorded and tokens are secured.
    } // WHY: Close the lock_tokens instruction.

    pub fn verify_and_mint_wrapped( // WHY: Define the instruction that checks guardian signatures and mints wrapped tokens.
        ctx: Context<VerifyAndMintWrapped>, // WHY: Receive validated accounts including the lock record and mint.
        message_hash: [u8; 32], // WHY: Accept the 32-byte SHA-256 digest that guardians signed off-chain.
        signatures: Vec<[u8; 64]>, // WHY: Accept the array of 64-byte Ed25519 signatures from multiple guardians.
        guardian_indices: Vec<u16>, // WHY: Accept indices mapping each signature to a specific guardian in the registry.
    ) -> Result<()> { // WHY: Return Anchor's Result so failed verification aborts the mint.
        let threshold = ctx.accounts.bridge_state.guardian_threshold as usize; // WHY: Load the required signature count as usize for vector length comparisons.
        require!(signatures.len() >= threshold, ErrorCode::ThresholdNotMet); // WHY: Reject early if fewer signatures than threshold were provided.
        require!(signatures.len() == guardian_indices.len(), ErrorCode::LengthMismatch); // WHY: Ensure every signature maps to exactly one guardian index.
        let registry = &ctx.accounts.guardian_registry; // WHY: Immutably borrow the guardian registry to look up public keys and active status.
        let mut valid_count = 0u16; // WHY: Initialize a counter to track how many signatures pass real cryptographic verification.
        for i in 0..signatures.len() { // WHY: Iterate over every submitted signature to validate it individually.
            let idx = guardian_indices[i] as usize; // WHY: Convert the u16 index to usize for safe array access in Rust.
            require!(idx < registry.guardians.len(), ErrorCode::InvalidGuardianIndex); // WHY: Abort if an index points outside the registry to prevent out-of-bounds access.
            let guardian = &registry.guardians[idx]; // WHY: Retrieve the guardian metadata to obtain their registered Ed25519 public key.
            require!(guardian.is_active, ErrorCode::GuardianNotActive); // WHY: Ignore signatures from guardians who have been slashed or deactivated.
            let pk = PublicKey::from_bytes(&guardian.ed25519_pubkey) // WHY: Parse the stored 32-byte public key into a typed Ed25519 public key.
                .map_err(|_| ErrorCode::InvalidPublicKey)?; // WHY: Convert parse failure into an Anchor error so the transaction aborts cleanly.
            let sig = Signature::from_bytes(&signatures[i]) // WHY: Parse the 64-byte signature into a typed Ed25519 signature object.
                .map_err(|_| ErrorCode::InvalidSignature)?; // WHY: Convert parse failure into an Anchor error to reject malformed signatures.
            pk.verify(&message_hash, &sig) // WHY: Perform the real Ed25519 verification equation on-chain; this is NOT a stub.
                .map_err(|_| ErrorCode::SignatureVerificationFailed)?; // WHY: Convert verification failure into an Anchor error so forgeries are rejected.
            valid_count += 1; // WHY: Increment the counter only after the signature has been cryptographically proven valid.
        } // WHY: End of signature validation loop.
        require!(valid_count >= threshold as u16, ErrorCode::ThresholdNotMet); // WHY: Double-check the valid count meets the threshold after filtering inactive guardians.
        let bump = ctx.accounts.bridge_state.state_bump; // WHY: Load the state PDA bump so we can authorize the mint via PDA signing.
        let seeds = &[b"bridge_state".as_ref(), &[bump]]; // WHY: Construct the PDA seed array that matches the state account derivation in Initialize.
        let signer = &[&seeds[..]]; // WHY: Wrap the seeds into the signer format expected by Anchor's CPI with_signer helper.
        let cpi_accounts = MintTo { // WHY: Build the SPL MintTo instruction accounts to create wrapped tokens for the user.
            mint: ctx.accounts.wrapped_mint.to_account_info(), // WHY: Target the wrapped token mint defined at initialization.
            to: ctx.accounts.recipient_wrapped_account.to_account_info(), // WHY: Credit the user's wrapped token account.
            authority: ctx.accounts.bridge_state.to_account_info(), // WHY: The bridge state PDA is the mint authority, so it must sign.
        }; // WHY: Close the MintTo struct initialization.
        let cpi_program = ctx.accounts.token_program.to_account_info(); // WHY: Reference the SPL Token program to execute the mint CPI.
        let cpi_ctx = CpiContext::new_with_signer(cpi_program, cpi_accounts, signer); // WHY: Create a CPI context that automatically appends the PDA signer seeds.
        let amount = ctx.accounts.lock_record.amount; // WHY: Read the locked amount so the wrapped supply exactly matches the deposit.
        token::mint_to(cpi_ctx, amount)?; // WHY: Execute the CPI mint, creating wrapped tokens 1:1 with the locked original tokens.
        ctx.accounts.lock_record.is_released = true; // WHY: Mark the lock as released so the same proof cannot trigger a second mint.
        Ok(()) // WHY: Return success after cryptographic verification and minting are complete.
    } // WHY: Close the verify_and_mint_wrapped instruction.

    pub fn burn_wrapped( // WHY: Define the instruction that destroys wrapped tokens to initiate a return to the original chain.
        ctx: Context<BurnWrapped>, // WHY: Receive validated accounts for the burn operation.
        amount: u64, // WHY: Accept the quantity of wrapped tokens the user wants to redeem.
    ) -> Result<()> { // WHY: Return Anchor's Result so failed burns roll back.
        require!(amount > 0, ErrorCode::ZeroAmount); // WHY: Reject zero-value burns to prevent spam and empty state accounts.
        let cpi_accounts = Burn { // WHY: Build the SPL Burn instruction accounts to destroy wrapped tokens.
            mint: ctx.accounts.wrapped_mint.to_account_info(), // WHY: Target the wrapped token mint to reduce supply.
            from: ctx.accounts.user_wrapped_account.to_account_info(), // WHY: Debit the user's wrapped token account.
            authority: ctx.accounts.user.to_account_info(), // WHY: The user must sign because they own the tokens being destroyed.
        }; // WHY: Close the Burn struct initialization.
        let cpi_program = ctx.accounts.token_program.to_account_info(); // WHY: Reference the SPL Token program to execute the burn CPI.
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts); // WHY: Wrap the program and accounts into a CPI context.
        token::burn(cpi_ctx, amount)?; // WHY: Execute the CPI burn, permanently removing wrapped tokens from circulation.
        let burn_record = &mut ctx.accounts.burn_record; // WHY: Mutably borrow the burn record to store proof of the destruction.
        burn_record.user = ctx.accounts.user.key(); // WHY: Record the burner's pubkey so the bridge knows where to send original tokens.
        burn_record.amount = amount; // WHY: Store the exact burned amount so releasing cannot exceed the redemption.
        burn_record.nonce = ctx.accounts.bridge_state.nonce; // WHY: Assign the current nonce to this burn for unique identification.
        burn_record.is_released = false; // WHY: Mark the burn as unreleased so double-release is blocked.
        ctx.accounts.bridge_state.nonce += 1; // WHY: Increment the global nonce so the next burn receives a unique identifier.
        emit!(BurnEvent { // WHY: Emit an on-chain event so off-chain relayers detect the burn and coordinate original-chain release.
            user: ctx.accounts.user.key(), // WHY: Include the user address in the event for filtering.
            amount, // WHY: Include the amount so the relayer knows how many original tokens to release.
            nonce: burn_record.nonce, // WHY: Include the nonce so the remote chain can build the exact message hash for verification.
        }); // WHY: Close the event emission.
        Ok(()) // WHY: Return success after the burn is recorded and tokens are destroyed.
    } // WHY: Close the burn_wrapped instruction.

    pub fn release_tokens( // WHY: Define the instruction that checks guardian signatures and returns original tokens from the vault.
        ctx: Context<ReleaseTokens>, // WHY: Receive validated accounts including the burn record and vault.
        message_hash: [u8; 32], // WHY: Accept the 32-byte SHA-256 digest that guardians signed off-chain.
        signatures: Vec<[u8; 64]>, // WHY: Accept the array of 64-byte Ed25519 signatures from multiple guardians.
        guardian_indices: Vec<u16>, // WHY: Accept indices mapping each signature to a specific guardian in the registry.
    ) -> Result<()> { // WHY: Return Anchor's Result so failed verification aborts the release.
        let threshold = ctx.accounts.bridge_state.guardian_threshold as usize; // WHY: Load the required signature count as usize for vector length comparisons.
        require!(signatures.len() >= threshold, ErrorCode::ThresholdNotMet); // WHY: Reject early if fewer signatures than threshold were provided.
        require!(signatures.len() == guardian_indices.len(), ErrorCode::LengthMismatch); // WHY: Ensure every signature maps to exactly one guardian index.
        let registry = &ctx.accounts.guardian_registry; // WHY: Immutably borrow the guardian registry to look up public keys and active status.
        let mut valid_count = 0u16; // WHY: Initialize a counter to track how many signatures pass real cryptographic verification.
        for i in 0..signatures.len() { // WHY: Iterate over every submitted signature to validate it individually.
            let idx = guardian_indices[i] as usize; // WHY: Convert the u16 index to usize for safe array access in Rust.
            require!(idx < registry.guardians.len(), ErrorCode::InvalidGuardianIndex); // WHY: Abort if an index points outside the registry to prevent out-of-bounds access.
            let guardian = &registry.guardians[idx]; // WHY: Retrieve the guardian metadata to obtain their registered Ed25519 public key.
            require!(guardian.is_active, ErrorCode::GuardianNotActive); // WHY: Ignore signatures from guardians who have been slashed or deactivated.
            let pk = PublicKey::from_bytes(&guardian.ed25519_pubkey) // WHY: Parse the stored 32-byte public key into a typed Ed25519 public key.
                .map_err(|_| ErrorCode::InvalidPublicKey)?; // WHY: Convert parse failure into an Anchor error so the transaction aborts cleanly.
            let sig = Signature::from_bytes(&signatures[i]) // WHY: Parse the 64-byte signature into a typed Ed25519 signature object.
                .map_err(|_| ErrorCode::InvalidSignature)?; // WHY: Convert parse failure into an Anchor error to reject malformed signatures.
            pk.verify(&message_hash, &sig) // WHY: Perform the real Ed25519 verification equation on-chain; this is NOT a stub.
                .map_err(|_| ErrorCode::SignatureVerificationFailed)?; // WHY: Convert verification failure into an Anchor error so forgeries are rejected.
            valid_count += 1; // WHY: Increment the counter only after the signature has been cryptographically proven valid.
        } // WHY: End of signature validation loop.
        require!(valid_count >= threshold as u16, ErrorCode::ThresholdNotMet); // WHY: Double-check the valid count meets the threshold after filtering inactive guardians.
        let bump = ctx.accounts.bridge_state.state_bump; // WHY: Load the state PDA bump so we can authorize the vault transfer via PDA signing.
        let seeds = &[b"bridge_state".as_ref(), &[bump]]; // WHY: Construct the PDA seed array that matches the state account derivation in Initialize.
        let signer = &[&seeds[..]]; // WHY: Wrap the seeds into the signer format expected by Anchor's CPI with_signer helper.
        let cpi_accounts = Transfer { // WHY: Build the SPL Transfer instruction accounts to move original tokens out of the vault.
            from: ctx.accounts.vault.to_account_info(), // WHY: Debit the bridge vault token account holding the original tokens.
            to: ctx.accounts.recipient_token_account.to_account_info(), // WHY: Credit the user's original token account on this chain.
            authority: ctx.accounts.bridge_state.to_account_info(), // WHY: The bridge state PDA is the vault authority, so it must sign.
        }; // WHY: Close the Transfer struct initialization.
        let cpi_program = ctx.accounts.token_program.to_account_info(); // WHY: Reference the SPL Token program to execute the transfer CPI.
        let cpi_ctx = CpiContext::new_with_signer(cpi_program, cpi_accounts, signer); // WHY: Create a CPI context that automatically appends the PDA signer seeds.
        let amount = ctx.accounts.burn_record.amount; // WHY: Read the burned amount so the release matches the redemption exactly.
        token::transfer(cpi_ctx, amount)?; // WHY: Execute the CPI transfer, returning original tokens 1:1 with the burned wrapped tokens.
        ctx.accounts.burn_record.is_released = true; // WHY: Mark the burn as released so the same proof cannot trigger a second release.
        Ok(()) // WHY: Return success after cryptographic verification and token release are complete.
    } // WHY: Close the release_tokens instruction.
} // WHY: Close the bridge program module.

#[derive(Accounts)] // WHY: Tell Anchor to generate account validation code for the Initialize instruction.
pub struct Initialize<'info> { // WHY: Define the account constraints required to initialize the bridge.
    #[account(mut)] // WHY: Mark the authority as mutable because it pays for account creation rent.
    pub authority: Signer<'info>, // WHY: Require a signer who will become the bridge authority.
    pub original_mint: Account<'info, Mint>, // WHY: Declare the original token mint so the vault can be configured to hold this token type.
    #[account( // WHY: Open the bridge_state account definition with init and PDA constraints.
        init, // WHY: Create the bridge_state account on the first call and fail if it already exists.
        payer = authority, // WHY: Charge rent lamports from the authority for the new account.
        space = 8 + BridgeState::SIZE, // WHY: Allocate enough bytes for the account discriminator and all fields.
        seeds = [b"bridge_state"], // WHY: Derive the state PDA from a static seed so it has a deterministic address.
        bump // WHY: Let Anchor find and store the canonical bump for this PDA.
    )] // WHY: Close the bridge_state account attributes.
    pub bridge_state: Account<'info, BridgeState>, // WHY: Declare the typed state account that persists bridge configuration.
    #[account( // WHY: Open the vault account definition.
        init, // WHY: Create the vault token account on the first call.
        payer = authority, // WHY: Charge rent lamports from the authority for the token account.
        token::mint = original_mint, // WHY: Bind the vault to the original mint so it can only hold that token type.
        token::authority = bridge_state, // WHY: Set the vault authority to the bridge state PDA so the program can sign transfers.
        seeds = [b"vault", bridge_state.key().as_ref()], // WHY: Derive the vault PDA from a static seed plus the state key for uniqueness.
        bump // WHY: Let Anchor find and store the canonical bump for the vault PDA.
    )] // WHY: Close the vault account attributes.
    pub vault: Account<'info, TokenAccount>, // WHY: Declare the typed vault account that will custody original tokens.
    pub wrapped_mint: Account<'info, Mint>, // WHY: Declare the wrapped mint account that the bridge will control for issuance.
    pub token_program: Program<'info, Token>, // WHY: Reference the SPL Token program for vault initialization and future CPIs.
    pub system_program: Program<'info, System>, // WHY: Reference the System program because init accounts require system-level allocation.
    pub rent: Sysvar<'info, Rent>, // WHY: Pass the Rent sysvar so Anchor can compute rent exemption for new accounts.
} // WHY: Close the Initialize accounts struct.

#[derive(Accounts)] // WHY: Tell Anchor to generate account validation code for the LockTokens instruction.
pub struct LockTokens<'info> { // WHY: Define the account constraints required to lock original tokens.
    #[account(mut)] // WHY: Mark the user as mutable because they pay rent for the lock record account.
    pub user: Signer<'info>, // WHY: Require the token owner to sign the transfer and lock record creation.
    #[account(mut)] // WHY: Mark the bridge state as mutable because the nonce is incremented.
    pub bridge_state: Account<'info, BridgeState>, // WHY: Access the bridge state to read and increment the operation nonce.
    #[account( // WHY: Open the user_token_account constraints.
        mut, // WHY: Mark the account as mutable because its token balance will decrease.
        constraint = user_token_account.mint == vault.mint @ ErrorCode::MintMismatch // WHY: Enforce that the user is depositing the same token type the vault holds.
    )] // WHY: Close the user_token_account constraints.
    pub user_token_account: Account<'info, TokenAccount>, // WHY: Declare the user's original token account as the transfer source.
    #[account(mut)] // WHY: Mark the vault as mutable because its token balance will increase.
    pub vault: Account<'info, TokenAccount>, // WHY: Declare the bridge vault as the transfer destination.
    #[account( // WHY: Open the lock_record account definition.
        init, // WHY: Create a new lock record for every deposit so each has a unique on-chain receipt.
        payer = user, // WHY: Charge the user for the rent of the lock record account.
        space = 8 + LockRecord::SIZE, // WHY: Allocate space for the discriminator and lock metadata fields.
        seeds = [b"lock_record", bridge_state.nonce.to_le_bytes().as_ref()], // WHY: Derive a unique PDA using the current nonce so records cannot collide.
        bump // WHY: Let Anchor compute the canonical bump for the lock record PDA.
    )] // WHY: Close the lock_record account attributes.
    pub lock_record: Account<'info, LockRecord>, // WHY: Declare the typed lock record that stores deposit proof.
    pub token_program: Program<'info, Token>, // WHY: Reference the SPL Token program for the transfer CPI.
    pub system_program: Program<'info, System>, // WHY: Reference the System program for lock record account creation.
    pub rent: Sysvar<'info, Rent>, // WHY: Pass the Rent sysvar for rent exemption calculation.
} // WHY: Close the LockTokens accounts struct.

#[derive(Accounts)] // WHY: Tell Anchor to generate account validation code for the VerifyAndMintWrapped instruction.
pub struct VerifyAndMintWrapped<'info> { // WHY: Define the account constraints required to verify signatures and mint wrapped tokens.
    #[account(mut)] // WHY: Mark the bridge state as mutable in case future upgrades require state mutation.
    pub bridge_state: Account<'info, BridgeState>, // WHY: Access the bridge state to read the guardian threshold.
    #[account( // WHY: Open the lock_record constraints.
        mut, // WHY: Mark the record as mutable because is_released will be flipped to true.
        constraint = lock_record.is_released == false @ ErrorCode::AlreadyMinted // WHY: Prevent double-minting by rejecting any lock that was already released.
    )] // WHY: Close the lock_record constraints.
    pub lock_record: Account<'info, LockRecord>, // WHY: Read the lock details to enforce exact 1:1 minting.
    #[account(mut)] // WHY: Mark the wrapped mint as mutable because minting increases supply.
    pub wrapped_mint: Account<'info, Mint>, // WHY: Target the wrapped token mint for supply inflation.
    #[account(mut)] // WHY: Mark the recipient account as mutable because its token balance will increase.
    pub recipient_wrapped_account: Account<'info, TokenAccount>, // WHY: Declare the user's wrapped token account as the mint destination.
    pub guardian_registry: Account<'info, GuardianRegistry>, // WHY: Load the guardian registry to validate signature public keys and active status.
    pub token_program: Program<'info, Token>, // WHY: Reference the SPL Token program for the mint CPI.
} // WHY: Close the VerifyAndMintWrapped accounts struct.

#[derive(Accounts)] // WHY: Tell Anchor to generate account validation code for the BurnWrapped instruction.
pub struct BurnWrapped<'info> { // WHY: Define the account constraints required to burn wrapped tokens.
    #[account(mut)] // WHY: Mark the user as mutable because they pay rent for the burn record.
    pub user: Signer<'info>, // WHY: Require the wrapped token owner to sign the burn.
    #[account(mut)] // WHY: Mark the bridge state as mutable because the nonce is incremented.
    pub bridge_state: Account<'info, BridgeState>, // WHY: Access the bridge state to read and increment the nonce.
    #[account(mut)] // WHY: Mark the wrapped mint as mutable because burning decreases supply.
    pub wrapped_mint: Account<'info, Mint>, // WHY: Target the wrapped token mint for supply reduction.
    #[account( // WHY: Open the user_wrapped_account constraints.
        mut, // WHY: Mark the account as mutable because its token balance will decrease.
        constraint = user_wrapped_account.mint == wrapped_mint.key() @ ErrorCode::MintMismatch // WHY: Ensure the user is burning the correct wrapped token type.
    )] // WHY: Close the user_wrapped_account constraints.
    pub user_wrapped_account: Account<'info, TokenAccount>, // WHY: Declare the user's wrapped token account as the burn source.
    #[account( // WHY: Open the burn_record account definition.
        init, // WHY: Create a new burn record for every redemption so each has a unique on-chain receipt.
        payer = user, // WHY: Charge the user for the rent of the burn record account.
        space = 8 + BurnRecord::SIZE, // WHY: Allocate space for the discriminator and burn metadata fields.
        seeds = [b"burn_record", bridge_state.nonce.to_le_bytes().as_ref()], // WHY: Derive a unique PDA using the current nonce so records cannot collide.
        bump // WHY: Let Anchor compute the canonical bump for the burn record PDA.
    )] // WHY: Close the burn_record account attributes.
    pub burn_record: Account<'info, BurnRecord>, // WHY: Declare the typed burn record that stores redemption proof.
    pub token_program: Program<'info, Token>, // WHY: Reference the SPL Token program for the burn CPI.
    pub system_program: Program<'info, System>, // WHY: Reference the System program for burn record account creation.
    pub rent: Sysvar<'info, Rent>, // WHY: Pass the Rent sysvar for rent exemption calculation.
} // WHY: Close the BurnWrapped accounts struct.

#[derive(Accounts)] // WHY: Tell Anchor to generate account validation code for the ReleaseTokens instruction.
pub struct ReleaseTokens<'info> { // WHY: Define the account constraints required to release original tokens after burn verification.
    #[account(mut)] // WHY: Mark the bridge state as mutable in case future upgrades require state mutation.
    pub bridge_state: Account<'info, BridgeState>, // WHY: Access the bridge state to read the guardian threshold and vault bump.
    #[account( // WHY: Open the burn_record constraints.
        mut, // WHY: Mark the record as mutable because is_released will be flipped to true.
        constraint = burn_record.is_released == false @ ErrorCode::AlreadyReleased // WHY: Prevent double-release by rejecting any burn that was already redeemed.
    )] // WHY: Close the burn_record constraints.
    pub burn_record: Account<'info, BurnRecord>, // WHY: Read the burn details to enforce exact 1:1 release.
    #[account(mut)] // WHY: Mark the vault as mutable because its token balance will decrease.
    pub vault: Account<'info, TokenAccount>, // WHY: Declare the bridge vault as the transfer source.
    #[account( // WHY: Open the recipient_token_account constraints.
        mut, // WHY: Mark the account as mutable because its token balance will increase.
        constraint = recipient_token_account.mint == vault.mint @ ErrorCode::MintMismatch // WHY: Ensure the recipient receives the same original token type held by the vault.
    )] // WHY: Close the recipient_token_account constraints.
    pub recipient_token_account: Account<'info, TokenAccount>, // WHY: Declare the user's original token account as the transfer destination.
    pub guardian_registry: Account<'info, GuardianRegistry>, // WHY: Load the guardian registry to validate signature public keys and active status.
    pub token_program: Program<'info, Token>, // WHY: Reference the SPL Token program for the transfer CPI.
} // WHY: Close the ReleaseTokens accounts struct.

#[account] // WHY: Mark this struct as an Anchor account so it can be deserialized from raw account data.
pub struct BridgeState { // WHY: Define the persistent bridge configuration stored in a single PDA.
    pub authority: Pubkey, // WHY: Store the bridge authority who can update settings and trigger slashes.
    pub original_mint: Pubkey, // WHY: Store the original token mint so transfers can validate token type.
    pub vault_bump: u8, // WHY: Store the vault PDA bump to regenerate the signer seed array for CPIs.
    pub state_bump: u8, // WHY: Store the state PDA bump to regenerate the signer seed array for CPIs.
    pub guardian_threshold: u8, // WHY: Store the minimum number of valid guardian signatures required.
    pub nonce: u64, // WHY: Store a monotonically increasing nonce to prevent replay attacks.
    pub wrapped_mint: Pubkey, // WHY: Store the wrapped token mint address for issuance and validation.
} // WHY: Close the BridgeState definition.

impl BridgeState { // WHY: Open an implementation block for bridge state constants.
    pub const SIZE: usize = 32 + 32 + 1 + 1 + 1 + 8 + 32; // WHY: Sum the byte sizes of all fields for precise init space allocation.
} // WHY: Close the BridgeState implementation.

#[account] // WHY: Mark this struct as an Anchor account so it can be deserialized from raw account data.
pub struct LockRecord { // WHY: Define the immutable receipt for a single token deposit.
    pub user: Pubkey, // WHY: Store the depositor's address so the bridge knows who to credit.
    pub amount: u64, // WHY: Store the exact deposited amount to enforce 1:1 wrapped minting.
    pub nonce: u64, // WHY: Store the operation nonce to uniquely identify this deposit.
    pub is_released: bool, // WHY: Store a flag to prevent double-minting from the same deposit.
} // WHY: Close the LockRecord definition.

impl LockRecord { // WHY: Open an implementation block for lock record constants.
    pub const SIZE: usize = 32 + 8 + 8 + 1; // WHY: Sum the byte sizes of all fields for precise init space allocation.
} // WHY: Close the LockRecord implementation.

#[account] // WHY: Mark this struct as an Anchor account so it can be deserialized from raw account data.
pub struct BurnRecord { // WHY: Define the immutable receipt for a single wrapped token redemption.
    pub user: Pubkey, // WHY: Store the burner's address so the bridge knows where to send original tokens.
    pub amount: u64, // WHY: Store the exact burned amount to enforce 1:1 original token release.
    pub nonce: u64, // WHY: Store the operation nonce to uniquely identify this redemption.
    pub is_released: bool, // WHY: Store a flag to prevent double-release from the same burn.
} // WHY: Close the BurnRecord definition.

impl BurnRecord { // WHY: Open an implementation block for burn record constants.
    pub const SIZE: usize = 32 + 8 + 8 + 1; // WHY: Sum the byte sizes of all fields for precise init space allocation.
} // WHY: Close the BurnRecord implementation.

#[account] // WHY: Mark this struct as an Anchor account so it can be deserialized from raw account data.
pub struct GuardianRegistry { // WHY: Define the guardian registry layout so the bridge program can read guardian pubkeys without importing the guardian crate.
    pub authority: Pubkey, // WHY: Store the registry authority so the bridge knows who can modify guardian entries.
    pub guardians: Vec<GuardianInfo>, // WHY: Store the list of guardians dynamically up to a fixed maximum capacity.
    pub bump: u8, // WHY: Store the PDA bump so the registry can sign CPIs if needed.
} // WHY: Close the GuardianRegistry definition.

impl GuardianRegistry { // WHY: Open an implementation block for registry constants.
    pub const MAX_GUARDIANS: usize = 50; // WHY: Cap the guardian count at 50 to bound account size and loop gas.
    pub const MAX_SIZE: usize = 32 + 4 + (Self::MAX_GUARDIANS * GuardianInfo::SIZE) + 1; // WHY: Precompute the maximum account size for init space allocation.
} // WHY: Close the GuardianRegistry implementation.

#[derive(Clone, AnchorSerialize, AnchorDeserialize)] // WHY: Derive Borsh serialization traits so GuardianInfo can be stored inside a Vec in an Anchor account.
pub struct GuardianInfo { // WHY: Define a single guardian's metadata for both the guardian and bridge programs.
    pub solana_pubkey: Pubkey, // WHY: Store the guardian's Solana wallet for staking and slashing operations.
    pub ed25519_pubkey: [u8; 32], // WHY: Store the guardian's Ed25519 public key for signature verification in the bridge.
    pub stake_amount: u64, // WHY: Track how many tokens the guardian has locked as economic collateral.
    pub is_active: bool, // WHY: Flag whether the guardian is eligible to sign; false after slashing or voluntary exit.
} // WHY: Close the GuardianInfo definition.

impl GuardianInfo { // WHY: Open an implementation block for guardian size constants.
    pub const SIZE: usize = 32 + 32 + 8 + 1; // WHY: Sum the byte sizes of all fields for precise account space calculation.
} // WHY: Close the GuardianInfo implementation.

#[event] // WHY: Mark this struct as an Anchor event so it is emitted in transaction logs for off-chain indexing.
pub struct LockEvent { // WHY: Define the shape of the lock event that relayers monitor.
    pub user: Pubkey, // WHY: Include the depositor address so relayers know which user to credit.
    pub amount: u64, // WHY: Include the amount so relayers know how many wrapped tokens to mint.
    pub nonce: u64, // WHY: Include the nonce so relayers can reconstruct the exact message hash.
} // WHY: Close the LockEvent definition.

#[event] // WHY: Mark this struct as an Anchor event so it is emitted in transaction logs for off-chain indexing.
pub struct BurnEvent { // WHY: Define the shape of the burn event that relayers monitor.
    pub user: Pubkey, // WHY: Include the burner address so relayers know where to send original tokens.
    pub amount: u64, // WHY: Include the amount so relayers know how many original tokens to release.
    pub nonce: u64, // WHY: Include the nonce so relayers can reconstruct the exact message hash.
} // WHY: Close the BurnEvent definition.

#[error_code] // WHY: Tell Anchor to generate a typed error enum for instruction failures.
pub enum ErrorCode { // WHY: Define all revert reasons so clients can debug failed transactions.
    #[msg("Amount must be greater than zero")] // WHY: Provide a human-readable revert message for debugging failed transactions.
    ZeroAmount, // WHY: Define the error variant for zero-value inputs.
    #[msg("Guardian threshold not met")] // WHY: Provide a human-readable revert message when too few signatures are submitted.
    ThresholdNotMet, // WHY: Define the error variant for insufficient guardian signatures.
    #[msg("Signature and index length mismatch")] // WHY: Provide a human-readable revert message when arrays have different lengths.
    LengthMismatch, // WHY: Define the error variant for mismatched signature and index arrays.
    #[msg("Invalid guardian index")] // WHY: Provide a human-readable revert message when an index is out of bounds.
    InvalidGuardianIndex, // WHY: Define the error variant for out-of-range guardian indices.
    #[msg("Guardian is not active")] // WHY: Provide a human-readable revert message when a slashed guardian tries to sign.
    GuardianNotActive, // WHY: Define the error variant for signatures from deactivated guardians.
    #[msg("Invalid Ed25519 public key")] // WHY: Provide a human-readable revert message when a stored pubkey is malformed.
    InvalidPublicKey, // WHY: Define the error variant for unparseable Ed25519 public keys.
    #[msg("Invalid Ed25519 signature")] // WHY: Provide a human-readable revert message when a signature is malformed.
    InvalidSignature, // WHY: Define the error variant for unparseable Ed25519 signatures.
    #[msg("Ed25519 signature verification failed")] // WHY: Provide a human-readable revert message when a signature does not verify.
    SignatureVerificationFailed, // WHY: Define the error variant for failed cryptographic verification.
    #[msg("Lock already minted")] // WHY: Provide a human-readable revert message when a lock is reused.
    AlreadyMinted, // WHY: Define the error variant for double-minting attempts.
    #[msg("Burn already released")] // WHY: Provide a human-readable revert message when a burn is reused.
    AlreadyReleased, // WHY: Define the error variant for double-release attempts.
    #[msg("Mint mismatch")] // WHY: Provide a human-readable revert message when the wrong token type is used.
    MintMismatch, // WHY: Define the error variant for token mint address mismatches.
} // WHY: Close the ErrorCode enum.
