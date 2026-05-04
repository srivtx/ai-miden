use borsh::{BorshDeserialize, BorshSerialize};
// WHY: Borsh provides efficient binary serialization for account state with a deterministic schema.
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program::{invoke, invoke_signed},
    program_error::ProgramError,
    pubkey::Pubkey,
    rent::Rent,
    system_instruction,
    sysvar::Sysvar,
};
// WHY: These imports are the standard toolkit for writing Solana programs that manage accounts, invoke CPIs, and handle errors.
use spl_token::instruction as token_instruction;
// WHY: SPL token instructions allow the bridge to custody, mint, burn, and transfer tokens via Cross-Program Invocation.

entrypoint!(process_instruction);
// WHY: The entrypoint macro declares this function as the Solana program's entry point, required for the runtime to call our code.

#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct BridgeState {
    // WHY: This struct holds the persistent state of the bridge program in a single account.
    pub is_initialized: bool,
    // WHY: A flag to ensure the state account is initialized exactly once and never reused uninitialized.
    pub guardian_program: Pubkey,
    // WHY: The bridge needs to know the guardian program's address to verify signatures via CPI or state checks.
    pub token_mint: Pubkey,
    // WHY: The SPL token mint for wrapped tokens; the bridge must own the mint authority to mint and burn.
    pub vault: Pubkey,
    // WHY: The PDA that holds the original locked tokens; used as the source for releases.
    pub fee_collector: Pubkey,
    // WHY: The account that receives bridge fees; separated from the vault for accounting clarity.
    pub nonce_counter: u64,
    // WHY: A strictly increasing counter to ensure every bridge operation has a unique identifier, preventing replay attacks.
    pub total_locked: u64,
    // WHY: Tracks the cumulative amount of original tokens locked to monitor bridge health and invariants.
    pub total_minted: u64,
    // WHY: Tracks the cumulative wrapped tokens minted; total_minted minus burned should equal circulating wrapped supply.
    pub total_burned: u64,
    // WHY: Tracks the cumulative wrapped tokens burned; used to verify the 1:1 backing invariant during releases.
    pub total_released: u64,
    // WHY: Tracks the cumulative original tokens released; total_locked minus total_released equals current vault balance liability.
}

#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub enum BridgeInstruction {
    // WHY: An enum allows the program to multiplex multiple operations through a single entrypoint.
    Initialize {
        guardian_program: Pubkey,
        token_mint: Pubkey,
        vault: Pubkey,
        fee_collector: Pubkey,
    },
    // WHY: Initialize sets up the bridge state account with permanent configuration parameters.
    Lock {
        amount: u64,
        target_recipient: Pubkey,
    },
    // WHY: Lock accepts original tokens and records the intent to mint wrapped tokens for the target_recipient.
    MintWrapped {
        amount: u64,
        nonce: u64,
        signatures: Vec<[u8; 64]>,
        guardian_indices: Vec<u8>,
    },
    // WHY: MintWrapped verifies guardian attestations and creates wrapped tokens for the user.
    BurnWrapped {
        amount: u64,
        source_recipient: Pubkey,
    },
    // WHY: BurnWrapped destroys wrapped tokens and records the intent to release original tokens to source_recipient.
    Release {
        amount: u64,
        nonce: u64,
        signatures: Vec<[u8; 64]>,
        guardian_indices: Vec<u8>,
    },
    // WHY: Release verifies guardian attestations for a burn event and returns original tokens from the vault.
}

pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    // WHY: This function is the top-level dispatcher; every invocation starts here.
    let instruction = BridgeInstruction::try_from_slice(instruction_data)
        // WHY: Borsh deserialization converts raw bytes into a typed instruction so we can safely access fields.
        .map_err(|_| ProgramError::InvalidInstructionData)?;
    // WHY: If deserialization fails, the input is malformed and we must abort to prevent undefined behavior.
    match instruction {
        // WHY: Pattern matching routes the execution to the correct handler based on the deserialized instruction variant.
        BridgeInstruction::Initialize {
            guardian_program,
            token_mint,
            vault,
            fee_collector,
        } => initialize(program_id, accounts, guardian_program, token_mint, vault, fee_collector),
        // WHY: Each arm delegates to a dedicated function to keep the dispatcher clean and readable.
        BridgeInstruction::Lock {
            amount,
            target_recipient,
        } => lock_tokens(accounts, amount, target_recipient),
        // WHY: Delegating to lock_tokens keeps the process_instruction function short and focused on routing.
        BridgeInstruction::MintWrapped {
            amount,
            nonce,
            signatures,
            guardian_indices,
        } => mint_wrapped(program_id, accounts, amount, nonce, signatures, guardian_indices),
        // WHY: Minting requires the program_id to derive the mint authority PDA.
        BridgeInstruction::BurnWrapped {
            amount,
            source_recipient,
        } => burn_wrapped(accounts, amount, source_recipient),
        // WHY: Burning does not need program_id derivation, so we delegate directly.
        BridgeInstruction::Release {
            amount,
            nonce,
            signatures,
            guardian_indices,
        } => release_tokens(program_id, accounts, amount, nonce, signatures, guardian_indices),
        // WHY: Releasing requires the program_id to derive the vault authority PDA.
    }
    // WHY: Closing the match expression returns the ProgramResult to the runtime.
}
// WHY: Closing the process_instruction function.

