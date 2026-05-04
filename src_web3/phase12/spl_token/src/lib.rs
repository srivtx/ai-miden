use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program::invoke,
    program_error::ProgramError,
    pubkey::Pubkey,
    system_instruction,
    sysvar::{rent::Rent, Sysvar},
};
use spl_token::instruction as token_instruction;
use spl_associated_token_account::instruction as ata_instruction;

// Define the program entrypoint so the Solana runtime routes instructions here
entrypoint!(process_instruction);

// Main instruction dispatcher for the SPL token demo program
pub fn process_instruction(
    program_id: &Pubkey,      // The public key of this deployed program
    accounts: &[AccountInfo], // All accounts passed by the client
    instruction_data: &[u8],  // Serialized instruction type and parameters
) -> ProgramResult {
    // Decode the instruction variant from the first byte
    let instruction = TokenDemoInstruction::unpack(instruction_data)?;

    // Route to the appropriate handler based on the decoded instruction
    match instruction {
        TokenDemoInstruction::CreateMint => {
            // Initialize a new SPL token mint
            process_create_mint(program_id, accounts)
        }
        TokenDemoInstruction::CreateTokenAccount => {
            // Create a standard token account for a specific mint and owner
            process_create_token_account(program_id, accounts)
        }
        TokenDemoInstruction::CreateAta => {
            // Create an Associated Token Account deterministically
            process_create_ata(program_id, accounts)
        }
        TokenDemoInstruction::MintTokens { amount } => {
            // Mint new tokens into a destination token account
            process_mint_tokens(program_id, accounts, amount)
        }
        TokenDemoInstruction::Transfer { amount } => {
            // Transfer tokens between two token accounts
            process_transfer(program_id, accounts, amount)
        }
    }
}

// Enumeration of all instructions supported by this demo program
pub enum TokenDemoInstruction {
    CreateMint,              // Initialize a new Mint account
    CreateTokenAccount,      // Initialize a new Token Account
    CreateAta,               // Initialize an Associated Token Account
    MintTokens { amount: u64 }, // Mint tokens to a token account
    Transfer { amount: u64 },   // Transfer tokens between accounts
}

impl TokenDemoInstruction {
    // Deserialize raw instruction bytes into a typed instruction variant
    pub fn unpack(input: &[u8]) -> Result<Self, ProgramError> {
        // Reject empty instruction data because we need at least a tag byte
        if input.is_empty() {
            return Err(ProgramError::InvalidInstructionData);
        }
        // Split the first byte as the variant tag and the rest as parameters
        let (tag, rest) = input.split_first().unwrap();
        match tag {
            0 => Ok(TokenDemoInstruction::CreateMint),       // No extra data
            1 => Ok(TokenDemoInstruction::CreateTokenAccount), // No extra data
            2 => Ok(TokenDemoInstruction::CreateAta),          // No extra data
            3 => {
                // MintTokens requires 8 bytes for the u64 amount
                if rest.len() != 8 {
                    return Err(ProgramError::InvalidInstructionData);
                }
                let amount = u64::from_le_bytes(rest.try_into().unwrap());
                Ok(TokenDemoInstruction::MintTokens { amount })
            }
            4 => {
                // Transfer requires 8 bytes for the u64 amount
                if rest.len() != 8 {
                    return Err(ProgramError::InvalidInstructionData);
                }
                let amount = u64::from_le_bytes(rest.try_into().unwrap());
                Ok(TokenDemoInstruction::Transfer { amount })
            }
            _ => Err(ProgramError::InvalidInstructionData), // Unknown tag
        }
    }
}

