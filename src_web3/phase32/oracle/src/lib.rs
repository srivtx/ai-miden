use solana_program::{ // Import the Solana program library for building on-chain programs
    account_info::{next_account_info, AccountInfo}, // Import account iteration and info types for reading accounts
    entrypoint, // Import the entrypoint macro to declare the program start
    entrypoint::ProgramResult, // Import the result type used by instruction handlers
    msg, // Import logging function for emitting messages to transaction logs
    program_error::ProgramError, // Import standard error types for validation failures
    pubkey::Pubkey, // Import the public key type for addressing and ownership checks
}; // Close the solana_program import block
use borsh::{BorshDeserialize, BorshSerialize}; // Import serialization traits for reading and writing account data

entrypoint!(process_instruction); // Declare the program entry point so the Solana runtime knows where to begin execution

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Derive traits so PriceUpdate can be serialized into account data
pub struct PriceUpdate { // Define the on-chain structure representing a consumed price update
    pub asset: [u8; 32], // Store a 32-byte asset identifier hash to label which market this price represents
    pub price: i64, // Store the price as a signed 64-bit integer to handle negative values and large magnitudes
    pub confidence: u64, // Store the confidence interval as an unsigned value to measure spread between sources
    pub publish_slot: u64, // Record the slot when the price was published so we can detect staleness
    pub expo: i32, // Store the exponent as a signed 32-bit integer to shift the price into real-world decimals
} // Close the PriceUpdate struct definition

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Derive traits so LoanAccount can be serialized into account data
pub struct LoanAccount { // Define the on-chain state for a collateralized loan that depends on oracle prices
    pub owner: Pubkey, // Store the borrower's public key so only they can withdraw or repay
    pub collateral_amount: u64, // Track how many collateral tokens have been deposited
    pub borrowed_amount: u64, // Track how many stablecoins have been borrowed against the collateral
    pub last_price: i64, // Cache the last observed price to detect significant changes
    pub liquidation_threshold: u64, // Define the collateral ratio below which liquidation becomes allowed
} // Close the LoanAccount struct definition

pub fn process_instruction( // Define the main instruction router called by the Solana runtime
    program_id: &Pubkey, // Accept the program's own address to validate program-derived accounts
    accounts: &[AccountInfo], // Accept the ordered list of accounts provided by the transaction
    instruction_data: &[u8], // Accept the raw byte payload that determines which instruction to execute
) -> ProgramResult { // Return ProgramResult to indicate success or specific failure
    let instruction = instruction_data // Start parsing the instruction discriminator from the first byte
        .first() // Safely get the first byte without panicking on empty input
        .ok_or(ProgramError::InvalidInstructionData)?; // Return error if the payload is empty
    match instruction { // Branch execution based on the discriminator byte value
        0 => consume_price(program_id, accounts, instruction_data), // Route to price consumption if byte is 0
        1 => check_liquidation(program_id, accounts), // Route to liquidation check if byte is 1
        _ => Err(ProgramError::InvalidInstructionData), // Reject unknown discriminators to prevent undefined behavior
    } // Close the match block
} // Close the process_instruction function

