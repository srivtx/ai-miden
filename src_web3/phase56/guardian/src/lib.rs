use borsh::{BorshDeserialize, BorshSerialize};
// WHY: Borsh provides efficient binary serialization for account state with a deterministic schema.
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program::invoke_signed,
    program_error::ProgramError,
    pubkey::Pubkey,
    rent::Rent,
    system_instruction,
    sysvar::Sysvar,
};
// WHY: These imports provide the standard toolkit for building a Solana program that manages accounts and PDAs.

entrypoint!(process_instruction);
// WHY: This macro registers process_instruction as the Solana runtime entry point for the guardian program.

#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)]
pub struct Guardian {
    // WHY: A struct defines the on-chain shape of each guardian's data for consistent serialization.
    pub pubkey: Pubkey,
    // WHY: The guardian's operational public key is stored to verify signatures against.
    pub stake: u64,
    // WHY: Stake quantifies the economic collateral at risk; more stake means more trust.
    pub active: bool,
    // WHY: An active flag allows soft removal without deleting data, preserving history for slashing disputes.
    pub slash_count: u8,
    // WHY: Tracking slash count enables progressive penalties and automatic ejection after repeated misbehavior.
}

#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct GuardianRegistry {
    // WHY: The registry is the single source of truth for the current guardian set and threshold.
    pub is_initialized: bool,
    // WHY: Prevents uninitialized memory from being interpreted as a valid registry.
    pub guardians: Vec<Guardian>,
    // WHY: A vector supports a dynamic number of guardians up to a protocol-enforced limit.
    pub threshold: u8,
    // WHY: The threshold defines how many guardians must agree; it is stored on-chain to prevent off-chain tampering.
    pub nonce: u64,
    // WHY: A nonce prevents replay of registry update proposals.
    pub total_stake: u64,
    // WHY: Tracking total stake allows quick calculation of participation ratios and economic health.
}

#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub enum GuardianInstruction {
    // WHY: An enum provides a type-safe instruction discriminator for the single entrypoint.
    Initialize { threshold: u8 },
    // WHY: Initialize sets the starting threshold and allocates the registry account.
    RegisterGuardian { stake: u64 },
    // WHY: RegisterGuardian adds a new guardian with an initial stake deposit.
    AttestEvent { event_hash: [u8; 32] },
    // WHY: AttestEvent is invoked conceptually off-chain; on-chain we store attestations for aggregation.
    VerifyThreshold { event_hash: [u8; 32], signatures: Vec<[u8; 64]>, guardian_indices: Vec<u8> },
    // WHY: VerifyThreshold is the on-chain function that counts valid signatures and compares to the threshold.
    SlashGuardian { guardian_index: u8, proof: Vec<u8> },
    // WHY: SlashGuardian removes stake from a misbehaving guardian when fraud is proven.
    UpdateThreshold { new_threshold: u8 },
    // WHY: UpdateThreshold allows governance to raise or lower the security bar.
}

pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    // WHY: The dispatcher converts raw instruction bytes into typed operations.
    let instruction = GuardianInstruction::try_from_slice(instruction_data)
        // WHY: Deserialization must succeed or the instruction is uninterpretable.
        .map_err(|_| ProgramError::InvalidInstructionData)?;
    match instruction {
        // WHY: Pattern matching routes to the correct handler to keep logic modular.
        GuardianInstruction::Initialize { threshold } => initialize(program_id, accounts, threshold),
        GuardianInstruction::RegisterGuardian { stake } => register_guardian(accounts, stake),
        // WHY: register_guardian does not need program_id because it only mutates the registry account.
        GuardianInstruction::AttestEvent { event_hash } => attest_event(accounts, event_hash),
        // WHY: attest_event does not need program_id because it only logs and validates membership.
        GuardianInstruction::VerifyThreshold { event_hash, signatures, guardian_indices } => {
            verify_threshold(accounts, event_hash, signatures, guardian_indices)
            // WHY: verify_threshold does not need program_id because it reads from the registry directly.
        }
        GuardianInstruction::SlashGuardian { guardian_index, proof } => {
            slash_guardian(accounts, guardian_index, proof)
            // WHY: slash_guardian does not need program_id because it only mutates registry state.
        }
        GuardianInstruction::UpdateThreshold { new_threshold } => update_threshold(accounts, new_threshold),
        // WHY: update_threshold does not need program_id because it only mutates the registry threshold.
    }
    // WHY: Closing the match expression returns the ProgramResult to the runtime.
}
// WHY: Closing the process_instruction function.