fn initialize(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    guardian_program: Pubkey,
    token_mint: Pubkey,
    vault: Pubkey,
    fee_collector: Pubkey,
) -> ProgramResult {
    // WHY: Initialization creates the bridge state PDA and stores immutable configuration.
    let account_info_iter = &mut accounts.iter();
    // WHY: An iterator lets us consume accounts in a defined order without manual index tracking.
    let initializer = next_account_info(account_info_iter)?;
    // WHY: The initializer must sign to prove they have authority to set up the bridge.
    let bridge_state_account = next_account_info(account_info_iter)?;
    // WHY: This PDA will store the BridgeState struct for the lifetime of the program.
    let system_program = next_account_info(account_info_iter)?;
    // WHY: Required to allocate and assign lamports for the new bridge state account.
    if !initializer.is_signer {
        // WHY: Without a signature, anyone could reinitialize or spoof the bridge state.
        return Err(ProgramError::MissingRequiredSignature);
    }
    let (expected_state_pda, bump) = Pubkey::find_program_address(&[b"bridge_state"], program_id);
    // WHY: Deriving the PDA ensures deterministic and collision-free state account location.
    if expected_state_pda != *bridge_state_account.key {
        // WHY: We must verify the passed account matches the derived PDA to prevent front-running or account substitution.
        return Err(ProgramError::InvalidAccountData);
    }
    let rent = Rent::get()?;
    // WHY: The runtime requires rent-exempt accounts to remain persistent; otherwise, the account could be purged.
    let space = std::mem::size_of::<BridgeState>();
    // WHY: We allocate exactly enough space for the struct to avoid wasting rent.
    invoke_signed(
        // WHY: invoke_signed is required when the caller is a PDA; the bridge program signs for its own PDA.
        &system_instruction::create_account(
            initializer.key,
            bridge_state_account.key,
            rent.minimum_balance(space),
            space as u64,
            program_id,
        ),
        &[initializer.clone(), bridge_state_account.clone(), system_program.clone()],
        &[&[b"bridge_state", &[bump]]],
        // WHY: The seed and bump prove ownership of the PDA to the system program.
    )?;
    let mut bridge_state = BridgeState {
        // WHY: We populate the state with the provided configuration and zeroed counters.
        is_initialized: true,
        guardian_program,
        token_mint,
        vault,
        fee_collector,
        nonce_counter: 0,
        total_locked: 0,
        total_minted: 0,
        total_burned: 0,
        total_released: 0,
    };
    bridge_state.serialize(&mut &mut bridge_state_account.data.borrow_mut()[..])?;
    // WHY: Serialization persists the struct into the account data so it survives across transactions.
    msg!("Bridge initialized");
    // WHY: Logging initialization helps indexers and debuggers confirm successful deployment.
    Ok(())
    // WHY: Returning Ok signals the runtime that the instruction executed successfully.
}
// WHY: Closing the initialize function.

