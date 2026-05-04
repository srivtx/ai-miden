use solana_program::{ // Import the Solana program SDK so we can write on-chain logic
    account_info::{next_account_info, AccountInfo}, // Need these to iterate through and validate accounts passed by the runtime
    entrypoint, // Import the entrypoint macro to register our program's main entry point
    entrypoint::ProgramResult, // Import ProgramResult for typed success and failure returns
    msg, // Import msg so we can log debug messages to the Solana runtime logs
    program_error::ProgramError, // Import ProgramError for typed error handling
    pubkey::Pubkey, // Import Pubkey for Solana public key types
};
use borsh::{BorshDeserialize, BorshSerialize}; // Import Borsh traits to serialize and deserialize account data

/// Phase 16: AMM Program
///
/// This program implements a constant product AMM (x * y = k) on Solana.
/// Instructions:
/// - Initialize: Creates a pool with initial reserves
/// - SwapAforB: Swaps token A for token B
/// - SwapBforA: Swaps token B for token A

entrypoint!(process_instruction); // Register process_instruction as the program's entry point so the runtime calls it

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Enable Borsh serialization and Debug printing for the pool state
pub struct AmmPool { // Define the on-chain state structure for our AMM pool
    pub token_a_reserve: u64, // Track how many Token A are currently in the pool
    pub token_b_reserve: u64, // Track how many Token B are currently in the pool
    pub k: u128, // Store the constant product; use u128 to prevent overflow when multiplying two u64 values
}

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Enable Borsh serialization and Debug printing for instructions
pub enum AmmInstruction { // Define all possible instructions this program can execute
    Initialize { init_a: u64, init_b: u64 }, // Create a new pool with starting reserves for both tokens
    SwapAforB { amount_in: u64 }, // Trade Token A into the pool to receive Token B out
    SwapBforA { amount_in: u64 }, // Trade Token B into the pool to receive Token A out
}

fn process_instruction( // Define the main instruction handler that the Solana runtime invokes
    _program_id: &Pubkey, // Accept the program ID even though we don't need it for this simple logic
    accounts: &[AccountInfo], // Accept the array of accounts passed by the transaction signer
    instruction_data: &[u8], // Accept the raw binary payload that encodes which instruction to run
) -> ProgramResult { // Return ProgramResult to indicate success or a specific error code
    let instruction = AmmInstruction::try_from_slice(instruction_data) // Deserialize the instruction payload using Borsh
        .map_err(|_| ProgramError::InvalidInstructionData)?; // If deserialization fails, return an invalid data error

    let account_info_iter = &mut accounts.iter(); // Create a mutable iterator so we can consume accounts in order
    let pool_account = next_account_info(account_info_iter)?; // Get the pool account first because it holds the state
    let user = next_account_info(account_info_iter)?; // Get the user account so we can verify they signed the transaction

    if !user.is_signer { // Reject the transaction if the user did not sign because state changes require authorization
        msg!("User must sign"); // Log the failure reason so developers can debug permission issues
        return Err(ProgramError::MissingRequiredSignature); // Return the standard missing signature error
    }

    let mut pool = AmmPool::try_from_slice(&pool_account.data.borrow()) // Attempt to load existing pool state from account data
        .unwrap_or(AmmPool { token_a_reserve: 0, token_b_reserve: 0, k: 0 }); // If uninitialized, default to zero reserves and zero k

    match instruction { // Branch execution based on which instruction variant was deserialized
        AmmInstruction::Initialize { init_a, init_b } => { // Handle pool initialization with starting token amounts
            if pool.k != 0 { // Prevent re-initialization because overwriting an active pool would destroy user funds
                msg!("Pool already initialized"); // Log the error so operators know why the transaction failed
                return Err(ProgramError::AccountAlreadyInitialized); // Return the standard already-initialized error
            }
            let k = (init_a as u128).checked_mul(init_b as u128) // Compute k = x * y using checked math to prevent overflow
                .ok_or(ProgramError::ArithmeticOverflow)?; // If multiplication overflows, abort with a clear error
            pool.token_a_reserve = init_a; // Set the initial reserve for Token A
            pool.token_b_reserve = init_b; // Set the initial reserve for Token B
            pool.k = k; // Store the constant product so future swaps can enforce it
            pool.serialize(&mut &mut pool_account.data.borrow_mut()[..])?; // Write the updated state back to the account data buffer
            msg!("Pool initialized: {} A, {} B, k={}", init_a, init_b, k); // Log success with all initial parameters
        }
        AmmInstruction::SwapAforB { amount_in } => { // Handle a swap where the user sends Token A and receives Token B
            let new_a = pool.token_a_reserve.checked_add(amount_in) // Calculate the new reserve of A after adding the input
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort if the addition overflows u64
            let new_b = (pool.k / new_a as u128) as u64; // Derive the new B reserve by enforcing k / new_a = new_b
            let amount_out = pool.token_b_reserve.checked_sub(new_b) // Compute how much B leaves the pool
                .ok_or(ProgramError::InsufficientFunds)?; // Abort if the math somehow requests more B than exists
            pool.token_a_reserve = new_a; // Update the A reserve to reflect the tokens deposited by the trader
            pool.token_b_reserve = new_b; // Update the B reserve to reflect the tokens withdrawn for the trader
            pool.serialize(&mut &mut pool_account.data.borrow_mut()[..])?; // Persist the new reserve values to the account
            msg!("Swapped {} A for {} B", amount_in, amount_out); // Log the trade details for indexers and debugging
        }
        AmmInstruction::SwapBforA { amount_in } => { // Handle a swap where the user sends Token B and receives Token A
            let new_b = pool.token_b_reserve.checked_add(amount_in) // Calculate the new reserve of B after adding the input
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort if the addition overflows u64
            let new_a = (pool.k / new_b as u128) as u64; // Derive the new A reserve by enforcing k / new_b = new_a
            let amount_out = pool.token_a_reserve.checked_sub(new_a) // Compute how much A leaves the pool
                .ok_or(ProgramError::InsufficientFunds)?; // Abort if the math somehow requests more A than exists
            pool.token_b_reserve = new_b; // Update the B reserve to reflect the tokens deposited by the trader
            pool.token_a_reserve = new_a; // Update the A reserve to reflect the tokens withdrawn for the trader
            pool.serialize(&mut &mut pool_account.data.borrow_mut()[..])?; // Persist the new reserve values to the account
            msg!("Swapped {} B for {} A", amount_in, amount_out); // Log the trade details for indexers and debugging
        }
    }

    Ok(()) // Return success so the runtime knows the instruction completed without errors
}
