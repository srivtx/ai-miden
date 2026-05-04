use borsh::{BorshDeserialize, BorshSerialize};
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    clock::Clock,
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program::{invoke, invoke_signed},
    program_error::ProgramError,
    pubkey::Pubkey,
    system_instruction,
    sysvar::{rent::Rent, Sysvar},
};
use spl_token::instruction as token_instruction;

// Define the program entrypoint so the Solana runtime routes instructions here
entrypoint!(process_instruction);

// Main instruction dispatcher for the escrow program
pub fn process_instruction(
    program_id: &Pubkey,      // Public key of this deployed escrow program
    accounts: &[AccountInfo], // All accounts provided in the instruction
    instruction_data: &[u8],  // Serialized instruction type and parameters
) -> ProgramResult {
    // Deserialize the instruction variant from raw bytes
    let instruction = EscrowInstruction::unpack(instruction_data)?;

    // Route to the appropriate handler based on the instruction variant
    match instruction {
        EscrowInstruction::Initialize {
            amount_a,
            amount_b,
            expiry,
        } => {
            // Create a new escrow with defined trade terms
            process_initialize(program_id, accounts, amount_a, amount_b, expiry)
        }
        EscrowInstruction::DepositA => {
            // Party A deposits their tokens into the escrow
            process_deposit_a(program_id, accounts)
        }
        EscrowInstruction::DepositB => {
            // Party B deposits their tokens into the escrow
            process_deposit_b(program_id, accounts)
        }
        EscrowInstruction::Release => {
            // Release tokens to both parties if both have deposited
            process_release(program_id, accounts)
        }
        EscrowInstruction::Cancel => {
            // Cancel the escrow and return any deposited funds
            process_cancel(program_id, accounts)
        }
    }
}

// Enumeration of all instructions supported by the escrow program
pub enum EscrowInstruction {
    Initialize {
        amount_a: u64, // Amount party A must deposit
        amount_b: u64, // Amount party B must deposit
        expiry: i64,   // Unix timestamp after which the escrow can be canceled
    },
    DepositA,  // Party A deposits their side of the trade
    DepositB,  // Party B deposits their side of the trade
    Release,   // Distribute tokens to both parties when conditions are met
    Cancel,    // Return deposited tokens and close the escrow
}

impl EscrowInstruction {
    // Deserialize raw instruction bytes into a typed instruction variant
    pub fn unpack(input: &[u8]) -> Result<Self, ProgramError> {
        // Require at least one byte for the variant tag
        if input.is_empty() {
            return Err(ProgramError::InvalidInstructionData);
        }
        let (tag, rest) = input.split_first().unwrap();
        match tag {
            0 => {
                // Initialize expects 8 + 8 + 8 = 24 bytes
                if rest.len() != 24 {
                    return Err(ProgramError::InvalidInstructionData);
                }
                let amount_a = u64::from_le_bytes(rest[0..8].try_into().unwrap());
                let amount_b = u64::from_le_bytes(rest[8..16].try_into().unwrap());
                let expiry = i64::from_le_bytes(rest[16..24].try_into().unwrap());
                Ok(EscrowInstruction::Initialize {
                    amount_a,
                    amount_b,
                    expiry,
                })
            }
            1 => Ok(EscrowInstruction::DepositA),
            2 => Ok(EscrowInstruction::DepositB),
            3 => Ok(EscrowInstruction::Release),
            4 => Ok(EscrowInstruction::Cancel),
            _ => Err(ProgramError::InvalidInstructionData),
        }
    }
}

