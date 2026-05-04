use solana_program::{ // Import the Solana program SDK to build on-chain logic
    account_info::{next_account_info, AccountInfo}, // Import account utilities to validate and iterate transaction accounts
    entrypoint, // Import the macro that registers the program's entry point with the runtime
    entrypoint::ProgramResult, // Import the typed result so we can return success or specific errors
    msg, // Import the logging utility to emit debug messages during execution
    program_error::ProgramError, // Import standard error types for clean failure reporting
    pubkey::Pubkey, // Import the Pubkey type for Solana address handling
};
use borsh::{BorshDeserialize, BorshSerialize}; // Import Borsh traits to read and write structured account data

/// Phase 17: Liquidity Pool Program
///
/// This program manages a two-token liquidity pool:
/// - InitializePool: Sets up the pool with initial reserves
/// - AddLiquidity: Deposits tokens and mints LP tokens
/// - RemoveLiquidity: Burns LP tokens and returns the proportional reserves

entrypoint!(process_instruction); // Register process_instruction as the function the Solana runtime calls

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Enable serialization and debugging for the pool state
pub struct LiquidityPool { // Define the on-chain data structure representing the pool
    pub reserve_a: u64, // Track the current amount of Token A held in the pool
    pub reserve_b: u64, // Track the current amount of Token B held in the pool
    pub total_lp_supply: u64, // Track the total number of LP tokens ever minted minus burned
}

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Enable serialization and debugging for instruction data
pub enum PoolInstruction { // Enumerate every instruction this program supports
    InitializePool { init_a: u64, init_b: u64 }, // Create a new pool and seed it with initial reserves
    AddLiquidity { amount_a: u64, amount_b: u64 }, // Deposit paired tokens and receive newly minted LP tokens
    RemoveLiquidity { lp_amount: u64 }, // Burn LP tokens and withdraw the corresponding share of reserves
}

