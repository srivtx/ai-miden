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

// Define the program entrypoint so Solana runtime routes instructions here
entrypoint!(process_instruction);

// Main instruction dispatcher for the vault program
pub fn process_instruction(
    program_id: &Pubkey,      // Public key of this deployed vault program
    accounts: &[AccountInfo], // All accounts provided in the instruction
    instruction_data: &[u8],  // Serialized instruction type and parameters
) -> ProgramResult {
    // Deserialize the instruction variant from raw bytes
    let instruction = VaultInstruction::unpack(instruction_data)?;

    // Route to the correct handler based on the instruction variant
    match instruction {
        VaultInstruction::Initialize { authority } => {
            // Set up a new vault with an owner and optional unlock time
            process_initialize(program_id, accounts, authority)
        }
        VaultInstruction::Deposit { amount } => {
            // Move tokens from user ATA into vault PDA ATA
            process_deposit(program_id, accounts, amount)
        }
        VaultInstruction::Withdraw { amount } => {
            // Move tokens from vault PDA ATA back to user ATA if rules pass
            process_withdraw(program_id, accounts, amount)
        }
        VaultInstruction::SetUnlockTime { unlock_time } => {
            // Admin function to change when withdrawals become allowed
            process_set_unlock_time(program_id, accounts, unlock_time)
        }
    }
}

// Enumeration of all instructions supported by the vault program
pub enum VaultInstruction {
    Initialize { authority: Pubkey }, // Create vault state with an authority
    Deposit { amount: u64 },          // Deposit tokens into the vault
    Withdraw { amount: u64 },         // Withdraw tokens from the vault
    SetUnlockTime { unlock_time: i64 }, // Update the unlock timestamp
}

impl VaultInstruction {
    // Deserialize raw bytes into a typed instruction variant
    pub fn unpack(input: &[u8]) -> Result<Self, ProgramError> {
        // Require at least one byte for the variant tag
        if input.is_empty() {
            return Err(ProgramError::InvalidInstructionData);
        }
        let (tag, rest) = input.split_first().unwrap();
        match tag {
            0 => {
                // Initialize expects 32 bytes for a Pubkey authority
                if rest.len() != 32 {
                    return Err(ProgramError::InvalidInstructionData);
                }
                let authority = Pubkey::new(rest);
                Ok(VaultInstruction::Initialize { authority })
            }
            1 => {
                // Deposit expects 8 bytes for a u64 amount
                if rest.len() != 8 {
                    return Err(ProgramError::InvalidInstructionData);
                }
                let amount = u64::from_le_bytes(rest.try_into().unwrap());
                Ok(VaultInstruction::Deposit { amount })
            }
            2 => {
                // Withdraw expects 8 bytes for a u64 amount
                if rest.len() != 8 {
                    return Err(ProgramError::InvalidInstructionData);
                }
                let amount = u64::from_le_bytes(rest.try_into().unwrap());
                Ok(VaultInstruction::Withdraw { amount })
            }
            3 => {
                // SetUnlockTime expects 8 bytes for an i64 timestamp
                if rest.len() != 8 {
                    return Err(ProgramError::InvalidInstructionData);
                }
                let unlock_time = i64::from_le_bytes(rest.try_into().unwrap());
                Ok(VaultInstruction::SetUnlockTime { unlock_time })
            }
            _ => Err(ProgramError::InvalidInstructionData),
        }
    }
}

// Borsh-serializable state stored in the vault state account
#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)]
pub struct VaultState {
    // The public key that controls this vault and can withdraw
    pub authority: Pubkey,
    // The SPL token mint that this vault accepts
    pub mint: Pubkey,
    // Unix timestamp after which withdrawals are permitted
    pub unlock_time: i64,
    // Total amount of tokens currently held in the vault
    pub total_deposited: u64,
    // Whether the vault has been initialized to prevent reinitialization
    pub is_initialized: bool,
}

