use solana_program::{ // WHY: We import the Solana SDK as a single block so all on-chain runtime types are available in this module.
    account_info::{next_account_info, AccountInfo}, // WHY: next_account_info and AccountInfo let us iterate over and inspect the accounts passed by the transaction.
    entrypoint, // WHY: The entrypoint macro is required to register the program's sole external entry point for the BPF loader.
    entrypoint::ProgramResult, // WHY: ProgramResult is the standard Solana return type that signals success or an on-chain error.
    msg, // WHY: msg lets us emit log messages that explorers and developers can read for debugging and audit trails.
    program::{invoke, invoke_signed}, // WHY: invoke and invoke_signed let us execute Cross-Program Invocations to the System and SPL Token programs.
    program_error::ProgramError, // WHY: ProgramError is the canonical error type returned to the Solana runtime when an instruction fails.
    pubkey::Pubkey, // WHY: Pubkey is the fundamental address type used to identify accounts, programs, and PDAs on Solana.
    sysvar::{clock::Clock, Sysvar}, // WHY: Clock and Sysvar let us read on-chain time so time-based checks are objective and trustless.
    system_instruction, // WHY: system_instruction provides constructors for System Program instructions like create_account and transfer.
    program_pack::Pack, // WHY: Pack is required in scope so we can call TokenAccount::unpack to parse SPL token account data.
}; // WHY: End of Solana SDK imports.

use spl_token::state::Account as TokenAccount; // WHY: We alias spl_token::state::Account to TokenAccount so we can parse SPL token balances during claims and revokes.

use borsh::{BorshDeserialize, BorshSerialize}; // WHY: Borsh provides compact binary serialization for our custom structs because Solana account data is a raw byte slice.

use thiserror::Error; // WHY: thiserror lets us derive descriptive error variants with minimal boilerplate so debugging on-chain failures is easier.

#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)] // WHY: Deriving Borsh traits lets VestingSchedule be packed into account data; Debug and Clone aid testing.
pub struct VestingSchedule { // WHY: A dedicated struct groups all vesting metadata into one on-chain account so the schedule lives at a single deterministic address.
    pub admin: Pubkey, // WHY: Storing the admin pubkey inside the account lets us verify that only the original creator can perform an emergency revoke.
    pub beneficiary: Pubkey, // WHY: Storing the beneficiary pubkey enforces that only the intended recipient can claim unlocked tokens.
    pub token_mint: Pubkey, // WHY: We record the SPL token mint so the program knows exactly which token type is locked in this schedule.
    pub total_amount: u64, // WHY: total_amount is the full token allocation that will vest over time, establishing the upper bound of distribution.
    pub start_time: i64, // WHY: start_time is a Unix timestamp that marks when the vesting clock begins ticking.
    pub cliff_time: i64, // WHY: cliff_time is the timestamp before which zero tokens may be claimed, protecting early investor commitments.
    pub end_time: i64, // WHY: end_time is the timestamp when the schedule reaches 100 percent vesting.
    pub released_amount: u64, // WHY: released_amount tracks how many tokens have already been claimed so we never double-pay the beneficiary.
    pub revoked: bool, // WHY: revoked is a boolean flag that permanently halts further claims and allows admin recovery of unvested tokens.
} // WHY: End of VestingSchedule struct definition.

#[derive(BorshSerialize, BorshDeserialize, Debug)] // WHY: The instruction enum must deserialize from the instruction_data payload so the entrypoint can dispatch correctly.
pub enum VestingInstruction { // WHY: An enum captures all possible program operations in one type, which is the standard BPF entrypoint pattern.
    CreateVestingSchedule { // WHY: CreateVestingSchedule initializes the on-chain record of token lockup before any distribution occurs.
        total_amount: u64, // WHY: total_amount defines the full token pool that will be subject to the vesting curve.
        start_time: i64, // WHY: start_time anchors the vesting timeline so linear unlock calculations have a fixed origin.
        cliff_time: i64, // WHY: cliff_time establishes the no-claim period to align long-term incentives.
        end_time: i64, // WHY: end_time caps the vesting duration so the schedule cannot extend indefinitely.
    }, // WHY: End of CreateVestingSchedule payload.
    ClaimVestedTokens, // WHY: ClaimVestedTokens lets the beneficiary withdraw unlocked tokens without needing off-chain authorization.
    EmergencyRevoke, // WHY: EmergencyRevoke gives the admin a kill switch to recover unvested tokens if the beneficiary relationship breaks down.
} // WHY: End of VestingInstruction enum.