fn consume_price( // Define the instruction handler that reads and stores an oracle price update
    program_id: &Pubkey, // Accept the program id for ownership validation
    accounts: &[AccountInfo], // Accept the accounts needed for price consumption
    instruction_data: &[u8], // Accept the payload containing the serialized price data
) -> ProgramResult { // Return ProgramResult to signal success or failure
    let account_info_iter = &mut accounts.iter(); // Create a mutable iterator to safely pull accounts in order
    let price_account = next_account_info(account_info_iter)?; // Get the account that stores the consumed price
    let oracle_account = next_account_info(account_info_iter)?; // Get the oracle account that provided the signed data
    if !price_account.is_writable { // Verify the destination account is writable so we can persist the update
        msg!("Price account must be writable"); // Log the failure reason for debugging
        return Err(ProgramError::InvalidAccountData); // Abort if the account cannot be modified
    } // Close the writable check
    let expected_oracle = Pubkey::new_from_array([ // Hardcode an example oracle program address for demonstration
        0u8, 0, 0, 0, 0, 0, 0, 0, // Zero-filled bytes represent a placeholder oracle program id
        0, 0, 0, 0, 0, 0, 0, 0, // Continue zero padding to fill 32 bytes
        0, 0, 0, 0, 0, 0, 0, 0, // Continue zero padding
        0, 0, 0, 0, 0, 0, 0, 0, // Finish the 32-byte public key array
    ]); // Close the placeholder oracle public key
    if oracle_account.owner != &expected_oracle { // Verify the oracle account is owned by the trusted oracle program
        msg!("Invalid oracle owner"); // Log why the validation failed
        return Err(ProgramError::IllegalOwner); // Abort if an untrusted account is passed as oracle
    } // Close the oracle owner check
    let publish_slot = instruction_data // Extract the published slot from the payload to verify freshness
        .get(1..9) // Read bytes 1 through 8 as a u64 slot number
        .and_then(|s| s.try_into().ok()) // Safely convert the slice to a fixed-size array
        .map(u64::from_le_bytes) // Convert little-endian bytes to a numeric slot value
        .unwrap_or(0); // Default to zero if the slot bytes are missing
    let current_slot = 1_000_000u64; // Use a placeholder current slot since we skip sysvar for simplicity
    if current_slot.saturating_sub(publish_slot) > 100 { // Reject prices older than 100 slots to prevent stale decisions
        msg!("Price is stale"); // Log the staleness rejection
        return Err(ProgramError::Custom(0)); // Use custom error 0 for stale price data
    } // Close the staleness check
    let price = instruction_data // Extract the price from bytes 9 through 17 of the payload
        .get(9..17) // Select the 8-byte slice representing the i64 price
        .and_then(|s| s.try_into().ok()) // Safely convert to a fixed-size array
        .map(i64::from_le_bytes) // Convert little-endian bytes to a signed 64-bit integer
        .unwrap_or(0); // Default to zero if the price bytes are missing
    let confidence = instruction_data // Extract the confidence from bytes 17 through 25
        .get(17..25) // Select the 8-byte slice representing the u64 confidence
        .and_then(|s| s.try_into().ok()) // Safely convert to a fixed-size array
        .map(u64::from_le_bytes) // Convert little-endian bytes to an unsigned 64-bit integer
        .unwrap_or(0); // Default to zero if confidence bytes are missing
    if confidence > (price.unsigned_abs() / 10) { // Reject prices where confidence exceeds 10% of the price value
        msg!("Confidence too high"); // Log the high-confidence rejection
        return Err(ProgramError::Custom(1)); // Use custom error 1 for unreliable price spreads
    } // Close the confidence check
    let price_update = PriceUpdate { // Construct the validated price update struct for storage
        asset: [0u8; 32], // Initialize asset identifier to zeros as a placeholder
        price, // Store the extracted and validated price
        confidence, // Store the extracted and validated confidence
        publish_slot, // Store the validated publish slot for future staleness checks
        expo: -8, // Set exponent to negative eight so the price represents values with eight decimal places
    }; // Close the PriceUpdate initialization
    price_update.serialize(&mut *price_account.data.borrow_mut())?; // Persist the validated price to the account
    msg!("Price consumed: {} with confidence {}", price, confidence); // Log the accepted price for indexers
    Ok(()) // Return success to signal the price was safely stored
} // Close the consume_price function

fn check_liquidation( // Define the instruction handler that evaluates whether a loan can be liquidated
    program_id: &Pubkey, // Accept the program id for validation
    accounts: &[AccountInfo], // Accept the accounts needed for liquidation evaluation
) -> ProgramResult { // Return ProgramResult to indicate success or failure
    let account_info_iter = &mut accounts.iter(); // Create an iterator to access accounts in order
    let loan_account = next_account_info(account_info_iter)?; // Get the loan account to read collateral and debt
    let price_account = next_account_info(account_info_iter)?; // Get the price account to read the current valuation
    let loan = LoanAccount::try_from_slice(&loan_account.data.borrow())?; // Deserialize the loan state
    let price_update = PriceUpdate::try_from_slice(&price_account.data.borrow())?; // Deserialize the consumed price
    let collateral_value = (loan.collateral_amount as i128) // Cast collateral to i128 to prevent overflow during multiplication
        .checked_mul(price_update.price as i128) // Multiply collateral amount by price to get raw value
        .ok_or(ProgramError::Custom(2))?; // Return custom error 2 if multiplication overflows
    let collateral_value_adjusted = collateral_value // Adjust the raw value by the price exponent
        .checked_div(10i128.pow(price_update.expo.abs() as u32)) // Divide by 10^8 to apply the decimal exponent
        .ok_or(ProgramError::Custom(3))?; // Return custom error 3 if division fails
    let threshold_value = (loan.borrowed_amount as i128) // Cast borrowed amount to i128 for safe math
        .checked_mul(loan.liquidation_threshold as i128) // Multiply debt by threshold percentage
        .ok_or(ProgramError::Custom(4))? // Return custom error 4 if multiplication overflows
        .checked_div(100) // Divide by 100 to convert the percentage into a proportional value
        .ok_or(ProgramError::Custom(5))?; // Return custom error 5 if division fails
    if collateral_value_adjusted < threshold_value { // Check if the collateral value has fallen below the safety threshold
        msg!("Loan eligible for liquidation"); // Log that the loan is underwater
        return Ok(()); // Return success because the check itself completed, allowing the caller to liquidate
    } // Close the undercollateralized check
    msg!("Loan is healthy"); // Log that the collateral still covers the debt adequately
    Ok(()) // Return success to signal the evaluation completed without errors
} // Close the check_liquidation function