// Handler to initialize a new vault state account
fn process_initialize(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    authority: Pubkey,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();

    // Payer funds the creation of the vault state account
    let payer_account = next_account_info(account_info_iter)?;
    // The vault state account that will hold serialized VaultState
    let vault_state_account = next_account_info(account_info_iter)?;
    // The mint of tokens this vault will accept
    let mint_account = next_account_info(account_info_iter)?;
    // Rent sysvar for calculating rent exemption
    let rent_sysvar = next_account_info(account_info_iter)?;
    // System program needed to create the vault state account
    let system_program = next_account_info(account_info_iter)?;

    // Only a signer can authorize the creation and funding of a new account
    if !payer_account.is_signer {
        msg!("Payer must sign to initialize vault");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // Derive the expected PDA for the vault state to ensure predictable addresses
    let vault_seeds = &[b"vault_state", payer_account.key.as_ref()];
    let (expected_vault_pda, vault_bump) =
        Pubkey::find_program_address(vault_seeds, program_id);

    // Reject if the provided state account does not match the derived PDA
    if expected_vault_pda != *vault_state_account.key {
        msg!("Invalid vault state account address");
        return Err(ProgramError::InvalidAccountData);
    }

    // Calculate the rent-exempt balance for the vault state account size
    let rent = Rent::from_account_info(rent_sysvar)?;
    let state_space = VaultState::default().try_to_vec().unwrap().len();
    let required_lamports = rent.minimum_balance(state_space);

    // CPI to system program to create the vault state PDA account
    invoke_signed(
        &system_instruction::create_account(
            payer_account.key,
            vault_state_account.key,
            required_lamports,
            state_space as u64,
            program_id, // The vault program owns the state account
        ),
        &[
            payer_account.clone(),
            vault_state_account.clone(),
            system_program.clone(),
        ],
        &[&[b"vault_state", payer_account.key.as_ref(), &[vault_bump]]],
    )?;

    // Construct the initial vault state with default values
    let vault_state = VaultState {
        authority,
        mint: *mint_account.key,
        unlock_time: 0, // Immediate withdrawal by default
        total_deposited: 0,
        is_initialized: true,
    };

    // Serialize the state into the account data so it persists on-chain
    vault_state.serialize(&mut &mut vault_state_account.data.borrow_mut()[..])?;

    msg!("Vault initialized with authority {}", authority);
    Ok(())
}

// Handler to deposit tokens from the user into the vault
fn process_deposit(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();

    // The user who is depositing tokens and must sign
    let depositor = next_account_info(account_info_iter)?;
    // The vault state account that tracks deposits and rules
    let vault_state_account = next_account_info(account_info_iter)?;
    // The user's ATA that holds the tokens being deposited
    let depositor_ata = next_account_info(account_info_iter)?;
    // The vault PDA's ATA that will receive the deposited tokens
    let vault_ata = next_account_info(account_info_iter)?;
    // The SPL Token program processes the transfer CPI
    let token_program = next_account_info(account_info_iter)?;

    // Verify the depositor signed to authorize moving their tokens
    if !depositor.is_signer {
        msg!("Depositor must sign");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // Deserialize the vault state to update the deposited total
    let mut vault_state = VaultState::try_from_slice(&vault_state_account.data.borrow())?;

    // Ensure the vault has been initialized before accepting deposits
    if !vault_state.is_initialized {
        msg!("Vault not initialized");
        return Err(ProgramError::UninitializedAccount);
    }

    // Derive the vault PDA seeds so we can use invoke_signed if needed
    let vault_seeds = &[b"vault_state", depositor.key.as_ref()];
    let (expected_vault_pda, _vault_bump) =
        Pubkey::find_program_address(vault_seeds, program_id);

    // Ensure the provided vault state account matches our derivation
    if expected_vault_pda != *vault_state_account.key {
        msg!("Invalid vault state account");
        return Err(ProgramError::InvalidAccountData);
    }

    // CPI to SPL Token program to transfer tokens from user to vault ATA
    invoke(
        &token_instruction::transfer(
            token_program.key,
            depositor_ata.key,
            vault_ata.key,
            depositor.key,
            &[],
            amount,
        )?,
        &[
            depositor_ata.clone(),
            vault_ata.clone(),
            depositor.clone(),
            token_program.clone(),
        ],
    )?;

    // Update the vault state to reflect the new deposit total
    vault_state.total_deposited += amount;
    vault_state.serialize(&mut &mut vault_state_account.data.borrow_mut()[..])?;

    msg!("Deposited {} tokens into vault", amount);
    Ok(())
}

// Handler to withdraw tokens from the vault back to the user
fn process_withdraw(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();

    // The authority who must sign to authorize the withdrawal
    let authority = next_account_info(account_info_iter)?;
    // The vault state account holding rules and deposit totals
    let vault_state_account = next_account_info(account_info_iter)?;
    // The vault PDA's ATA that holds the tokens
    let vault_ata = next_account_info(account_info_iter)?;
    // The user's ATA that will receive the withdrawn tokens
    let recipient_ata = next_account_info(account_info_iter)?;
    // SPL Token program for the transfer CPI
    let token_program = next_account_info(account_info_iter)?;
    // Clock sysvar to check the current time against unlock_time
    let clock_sysvar = next_account_info(account_info_iter)?;

    // Verify the authority signed to prove they control the vault
    if !authority.is_signer {
        msg!("Authority must sign to withdraw");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // Deserialize the vault state to read rules and update balance
    let mut vault_state = VaultState::try_from_slice(&vault_state_account.data.borrow())?;

    // Confirm the vault has been initialized
    if !vault_state.is_initialized {
        msg!("Vault not initialized");
        return Err(ProgramError::UninitializedAccount);
    }

    // Only the stored authority can withdraw from this vault
    if vault_state.authority != *authority.key {
        msg!("Signer is not the vault authority");
        return Err(ProgramError::IllegalOwner);
    }

    // Load the current Unix timestamp from the clock sysvar
    let clock = Clock::from_account_info(clock_sysvar)?;

    // Reject withdrawal if the unlock time has not been reached yet
    if clock.unix_timestamp < vault_state.unlock_time {
        msg!(
            "Withdrawal locked until {}. Current time is {}.",
            vault_state.unlock_time,
            clock.unix_timestamp
        );
        return Err(ProgramError::Custom(1)); // Custom error for time lock
    }

    // Prevent withdrawing more than the recorded deposit total
    if amount > vault_state.total_deposited {
        msg!("Withdrawal amount exceeds deposited total");
        return Err(ProgramError::InsufficientFunds);
    }

    // Derive the PDA seeds so the program can sign for the vault ATA
    let vault_seeds = &[b"vault_state", authority.key.as_ref()];
    let (expected_vault_pda, vault_bump) =
        Pubkey::find_program_address(vault_seeds, program_id);

    // Verify the state account matches the expected derived address
    if expected_vault_pda != *vault_state_account.key {
        msg!("Invalid vault state account");
        return Err(ProgramError::InvalidAccountData);
    }

    // CPI to SPL Token program to transfer tokens from vault ATA to recipient
    // Using invoke_signed because the vault PDA must act as the signer
    invoke_signed(
        &token_instruction::transfer(
            token_program.key,
            vault_ata.key,
            recipient_ata.key,
            &expected_vault_pda, // SPL Token requires the owner as the authority
            &[],
            amount,
        )?,
        &[
            vault_ata.clone(),
            recipient_ata.clone(),
            vault_state_account.clone(), // Included to satisfy account list
            token_program.clone(),
        ],
        &[&[b"vault_state", authority.key.as_ref(), &[vault_bump]]],
    )?;

    // Update the vault state to reflect the reduced balance
    vault_state.total_deposited -= amount;
    vault_state.serialize(&mut &mut vault_state_account.data.borrow_mut()[..])?;

    msg!("Withdrew {} tokens from vault", amount);
    Ok(())
}

// Handler to update the unlock time, restricted to the vault authority
fn process_set_unlock_time(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    unlock_time: i64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();

    // The authority who must sign to change vault settings
    let authority = next_account_info(account_info_iter)?;
    // The vault state account that will be modified
    let vault_state_account = next_account_info(account_info_iter)?;

    // Verify the authority signed the transaction
    if !authority.is_signer {
        msg!("Authority must sign to set unlock time");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // Deserialize the current vault state
    let mut vault_state = VaultState::try_from_slice(&vault_state_account.data.borrow())?;

    // Ensure the vault is initialized before allowing modifications
    if !vault_state.is_initialized {
        msg!("Vault not initialized");
        return Err(ProgramError::UninitializedAccount);
    }

    // Only the stored authority can change the unlock time
    if vault_state.authority != *authority.key {
        msg!("Signer is not the vault authority");
        return Err(ProgramError::IllegalOwner);
    }

    // Update the unlock timestamp in the vault state
    vault_state.unlock_time = unlock_time;
    vault_state.serialize(&mut &mut vault_state_account.data.borrow_mut()[..])?;

    msg!("Unlock time set to {}", unlock_time);
    Ok(())
}

impl Default for VaultState {
    // Provide a default VaultState so we can compute its serialized size
    fn default() -> Self {
        VaultState {
            authority: Pubkey::default(),
            mint: Pubkey::default(),
            unlock_time: 0,
            total_deposited: 0,
            is_initialized: false,
        }
    }
}
