use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program_error::ProgramError,
    pubkey::Pubkey,
};
use borsh::{BorshDeserialize, BorshSerialize};

/// Phase 9: Counter Program
///
/// This program stores a counter value in a data account.
/// Instructions:
/// - Initialize: Creates the counter with value 0
/// - Increment: Increments the counter by 1

// WHY: Register process_instruction as the runtime entrypoint.
entrypoint!(process_instruction);

// WHY: Define the state struct that will be serialized into account data.
// BorshSerialize converts it to bytes; BorshDeserialize reconstructs it.
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct Counter {
    pub count: u64,
}

// WHY: Define an enum representing the different instructions this program accepts.
// Borsh encodes enums as a discriminant byte followed by variant data.
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub enum CounterInstruction {
    Initialize,
    Increment,
}

fn process_instruction(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    // WHY: Deserialize the first bytes into a CounterInstruction to know which operation to run.
    let instruction = CounterInstruction::try_from_slice(instruction_data)
        .map_err(|_| ProgramError::InvalidInstructionData)?;

    // WHY: Create an iterator over accounts so we can safely extract them in order.
    let account_info_iter = &mut accounts.iter();

    // WHY: Pull the first account from the iterator. This is the counter data account.
    let counter_account = next_account_info(account_info_iter)?;

    // WHY: Use a match statement to route to the correct logic based on the instruction variant.
    match instruction {
        CounterInstruction::Initialize => {
            // WHY: Log the instruction so explorers and debuggers can follow execution.
            msg!("Instruction: Initialize");

            // WHY: Create a new Counter with count set to 0.
            let mut counter = Counter { count: 0 };

            // WHY: Serialize the counter struct into the account's raw byte data.
            // The account must be writable and properly sized for this to succeed.
            counter.serialize(&mut &mut counter_account.data.borrow_mut()[..])?;

            // WHY: Log the initialization so it appears in transaction logs.
            msg!("Counter initialized to 0");
        }
        CounterInstruction::Increment => {
            msg!("Instruction: Increment");

            // WHY: Deserialize the existing bytes from the account into a Counter struct.
            let mut counter = Counter::try_from_slice(&counter_account.data.borrow())?;

            // WHY: Mutate the count field in memory.
            counter.count += 1;

            // WHY: Write the updated struct back into the account's byte data.
            counter.serialize(&mut &mut counter_account.data.borrow_mut()[..])?;

            // WHY: Log the new value for debugging and verification.
            msg!("Counter incremented to {}", counter.count);
        }
    }

    // WHY: Return Ok to signal that the instruction executed successfully.
    Ok(())
}