fn process_instruction( // Define the main handler that the runtime invokes for every transaction
    _program_id: &Pubkey, // Accept the program ID even though this simple demo does not use it
    accounts: &[AccountInfo], // Receive the ordered array of accounts provided by the transaction
    instruction_data: &[u8], // Receive the raw instruction payload that determines which operation to run
) -> ProgramResult { // Return a typed result so the runtime knows if execution succeeded
    let instruction = PoolInstruction::try_from_slice(instruction_data) // Deserialize the instruction bytes into a typed enum
        .map_err(|_| ProgramError::InvalidInstructionData)?; // If deserialization fails, abort with a clear error code

    let account_info_iter = &mut accounts.iter(); // Create a mutable iterator to consume accounts in order
    let pool_account = next_account_info(account_info_iter)?; // Fetch the pool account because it stores the program state
    let user = next_account_info(account_info_iter)?; // Fetch the user account to verify transaction authorization

    if !user.is_signer { // Ensure the user signed the transaction because state mutations require permission
        msg!("User must sign"); // Log the requirement so developers can debug signature failures
        return Err(ProgramError::MissingRequiredSignature); // Return the standard missing-signature error
    } // Close the signature check

    let mut pool = LiquidityPool::try_from_slice(&pool_account.data.borrow()) // Load existing pool state from account storage
        .unwrap_or(LiquidityPool { reserve_a: 0, reserve_b: 0, total_lp_supply: 0 }); // Default to zeros if the account is uninitialized

    match instruction { // Branch to the correct handler based on the deserialized instruction variant
        PoolInstruction::InitializePool { init_a, init_b } => { // Handle the creation of a new liquidity pool
            if pool.total_lp_supply != 0 { // Prevent overwriting an existing pool because that would erase provider data
                msg!("Pool already initialized"); // Log the conflict so operators understand the failure
                return Err(ProgramError::AccountAlreadyInitialized); // Return the standard already-initialized error
            } // Close the duplicate-initialization guard
            pool.reserve_a = init_a; // Set the initial reserve for Token A
            pool.reserve_b = init_b; // Set the initial reserve for Token B
            pool.total_lp_supply = ((init_a as u128) * (init_b as u128)).sqrt() as u64; // Use geometric mean as initial LP supply for fairness
            pool.serialize(&mut &mut pool_account.data.borrow_mut()[..])?; // Persist the new state into the account data buffer
            msg!("Pool initialized: {} A, {} B, LP={}", init_a, init_b, pool.total_lp_supply); // Log the initialization details
        } // Close the InitializePool arm
        PoolInstruction::AddLiquidity { amount_a, amount_b } => { // Handle a user depositing liquidity into the pool
            if pool.total_lp_supply == 0 { // Reject deposits into an uninitialized pool because there is no baseline for shares
                msg!("Pool not initialized"); // Log the error for debugging
                return Err(ProgramError::UninitializedAccount); // Return the standard uninitialized error
            } // Close the uninitialized guard
            let lp_a = (amount_a as u128).checked_mul(pool.total_lp_supply as u128) // Calculate LP share based on Token A contribution
                .and_then(|v| v.checked_div(pool.reserve_a as u128)) // Divide by current reserve A to get proportional share
                .ok_or(ProgramError::ArithmeticOverflow)? as u64; // Abort if math overflows
            let lp_b = (amount_b as u128).checked_mul(pool.total_lp_supply as u128) // Calculate LP share based on Token B contribution
                .and_then(|v| v.checked_div(pool.reserve_b as u128)) // Divide by current reserve B to get proportional share
                .ok_or(ProgramError::ArithmeticOverflow)? as u64; // Abort if math overflows
            let lp_minted = std::cmp::min(lp_a, lp_b); // Take the minimum to prevent dilution from imbalanced deposits
            pool.reserve_a = pool.reserve_a.checked_add(amount_a) // Increase reserve A by the deposited amount
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on overflow
            pool.reserve_b = pool.reserve_b.checked_add(amount_b) // Increase reserve B by the deposited amount
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on overflow
            pool.total_lp_supply = pool.total_lp_supply.checked_add(lp_minted) // Expand the LP supply by the newly minted amount
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on overflow
            pool.serialize(&mut &mut pool_account.data.borrow_mut()[..])?; // Write the updated state back to the account
            msg!("Added {} A, {} B, minted {} LP", amount_a, amount_b, lp_minted); // Log the deposit and minting event
        } // Close the AddLiquidity arm
        PoolInstruction::RemoveLiquidity { lp_amount } => { // Handle a user withdrawing liquidity by burning LP tokens
            if pool.total_lp_supply == 0 { // Reject withdrawals from an empty pool because division by zero would occur
                msg!("Pool not initialized"); // Log the error so the failure reason is visible
                return Err(ProgramError::UninitializedAccount); // Return the standard uninitialized error
            } // Close the empty-pool guard
            let amount_a_out = (lp_amount as u128).checked_mul(pool.reserve_a as u128) // Compute the Token A share proportional to burned LP
                .and_then(|v| v.checked_div(pool.total_lp_supply as u128)) // Divide by total LP supply to get the exact share
                .ok_or(ProgramError::ArithmeticOverflow)? as u64; // Abort if the math overflows
            let amount_b_out = (lp_amount as u128).checked_mul(pool.reserve_b as u128) // Compute the Token B share proportional to burned LP
                .and_then(|v| v.checked_div(pool.total_lp_supply as u128)) // Divide by total LP supply to get the exact share
                .ok_or(ProgramError::ArithmeticOverflow)? as u64; // Abort if the math overflows
            pool.reserve_a = pool.reserve_a.checked_sub(amount_a_out) // Decrease reserve A by the withdrawn amount
                .ok_or(ProgramError::InsufficientFunds)?; // Abort if the pool somehow lacks enough tokens
            pool.reserve_b = pool.reserve_b.checked_sub(amount_b_out) // Decrease reserve B by the withdrawn amount
                .ok_or(ProgramError::InsufficientFunds)?; // Abort if the pool somehow lacks enough tokens
            pool.total_lp_supply = pool.total_lp_supply.checked_sub(lp_amount) // Shrink the LP supply by the burned amount
                .ok_or(ProgramError::InsufficientFunds)?; // Abort if the user tries to burn more LP than exists
            pool.serialize(&mut &mut pool_account.data.borrow_mut()[..])?; // Persist the reduced state to the account
            msg!("Removed {} LP, withdrew {} A, {} B", lp_amount, amount_a_out, amount_b_out); // Log the redemption details
        } // Close the RemoveLiquidity arm
    } // Close the match block

    Ok(()) // Return success so the runtime finalizes the transaction
} // Close the process_instruction function
