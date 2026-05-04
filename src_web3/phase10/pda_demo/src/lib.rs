use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program_error::ProgramError,
    pubkey::Pubkey,
    system_instruction,
    program::invoke_signed,
    sysvar::{rent::Rent, Sysvar},
};
use borsh::{BorshDeserialize, BorshSerialize};

/// Phase 10: PDA Demo Program
///
/// This program demonstrates Program Derived Addresses (PDAs):
/// - Each user gets their own PDA-derived counter account
/// - The PDA is derived from [user_pubkey, "counter", program_id]
/// - Only this program can sign for the PDA

// WHY: Register process_instruction as the runtime entrypoint.
entrypoint!(process_instruction);

// WHY: Define the state stored inside the PDA account.
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct UserCounter {
    pub count: u64,
}

// WHY: Define the available instructions for this program.
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub enum PdaInstruction {
    Initialize,
    Increment,
}

fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    // WHY: Deserialize the instruction to determine which operation to execute.
    let instruction = PdaInstruction::try_from_slice(instruction_data)
        .map_err(|_| ProgramError::InvalidInstructionData)?;

    // WHY: Create an iterator to safely extract accounts in the expected order.
    let account_info_iter = &mut accounts.iter();

    // WHY: The first account is the user who pays for and authorizes the operation.
    let user = next_account_info(account_info_iter)?;

    // WHY: The second account is the PDA that will hold the counter state.
    let pda_account = next_account_info(account_info_iter)?;

    // WHY: The third account is the System Program, needed for CPI to create accounts.
    let system_program = next_account_info(account_info_iter)?;

    // WHY: Derive the expected PDA from the user's pubkey and the seed "counter".
    // This ensures the provided account matches the deterministic address.
    let (expected_pda, bump_seed) = Pubkey::find_program_address(
        &[user.key.as_ref(), b"counter"],
        program_id,
    );

    // WHY: Verify that the PDA account passed in the transaction matches the derived address.
    // This prevents users from passing arbitrary accounts.
    if expected_pda != *pda_account.key {
        msg!("Invalid PDA");
        return Err(ProgramError::InvalidArgument);
    }

    // WHY: Route to the appropriate processor based on the instruction variant.
    match instruction {
        PdaInstruction::Initialize => {
            msg!("Instruction: Initialize PDA");

            // WHY: Fetch the Rent sysvar to calculate the minimum lamports for rent exemption.
            let rent = Rent::get()?;

            // WHY: Calculate the exact lamports needed for an 8-byte account to be rent-exempt.
            let rent_lamports = rent.minimum_balance(8);

            // WHY: Use invoke_signed to create the PDA account.
            // The runtime verifies the seeds + bump to authorize the program to sign for the PDA.
            invoke_signed(
                &system_instruction::create_account(
                    user.key,       // WHY: The user pays for the new account.
                    pda_account.key,// WHY: The address of the new account (the PDA).
                    rent_lamports,  // WHY: Fund it with exactly the rent-exempt minimum.
                    8,              // WHY: Allocate 8 bytes for one u64 counter value.
                    program_id,     // WHY: Set this program as the owner so it can write later.
                ),
                // WHY: Pass the accounts involved in the CPI. Order must match the instruction.
                &[user.clone(), pda_account.clone(), system_program.clone()],
                // WHY: Provide the seeds and bump so the runtime can verify PDA ownership.
                &[&[user.key.as_ref(), b"counter", &[bump_seed]]],
            )?;

            // WHY: Initialize the counter to 0 and serialize it into the new account.
            let counter = UserCounter { count: 0 };
            counter.serialize(&mut &mut pda_account.data.borrow_mut()[..])?;
            msg!("PDA initialized at {}", expected_pda);
        }
        PdaInstruction::Increment => {
            msg!("Instruction: Increment PDA Counter");

            // WHY: Deserialize the existing counter state from the PDA account.
            let mut counter = UserCounter::try_from_slice(&pda_account.data.borrow())?;

            // WHY: Increment the count by 1.
            counter.count += 1;

            // WHY: Serialize the updated state back into the PDA account.
            counter.serialize(&mut &mut pda_account.data.borrow_mut()[..])?;
            msg!("Counter incremented to {}", counter.count);
        }
    }

    // WHY: Return Ok to indicate the instruction completed successfully.
    Ok(())
}