// Borsh-serializable state stored in the escrow state account
#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)]
pub struct EscrowState {
    // Public key of party A who deposits token A
    pub party_a: Pubkey,
    // Public key of party B who deposits token B
    pub party_b: Pubkey,
    // SPL mint of token A
    pub mint_a: Pubkey,
    // SPL mint of token B
    pub mint_b: Pubkey,
    // Required deposit amount from party A
    pub amount_a: u64,
    // Required deposit amount from party B
    pub amount_b: u64,
    // Unix timestamp after which either party can cancel
    pub expiry: i64,
    // Current deposited amount from party A
    pub deposited_a: u64,
    // Current deposited amount from party B
    pub deposited_b: u64,
    // Whether the escrow has been initialized
    pub is_initialized: bool,
    // Whether the escrow has been released or canceled
    pub is_closed: bool,
}

// Handler to initialize a new escrow trade
fn process_initialize(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount_a: u64,
    amount_b: u64,
    expiry: i64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();

    // Payer funds the creation of the escrow state account
    let payer_account = next_account_info(account_info_iter)?;
    // The escrow state account that will persist trade terms
    let escrow_account = next_account_info(account_info_iter)?;
    // Party A's wallet address
    let party_a = next_account_info(account_info_iter)?;
    // Party B's wallet address
    let party_b = next_account_info(account_info_iter)?;
    // Mint of token A
    let mint_a = next_account_info(account_info_iter)?;
    // Mint of token B
    let mint_b = next_account_info(account_info_iter)?;
    // Rent sysvar for rent exemption calculation
    let rent_sysvar = next_account_info(account_info_iter)?;
    // System program to create the escrow state account
    let system_program = next_account_info(account_info_iter)?;

    // Only the payer can authorize the creation of the escrow account
    if !payer_account.is_signer {
        msg!("Payer must sign to initialize escrow");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // Derive a PDA for the escrow state to make the address predictable
    let escrow_seeds = &[
        b"escrow",
        party_a.key.as_ref(),
        party_b.key.as_ref(),
    ];
    let (expected_escrow_pda, escrow_bump) =
        Pubkey::find_program_address(escrow_seeds, program_id);

    // Reject if the provided escrow account does not match the derived PDA
    if expected_escrow_pda != *escrow_account.key {
        msg!("Invalid escrow account address");
        return Err(ProgramError::InvalidAccountData);
    }

    // Calculate rent-exempt balance for the escrow state account size
    let rent = Rent::from_account_info(rent_sysvar)?;
    let state_space = EscrowState::default().try_to_vec().unwrap().len();
    let required_lamports = rent.minimum_balance(state_space);

    // CPI to system program to create the escrow state PDA account
    invoke_signed(
        &system_instruction::create_account(
            payer_account.key,
            escrow_account.key,
            required_lamports,
            state_space as u64,
            program_id, // Escrow program owns the state account
        ),
        &[
            payer_account.clone(),
            escrow_account.clone(),
            system_program.clone(),
        ],
        &[&[
            b"escrow",
            party_a.key.as_ref(),
            party_b.key.as_ref(),
            &[escrow_bump],
        ]],
    )?;

    // Construct the initial escrow state with the trade terms
    let escrow_state = EscrowState {
        party_a: *party_a.key,
        party_b: *party_b.key,
        mint_a: *mint_a.key,
        mint_b: *mint_b.key,
        amount_a,
        amount_b,
        expiry,
        deposited_a: 0,
        deposited_b: 0,
        is_initialized: true,
        is_closed: false,
    };

    // Serialize the escrow state into the account data for on-chain persistence
    escrow_state.serialize(&mut &mut escrow_account.data.borrow_mut()[..])?;

    msg!("Escrow initialized between {} and {}", party_a.key, party_b.key);
    Ok(())
}

// Handler for party A to deposit tokens into the escrow
fn process_deposit_a(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();

    // Party A must sign to authorize moving their tokens
    let party_a = next_account_info(account_info_iter)?;
    // Escrow state account tracks the deposit
    let escrow_account = next_account_info(account_info_iter)?;
    // Party A's token account that holds the tokens being deposited
    let party_a_ata = next_account_info(account_info_iter)?;
    // Escrow's token account that will receive the deposit for token A
    let escrow_ata_a = next_account_info(account_info_iter)?;
    // SPL Token program processes the transfer
    let token_program = next_account_info(account_info_iter)?;

    // Verify that party A signed the transaction
    if !party_a.is_signer {
        msg!("Party A must sign to deposit");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // Deserialize the escrow state to validate and update it
    let mut escrow_state = EscrowState::try_from_slice(&escrow_account.data.borrow())?;

    // Ensure the escrow is active and not already closed
    if !escrow_state.is_initialized || escrow_state.is_closed {
        msg!("Escrow is not active");
        return Err(ProgramError::InvalidAccountData);
    }

    // Only the designated party A can deposit for side A
    if escrow_state.party_a != *party_a.key {
        msg!("Signer is not party A");
        return Err(ProgramError::IllegalOwner);
    }

    // Prevent double depositing for side A
    if escrow_state.deposited_a > 0 {
        msg!("Party A has already deposited");
        return Err(ProgramError::InvalidArgument);
    }

    // CPI to SPL Token program to transfer tokens from party A to escrow
    invoke(
        &token_instruction::transfer(
            token_program.key,
            party_a_ata.key,
            escrow_ata_a.key,
            party_a.key,
            &[],
            escrow_state.amount_a,
        )?,
        &[
            party_a_ata.clone(),
            escrow_ata_a.clone(),
            party_a.clone(),
            token_program.clone(),
        ],
    )?;

    // Update the escrow state to reflect party A's deposit
    escrow_state.deposited_a = escrow_state.amount_a;
    escrow_state.serialize(&mut &mut escrow_account.data.borrow_mut()[..])?;

    msg!("Party A deposited {} tokens", escrow_state.amount_a);
    Ok(())
}

// Handler for party B to deposit tokens into the escrow
fn process_deposit_b(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();

    // Party B must sign to authorize moving their tokens
    let party_b = next_account_info(account_info_iter)?;
    // Escrow state account tracks the deposit
    let escrow_account = next_account_info(account_info_iter)?;
    // Party B's token account that holds the tokens being deposited
    let party_b_ata = next_account_info(account_info_iter)?;
    // Escrow's token account that will receive the deposit for token B
    let escrow_ata_b = next_account_info(account_info_iter)?;
    // SPL Token program processes the transfer
    let token_program = next_account_info(account_info_iter)?;

    // Verify that party B signed the transaction
    if !party_b.is_signer {
        msg!("Party B must sign to deposit");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // Deserialize the escrow state to validate and update it
    let mut escrow_state = EscrowState::try_from_slice(&escrow_account.data.borrow())?;

    // Ensure the escrow is active and not already closed
    if !escrow_state.is_initialized || escrow_state.is_closed {
        msg!("Escrow is not active");
        return Err(ProgramError::InvalidAccountData);
    }

    // Only the designated party B can deposit for side B
    if escrow_state.party_b != *party_b.key {
        msg!("Signer is not party B");
        return Err(ProgramError::IllegalOwner);
    }

    // Prevent double depositing for side B
    if escrow_state.deposited_b > 0 {
        msg!("Party B has already deposited");
        return Err(ProgramError::InvalidArgument);
    }

    // CPI to SPL Token program to transfer tokens from party B to escrow
    invoke(
        &token_instruction::transfer(
            token_program.key,
            party_b_ata.key,
            escrow_ata_b.key,
            party_b.key,
            &[],
            escrow_state.amount_b,
        )?,
        &[
            party_b_ata.clone(),
            escrow_ata_b.clone(),
            party_b.clone(),
            token_program.clone(),
        ],
    )?;

    // Update the escrow state to reflect party B's deposit
    escrow_state.deposited_b = escrow_state.amount_b;
    escrow_state.serialize(&mut &mut escrow_account.data.borrow_mut()[..])?;

    msg!("Party B deposited {} tokens", escrow_state.amount_b);
    Ok(())
}

// Handler to release tokens to both parties when both have deposited
fn process_release(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();

    // Either party can trigger release once conditions are met
    let signer = next_account_info(account_info_iter)?;
    // Escrow state account holding trade terms and deposit status
    let escrow_account = next_account_info(account_info_iter)?;
    // Escrow's token account holding token A
    let escrow_ata_a = next_account_info(account_info_iter)?;
    // Escrow's token account holding token B
    let escrow_ata_b = next_account_info(account_info_iter)?;
    // Party A's token account that will receive token B
    let party_a_ata = next_account_info(account_info_iter)?;
    // Party B's token account that will receive token A
    let party_b_ata = next_account_info(account_info_iter)?;
    // SPL Token program for both transfer CPIs
    let token_program = next_account_info(account_info_iter)?;

    // Deserialize the escrow state to check deposit status
    let mut escrow_state = EscrowState::try_from_slice(&escrow_account.data.borrow())?;

    // Ensure the escrow is active
    if !escrow_state.is_initialized || escrow_state.is_closed {
        msg!("Escrow is not active");
        return Err(ProgramError::InvalidAccountData);
    }

    // Verify that both parties have fully deposited their required amounts
    if escrow_state.deposited_a != escrow_state.amount_a
        || escrow_state.deposited_b != escrow_state.amount_b
    {
        msg!("Both parties must deposit before release");
        return Err(ProgramError::InvalidArgument);
    }

    // Derive the escrow PDA seeds so the program can sign for the escrow ATAs
    let escrow_seeds = &[
        b"escrow",
        escrow_state.party_a.as_ref(),
        escrow_state.party_b.as_ref(),
    ];
    let (expected_escrow_pda, escrow_bump) =
        Pubkey::find_program_address(escrow_seeds, program_id);

    // Verify the provided escrow account matches the derived address
    if expected_escrow_pda != *escrow_account.key {
        msg!("Invalid escrow account");
        return Err(ProgramError::InvalidAccountData);
    }

    // CPI to transfer token B from escrow to party A using invoke_signed
    invoke_signed(
        &token_instruction::transfer(
            token_program.key,
            escrow_ata_b.key,
            party_a_ata.key,
            &expected_escrow_pda,
            &[],
            escrow_state.amount_b,
        )?,
        &[
            escrow_ata_b.clone(),
            party_a_ata.clone(),
            escrow_account.clone(),
            token_program.clone(),
        ],
        &[&[
            b"escrow",
            escrow_state.party_a.as_ref(),
            escrow_state.party_b.as_ref(),
            &[escrow_bump],
        ]],
    )?;

    // CPI to transfer token A from escrow to party B using invoke_signed
    invoke_signed(
        &token_instruction::transfer(
            token_program.key,
            escrow_ata_a.key,
            party_b_ata.key,
            &expected_escrow_pda,
            &[],
            escrow_state.amount_a,
        )?,
        &[
            escrow_ata_a.clone(),
            party_b_ata.clone(),
            escrow_account.clone(),
            token_program.clone(),
        ],
        &[&[
            b"escrow",
            escrow_state.party_a.as_ref(),
            escrow_state.party_b.as_ref(),
            &[escrow_bump],
        ]],
    )?;

    // Mark the escrow as closed so it cannot be released again
    escrow_state.is_closed = true;
    escrow_state.serialize(&mut &mut escrow_account.data.borrow_mut()[..])?;

    msg!("Escrow released. Party A received token B, Party B received token A.");
    Ok(())
}

// Handler to cancel the escrow and return any deposited funds
fn process_cancel(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();

    // Either party or a designated canceler can initiate cancellation
    let signer = next_account_info(account_info_iter)?;
    // Escrow state account holding deposit records
    let escrow_account = next_account_info(account_info_iter)?;
    // Escrow's token account for token A
    let escrow_ata_a = next_account_info(account_info_iter)?;
    // Escrow's token account for token B
    let escrow_ata_b = next_account_info(account_info_iter)?;
    // Party A's token account to receive returned token A
    let party_a_ata = next_account_info(account_info_iter)?;
    // Party B's token account to receive returned token B
    let party_b_ata = next_account_info(account_info_iter)?;
    // SPL Token program for return transfers
    let token_program = next_account_info(account_info_iter)?;
    // Clock sysvar to check if expiry has been reached
    let clock_sysvar = next_account_info(account_info_iter)?;

    // Deserialize the escrow state to check status and deposits
    let mut escrow_state = EscrowState::try_from_slice(&escrow_account.data.borrow())?;

    // Ensure the escrow is active
    if !escrow_state.is_initialized || escrow_state.is_closed {
        msg!("Escrow is not active");
        return Err(ProgramError::InvalidAccountData);
    }

    // Load the current time to enforce the expiry condition
    let clock = Clock::from_account_info(clock_sysvar)?;

    // Cancellation is only allowed after the expiry time has passed
    if clock.unix_timestamp < escrow_state.expiry {
        msg!(
            "Cannot cancel before expiry. Expiry: {}, Now: {}",
            escrow_state.expiry,
            clock.unix_timestamp
        );
        return Err(ProgramError::Custom(2)); // Custom error for early cancel
    }

    // Derive the escrow PDA seeds for signing returns
    let escrow_seeds = &[
        b"escrow",
        escrow_state.party_a.as_ref(),
        escrow_state.party_b.as_ref(),
    ];
    let (expected_escrow_pda, escrow_bump) =
        Pubkey::find_program_address(escrow_seeds, program_id);

    // Verify the escrow account matches the expected derived address
    if expected_escrow_pda != *escrow_account.key {
        msg!("Invalid escrow account");
        return Err(ProgramError::InvalidAccountData);
    }

    // Return party A's deposit if it exists
    if escrow_state.deposited_a > 0 {
        invoke_signed(
            &token_instruction::transfer(
                token_program.key,
                escrow_ata_a.key,
                party_a_ata.key,
                &expected_escrow_pda,
                &[],
                escrow_state.deposited_a,
            )?,
            &[
                escrow_ata_a.clone(),
                party_a_ata.clone(),
                escrow_account.clone(),
                token_program.clone(),
            ],
            &[&[
                b"escrow",
                escrow_state.party_a.as_ref(),
                escrow_state.party_b.as_ref(),
                &[escrow_bump],
            ]],
        )?;
    }

    // Return party B's deposit if it exists
    if escrow_state.deposited_b > 0 {
        invoke_signed(
            &token_instruction::transfer(
                token_program.key,
                escrow_ata_b.key,
                party_b_ata.key,
                &expected_escrow_pda,
                &[],
                escrow_state.deposited_b,
            )?,
            &[
                escrow_ata_b.clone(),
                party_b_ata.clone(),
                escrow_account.clone(),
                token_program.clone(),
            ],
            &[&[
                b"escrow",
                escrow_state.party_a.as_ref(),
                escrow_state.party_b.as_ref(),
                &[escrow_bump],
            ]],
        )?;
    }

    // Mark the escrow as closed after returning all funds
    escrow_state.is_closed = true;
    escrow_state.serialize(&mut &mut escrow_account.data.borrow_mut()[..])?;

    msg!("Escrow canceled and funds returned");
    Ok(())
}

impl Default for EscrowState {
    // Provide a default EscrowState so we can compute its serialized size
    fn default() -> Self {
        EscrowState {
            party_a: Pubkey::default(),
            party_b: Pubkey::default(),
            mint_a: Pubkey::default(),
            mint_b: Pubkey::default(),
            amount_a: 0,
            amount_b: 0,
            expiry: 0,
            deposited_a: 0,
            deposited_b: 0,
            is_initialized: false,
            is_closed: false,
        }
    }
}
