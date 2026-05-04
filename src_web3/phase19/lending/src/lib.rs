use solana_program::{ // Import the Solana program SDK to build on-chain lending logic
    account_info::{next_account_info, AccountInfo}, // Import utilities to iterate and validate transaction accounts
    entrypoint, // Import the macro to register the program's main entry point
    entrypoint::ProgramResult, // Import the typed result for success and error returns
    msg, // Import the logging utility to emit debug messages during execution
    program_error::ProgramError, // Import standard error types for clean failure reporting
    pubkey::Pubkey, // Import the Pubkey type for Solana address handling
};
use borsh::{BorshDeserialize, BorshSerialize}; // Import Borsh traits to read and write structured account data

/// Phase 19: Lending Protocol Program
///
/// This program manages collateralized lending:
/// - DepositCollateral: Locks collateral and credits the user's account
/// - Borrow: Allows borrowing against collateral up to a health factor threshold
/// - Repay: Returns borrowed funds and reduces debt
/// - Liquidate: Repays debt for an unhealthy borrower and seizes collateral

entrypoint!(process_instruction); // Register process_instruction as the function the Solana runtime calls

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Enable serialization and debugging for user positions
pub struct UserPosition { // Define the on-chain state for an individual borrower or lender
    pub collateral: u64, // Amount of collateral tokens deposited by the user
    pub debt: u64, // Amount of borrowed tokens currently owed by the user
    pub collateral_value: u64, // Cached dollar value of collateral for health factor checks
}

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Enable serialization and debugging for the market state
pub struct LendingMarket { // Define the global on-chain state for the lending protocol
    pub liquidation_threshold: u64, // Percentage below which liquidation is triggered, scaled by 100 for precision
    pub ltv_ratio: u64, // Maximum loan-to-value ratio allowed, scaled by 100 for precision
    pub total_collateral: u64, // Sum of all collateral deposited across all users
    pub total_debt: u64, // Sum of all debt borrowed across all users
}

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Enable serialization and debugging for instruction data
pub enum LendingInstruction { // Enumerate every instruction this program supports
    DepositCollateral { amount: u64, collateral_price: u64 }, // Lock collateral and record its current dollar value
    Borrow { amount: u64 }, // Borrow tokens if the user's health factor remains above one
    Repay { amount: u64 }, // Return borrowed tokens and reduce the user's debt
    Liquidate { borrower: Pubkey, repay_amount: u64 }, // Repay a borrower's debt and seize proportional collateral
}