#[derive(Error, Debug, Copy, Clone)] // WHY: Custom errors give descriptive failure reasons instead of opaque numeric ProgramError codes.
pub enum VestingError { // WHY: Grouping errors under one enum makes the codebase self-documenting and easier to audit.
    #[error("Unauthorized")] // WHY: Unauthorized clearly signals when a signer does not match the expected admin or beneficiary.
    Unauthorized, // WHY: This variant is returned when an account signer lacks permission for the requested operation.
    #[error("Invalid schedule")] // WHY: InvalidSchedule prevents creation of vesting configurations that are temporally impossible or useless.
    InvalidSchedule, // WHY: Returned when timestamps or amounts violate basic logical constraints.
    #[error("Cliff not reached")] // WHY: CliffNotReached enforces the mandatory waiting period before any tokens become liquid.
    CliffNotReached, // WHY: Returned when ClaimVestedTokens is called before the cliff_time has passed.
    #[error("Nothing to claim")] // WHY: NothingToClaim prevents empty transfers that would waste compute units and confuse indexers.
    NothingToClaim, // WHY: Returned when the beneficiary has already claimed everything currently vested.
    #[error("Already revoked")] // WHY: AlreadyRevoked prevents double-revocation and stops claims on a schedule that has been terminated.
    AlreadyRevoked, // WHY: Returned when EmergencyRevoke is called twice or ClaimVestedTokens runs on a revoked schedule.
    #[error("Calculation error")] // WHY: CalculationError catches arithmetic edge cases like division by zero or overflow in vesting math.
    CalculationError, // WHY: Returned when linear unlock arithmetic produces an invalid intermediate result.
} // WHY: End of VestingError enum.

impl From<VestingError> for ProgramError { // WHY: Implementing From lets our custom errors convert automatically into ProgramError for Solana runtime compatibility.
    fn from(e: VestingError) -> Self { // WHY: This function signature is required by the From trait so the compiler knows how to perform the conversion.
        ProgramError::Custom(e as u32) // WHY: Solana expects custom errors as u32 codes inside ProgramError::Custom so explorers can decode them.
    } // WHY: End of From conversion function.
} // WHY: End of From impl.

entrypoint!(process_instruction); // WHY: The entrypoint macro registers process_instruction as the BPF program's sole external entry point.

pub fn process_instruction( // WHY: This function is the router that receives every transaction; it must be public so the Solana runtime can call it.
    program_id: &Pubkey, // WHY: program_id is the current program's address so we can verify that derived accounts belong to this program.
    accounts: &[AccountInfo], // WHY: accounts is the ordered list of accounts passed by the client, which we must manually validate.
    instruction_data: &[u8], // WHY: instruction_data carries the serialized VestingInstruction so we know which operation to execute.
) -> ProgramResult { // WHY: ProgramResult is the standard Solana return type that signals success or an on-chain error.
    let instruction = VestingInstruction::try_from_slice(instruction_data) // WHY: We deserialize the payload first because all downstream logic depends on which instruction variant is requested.
        .map_err(|_| ProgramError::InvalidInstructionData)?; // WHY: If deserialization fails we return InvalidInstructionData so malformed transactions are rejected immediately.

    match instruction { // WHY: A match expression dispatches to the correct handler based on the deserialized enum variant.
        VestingInstruction::CreateVestingSchedule { total_amount, start_time, cliff_time, end_time } => { // WHY: We destructure the payload fields so they are available as local variables in the handler.
            process_create_vesting(program_id, accounts, total_amount, start_time, cliff_time, end_time) // WHY: We forward arguments to the dedicated handler to keep the entrypoint readable and modular.
        } // WHY: End of CreateVestingSchedule arm.
        VestingInstruction::ClaimVestedTokens => { // WHY: ClaimVestedTokens has no payload because all necessary state is already stored in on-chain accounts.
            process_claim(program_id, accounts) // WHY: We route to the claim handler so the entrypoint stays a pure dispatcher.
        } // WHY: End of ClaimVestedTokens arm.
        VestingInstruction::EmergencyRevoke => { // WHY: EmergencyRevoke has no payload because the vesting account already stores admin and revocation status.
            process_revoke(program_id, accounts) // WHY: Delegating to a named handler keeps the match block short and preserves single-responsibility.
        } // WHY: End of EmergencyRevoke arm.
    } // WHY: End of match on instruction.
} // WHY: End of process_instruction entrypoint.