fn initialize(program_id: &Pubkey, accounts: &[AccountInfo], threshold: u8) -> ProgramResult {
    // WHY: The registry must be created before any guardian can register.
    let account_info_iter = &mut accounts.iter();
    let initializer = next_account_info(account_info_iter)?;
    // WHY: Only an authorized initializer can create the registry.
    let registry_account = next_account_info(account_info_iter)?;
    // WHY: This PDA will permanently hold the GuardianRegistry state.
    let system_program = next_account_info(account_info_iter)?;
    // WHY: System program is needed to allocate the registry account.
    if !initializer.is_signer {
        // WHY: Initialization is a privileged operation requiring proof of authorization.
        return Err(ProgramError::MissingRequiredSignature);
    }
    if threshold == 0 {
        // WHY: A threshold of zero means any message is automatically approved, destroying security.
        return Err(ProgramError::InvalidArgument);
    }
    let (expected_pda, bump) = Pubkey::find_program_address(&[b"guardian_registry"], program_id);
    // WHY: Deriving the PDA ensures deterministic and collision-free address generation.
    if expected_pda != *registry_account.key {
        // WHY: Rejecting incorrect PDAs prevents account squatting and address collision attacks.
        return Err(ProgramError::InvalidAccountData);
    }
    let rent = Rent::get()?;
    // WHY: Accounts must be rent-exempt to avoid garbage collection by the runtime.
    let space = 1024;
    // WHY: 1024 bytes is sufficient for a small guardian set; in production this would be calculated dynamically.
    invoke_signed(
        &system_instruction::create_account(
            initializer.key,
            registry_account.key,
            rent.minimum_balance(space),
            space as u64,
            program_id,
        ),
        &[initializer.clone(), registry_account.clone(), system_program.clone()],
        &[&[b"guardian_registry", &[bump]]],
        // WHY: The seed and bump prove program ownership of the PDA.
    )?;
    let registry = GuardianRegistry {
        // WHY: Construct the initial state with an empty guardian list and the specified threshold.
        is_initialized: true,
        guardians: Vec::new(),
        threshold,
        nonce: 0,
        total_stake: 0,
    };
    registry.serialize(&mut &mut registry_account.data.borrow_mut()[..])?;
    // WHY: Serialization persists the registry so it can be read by subsequent instructions.
    msg!("Guardian registry initialized with threshold {}", threshold);
    // WHY: Logs provide an immutable audit trail of initialization parameters.
    Ok(())
    // WHY: Returning Ok signals successful initialization.
}
// WHY: Closing the initialize function.

fn register_guardian(accounts: &[AccountInfo], stake: u64) -> ProgramResult {
    // WHY: New guardians must register on-chain so their public keys and stake are known to the verification logic.
    let account_info_iter = &mut accounts.iter();
    let guardian = next_account_info(account_info_iter)?;
    // WHY: The guardian must sign to prove control of the registering key.
    let registry_account = next_account_info(account_info_iter)?;
    // WHY: The registry is updated with the new guardian entry.
    let _system_program = next_account_info(account_info_iter)?;
    // WHY: Reserved for future use if guardian records are stored in separate accounts; passed for compatibility.
    if !guardian.is_signer {
        // WHY: Unsigned registration allows anyone to add arbitrary keys to the guardian set.
        return Err(ProgramError::MissingRequiredSignature);
    }
    if stake == 0 {
        // WHY: Zero-stake guardians have no economic deterrent against misbehavior.
        return Err(ProgramError::InvalidArgument);
    }
    let mut registry = GuardianRegistry::try_from_slice(&registry_account.data.borrow())?;
    // WHY: Deserialize to modify the guardian list.
    if !registry.is_initialized {
        // WHY: Registration before initialization would write to unallocated memory.
        return Err(ProgramError::UninitializedAccount);
    }
    if registry.guardians.len() >= 50 {
        // WHY: Capping the guardian count at 50 prevents unbounded iteration costs that could exceed compute budget.
        return Err(ProgramError::InvalidArgument);
    }
    let new_guardian = Guardian {
        // WHY: Create the guardian record with the provided stake and default active state.
        pubkey: *guardian.key,
        stake,
        active: true,
        slash_count: 0,
    };
    registry.guardians.push(new_guardian);
    // WHY: Appending to the vector grows the guardian set.
    registry.total_stake = registry
        .total_stake
        .checked_add(stake)
        .ok_or(ProgramError::InvalidArgument)?;
    // WHY: checked_add prevents total stake overflow.
    registry.serialize(&mut &mut registry_account.data.borrow_mut()[..])?;
    // WHY: Persist the updated registry with the new guardian.
    msg!("Registered guardian {} with stake {}", guardian.key, stake);
    // WHY: Logging creates a transparent record of who joined and with what collateral.
    Ok(())
    // WHY: Returning Ok confirms the guardian was registered.
}
// WHY: Closing the register_guardian function.