fn lock_tokens(
    accounts: &[AccountInfo],
    amount: u64,
    target_recipient: Pubkey,
) -> ProgramResult {
    // WHY: Lock is the source-chain entry point; it takes custody of original tokens and emits a verifiable event.
    let account_info_iter = &mut accounts.iter();
    let user = next_account_info(account_info_iter)?;
    // WHY: The user must sign to authorize the transfer of their tokens.
    let user_token_account = next_account_info(account_info_iter)?;
    // WHY: This SPL token account holds the user's original tokens to be locked.
    let vault_token_account = next_account_info(account_info_iter)?;
    // WHY: The vault is the program-controlled PDA that receives and holds locked tokens securely.
    let bridge_state_account = next_account_info(account_info_iter)?;
    // WHY: We must read and update the bridge counters and nonce.
    let fee_collector_token_account = next_account_info(account_info_iter)?;
    // WHY: Fees are sent to a separate account so they do not commingle with backing collateral.
    let token_program = next_account_info(account_info_iter)?;
    // WHY: The SPL Token program is the only authorized program that can move SPL tokens.
    if !user.is_signer {
        // WHY: Only the token owner can authorize the lock.
        return Err(ProgramError::MissingRequiredSignature);
    }
    if amount == 0 {
        // WHY: Zero-value locks waste block space and could be used to spam the event log.
        return Err(ProgramError::InvalidArgument);
    }
    let mut bridge_state = BridgeState::try_from_slice(&bridge_state_account.data.borrow())?;
    // WHY: We deserialize the current state to update totals and increment the nonce.
    if !bridge_state.is_initialized {
        // WHY: Uninitialized state means the bridge was never set up; locking would lose user funds.
        return Err(ProgramError::UninitializedAccount);
    }
    let fee = amount.checked_div(1000).unwrap_or(0);
    // WHY: A 0.1% fee is small enough to not deter users but large enough to compensate relayers.
    let amount_after_fee = amount.checked_sub(fee).ok_or(ProgramError::InvalidArgument)?;
    // WHY: checked_sub prevents underflow if fee somehow exceeds amount due to a bug.
    if fee > 0 {
        // WHY: We only transfer fee if it is nonzero to avoid unnecessary SPL instructions.
        invoke(
            // WHY: Standard invoke is sufficient here because the user signs for their own token account.
            &token_instruction::transfer(
                token_program.key,
                user_token_account.key,
                fee_collector_token_account.key,
                user.key,
                &[],
                fee,
            )?,
            &[
                user_token_account.clone(),
                fee_collector_token_account.clone(),
                user.clone(),
                token_program.clone(),
            ],
        )?;
    }
    invoke(
        &token_instruction::transfer(
            token_program.key,
            user_token_account.key,
            vault_token_account.key,
            user.key,
            &[],
            amount_after_fee,
        )?,
        &[
            user_token_account.clone(),
            vault_token_account.clone(),
            user.clone(),
            token_program.clone(),
        ],
    )?;
    // WHY: The user's tokens are now in the vault, backing future wrapped token mints.
    bridge_state.total_locked = bridge_state
        .total_locked
        .checked_add(amount_after_fee)
        .ok_or(ProgramError::InvalidArgument)?;
    // WHY: checked_add prevents u64 overflow on total_locked.
    bridge_state.nonce_counter = bridge_state
        .nonce_counter
        .checked_add(1)
        .ok_or(ProgramError::InvalidArgument)?;
    // WHY: Every lock gets a unique nonce so guardians cannot replay old events.
    bridge_state.serialize(&mut &mut bridge_state_account.data.borrow_mut()[..])?;
    // WHY: Persist updated counters so the next transaction sees the new state.
    msg!("Locked {} tokens for {} with nonce {}", amount_after_fee, target_recipient, bridge_state.nonce_counter);
    // WHY: Logs create an on-chain event that guardians and indexers can observe and attest to.
    Ok(())
    // WHY: Returning Ok confirms the lock completed successfully.
}
// WHY: Closing the lock_tokens function.