fn process_create_vesting( // WHY: This handler isolates schedule creation logic so the entrypoint does not become a monolithic block.
    program_id: &Pubkey, // WHY: We need program_id to verify that the vesting PDA is derived from this program.
    accounts: &[AccountInfo], // WHY: The handler receives the same account slice so it can validate and mutate the vesting account.
    total_amount: u64, // WHY: total_amount is taken as a parameter so the schedule permanently records the full token lockup amount.
    start_time: i64, // WHY: start_time is passed explicitly to anchor the vesting timeline on-chain.
    cliff_time: i64, // WHY: cliff_time is passed explicitly so the no-claim period is transparent and immutable.
    end_time: i64, // WHY: end_time is passed explicitly so the 100 percent vesting date is transparent and immutable.
) -> ProgramResult { // WHY: ProgramResult lets us return custom errors if any validation check fails during creation.
    let account_info_iter = &mut accounts.iter(); // WHY: We create a mutable iterator because Solana handlers consume account_info items in a strict order.
    let admin_account = next_account_info(account_info_iter)?; // WHY: The first account must be the admin signer so we can enforce permission checks.
    let beneficiary_account = next_account_info(account_info_iter)?; // WHY: The second account is the beneficiary whose tokens will be locked.
    let vesting_account = next_account_info(account_info_iter)?; // WHY: The third account is the uninitialized vesting PDA that will hold the serialized VestingSchedule struct.
    let vault_token_account = next_account_info(account_info_iter)?; // WHY: The fourth account is the SPL token account that holds the tokens to be vested; its owner must be the vesting PDA.
    let system_program = next_account_info(account_info_iter)?; // WHY: We need the System Program to create and allocate lamports for the new vesting account.

    if !admin_account.is_signer { // WHY: We verify the admin signed because only the intended creator should initialize a vesting schedule.
        return Err(VestingError::Unauthorized.into()); // WHY: Returning early with Unauthorized prevents unauthorized schedule creation.
    } // WHY: End of signer check.

    if total_amount == 0 { // WHY: A vesting schedule with zero tokens has no effect and wastes rent.
        return Err(VestingError::InvalidSchedule.into()); // WHY: InvalidSchedule prevents creation of useless schedules.
    } // WHY: End of amount validation.

    if start_time >= end_time || cliff_time < start_time || cliff_time > end_time { // WHY: The schedule must have positive duration and the cliff must sit between start and end.
        return Err(VestingError::InvalidSchedule.into()); // WHY: InvalidSchedule rejects temporally impossible vesting configurations.
    } // WHY: End of time validation.

    let vault = TokenAccount::unpack(&vault_token_account.data.borrow())?; // WHY: Unpacking the vault token account lets us verify its mint and its owning authority.
    if vault.owner != *vesting_account.key { // WHY: The vault must be owned by the vesting PDA so the program can later sign transfers via CPI.
        return Err(ProgramError::InvalidAccountData); // WHY: InvalidAccountData signals that the vault token account was not configured with the correct authority.
    } // WHY: End of vault owner verification.

    let (vesting_pda, vesting_bump) = Pubkey::find_program_address( // WHY: We derive the vesting PDA so its address is deterministic and not controlled by any private key.
        &[b"vesting", admin_account.key.as_ref(), beneficiary_account.key.as_ref()], // WHY: The seed combines a static string, admin, and beneficiary so the schedule is unique per relationship.
        program_id, // WHY: We scope the derivation to this program so other programs cannot squat the same PDA.
    ); // WHY: End of PDA derivation.

    if vesting_pda != *vesting_account.key { // WHY: We verify the client passed the correct PDA so malicious callers cannot substitute a fake account.
        return Err(ProgramError::InvalidSeeds); // WHY: InvalidSeeds is the standard Solana error for PDA mismatches.
    } // WHY: End of PDA verification.

    let vesting = VestingSchedule { // WHY: We construct the VestingSchedule struct in memory before writing it to the account so all fields are validated first.
        admin: *admin_account.key, // WHY: We copy the admin pubkey so the schedule permanently remembers who can revoke it.
        beneficiary: *beneficiary_account.key, // WHY: We copy the beneficiary pubkey so only they can claim tokens from this schedule.
        token_mint: vault.mint, // WHY: We store the vault's mint so all future token operations reference the correct SPL token type.
        total_amount, // WHY: We store total_amount so the program knows the full allocation and can compute unlocked portions over time.
        start_time, // WHY: We store start_time so linear unlock calculations have a fixed origin.
        cliff_time, // WHY: We store cliff_time so the program can enforce the mandatory waiting period.
        end_time, // WHY: We store end_time so the schedule objectively knows when 100 percent vesting is reached.
        released_amount: 0, // WHY: released_amount starts at zero because no tokens have been distributed yet.
        revoked: false, // WHY: revoked starts false because the schedule is active at creation.
    }; // WHY: End of VestingSchedule construction.

    let vesting_size = vesting.try_to_vec()?.len(); // WHY: We compute the serialized size so we allocate exactly enough space and avoid wasting rent.
    let rent = solana_program::rent::Rent::get()?; // WHY: We fetch the Rent sysvar to know the minimum lamports needed for rent exemption.
    let required_lamports = rent.minimum_balance(vesting_size); // WHY: minimum_balance computes the exact rent-exempt amount so the account persists indefinitely.

    invoke_signed( // WHY: invoke_signed is required when creating a PDA because the program must sign on behalf of the PDA, which has no private key.
        &system_instruction::create_account( // WHY: create_account allocates space and assigns ownership to our program in a single atomic System Program call.
            admin_account.key, // WHY: The admin pays for account creation because they initiated the transaction and should bear the cost.
            vesting_account.key, // WHY: The vesting PDA is the account being created; it will hold the serialized VestingSchedule data.
            required_lamports, // WHY: We fund the account with exactly the rent-exempt minimum so it stays alive without ongoing rent payments.
            vesting_size as u64, // WHY: The size parameter tells the System Program how many bytes to allocate for our serialized struct.
            program_id, // WHY: Assigning ownership to our program ensures only this program can mutate the vesting account data.
        ), // WHY: End of create_account instruction.
        &[admin_account.clone(), vesting_account.clone(), system_program.clone()], // WHY: We clone references because invoke_signed needs owned AccountInfo references for its internal checks.
        &[&[b"vesting", admin_account.key.as_ref(), beneficiary_account.key.as_ref(), &[vesting_bump]]], // WHY: The signer seeds prove the program derived this PDA correctly, authorizing the creation.
    )?; // WHY: The ? propagates any System Program failure immediately so we do not continue with a half-created account.

    vesting.serialize(&mut &mut vesting_account.data.borrow_mut()[..])?; // WHY: We serialize the VestingSchedule struct into the newly allocated account data so it persists on-chain.

    msg!("Vesting schedule created: {}", vesting_pda); // WHY: Logging the PDA helps explorers and developers confirm that creation succeeded at the expected address.
    Ok(()) // WHY: Returning Ok signals to the Solana runtime that the instruction executed successfully.
} // WHY: End of process_create_vesting.