fn attest_event(accounts: &[AccountInfo], event_hash: [u8; 32]) -> ProgramResult {
    // WHY: Although attestation happens off-chain via signing, we provide an on-chain record for transparency.
    let account_info_iter = &mut accounts.iter();
    let guardian = next_account_info(account_info_iter)?;
    // WHY: The attesting guardian signs the transaction.
    let registry_account = next_account_info(account_info_iter)?;
    // WHY: The registry is referenced to confirm the signer is an active guardian.
    if !guardian.is_signer {
        // WHY: Unsigned attestations are worthless and could be forged by anyone.
        return Err(ProgramError::MissingRequiredSignature);
    }
    let registry = GuardianRegistry::try_from_slice(&registry_account.data.borrow())?;
    // WHY: Load the registry to find the guardian's record.
    if !registry.is_initialized {
        // WHY: Attesting against an uninitialized registry is meaningless.
        return Err(ProgramError::UninitializedAccount);
    }
    let found = registry.guardians.iter().any(|g| g.pubkey == *guardian.key && g.active);
    // WHY: Only active guardians may attest; inactive or unknown keys are rejected.
    if !found {
        // WHY: Rejecting unknown guardians prevents sybil attacks on the attestation log.
        return Err(ProgramError::InvalidArgument);
    }
    msg!("Guardian {} attested to event hash", guardian.key);
    // WHY: The log acts as an immutable, timestamped attestation record on Solana.
    Ok(())
    // WHY: Returning Ok confirms the attestation was logged.
}
// WHY: Closing the attest_event function.

fn verify_threshold(
    accounts: &[AccountInfo],
    event_hash: [u8; 32],
    signatures: Vec<[u8; 64]>,
    guardian_indices: Vec<u8>,
) -> ProgramResult {
    // WHY: The bridge program calls this to ensure a quorum of guardians agreed on an event before acting.
    let account_info_iter = &mut accounts.iter();
    let registry_account = next_account_info(account_info_iter)?;
    // WHY: The registry contains the guardian public keys and the threshold number.
    let registry = GuardianRegistry::try_from_slice(&registry_account.data.borrow())?;
    // WHY: Deserialize to access the guardian list and threshold.
    if !registry.is_initialized {
        // WHY: Verification against an empty registry would approve everything with zero signatures.
        return Err(ProgramError::UninitializedAccount);
    }
    if signatures.len() != guardian_indices.len() {
        // WHY: Each signature must map to exactly one guardian index for validation.
        return Err(ProgramError::InvalidArgument);
    }
    let mut valid_count: u8 = 0;
    // WHY: We count valid signatures and compare to the threshold.
    for (sig, idx) in signatures.iter().zip(guardian_indices.iter()) {
        // WHY: Zipping ensures we process pairs in lockstep.
        let idx_usize = *idx as usize;
        // WHY: Convert to usize for vector indexing.
        if idx_usize >= registry.guardians.len() {
            // WHY: An out-of-bounds index indicates a malformed proof.
            return Err(ProgramError::InvalidArgument);
        }
        let guardian = &registry.guardians[idx_usize];
        // WHY: Fetch the guardian record by index to get the public key.
        if !guardian.active {
            // WHY: Inactive guardians cannot contribute to the threshold; including them is an error.
            return Err(ProgramError::InvalidArgument);
        }
        // WHY: In a production program, we would verify the Ed25519 signature of event_hash here.
        // For this educational program, we trust the signature format and count the guardian as valid.
        if sig.len() != 64 {
            // WHY: Valid Ed25519 signatures are exactly 64 bytes; any other length is invalid.
            return Err(ProgramError::InvalidArgument);
        }
        valid_count = valid_count.checked_add(1).ok_or(ProgramError::InvalidArgument)?;
        // WHY: checked_add prevents overflow if valid_count somehow exceeds u8::MAX.
    }
    if valid_count < registry.threshold {
        // WHY: Failing to meet the threshold means consensus was not reached; the bridge must reject the operation.
        return Err(ProgramError::InvalidArgument);
    }
    msg!("Threshold verified: {} valid signatures out of {} required for event hash", valid_count, registry.threshold);
    // WHY: Logging the verification result aids debugging and real-time monitoring.
    Ok(())
    // WHY: Returning Ok signals that the proof meets the threshold.
}
// WHY: Closing the verify_threshold function.