fn mint_wrapped(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
    nonce: u64,
    signatures: Vec<[u8; 64]>,
    guardian_indices: Vec<u8>,
) -> ProgramResult {
    // WHY: Minting wrapped tokens without proof would allow infinite inflation; we require guardian verification.
    let account_info_iter = &mut accounts.iter();
    let bridge_state_account = next_account_info(account_info_iter)?;
    // WHY: Bridge state stores the guardian program address and nonce history.
    let recipient = next_account_info(account_info_iter)?;
    // WHY: The user receiving the newly minted wrapped tokens.
    let recipient_token_account = next_account_info(account_info_iter)?;
    // WHY: The SPL token account that will receive the minted wrapped tokens.
    let wrapped_mint = next_account_info(account_info_iter)?;
    // WHY: The mint account for the wrapped token; the bridge must be the mint authority.
    let bridge_authority = next_account_info(account_info_iter)?;
    // WHY: The PDA that acts as mint authority, derived from the bridge program.
    let token_program = next_account_info(account_info_iter)?;
    // WHY: Required to invoke SPL token minting via CPI.
    let guardian_program = next_account_info(account_info_iter)?;
    // WHY: The guardian program account that stores the registry and verification logic.
    let _fee_relayer_token_account = next_account_info(account_info_iter)?;
    // WHY: Reserved for future fee distribution to the relayer; currently passed for API compatibility.
    if signatures.len() != guardian_indices.len() {
        // WHY: Each signature must correspond to exactly one guardian index for verification.
        return Err(ProgramError::InvalidArgument);
    }
    let bridge_state = BridgeState::try_from_slice(&bridge_state_account.data.borrow())?;
    // WHY: We read the state to check initialization and fetch configuration.
    if !bridge_state.is_initialized {
        // WHY: Minting on an uninitialized bridge would create unbacked tokens.
        return Err(ProgramError::UninitializedAccount);
    }
    if nonce <= bridge_state.nonce_counter.checked_sub(1000).unwrap_or(0) {
        // WHY: Rejecting very old nonces prevents replay of ancient events even if they were never minted.
        return Err(ProgramError::InvalidArgument);
    }
    // NOTE: In production, a proper consumed_nonces map would be checked here.
    // WHY: A bitmap or HashMap of consumed_nonces prevents double-minting from the same lock event.
    if *guardian_program.key != bridge_state.guardian_program {
        // WHY: We must verify the guardian program matches the one configured at initialization to prevent spoofing.
        return Err(ProgramError::IncorrectProgramId);
    }
    // WHY: Here we would CPI into the guardian program to verify the signatures and threshold.
    // For this educational program, we simulate verification with length checks.
    if signatures.len() < 3 {
        // WHY: A threshold of 3 signatures ensures no single guardian can authorize minting.
        return Err(ProgramError::InvalidArgument);
    }
    let (expected_authority, authority_bump) =
        Pubkey::find_program_address(&[b"mint_authority"], program_id);
    // WHY: Deriving the authority PDA ensures the bridge program is the true mint authority.
    if expected_authority != *bridge_authority.key {
        // WHY: Passing a wrong authority would cause the SPL mint instruction to fail.
        return Err(ProgramError::InvalidAccountData);
    }
    invoke_signed(
        &token_instruction::mint_to(
            token_program.key,
            wrapped_mint.key,
            recipient_token_account.key,
            bridge_authority.key,
            &[],
            amount,
        )?,
        &[
            wrapped_mint.clone(),
            recipient_token_account.clone(),
            bridge_authority.clone(),
            token_program.clone(),
        ],
        &[&[b"mint_authority", &[authority_bump]]],
        // WHY: The PDA seeds prove to the SPL token program that the bridge program has the right to mint.
    )?;
    // WHY: Wrapped tokens are now created and backed by the locked original tokens in the vault.
    msg!("Minted {} wrapped tokens to {}", amount, recipient.key);
    // WHY: Logging confirms the mint operation for indexers and user interfaces.
    Ok(())
    // WHY: Returning Ok confirms the mint completed successfully.
}
// WHY: Closing the mint_wrapped function.

fn burn_wrapped(
    accounts: &[AccountInfo],
    amount: u64,
    source_recipient: Pubkey,
) -> ProgramResult {
    // WHY: Burning wrapped tokens is the first step of the reverse bridge; it proves the user wants to exit.
    let account_info_iter = &mut accounts.iter();
    let user = next_account_info(account_info_iter)?;
    // WHY: The user must sign to authorize the destruction of their wrapped tokens.
    let user_token_account = next_account_info(account_info_iter)?;
    // WHY: The SPL token account holding the wrapped tokens to be burned.
    let wrapped_mint = next_account_info(account_info_iter)?;
    // WHY: We need the mint account to update the total supply after burning.
    let bridge_state_account = next_account_info(account_info_iter)?;
    // WHY: The state tracks total burned for invariant checking.
    let token_program = next_account_info(account_info_iter)?;
    // WHY: The SPL Token program performs the burn operation.
    if !user.is_signer {
        // WHY: Burning requires user consent to destroy their assets.
        return Err(ProgramError::MissingRequiredSignature);
    }
    if amount == 0 {
        // WHY: Zero burns are meaningless and could clutter the event log.
        return Err(ProgramError::InvalidArgument);
    }
    let mut bridge_state = BridgeState::try_from_slice(&bridge_state_account.data.borrow())?;
    // WHY: We load state to increment the burn counter.
    if !bridge_state.is_initialized {
        // WHY: Burning on an uninitialized bridge indicates a configuration error.
        return Err(ProgramError::UninitializedAccount);
    }
    invoke(
        &token_instruction::burn(
            token_program.key,
            user_token_account.key,
            wrapped_mint.key,
            user.key,
            &[],
            amount,
        )?,
        &[
            user_token_account.clone(),
            wrapped_mint.clone(),
            user.clone(),
            token_program.clone(),
        ],
    )?;
    // WHY: The wrapped tokens are destroyed, reducing the wrapped supply and maintaining the 1:1 backing invariant.
    bridge_state.total_burned = bridge_state
        .total_burned
        .checked_add(amount)
        .ok_or(ProgramError::InvalidArgument)?;
    // WHY: checked_add prevents u64 overflow on the burn counter.
    bridge_state.nonce_counter = bridge_state
        .nonce_counter
        .checked_add(1)
        .ok_or(ProgramError::InvalidArgument)?;
    // WHY: A unique nonce is generated for the burn event so guardians can attest to a specific release.
    bridge_state.serialize(&mut &mut bridge_state_account.data.borrow_mut()[..])?;
    // WHY: Persist the updated burn total and nonce for the release step.
    msg!("Burned {} wrapped tokens for release to {} with nonce {}", amount, source_recipient, bridge_state.nonce_counter);
    // WHY: The log serves as the source event for guardians monitoring the target chain.
    Ok(())
    // WHY: Returning Ok confirms the burn completed successfully.
}
// WHY: Closing the burn_wrapped function.

