use solana_program::{ // Import the Solana program SDK to build on-chain time-lock logic
    account_info::{next_account_info, AccountInfo}, // Import utilities to iterate and validate transaction accounts
    entrypoint, // Import the macro to register the program's main entry point
    entrypoint::ProgramResult, // Import the typed result for success and error returns
    msg, // Import the logging utility to emit debug messages during execution
    program_error::ProgramError, // Import standard error types for clean failure reporting
    pubkey::Pubkey, // Import the Pubkey type for Solana address handling
    clock::Clock, // Import the Clock struct to access trustless on-chain time
    sysvar::Sysvar, // Import the Sysvar trait to load system variables like Clock
};
use borsh::{BorshDeserialize, BorshSerialize}; // Import Borsh traits to serialize and deserialize account data

/// Phase 20: Time-Locked Vault Program
///
/// This program manages time-locked token releases and vesting schedules:
/// - InitializeLock: Creates a lock with an unlock timestamp and optional vesting
/// - LockTokens: Deposits tokens into the vault
/// - UnlockTokens: Releases tokens only if the current time has passed the deadline
/// - CancelLock: Allows the guardian to cancel and return tokens before unlock
/// - ClaimVested: Releases tokens according to a linear vesting schedule

entrypoint!(process_instruction); // Register process_instruction as the function the Solana runtime invokes

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Enable serialization and debugging for the vault state
pub struct TimeLockVault { // Define the on-chain data structure for a time-locked vault
    pub owner: Pubkey, // The user who owns the locked tokens
    pub guardian: Pubkey, // An authorized address that can cancel the lock before expiration
    pub amount: u64, // Total number of tokens currently locked in the vault
    pub unlock_time: i64, // Unix timestamp after which the owner can withdraw tokens
    pub vesting_start: i64, // Unix timestamp when vesting begins, used for schedule calculations
    pub vesting_duration: i64, // Total seconds over which tokens vest linearly
    pub claimed: u64, // Number of tokens already withdrawn through vesting or unlock
}

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Enable serialization and debugging for instructions
pub enum TimeLockInstruction { // Enumerate every instruction this program supports
    InitializeLock { unlock_time: i64, guardian: Pubkey, vesting_start: i64, vesting_duration: i64 }, // Create a new vault with time and vesting parameters
    LockTokens { amount: u64 }, // Deposit tokens into an existing vault
    UnlockTokens, // Withdraw all tokens if the unlock time has passed
    CancelLock, // Allow the guardian to return all tokens to the owner before unlock
    ClaimVested, // Withdraw only the portion of tokens that have vested according to the schedule
}