// Handler to create and initialize a new SPL token Mint account
fn process_create_mint(
    _program_id: &Pubkey, // Unused; mint initialization uses SPL Token program CPI
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();

    // The payer funds the creation of the Mint account and pays rent
    let payer_account = next_account_info(account_info_iter)?;
    // The new Mint account that will hold the token metadata
    let mint_account = next_account_info(account_info_iter)?;
    // The rent sysvar tells us the minimum lamports needed for rent exemption
    let rent_sysvar = next_account_info(account_info_iter)?;
    // The SPL Token program processes the initialization CPI
    let token_program = next_account_info(account_info_iter)?;

    // Only a signer can authorize the creation of a new Mint and pay for it
    if !payer_account.is_signer {
        msg!("Payer must sign to create mint");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // Load the rent sysvar to determine the exact lamports needed for the Mint
    let rent = Rent::from_account_info(rent_sysvar)?;
    let mint_space = spl_token::state::Mint::LEN; // 82 bytes for a Mint
    let required_lamports = rent.minimum_balance(mint_space);

    // CPI to the system program to create the Mint account with the right size
    invoke(
        &system_instruction::create_account(
            payer_account.key, // Funding account
            mint_account.key,  // New account to create
            required_lamports, // Rent-exempt lamports
            mint_space as u64, // Data length for a Mint
            token_program.key, // Owner will be the SPL Token program
        ),
        &[
            payer_account.clone(),
            mint_account.clone(),
        ],
    )?;

    // CPI to the SPL Token program to initialize the Mint with 6 decimals
    invoke(
        &token_instruction::initialize_mint(
            token_program.key,   // SPL Token program ID
            mint_account.key,    // Mint account to initialize
            payer_account.key,   // Mint authority
            Some(payer_account.key), // Freeze authority
            6,                   // Decimals
        )?,
        &[
            mint_account.clone(),
            rent_sysvar.clone(),
        ],
    )?;

    msg!("Mint created successfully with 6 decimals");
    Ok(())
}

// Handler to create a standard token account for a specific mint
fn process_create_token_account(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();

    // Payer funds the creation of the token account
    let payer_account = next_account_info(account_info_iter)?;
    // The new token account to initialize
    let token_account = next_account_info(account_info_iter)?;
    // The mint that this token account will hold balances for
    let mint_account = next_account_info(account_info_iter)?;
    // The owner who will control this token account
    let owner_account = next_account_info(account_info_iter)?;
    // Rent sysvar for calculating rent-exempt lamports
    let rent_sysvar = next_account_info(account_info_iter)?;
    // SPL Token program ID
    let token_program = next_account_info(account_info_iter)?;

    // Verify the payer signed to authorize account creation costs
    if !payer_account.is_signer {
        msg!("Payer must sign to create token account");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // Calculate rent-exempt balance for a token account (165 bytes)
    let rent = Rent::from_account_info(rent_sysvar)?;
    let token_space = spl_token::state::Account::LEN;
    let required_lamports = rent.minimum_balance(token_space);

    // CPI to system program to allocate the token account
    invoke(
        &system_instruction::create_account(
            payer_account.key,
            token_account.key,
            required_lamports,
            token_space as u64,
            token_program.key, // SPL Token program must own the account
        ),
        &[
            payer_account.clone(),
            token_account.clone(),
        ],
    )?;

    // CPI to SPL Token program to initialize the account with mint and owner
    invoke(
        &token_instruction::initialize_account(
            token_program.key,
            token_account.key,
            mint_account.key,
            owner_account.key,
        )?,
        &[
            token_account.clone(),
            mint_account.clone(),
            owner_account.clone(),
            rent_sysvar.clone(),
        ],
    )?;

    msg!("Token account created successfully");
    Ok(())
}

// Handler to create an Associated Token Account deterministically
fn process_create_ata(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();

    // Payer funds the ATA creation if it does not yet exist
    let payer_account = next_account_info(account_info_iter)?;
    // The ATA account address, derived from wallet and mint
    let ata_account = next_account_info(account_info_iter)?;
    // The wallet that will own the ATA
    let wallet_account = next_account_info(account_info_iter)?;
    // The mint for which the ATA is created
    let mint_account = next_account_info(account_info_iter)?;
    // System program needed to create the account if missing
    let system_program = next_account_info(account_info_iter)?;
    // SPL Token program ID
    let token_program = next_account_info(account_info_iter)?;
    // Associated Token Account program ID
    let ata_program = next_account_info(account_info_iter)?;

    // Only the payer can authorize lamport spending for account creation
    if !payer_account.is_signer {
        msg!("Payer must sign to create ATA");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // CPI to the Associated Token Account program to create the ATA
    // This instruction is idempotent: it succeeds even if the ATA already exists
    invoke(
        &ata_instruction::create_associated_token_account(
            payer_account.key,
            wallet_account.key,
            mint_account.key,
            token_program.key,
        ),
        &[
            payer_account.clone(),
            ata_account.clone(),
            wallet_account.clone(),
            mint_account.clone(),
            system_program.clone(),
            token_program.clone(),
            ata_program.clone(),
        ],
    )?;

    msg!("Associated token account created or already exists");
    Ok(())
}

// Handler to mint new tokens into a destination token account
fn process_mint_tokens(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();

    // The mint authority must sign to authorize increasing the supply
    let mint_authority = next_account_info(account_info_iter)?;
    // The Mint account whose supply will increase
    let mint_account = next_account_info(account_info_iter)?;
    // The destination token account that will receive the new tokens
    let destination_account = next_account_info(account_info_iter)?;
    // SPL Token program ID
    let token_program = next_account_info(account_info_iter)?;

    // Verify the mint authority signed, otherwise anyone could inflate supply
    if !mint_authority.is_signer {
        msg!("Mint authority must sign to mint tokens");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // CPI to the SPL Token program to mint tokens into the destination account
    invoke(
        &token_instruction::mint_to(
            token_program.key,
            mint_account.key,
            destination_account.key,
            mint_authority.key,
            &[], // No additional signers required
            amount,
        )?,
        &[
            mint_account.clone(),
            destination_account.clone(),
            mint_authority.clone(),
            token_program.clone(),
        ],
    )?;

    msg!("Minted {} tokens to destination account", amount);
    Ok(())
}

// Handler to transfer tokens from one token account to another
fn process_transfer(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();

    // The source token account owner who authorizes the transfer
    let source_owner = next_account_info(account_info_iter)?;
    // The source token account that holds the tokens being sent
    let source_account = next_account_info(account_info_iter)?;
    // The destination token account that will receive the tokens
    let destination_account = next_account_info(account_info_iter)?;
    // SPL Token program ID
    let token_program = next_account_info(account_info_iter)?;

    // The source owner must sign to prove they control the tokens
    if !source_owner.is_signer {
        msg!("Source owner must sign to transfer tokens");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // CPI to the SPL Token program to execute the transfer
    invoke(
        &token_instruction::transfer(
            token_program.key,
            source_account.key,
            destination_account.key,
            source_owner.key,
            &[], // No additional signers
            amount,
        )?,
        &[
            source_account.clone(),      // Writable because balance decreases
            destination_account.clone(), // Writable because balance increases
            source_owner.clone(),        // Signer authorization
            token_program.clone(),
        ],
    )?;

    msg!("Transferred {} tokens from source to destination", amount);
    Ok(())
}