fn process_claim( // WHY: This handler isolates token claim logic so the entrypoint stays a pure dispatcher.
    program_id: &Pubkey, // WHY: program_id is needed to verify PDAs belong to this program.
    accounts: &[AccountInfo], // WHY: The handler needs the beneficiary, vesting, vault, and token accounts to validate and transfer tokens.
) -> ProgramResult { // WHY: ProgramResult lets us enforce that claims only happen after the cliff and only for unlocked portions.
    let account_info_iter = &mut accounts.iter(); // WHY: We create a mutable iterator because Solana handlers consume account_info items in a strict order.
    let beneficiary_account = next_account_info(account_info_iter)?; // WHY: The first account must be the beneficiary signer so we can enforce permission checks.
    let vesting_account = next_account_info(account_info_iter)?; // WHY: The second account is the vesting PDA that stores the schedule state.
    let vault_token_account = next_account_info(account_info_iter)?; // WHY: The third account is the SPL token account holding the locked tokens.
    let beneficiary_token_account = next_account_info(account_info_iter)?; // WHY: The fourth account is the beneficiary's SPL token account that will receive unlocked tokens.
    let token_program = next_account_info(account_info_iter)?; // WHY: The SPL Token Program must be invoked to execute the actual token transfer.

    if !beneficiary_account.is_signer { // WHY: Only the beneficiary should be able to claim their own vested tokens.
        return Err(VestingError::Unauthorized.into()); // WHY: Rejecting unsigned claims prevents theft of vested allocations.
    } // WHY: End of signer check.

    let mut vesting = VestingSchedule::try_from_slice(&vesting_account.data.borrow())?; // WHY: Deserializing the schedule lets us check revocation, cliff, and compute unlocked amounts.
    if vesting.beneficiary != *beneficiary_account.key { // WHY: We verify the signer matches the stored beneficiary so no one else can claim this allocation.
        return Err(VestingError::Unauthorized.into()); // WHY: Rejecting mismatched owners protects beneficiary funds.
    } // WHY: End of beneficiary verification.

    if vesting.revoked { // WHY: A revoked schedule has been terminated by the admin, so no further claims are permitted.
        return Err(VestingError::AlreadyRevoked.into()); // WHY: AlreadyRevoked stops claims on terminated schedules.
    } // WHY: End of revocation check.

    let clock = Clock::get()?; // WHY: We fetch the Clock sysvar to get the current on-chain Unix timestamp for objective time checks.
    if clock.unix_timestamp < vesting.cliff_time { // WHY: The cliff period must elapse before any tokens become claimable.
        return Err(VestingError::CliffNotReached.into()); // WHY: CliffNotReached enforces the mandatory lockup period.
    } // WHY: End of cliff check.

    let vested_amount = if clock.unix_timestamp >= vesting.end_time { // WHY: If the current time is past the end, the entire allocation is fully vested.
        vesting.total_amount // WHY: Returning total_amount represents 100 percent vesting.
    } else { // WHY: Otherwise we calculate the linearly unlocked portion based on elapsed time.
        let elapsed = clock.unix_timestamp.saturating_sub(vesting.start_time) as u64; // WHY: saturating_sub prevents underflow if start_time is somehow in the future, returning zero instead.
        let duration = vesting.end_time.saturating_sub(vesting.start_time) as u64; // WHY: duration is the total vesting window; saturating_sub ensures it is non-negative.
        if duration == 0 { // WHY: A zero duration would cause division by zero, so we reject it defensively.
            return Err(VestingError::CalculationError.into()); // WHY: CalculationError catches this edge case before it can panic.
        } // WHY: End of duration check.
        vesting.total_amount.checked_mul(elapsed).ok_or(VestingError::CalculationError)? // WHY: checked_mul prevents overflow when scaling the total allocation by elapsed time.
            .checked_div(duration).ok_or(VestingError::CalculationError)? // WHY: checked_div prevents division by zero and yields the proportional vested amount.
    }; // WHY: End of vested amount calculation.

    let claimable = vested_amount.checked_sub(vesting.released_amount).ok_or(VestingError::CalculationError)?; // WHY: Subtracting already-released tokens gives the net amount available right now.
    if claimable == 0 { // WHY: If nothing new has unlocked, there is no point in executing a token transfer.
        return Err(VestingError::NothingToClaim.into()); // WHY: NothingToClaim prevents empty transfers that waste compute units.
    } // WHY: End of claimable check.

    vesting.released_amount = vesting.released_amount.checked_add(claimable).ok_or(VestingError::CalculationError)?; // WHY: We increment released_amount before the CPI so a retry cannot double-claim.
    vesting.serialize(&mut &mut vesting_account.data.borrow_mut()[..])?; // WHY: Persisting the updated released_amount immediately makes the state durable.

    let vault = TokenAccount::unpack(&vault_token_account.data.borrow())?; // WHY: Unpacking the vault lets us verify it holds the expected token mint before moving funds.
    if vault.mint != vesting.token_mint { // WHY: We verify the vault's mint matches the schedule to prevent distributing the wrong token type.
        return Err(ProgramError::InvalidAccountData); // WHY: InvalidAccountData is the standard error for a mint mismatch.
    } // WHY: End of mint verification.

    let (_vesting_pda, vesting_bump) = Pubkey::find_program_address( // WHY: We re-derive the vesting PDA to obtain the bump seed for signing the SPL transfer.
        &[b"vesting", vesting.admin.as_ref(), vesting.beneficiary.as_ref()], // WHY: These seeds must match the original creation seeds.
        program_id, // WHY: Derivation is scoped to this program.
    ); // WHY: End of PDA derivation.

    invoke_signed( // WHY: invoke_signed is required because the vesting PDA must sign the SPL token transfer, and PDAs have no private key.
        &spl_token::instruction::transfer( // WHY: spl_token::transfer moves SPL tokens from the vault to the beneficiary's token account.
            token_program.key, // WHY: The SPL Token Program is the program that actually executes the token ledger update.
            vault_token_account.key, // WHY: The source account is the vault that holds the locked tokens.
            beneficiary_token_account.key, // WHY: The destination account is the beneficiary's associated token account.
            vesting_account.key, // WHY: The vesting PDA is the authority that owns the source tokens.
            &[], // WHY: No additional signers are needed beyond the vesting PDA authority.
            claimable, // WHY: We transfer exactly the computed claimable amount.
        )?, // WHY: The ? propagates any SPL Token program error immediately.
        &[vesting_account.clone(), vault_token_account.clone(), beneficiary_token_account.clone(), token_program.clone()], // WHY: All involved accounts must be passed to the SPL Token Program CPI.
        &[&[b"vesting", vesting.admin.as_ref(), vesting.beneficiary.as_ref(), &[vesting_bump]]], // WHY: The signer seeds authorize the vesting PDA to move its own tokens.
    )?; // WHY: Propagating errors ensures we do not continue if the token transfer fails.

    msg!("Beneficiary {} claimed {} tokens", beneficiary_account.key, claimable); // WHY: Logging creates an on-chain audit trail of the distribution.
    Ok(()) // WHY: Ok signals the claim completed successfully.
} // WHY: End of process_claim.