fn process_instruction( // Define the main handler that the runtime invokes for every transaction
    _program_id: &Pubkey, // Accept the program ID even though this simple demo does not use it
    accounts: &[AccountInfo], // Receive the ordered array of accounts provided by the transaction
    instruction_data: &[u8], // Receive the raw instruction payload that determines which operation to run
) -> ProgramResult { // Return a typed result so the runtime knows if execution succeeded
    let instruction = LendingInstruction::try_from_slice(instruction_data) // Deserialize the instruction bytes into a typed enum
        .map_err(|_| ProgramError::InvalidInstructionData)?; // If deserialization fails, abort with a clear error code

    let account_info_iter = &mut accounts.iter(); // Create a mutable iterator to consume accounts in order
    let market_account = next_account_info(account_info_iter)?; // Fetch the global market account for protocol parameters
    let user = next_account_info(account_info_iter)?; // Fetch the user account to verify transaction authorization

    if !user.is_signer { // Reject the transaction if the user did not sign because state mutations require permission
        msg!("User must sign"); // Log the requirement so developers can debug signature failures
        return Err(ProgramError::MissingRequiredSignature); // Return the standard missing-signature error
    } // Close the signature check

    let mut market = LendingMarket::try_from_slice(&market_account.data.borrow()) // Load existing market state from account storage
        .unwrap_or(LendingMarket { // Default to safe parameters if the account is uninitialized
            liquidation_threshold: 120, // Require 120% collateral ratio before liquidation
            ltv_ratio: 75, // Allow borrowing up to 75% of collateral value
            total_collateral: 0, // Start with zero global collateral
            total_debt: 0, // Start with zero global debt
        }); // Close the default market initialization

    match instruction { // Branch execution based on which instruction variant was deserialized
        LendingInstruction::DepositCollateral { amount, collateral_price } => { // Handle a user locking collateral into the protocol
            let user_position_account = next_account_info(account_info_iter)?; // Fetch the user's position account to store their data
            let mut position = UserPosition::try_from_slice(&user_position_account.data.borrow()) // Attempt to load the user's existing position
                .unwrap_or(UserPosition { collateral: 0, debt: 0, collateral_value: 0 }); // Default to empty if uninitialized
            position.collateral = position.collateral.checked_add(amount) // Increase the user's collateral balance
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort if the addition overflows u64
            let added_value = (amount as u128).checked_mul(collateral_price as u128) // Compute the dollar value of the deposited collateral
                .and_then(|v| v.checked_div(1_000_000)) // Divide by a scaling factor because price uses fixed-point math
                .ok_or(ProgramError::ArithmeticOverflow)? as u64; // Cast back to u64 for storage
            position.collateral_value = position.collateral_value.checked_add(added_value) // Increase the cached collateral value
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on overflow
            position.serialize(&mut &mut user_position_account.data.borrow_mut()[..])?; // Persist the updated position to the account
            market.total_collateral = market.total_collateral.checked_add(amount) // Increase the global collateral tracker
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on overflow
            market.serialize(&mut &mut market_account.data.borrow_mut()[..])?; // Persist the updated market totals
            msg!("Deposited {} collateral, value={}", amount, added_value); // Log the deposit with computed value
        } // Close the DepositCollateral arm
        LendingInstruction::Borrow { amount } => { // Handle a user borrowing tokens against their collateral
            let user_position_account = next_account_info(account_info_iter)?; // Fetch the user's position account
            let mut position = UserPosition::try_from_slice(&user_position_account.data.borrow())?; // Deserialize the user's position
            let max_borrow = (position.collateral_value as u128) // Use u128 to prevent overflow during multiplication
                .checked_mul(market.ltv_ratio as u128) // Multiply collateral value by the allowed LTV ratio
                .and_then(|v| v.checked_div(100)) // Divide by 100 because LTV is stored as a percentage
                .ok_or(ProgramError::ArithmeticOverflow)? as u64; // Cast back to u64 for comparison
            if position.debt.checked_add(amount).ok_or(ProgramError::ArithmeticOverflow)? > max_borrow { // Reject if the new debt would exceed the LTV limit
                msg!("Borrow exceeds LTV limit: max={}", max_borrow); // Log the limit so the user knows why it failed
                return Err(ProgramError::InsufficientFunds); // Return insufficient funds because the collateral cannot cover the request
            } // Close the LTV check
            position.debt = position.debt.checked_add(amount) // Increase the user's debt by the borrowed amount
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on overflow
            position.serialize(&mut &mut user_position_account.data.borrow_mut()[..])?; // Persist the updated position
            market.total_debt = market.total_debt.checked_add(amount) // Increase the global debt tracker
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on overflow
            market.serialize(&mut &mut market_account.data.borrow_mut()[..])?; // Persist the updated market totals
            msg!("Borrowed {} against collateral value {}", amount, position.collateral_value); // Log the borrow event
        } // Close the Borrow arm
        LendingInstruction::Repay { amount } => { // Handle a user returning borrowed tokens
            let user_position_account = next_account_info(account_info_iter)?; // Fetch the user's position account
            let mut position = UserPosition::try_from_slice(&user_position_account.data.borrow())?; // Deserialize the user's position
            if amount > position.debt { // Reject if the user tries to repay more than they owe
                msg!("Repay amount exceeds debt"); // Log the overpayment attempt
                return Err(ProgramError::InvalidArgument); // Return invalid argument because the amount is nonsensical
            } // Close the overpayment check
            position.debt = position.debt.checked_sub(amount) // Decrease the user's debt by the repaid amount
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort if subtraction underflows
            position.serialize(&mut &mut user_position_account.data.borrow_mut()[..])?; // Persist the updated position
            market.total_debt = market.total_debt.checked_sub(amount) // Decrease the global debt tracker
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on underflow
            market.serialize(&mut &mut market_account.data.borrow_mut()[..])?; // Persist the updated market totals
            msg!("Repaid {}, remaining debt {}", amount, position.debt); // Log the repayment with remaining balance
        } // Close the Repay arm
        LendingInstruction::Liquidate { borrower: _borrower, repay_amount } => { // Handle a third party repaying an unhealthy borrower's debt
            let liquidator = user; // The transaction signer is the liquidator
            let borrower_position_account = next_account_info(account_info_iter)?; // Fetch the borrower's position account
            let mut position = UserPosition::try_from_slice(&borrower_position_account.data.borrow())?; // Deserialize the borrower's position
            let health_factor = if position.debt == 0 { // Avoid division by zero if the borrower somehow has no debt
                u64::MAX // Set health factor to maximum because a debt-free position is perfectly safe
            } else { // If there is debt, calculate the health factor normally
                (position.collateral_value as u128) // Use u128 to prevent overflow
                    .checked_mul(market.liquidation_threshold as u128) // Multiply collateral value by the threshold percentage
                    .and_then(|v| v.checked_div(100)) // Divide by 100 because the threshold is stored as a percentage
                    .and_then(|v| v.checked_div(position.debt as u128)) // Divide by total debt to get the ratio
                    .ok_or(ProgramError::ArithmeticOverflow)? as u64 // Cast back to u64 for comparison
            }; // Close the health factor calculation
            if health_factor >= 1 { // Reject if the borrower's health factor is still safe
                msg!("Position is healthy, cannot liquidate: hf={}", health_factor); // Log the health factor for debugging
                return Err(ProgramError::InvalidArgument); // Return invalid argument because liquidation is not permitted
            } // Close the health check
            if repay_amount > position.debt { // Reject if the liquidator tries to repay more than the total debt
                msg!("Repay amount exceeds borrower debt"); // Log the excessive repayment attempt
                return Err(ProgramError::InvalidArgument); // Return invalid argument
            } // Close the repay amount check
            let collateral_to_seize = (repay_amount as u128) // Use u128 for safe intermediate math
                .checked_mul(105) // Multiply by 105 to give the liquidator a 5% bonus on the collateral seized
                .and_then(|v| v.checked_div(100)) // Divide by 100 to apply the percentage bonus
                .ok_or(ProgramError::ArithmeticOverflow)? as u64; // Cast back to u64
            if collateral_to_seize > position.collateral { // Reject if the seizure would exceed the borrower's collateral
                msg!("Collateral to seize exceeds borrower collateral"); // Log the shortfall
                return Err(ProgramError::InsufficientFunds); // Return insufficient funds
            } // Close the collateral check
            position.debt = position.debt.checked_sub(repay_amount) // Reduce the borrower's debt by the repaid amount
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on underflow
            position.collateral = position.collateral.checked_sub(collateral_to_seize) // Reduce the borrower's collateral by the seized amount
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on underflow
            position.collateral_value = (position.collateral as u128) // Recalculate the cached collateral value after seizure
                .checked_mul(position.collateral_value as u128) // Use the previous value as a proxy for price
                .and_then(|v| v.checked_div((position.collateral.checked_add(collateral_to_seize).unwrap_or(1)) as u128)) // Approximate the new value
                .ok_or(ProgramError::ArithmeticOverflow)? as u64; // Cast back to u64
            position.serialize(&mut &mut borrower_position_account.data.borrow_mut()[..])?; // Persist the updated borrower position
            market.total_debt = market.total_debt.checked_sub(repay_amount) // Decrease global debt by the repaid amount
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on underflow
            market.total_collateral = market.total_collateral.checked_sub(collateral_to_seize) // Decrease global collateral by the seized amount
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on underflow
            market.serialize(&mut &mut market_account.data.borrow_mut()[..])?; // Persist the updated market totals
            msg!("Liquidated {} debt, seized {} collateral", repay_amount, collateral_to_seize); // Log the liquidation event
            msg!("Liquidator: {}", liquidator.key); // Log the liquidator's address for transparency
        } // Close the Liquidate arm
    } // Close the match block

    Ok(()) // Return success so the runtime finalizes the transaction
} // Close the process_instruction function
