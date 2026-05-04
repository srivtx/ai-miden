use solana_program::{
    // WHY: Import AccountInfo so the program can inspect and modify on-chain accounts.
    account_info::{next_account_info, AccountInfo},
    // WHY: Import the entrypoint macro so Solana knows where execution begins.
    entrypoint,
    // WHY: Import ProgramResult as the standard success-or-error return type.
    entrypoint::ProgramResult,
    // WHY: Import msg for logging so developers can trace instruction execution.
    msg,
    // WHY: Import ProgramError for standard error codes.
    program_error::ProgramError,
    // WHY: Import Pubkey to identify accounts and store the oracle authority.
    pubkey::Pubkey,
    // WHY: Import Rent to verify accounts are rent-exempt.
    sysvar::rent::Rent,
    // WHY: Import Sysvar so Rent can be deserialized from the sysvar account.
    sysvar::Sysvar,
};
// WHY: Import Borsh for compact binary serialization.
use borsh::{BorshDeserialize, BorshSerialize};
// WHY: Import thiserror to define custom errors with minimal boilerplate.
use thiserror::Error;

// WHY: Register process_instruction as the program entrypoint.
entrypoint!(process_instruction);

// WHY: Define custom errors so clients receive clear failure messages.
#[derive(Error, Debug, Copy, Clone, PartialEq)]
pub enum OracleError {
    // WHY: Prevent re-initialization which would overwrite authority.
    #[error("Already initialized")]
    AlreadyInitialized,
    // WHY: Block operations on uninitialized accounts.
    #[error("Not initialized")]
    NotInitialized,
    // WHY: Enforce that only the designated authority can update prices.
    #[error("Unauthorized")]
    Unauthorized,
}

// WHY: Map OracleError into the standard ProgramError type.
impl From<OracleError> for ProgramError {
    fn from(e: OracleError) -> Self {
        ProgramError::Custom(e as u32)
    }
}

// WHY: Enumerate supported instructions so the entrypoint can route correctly.
#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)]
pub enum OracleInstruction {
    // WHY: Initialize creates the oracle state and assigns an authority.
    Initialize,
    // WHY: UpdatePrice changes the stored price for a collateral asset.
    UpdatePrice { price: u64, decimals: u8 },
}

// WHY: OracleState is the persistent account structure that holds price data.
#[derive(BorshSerialize, BorshDeserialize, Debug, Clone, Default)]
pub struct OracleState {
    // WHY: A flag distinguishes initialized accounts from empty ones.
    pub is_initialized: bool,
    // WHY: authority stores the public key allowed to mutate prices.
    pub authority: Pubkey,
    // WHY: price is the latest reported market price.
    pub price: u64,
    // WHY: decimals indicates the precision of the reported price.
    pub decimals: u8,
}

// WHY: The entrypoint deserializes the instruction and dispatches to the correct handler.
fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    // WHY: Parse the instruction payload to determine which operation to run.
    let instruction = OracleInstruction::try_from_slice(instruction_data)
        .map_err(|_| ProgramError::InvalidInstructionData)?;
    // WHY: Match each variant to its dedicated processor.
    match instruction {
        OracleInstruction::Initialize => process_initialize(program_id, accounts),
        OracleInstruction::UpdatePrice { price, decimals } => {
            process_update_price(program_id, accounts, price, decimals)
        }
    }
}

// WHY: process_initialize validates the account and sets up the oracle authority.
fn process_initialize(program_id: &Pubkey, accounts: &[AccountInfo]) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let oracle_account = next_account_info(account_info_iter)?;
    let authority = next_account_info(account_info_iter)?;
    let rent_info = next_account_info(account_info_iter)?;
    // WHY: Only the signer can initialize to prevent unauthorized state creation.
    if !authority.is_signer {
        return Err(OracleError::Unauthorized.into());
    }
    // WHY: Verify the account is owned by this program so data is trusted.
    if oracle_account.owner != program_id {
        return Err(ProgramError::IncorrectProgramId);
    }
    // WHY: Deserialize the rent sysvar to check the account meets rent-exempt requirements.
    let rent = Rent::from_account_info(rent_info)?;
    if !rent.is_exempt(oracle_account.lamports(), oracle_account.data_len()) {
        return Err(ProgramError::AccountNotRentExempt);
    }
    // WHY: Load existing data to verify the account has not already been initialized.
    let mut oracle_data = OracleState::try_from_slice(&oracle_account.data.borrow())?;
    if oracle_data.is_initialized {
        return Err(OracleError::AlreadyInitialized.into());
    }
    // WHY: Mark the account as initialized so subsequent instructions treat it as valid.
    oracle_data.is_initialized = true;
    // WHY: Store the authority so only this key can update prices later.
    oracle_data.authority = *authority.key;
    // WHY: Default price is zero until an explicit update is issued.
    oracle_data.price = 0;
    // WHY: Default decimals are zero until explicitly set.
    oracle_data.decimals = 0;
    // WHY: Serialize the state back to the account so it persists on-chain.
    oracle_data.serialize(&mut *oracle_account.data.borrow_mut())?;
    msg!("Oracle initialized");
    Ok(())
}

// WHY: process_update_price modifies the stored price after validating authority.
fn process_update_price(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    price: u64,
    decimals: u8,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let oracle_account = next_account_info(account_info_iter)?;
    let authority = next_account_info(account_info_iter)?;
    // WHY: Require the caller to sign so unauthorized price manipulation is impossible.
    if !authority.is_signer {
        return Err(OracleError::Unauthorized.into());
    }
    // WHY: Ensure the account is owned by this program to prevent spoofing.
    if oracle_account.owner != program_id {
        return Err(ProgramError::IncorrectProgramId);
    }
    // WHY: Load the current oracle state before modifying it.
    let mut oracle_data = OracleState::try_from_slice(&oracle_account.data.borrow())?;
    // WHY: Reject updates to uninitialized accounts to prevent writing garbage data.
    if !oracle_data.is_initialized {
        return Err(OracleError::NotInitialized.into());
    }
    // WHY: Verify the signer matches the stored authority to enforce access control.
    if oracle_data.authority != *authority.key {
        return Err(OracleError::Unauthorized.into());
    }
    // WHY: Update the price so lending instructions can value collateral accurately.
    oracle_data.price = price;
    // WHY: Update decimals so consumers know how to interpret the price magnitude.
    oracle_data.decimals = decimals;
    // WHY: Persist the new state on-chain.
    oracle_data.serialize(&mut *oracle_account.data.borrow_mut())?;
    msg!("Price updated to {} with {} decimals", price, decimals);
    Ok(())
}