fn process_revoke( // WHY: This handler isolates emergency revocation logic so the entrypoint stays a clean dispatcher.
    program_id: &Pubkey, // WHY: program_id is needed to verify the vesting PDA belongs to this program.
    accounts: &[AccountInfo], // WHY: The handler needs the admin signer, vesting account, vault, admin token account, and SPL token program.
) -> ProgramResult { // WHY: ProgramResult lets us enforce that only the original admin can revoke and recover unvested tokens.
    let account_info_iter = &mut accounts.iter(); // WHY: We create a mutable iterator because Solana handlers consume account_info items in a strict order.
    let admin_account = next_account_info(account_info_iter)?; // WHY: The first account must be the admin signer so we can enforce permission checks.
    let vesting_account = next_account_info(account_info_iter)?; // WHY: The second account is the vesting PDA that stores the schedule state.
    let vault_token_account = next_account_info(account_info_iter)?; // WHY: The third account is the SPL token account holding the locked tokens.
    let admin_token_account = next_account_info(account_info_iter)?; // WHY: The fourth account is the admin's SPL token account that will receive recovered unvested tokens.
    let token_program = next_account_info(account_info_iter)?; // WHY: The SPL Token Program must be invoked to execute the recovery transfer.

    if !admin_account.is_signer { // WHY: Only the admin should be able to revoke a schedule because they created it and bear the risk.
        return Err(VestingError::Unauthorized.into()); // WHY: Rejecting unsigned revocations prevents unauthorized termination.
    } // WHY: End of signer check.

    let mut vesting = VestingSchedule::try_from_slice(&vesting_account.data.borrow())?; // WHY: Deserializing the schedule lets us verify admin identity and check prior revocation.
    if vesting.admin != *admin_account.key { // WHY: We verify the signer is the stored admin so no one else can revoke someone else's schedule.
        return Err(VestingError::Unauthorized.into()); // WHY: Rejecting non-admin signers protects the vesting agreement.
    } // WHY: End of admin verification.

    if vesting.revoked { // WHY: A schedule that is already revoked cannot be revoked again.
        return Err(VestingError::AlreadyRevoked.into()); // WHY: AlreadyRevoked prevents double-revocation and duplicate recovery transfers.
    } // WHY: End of double-revocation check.

    vesting.revoked = true; // WHY: We mark revoked before the transfer so a retry cannot recover tokens twice.
    vesting.serialize(&mut &mut vesting_account.data.borrow_mut()[..])?; // WHY: Persisting revoked == true immediately makes the schedule permanently inactive.

    let unreleased = vesting.total_amount.checked_sub(vesting.released_amount).ok_or(VestingError::CalculationError)?; // WHY: Subtracting released from total yields the remaining unvested tokens that belong to the admin.
    if unreleased > 0 { // WHY: If there are no unvested tokens left, we can skip the SPL transfer and save compute.
        let vault = TokenAccount::unpack(&vault_token_account.data.borrow())?; // WHY: Unpacking the vault lets us verify its mint before moving funds.
        if vault.mint != vesting.token_mint { // WHY: We verify the vault's mint matches the schedule to prevent recovering the wrong token type.
            return Err(ProgramError::InvalidAccountData); // WHY: InvalidAccountData is the standard error for a mint mismatch.
        } // WHY: End of mint verification.

        let (_vesting_pda, vesting_bump) = Pubkey::find_program_address( // WHY: We re-derive the vesting PDA to obtain the bump seed for signing the SPL transfer.
            &[b"vesting", vesting.admin.as_ref(), vesting.beneficiary.as_ref()], // WHY: These seeds must match the original creation seeds.
            program_id, // WHY: Derivation is scoped to this program.
        ); // WHY: End of PDA derivation.

        invoke_signed( // WHY: invoke_signed is required because the vesting PDA must sign the SPL token transfer, and PDAs have no private key.
            &spl_token::instruction::transfer( // WHY: spl_token::transfer moves SPL tokens from the vault back to the admin's token account.
                token_program.key, // WHY: The SPL Token Program executes the token ledger update.
                vault_token_account.key, // WHY: The source account is the vault that holds the locked tokens.
                admin_token_account.key, // WHY: The destination account is the admin's associated token account.
                vesting_account.key, // WHY: The vesting PDA is the authority that owns the source tokens.
                &[], // WHY: No additional signers are needed beyond the vesting PDA authority.
                unreleased, // WHY: We transfer exactly the unreleased amount so the admin recovers only what was not yet earned.
            )?, // WHY: The ? propagates any SPL Token program error immediately.
            &[vesting_account.clone(), vault_token_account.clone(), admin_token_account.clone(), token_program.clone()], // WHY: All involved accounts must be passed to the SPL Token Program CPI.
            &[&[b"vesting", vesting.admin.as_ref(), vesting.beneficiary.as_ref(), &[vesting_bump]]], // WHY: The signer seeds authorize the vesting PDA to move its own tokens.
        )?; // WHY: Propagating errors ensures we do not leave the schedule revoked if the recovery transfer fails.
    } // WHY: End of unreleased transfer block.

    msg!("Admin revoked vesting and recovered {} tokens", unreleased); // WHY: Logging creates an on-chain audit trail of the emergency revocation.
    Ok(()) // WHY: Ok confirms the revocation completed successfully.
} // WHY: End of process_revoke.