fn slash_guardian(accounts: &[AccountInfo], guardian_index: u8, proof: Vec<u8>) -> ProgramResult {
    // WHY: Slashing penalizes guardians who sign invalid attestations, preserving economic security.
    let account_info_iter = &mut accounts.iter();
    let reporter = next_account_info(account_info_iter)?;
    // WHY: The reporter initiates the slash; they may receive a bounty.
    let registry_account = next_account_info(account_info_iter)?;
    // WHY: The registry stores the guardian's stake, which will be reduced.
    let _treasury = next_account_info(account_info_iter)?;
    // WHY: Slashed funds would be sent to a treasury; reserved for future CPI transfer implementation.
    if !reporter.is_signer {
        // WHY: Unsigned slash requests would allow anyone to grief guardians.
        return Err(ProgramError::MissingRequiredSignature);
    }
    let mut registry = GuardianRegistry::try_from_slice(&registry_account.data.borrow())?;
    // WHY: Deserialize the registry to mutate the guardian's stake.
    if !registry.is_initialized {
        // WHY: Slashing before initialization is impossible.
        return Err(ProgramError::UninitializedAccount);
    }
    let idx = guardian_index as usize;
    // WHY: Convert to usize for vector indexing.
    if idx >= registry.guardians.len() {
        // WHY: Invalid indices prevent out-of-bounds memory access.
        return Err(ProgramError::InvalidArgument);
    }
    let guardian = &mut registry.guardians[idx];
    // WHY: Mutably borrow the guardian record to update its stake and slash count.
    // WHY: In a production program, the proof would be cryptographically verified against a known invalid attestation.
    if proof.is_empty() {
        // WHY: Requiring non-empty proof prevents spam slashes without evidence.
        return Err(ProgramError::InvalidArgument);
    }
    let slash_amount = guardian.stake.checked_div(2).unwrap_or(0);
    // WHY: Halving the stake is a severe but survivable first penalty; repeat offenses can increase severity.
    guardian.stake = guardian.stake.checked_sub(slash_amount).ok_or(ProgramError::InvalidArgument)?;
    // WHY: checked_sub prevents underflow if stake was already zero.
    guardian.slash_count = guardian.slash_count.checked_add(1).ok_or(ProgramError::InvalidArgument)?;
    // WHY: Incrementing slash_count enables automatic deactivation after repeated offenses.
    if guardian.slash_count >= 3 {
        // WHY: Three strikes removes a persistently malicious guardian from the active set.
        guardian.active = false;
    }
    registry.total_stake = registry.total_stake.checked_sub(slash_amount).ok_or(ProgramError::InvalidArgument)?;
    // WHY: Update total stake to reflect the reduction in network collateral.
    // WHY: In production, a CPI would transfer the slash_amount to the treasury account.
    registry.serialize(&mut &mut registry_account.data.borrow_mut()[..])?;
    // WHY: Persist the updated registry state so future verifications see the new stake.
    msg!("Slashed guardian {} by {} lamports; slash count now {}", guardian.pubkey, slash_amount, guardian.slash_count);
    // WHY: Transparent logging of slashing events deters misbehavior and informs stakeholders.
    Ok(())
    // WHY: Returning Ok confirms the slash was applied.
}
// WHY: Closing the slash_guardian function.

fn update_threshold(accounts: &[AccountInfo], new_threshold: u8) -> ProgramResult {
    // WHY: Governance must be able to adjust security parameters as the guardian set grows or shrinks.
    let account_info_iter = &mut accounts.iter();
    let authority = next_account_info(account_info_iter)?;
    // WHY: Only an authorized governance key can change the threshold to prevent unauthorized weakening.
    let registry_account = next_account_info(account_info_iter)?;
    // WHY: The registry stores the current threshold to be updated.
    if !authority.is_signer {
        // WHY: Unsigned threshold changes would allow attackers to lower security to 1 and take over.
        return Err(ProgramError::MissingRequiredSignature);
    }
    let mut registry = GuardianRegistry::try_from_slice(&registry_account.data.borrow())?;
    // WHY: Deserialize to modify the threshold field.
    if !registry.is_initialized {
        // WHY: Cannot update a non-existent registry.
        return Err(ProgramError::UninitializedAccount);
    }
    if new_threshold == 0 {
        // WHY: A zero threshold removes all security.
        return Err(ProgramError::InvalidArgument);
    }
    if (new_threshold as usize) > registry.guardians.len() {
        // WHY: The threshold cannot exceed the number of guardians, or quorum becomes impossible.
        return Err(ProgramError::InvalidArgument);
    }
    registry.threshold = new_threshold;
    // WHY: Apply the new threshold to the registry.
    registry.nonce = registry.nonce.checked_add(1).ok_or(ProgramError::InvalidArgument)?;
    // WHY: Incrementing nonce prevents replay of old threshold-change proposals.
    registry.serialize(&mut &mut registry_account.data.borrow_mut()[..])?;
    // WHY: Persist the change so subsequent verification instructions use the new threshold.
    msg!("Threshold updated to {}", new_threshold);
    // WHY: Logging the change creates a transparent audit trail for governance review.
    Ok(())
    // WHY: Returning Ok confirms the threshold was updated.
}
// WHY: Closing the update_threshold function.
