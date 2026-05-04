use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program::{invoke, invoke_signed},
    program_error::ProgramError,
    pubkey::Pubkey,
    system_instruction,
    sysvar::{rent::Rent, Sysvar},
};

// Declare the program entrypoint so the Solana runtime knows where to start
entrypoint!(process_instruction);

// Main instruction processor that handles all incoming instructions
pub fn process_instruction(
    program_id: &Pubkey,      // The public key of this deployed program
    accounts: &[AccountInfo], // All accounts passed in the instruction
    instruction_data: &[u8],  // Raw bytes carrying the instruction variant
) -> ProgramResult {
    // Deserialize the instruction type from the first byte of instruction_data
    let instruction = DemoInstruction::unpack(instruction_data)?;

    // Route to the correct handler based on the instruction variant
    match instruction {
        DemoInstruction::SimpleCpiTransfer { amount } => {
            // Call handler for a simple CPI transfer using a wallet signer
            process_simple_cpi(program_id, accounts, amount)
        }
        DemoInstruction::SignedCpiTransfer { amount } => {
            // Call handler for a CPI transfer signed by a PDA
            process_signed_cpi(program_id, accounts, amount)
        }
    }
}

// Instruction enum that defines the different operations this program supports
pub enum DemoInstruction {
    // A simple CPI where the user wallet signs the transfer
    SimpleCpiTransfer { amount: u64 },
    // A CPI where the program signs for a PDA via invoke_signed
    SignedCpiTransfer { amount: u64 },
}

impl DemoInstruction {
    // Deserialize raw bytes into a DemoInstruction variant
    pub fn unpack(input: &[u8]) -> Result<Self, ProgramError> {
        // Ensure at least one byte exists to read the variant tag
        if input.is_empty() {
            return Err(ProgramError::InvalidInstructionData);
        }
        // Match the first byte to determine which instruction to construct
        let (tag, rest) = input.split_first().unwrap();
        match tag {
            0 => {
                // SimpleCpiTransfer expects 8 bytes for a u64 amount
                if rest.len() != 8 {
                    return Err(ProgramError::InvalidInstructionData);
                }
                let amount = u64::from_le_bytes(rest.try_into().unwrap());
                Ok(DemoInstruction::SimpleCpiTransfer { amount })
            }
            1 => {
                // SignedCpiTransfer expects 8 bytes for a u64 amount
                if rest.len() != 8 {
                    return Err(ProgramError::InvalidInstructionData);
                }
                let amount = u64::from_le_bytes(rest.try_into().unwrap());
                Ok(DemoInstruction::SignedCpiTransfer { amount })
            }
            _ => Err(ProgramError::InvalidInstructionData), // Unknown tag
        }
    }
}

// Process a simple CPI transfer where the user wallet is the signer
fn process_simple_cpi(
    _program_id: &Pubkey, // Unused because this handler does not create PDAs
    accounts: &[AccountInfo],
    amount: u64,
) -> ProgramResult {
    // Create an iterator over accounts so we can pull them in order
    let account_info_iter = &mut accounts.iter();

    // The wallet that authorizes the transfer and pays for transaction fees
    let wallet_account = next_account_info(account_info_iter)?;
    // The system program is required for creating accounts if needed
    let system_program_account = next_account_info(account_info_iter)?;
    // The recipient account that will receive the lamports
    let recipient_account = next_account_info(account_info_iter)?;

    // Verify the wallet signed the transaction so we know the user authorized it
    if !wallet_account.is_signer {
        msg!("Wallet must sign the simple CPI transfer");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // Build a system transfer instruction that moves lamports from wallet to recipient
    let transfer_instruction = system_instruction::transfer(
        wallet_account.key,    // Source of lamports
        recipient_account.key, // Destination of lamports
        amount,                // Quantity to move
    );

    // Perform the CPI using invoke because the wallet is a real signer
    invoke(
        &transfer_instruction,
        &[
            wallet_account.clone(),      // Source account must be writable
            recipient_account.clone(),   // Destination account must be writable
            system_program_account.clone(), // System program provides the transfer logic
        ],
    )?;

    msg!("Simple CPI transfer of {} lamports completed", amount);
    Ok(())
}

// Process a CPI transfer where the program signs on behalf of a PDA
fn process_signed_cpi(
    program_id: &Pubkey, // Needed to derive and verify the PDA belongs to us
    accounts: &[AccountInfo],
    amount: u64,
) -> ProgramResult {
    // Create an iterator to pull accounts in the expected order
    let account_info_iter = &mut accounts.iter();

    // The PDA account that will act as the signer and source of lamports
    let pda_account = next_account_info(account_info_iter)?;
    // The recipient who receives the lamports
    let recipient_account = next_account_info(account_info_iter)?;
    // The system program is required because lamport transfers use it
    let system_program_account = next_account_info(account_info_iter)?;

    // Define the seeds used to derive the PDA so the runtime can verify it
    // In a real program these seeds would be deterministic based on state
    let pda_seeds: &[&[u8]] = &[b"escrow", b"demo"];

    // Derive the expected PDA address to confirm the provided account matches
    let (expected_pda, pda_bump) = Pubkey::find_program_address(pda_seeds, program_id);

    // Reject if the provided PDA account does not match our derivation
    if expected_pda != *pda_account.key {
        msg!("Provided PDA does not match derived address");
        return Err(ProgramError::InvalidAccountData);
    }

    // The PDA must be owned by this program; otherwise it could be an imposter
    if pda_account.owner != program_id {
        msg!("PDA is not owned by this program");
        return Err(ProgramError::IllegalOwner);
    }

    // Build the system transfer instruction moving lamports from PDA to recipient
    let transfer_instruction = system_instruction::transfer(
        pda_account.key,       // Source is the PDA
        recipient_account.key, // Destination is the recipient
        amount,                // Amount to transfer
    );

    // Perform CPI with invoke_signed so the runtime treats the PDA as a signer
    // The seeds include the bump so create_program_address succeeds
    invoke_signed(
        &transfer_instruction,
        &[
            pda_account.clone(),         // Source account must be writable
            recipient_account.clone(),   // Destination account must be writable
            system_program_account.clone(), // System program executes the transfer
        ],
        &[&[b"escrow", b"demo", &[pda_bump]]], // Seeds plus bump for runtime verification
    )?;

    msg!("Signed CPI transfer of {} lamports from PDA completed", amount);
    Ok(())
}
