use solana_program::{ // Import the Solana program library to build the on-chain swap logic
    account_info::{next_account_info, AccountInfo}, // Import account iteration and info types for reading accounts
    entrypoint, // Import the entrypoint macro to declare where program execution begins
    entrypoint::ProgramResult, // Import the result type used by all instruction handlers
    msg, // Import logging function for emitting debug messages to transaction logs
    program::invoke, // Import the Cross-Program Invocation function for calling token programs
    program_error::ProgramError, // Import standard error types for validation failures
    pubkey::Pubkey, // Import the public key type for ownership and address validation
    sysvar::{clock::Clock, Sysvar}, // Import the clock sysvar to access on-chain time for deadline checks
}; // Close the solana_program import block
use borsh::{BorshDeserialize, BorshSerialize}; // Import serialization traits for storing state in account data

entrypoint!(process_instruction); // Declare the program entry point so the Solana runtime routes transactions here

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Derive traits so SwapParams can be deserialized from instruction data
pub struct SwapParams { // Define the user-provided parameters for a protected swap
    pub amount_in: u64, // Store how many input tokens the user wants to trade
    pub minimum_amount_out: u64, // Store the least output the user will accept to prevent excessive slippage
    pub deadline_slot: u64, // Store the last valid slot so stale transactions cannot execute later
} // Close the SwapParams struct definition

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Derive traits so PoolState can be serialized into account data
pub struct PoolState { // Define the on-chain state of the constant product liquidity pool
    pub token_a_reserve: u64, // Track the current balance of token A in the pool
    pub token_b_reserve: u64, // Track the current balance of token B in the pool
    pub fee_numerator: u64, // Store the fee numerator for calculating swap fees
    pub fee_denominator: u64, // Store the fee denominator so the fee is a proper fraction
} // Close the PoolState struct definition

pub fn process_instruction( // Define the main instruction router called by the Solana runtime
    program_id: &Pubkey, // Accept the program's own address to verify program-derived accounts
    accounts: &[AccountInfo], // Accept the ordered list of accounts passed by the transaction
    instruction_data: &[u8], // Accept the raw byte payload containing the instruction discriminator and parameters
) -> ProgramResult { // Return ProgramResult to indicate success or specific failure
    let instruction = instruction_data // Start parsing the instruction discriminator from the first byte
        .first() // Safely get the first byte without panicking on empty input
        .ok_or(ProgramError::InvalidInstructionData)?; // Return error if no instruction byte exists
    match instruction { // Branch execution based on the discriminator value
        0 => swap(program_id, accounts, instruction_data), // Route to swap if byte is 0
        _ => Err(ProgramError::InvalidInstructionData), // Reject unknown discriminators to prevent undefined behavior
    } // Close the match block
} // Close the process_instruction function

fn swap( // Define the swap instruction handler with slippage and deadline protection
    program_id: &Pubkey, // Accept the program id for ownership validation
    accounts: &[AccountInfo], // Accept the accounts required for the swap
    instruction_data: &[u8], // Accept the payload containing serialized swap parameters
) -> ProgramResult { // Return ProgramResult to signal success or failure
    let account_info_iter = &mut accounts.iter(); // Create a mutable iterator to safely pull accounts in order
    let pool_account = next_account_info(account_info_iter)?; // Get the pool state account to read reserves
    let user_account = next_account_info(account_info_iter)?; // Get the user's account to verify they signed
    let user_token_a = next_account_info(account_info_iter)?; // Get the user's token A account to debit
    let user_token_b = next_account_info(account_info_iter)?; // Get the user's token B account to credit
    let token_program = next_account_info(account_info_iter)?; // Get the SPL token program for CPI transfers
    if !user_account.is_signer { // Verify the user signed the transaction to prevent unauthorized swaps
        msg!("User must sign"); // Log the failure reason for debugging
        return Err(ProgramError::MissingRequiredSignature); // Abort if the required signature is absent
    } // Close the signature check
    let clock = Clock::get()?; // Fetch the current on-chain slot for deadline validation
    let params = SwapParams::try_from_slice(&instruction_data[1..])?; // Deserialize swap params after the discriminator byte
    if clock.slot > params.deadline_slot { // Reject the transaction if the current slot exceeds the user's deadline
        msg!("Transaction expired"); // Inform the client that the deadline has passed
        return Err(ProgramError::Custom(0)); // Use custom error 0 for expired transactions
    } // Close the deadline check
    let mut pool = PoolState::try_from_slice(&pool_account.data.borrow())?; // Deserialize the pool state from chain
    if pool.token_a_reserve == 0 || pool.token_b_reserve == 0 { // Reject swaps against empty pools to prevent division by zero
        msg!("Pool has no liquidity"); // Log the specific failure
        return Err(ProgramError::Custom(1)); // Use custom error 1 for empty pool state
    } // Close the liquidity check
    let amount_in_with_fee = (params.amount_in as u128) // Cast amount to u128 to prevent overflow during fee math
        .checked_mul(pool.fee_numerator as u128) // Multiply input by fee numerator to compute fee portion
        .ok_or(ProgramError::Custom(2))? // Use custom error 2 if multiplication overflows
        .checked_div(pool.fee_denominator as u128) // Divide by denominator to apply the fee fraction
        .ok_or(ProgramError::Custom(3))?; // Use custom error 3 if division fails
    let amount_in_after_fee = (params.amount_in as u128) // Cast again for safe arithmetic
        .checked_sub(amount_in_with_fee) // Subtract the fee from the input to get the tradable amount
        .ok_or(ProgramError::Custom(4))?; // Use custom error 4 if subtraction underflows
    let numerator = amount_in_after_fee // Compute the numerator of the constant product output formula
        .checked_mul(pool.token_b_reserve as u128) // Multiply tradable input by the output reserve
        .ok_or(ProgramError::Custom(5))?; // Use custom error 5 if multiplication overflows
    let denominator = (pool.token_a_reserve as u128) // Compute the denominator of the output formula
        .checked_add(amount_in_after_fee) // Add the tradable input to the input reserve
        .ok_or(ProgramError::Custom(6))?; // Use custom error 6 if addition overflows
    let amount_out = numerator // Divide numerator by denominator to find the output amount
        .checked_div(denominator) // Perform the division to solve constant product math
        .ok_or(ProgramError::Custom(7))? // Use custom error 7 if division fails
        as u64; // Cast the result back to u64 for token transfer amounts
    if amount_out < params.minimum_amount_out { // Reject the swap if the output falls below the user's slippage tolerance
        msg!("Slippage exceeded: expected at least {}, got {}", params.minimum_amount_out, amount_out); // Log the failure
        return Err(ProgramError::Custom(8)); // Use custom error 8 for slippage violations
    } // Close the slippage check
    pool.token_a_reserve = pool.token_a_reserve // Update the input reserve by adding the user's full input amount
        .checked_add(params.amount_in) // Safely add the input tokens to the pool
        .ok_or(ProgramError::Custom(9))?; // Use custom error 9 if reserve overflows
    pool.token_b_reserve = pool.token_b_reserve // Update the output reserve by subtracting the tokens sent to user
        .checked_sub(amount_out) // Safely subtract the output tokens from the pool
        .ok_or(ProgramError::Custom(10))?; // Use custom error 10 if reserve underflows
    pool.serialize(&mut *pool_account.data.borrow_mut())?; // Persist the updated pool reserves to the account
    msg!("Swap executed: {} in, {} out", params.amount_in, amount_out); // Log the successful swap for transparency
    Ok(()) // Return success to signal the protected swap completed
} // Close the swap function