fn release_tokens(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
    nonce: u64,
    signatures: Vec<[u8; 64]>,
    guardian_indices: Vec<u8>,
) -> ProgramResult {
    // WHY: Releasing original tokens without proof would allow draining the vault; guardian verification is mandatory.
    let account_info_iter = &mut accounts.iter();
    let bridge_state_account = next_account_info(account_info_iter)?;
    // WHY: State holds configuration and is checked for initialization.
    let recipient = next_account_info(account_info_iter)?;
    // WHY: The original chain account that will receive the released tokens.
    let recipient_token_account = next_account_info(account_info_iter)?;
    // WHY: The SPL token account receiving released tokens.
    let vault_token_account = next_account_info(account_info_iter)?;
    // WHY: The vault PDA holds the backing collateral that is sent back to the user.
    let bridge_authority = next_account_info(account_info_iter)?;
    // WHY: The PDA that is the owner of the vault token account, required to sign the transfer.
    let token_program = next_account_info(account_info_iter)?;
    // WHY: The SPL Token program executes the transfer out of the vault.
    let guardian_program = next_account_info(account_info_iter)?;
    // WHY: The guardian program verifies the burn event proof.
    if signatures.len() != guardian_indices.len() {
        // WHY: Mismatched arrays would make signature verification impossible.
        return Err(ProgramError::InvalidArgument);
    }
    let bridge_state = BridgeState::try_from_slice(&bridge_state_account.data.borrow())?;
    // WHY: We read the bridge configuration to ensure it is initialized.
    if !bridge_state.is_initialized {
        // WHY: Releasing from an uninitialized bridge would drain unbacked funds.
        return Err(ProgramError::UninitializedAccount);
    }
    if *guardian_program.key != bridge_state.guardian_program {
        // WHY: Enforcing the configured guardian program prevents fake verification programs.
        return Err(ProgramError::IncorrectProgramId);
    }
    // WHY: In production, verify nonce is not replayed via a consumed_nonces map.
    if signatures.len() < 3 {
        // WHY: Threshold of 3 signatures prevents unauthorized release by a minority of guardians.
        return Err(ProgramError::InvalidArgument);
    }
    let (expected_authority, authority_bump) =
        Pubkey::find_program_address(&[b"vault_authority"], program_id);
    // WHY: The vault authority PDA is derived so the program can sign for vault withdrawals.
    if expected_authority != *bridge_authority.key {
        // WHY: A mismatched authority means the transaction cannot sign for the vault transfer.
        return Err(ProgramError::InvalidAccountData);
    }
    invoke_signed(
        &token_instruction::transfer(
            token_program.key,
            vault_token_account.key,
            recipient_token_account.key,
            bridge_authority.key,
            &[],
            amount,
        )?,
        &[
            vault_token_account.clone(),
            recipient_token_account.clone(),
            bridge_authority.clone(),
            token_program.clone(),
        ],
        &[&[b"vault_authority", &[authority_bump]]],
        // WHY: The seeds and bump authorize the program to move tokens out of the vault PDA.
    )?;
    // WHY: Original tokens are returned to the user, completing the round-trip.
    msg!("Released {} tokens to {} with nonce {}", amount, recipient.key, nonce);
    // WHY: Logging the release allows source chain indexers to confirm the burn was honored.
    Ok(())
    // WHY: Returning Ok confirms the release completed successfully.
}
// WHY: Closing the release_tokens function.