fn process_instruction( // Define the main handler that the runtime invokes for every transaction
    _program_id: &Pubkey, // Accept the program ID even though this simple demo does not use it
    accounts: &[AccountInfo], // Receive the ordered array of accounts provided by the transaction
    instruction_data: &[u8], // Receive the raw instruction payload that determines which operation to run
) -> ProgramResult { // Return a typed result so the runtime knows if execution succeeded
    let instruction = TimeLockInstruction::try_from_slice(instruction_data) // Deserialize the instruction bytes into a typed enum
        .map_err(|_| ProgramError::InvalidInstructionData)?; // If deserialization fails, abort with a clear error code

    let account_info_iter = &mut accounts.iter(); // Create a mutable iterator to consume accounts in order
    let vault_account = next_account_info(account_info_iter)?; // Fetch the vault account because it holds the lock state
    let user = next_account_info(account_info_iter)?; // Fetch the user account to verify transaction authorization

    if !user.is_signer { // Reject the transaction if the user did not sign because state mutations require permission
        msg!("User must sign"); // Log the requirement so developers can debug signature failures
        return Err(ProgramError::MissingRequiredSignature); // Return the standard missing-signature error
    } // Close the signature check

    let mut vault = TimeLockVault::try_from_slice(&vault_account.data.borrow()) // Attempt to load existing vault state
        .unwrap_or(TimeLockVault { // Default to an empty vault if the account is uninitialized
            owner: Pubkey::default(), // Use the default pubkey as a sentinel for uninitialized state
            guardian: Pubkey::default(), // Use the default pubkey as a sentinel
            amount: 0, // Start with zero locked tokens
            unlock_time: 0, // Start with no unlock time
            vesting_start: 0, // Start with no vesting start
            vesting_duration: 0, // Start with no vesting duration
            claimed: 0, // Start with zero claimed tokens
        }); // Close the default vault initialization

    match instruction { // Branch execution based on which instruction variant was deserialized
        TimeLockInstruction::InitializeLock { unlock_time, guardian, vesting_start, vesting_duration } => { // Handle vault creation
            if vault.amount != 0 { // Prevent overwriting an existing vault to avoid destroying locked funds
                msg!("Vault already initialized"); // Log the conflict for debugging
                return Err(ProgramError::AccountAlreadyInitialized); // Return the standard already-initialized error
            } // Close the duplicate guard
            vault.owner = *user.key; // Set the transaction signer as the vault owner
            vault.guardian = guardian; // Store the guardian who can cancel the lock
            vault.unlock_time = unlock_time; // Store the absolute timestamp after which unlock is allowed
            vault.vesting_start = vesting_start; // Store when the linear vesting schedule begins
            vault.vesting_duration = vesting_duration; // Store how many seconds the vesting lasts
            vault.amount = 0; // Explicitly start with zero tokens until LockTokens is called
            vault.claimed = 0; // Explicitly start with zero claimed tokens
            vault.serialize(&mut &mut vault_account.data.borrow_mut()[..])?; // Persist the new vault state to the account
            msg!("Vault initialized: unlock={}, guardian={}", unlock_time, guardian); // Log the initialization parameters
        } // Close the InitializeLock arm
        TimeLockInstruction::LockTokens { amount } => { // Handle a user depositing tokens into the vault
            if vault.owner != *user.key { // Reject if the caller is not the vault owner
                msg!("Only vault owner can lock tokens"); // Log the unauthorized attempt
                return Err(ProgramError::IllegalOwner); // Return the standard illegal owner error
            } // Close the ownership check
            vault.amount = vault.amount.checked_add(amount) // Increase the locked amount by the deposit
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort if the addition overflows u64
            vault.serialize(&mut &mut vault_account.data.borrow_mut()[..])?; // Persist the updated balance
            msg!("Locked {} tokens, total={}", amount, vault.amount); // Log the deposit and new total
        } // Close the LockTokens arm
        TimeLockInstruction::UnlockTokens => { // Handle a user requesting full withdrawal after the unlock time
            if vault.owner != *user.key { // Reject if the caller is not the vault owner
                msg!("Only vault owner can unlock tokens"); // Log the unauthorized attempt
                return Err(ProgramError::IllegalOwner); // Return the standard illegal owner error
            } // Close the ownership check
            let clock = Clock::get()?; // Load the on-chain clock to get the current Unix timestamp
            if clock.unix_timestamp < vault.unlock_time { // Reject if the current time is before the unlock deadline
                msg!("Unlock time not reached: now={}, unlock={}", clock.unix_timestamp, vault.unlock_time); // Log the remaining time
                return Err(ProgramError::Custom(1)); // Return a custom error code to indicate the time lock is still active
            } // Close the time check
            let withdraw_amount = vault.amount.checked_sub(vault.claimed) // Compute the remaining unlocked tokens
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on underflow
            vault.claimed = vault.amount; // Mark all tokens as claimed because this is a full unlock
            vault.serialize(&mut &mut vault_account.data.borrow_mut()[..])?; // Persist the updated claimed amount
            msg!("Unlocked {} tokens at timestamp {}", withdraw_amount, clock.unix_timestamp); // Log the unlock event
        } // Close the UnlockTokens arm
        TimeLockInstruction::CancelLock => { // Handle a guardian canceling the lock before expiration
            if vault.guardian != *user.key { // Reject if the caller is not the authorized guardian
                msg!("Only guardian can cancel lock"); // Log the unauthorized attempt
                return Err(ProgramError::IllegalOwner); // Return the standard illegal owner error
            } // Close the guardian check
            let clock = Clock::get()?; // Load the on-chain clock to verify cancellation timing
            if clock.unix_timestamp >= vault.unlock_time { // Reject if the unlock time has already passed
                msg!("Lock already expired, cannot cancel"); // Log that the window has closed
                return Err(ProgramError::Custom(2)); // Return a custom error code for expired lock
            } // Close the expiration check
            let return_amount = vault.amount.checked_sub(vault.claimed) // Compute the remaining tokens to return
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on underflow
            vault.claimed = vault.amount; // Mark all tokens as returned to prevent double withdrawal
            vault.serialize(&mut &mut vault_account.data.borrow_mut()[..])?; // Persist the updated state
            msg!("Lock cancelled by guardian, returning {} tokens", return_amount); // Log the cancellation and return amount
        } // Close the CancelLock arm
        TimeLockInstruction::ClaimVested => { // Handle a user claiming tokens according to the vesting schedule
            if vault.owner != *user.key { // Reject if the caller is not the vault owner
                msg!("Only vault owner can claim vested tokens"); // Log the unauthorized attempt
                return Err(ProgramError::IllegalOwner); // Return the standard illegal owner error
            } // Close the ownership check
            let clock = Clock::get()?; // Load the on-chain clock to determine how much time has elapsed
            if clock.unix_timestamp < vault.vesting_start { // Reject if vesting has not yet started
                msg!("Vesting has not started"); // Log the premature claim attempt
                return Err(ProgramError::Custom(3)); // Return a custom error code for pre-cliff claims
            } // Close the pre-vesting check
            let elapsed = (clock.unix_timestamp - vault.vesting_start) as u64; // Calculate seconds since vesting began
            let duration = vault.vesting_duration as u64; // Convert vesting duration to u64 for ratio math
            if duration == 0 { // Avoid division by zero if vesting duration was not set
                msg!("Vesting duration is zero"); // Log the configuration error
                return Err(ProgramError::InvalidArgument); // Return invalid argument because the schedule is malformed
            } // Close the zero-duration guard
            let vested_ratio = std::cmp::min(elapsed, duration) as u128 // Cap elapsed time at duration to prevent over-vesting
                .checked_mul(1000) // Multiply by 1000 for fixed-point precision in the ratio
                .and_then(|v| v.checked_div(duration as u128)) // Divide by total duration to get the vested fraction
                .ok_or(ProgramError::ArithmeticOverflow)? as u64; // Cast back to u64
            let total_vested = ((vault.amount as u128) // Use u128 to prevent overflow
                .checked_mul(vested_ratio as u128) // Multiply total amount by the vested ratio
                .and_then(|v| v.checked_div(1000)) // Divide by the scaling factor to get the absolute vested amount
                .ok_or(ProgramError::ArithmeticOverflow)?) as u64; // Cast back to u64
            let claimable = total_vested.checked_sub(vault.claimed) // Calculate how many tokens are newly claimable
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on underflow
            if claimable == 0 { // Reject if there are no new tokens to claim
                msg!("No vested tokens available to claim"); // Log the empty claim attempt
                return Err(ProgramError::InsufficientFunds); // Return insufficient funds because nothing is available
            } // Close the zero-claimable check
            vault.claimed = vault.claimed.checked_add(claimable) // Increase the lifetime claimed counter
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on overflow
            vault.serialize(&mut &mut vault_account.data.borrow_mut()[..])?; // Persist the updated claimed amount
            msg!("Claimed {} vested tokens at timestamp {}", claimable, clock.unix_timestamp); // Log the claim event
        } // Close the ClaimVested arm
    } // Close the match block

    Ok(()) // Return success so the runtime finalizes the transaction
} // Close the process_instruction function
