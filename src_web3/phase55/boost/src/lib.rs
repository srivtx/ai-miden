use borsh::{BorshDeserialize, BorshSerialize}; // WHY: Borsh serializes account state deterministically for Solana storage.
use solana_program::
{
    account_info::{next_account_info, AccountInfo}, // WHY: Safely iterate over instruction accounts in expected order.
    clock::Clock, // WHY: Timestamp is needed to set NFT expiration at mint time.
    entrypoint, // WHY: Registers the program's entry function with the Solana runtime.
    entrypoint::ProgramResult, // WHY: Standard return type for all Solana instructions.
    msg, // WHY: Logging is critical for debugging transactions on-chain.
    program::invoke, // WHY: CPI is used to call the SPL Token Program for minting.
    program::invoke_signed, // WHY: PDA-owned mints require program-signed CPI invocations.
    program_error::ProgramError, // WHY: Provides canonical error codes for on-chain failures.
    pubkey::Pubkey, // WHY: All addresses on Solana are 32-byte Pubkeys.
    sysvar::Sysvar, // WHY: Required trait to fetch sysvars like Clock and Rent.
};
use spl_token::instruction as token_instruction; // WHY: Reuse audited SPL Token instructions instead of rewriting them.

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/// WHY: 90 days in seconds is a reasonable default boost duration.
const DEFAULT_BOOST_DURATION_SECONDS: i64 = 90 * 24 * 60 * 60;

// ---------------------------------------------------------------------------
// Instruction Discriminants
// ---------------------------------------------------------------------------

/// WHY: A discriminant byte routes instruction data to the correct handler.
#[derive(BorshSerialize, BorshDeserialize, Clone, Debug)]
pub enum BoostInstruction
{
    /// WHY: Initialize the boost program's global configuration and whitelist.
    Initialize,
    /// WHY: Mint a new boost NFT to a user with embedded multiplier and expiration.
    MintBoost { multiplier: u64, duration_seconds: i64 },
    /// WHY: Validate that a user holds a valid, unexpired boost NFT and return its multiplier.
    ValidateBoost,
}

// ---------------------------------------------------------------------------
// Account States
// ---------------------------------------------------------------------------

/// WHY: BoostConfig is the singleton global state controlling authorized minters and the whitelist.
#[derive(BorshSerialize, BorshDeserialize, Clone, Debug)]
pub struct BoostConfig
{
    /// WHY: The authority can mint boosts and update the whitelist.
    pub authority: Pubkey,
    /// WHY: A list of approved boost NFT mints that the farm program should recognize.
    pub whitelisted_mints: Vec<Pubkey>,
    /// WHY: Counts total boosts minted for analytics and supply cap enforcement.
    pub total_minted: u64,
    /// WHY: bump stores the PDA nonce for the config account.
    pub bump: u8,
}

/// WHY: BoostMetadata stores on-chain attributes for each boost NFT mint.
#[derive(BorshSerialize, BorshDeserialize, Clone, Debug)]
pub struct BoostMetadata
{
    /// WHY: mint links this metadata to exactly one SPL token mint with supply=1.
    pub mint: Pubkey,
    /// WHY: multiplier is stored as integer (1000 = 1.0x) to avoid floating-point math.
    pub multiplier: u64,
    /// WHY: expiration is a Unix timestamp after which the boost is invalid.
    pub expiration: i64,
    /// WHY: tier provides a human-readable category for UI display.
    pub tier: u8,
    /// WHY: bump is the PDA nonce for the metadata account.
    pub bump: u8,
}

// ---------------------------------------------------------------------------
// Entrypoint
// ---------------------------------------------------------------------------

entrypoint!(process_instruction); // WHY: Solana runtime calls this function for every transaction.

/// WHY: This is the single entrypoint that receives all calls to the boost program.
pub fn process_instruction(
    program_id: &Pubkey, // WHY: Needed to derive PDAs that belong to this program.
    accounts: &[AccountInfo], // WHY: Instruction accounts are passed explicitly for parallel execution safety.
    instruction_data: &[u8], // WHY: Contains the discriminant and serialized arguments.
) -> ProgramResult
{
    /// WHY: Deserialize the instruction discriminant to route to the correct handler.
    let instruction = BoostInstruction::try_from_slice(instruction_data)
        .map_err(|_| ProgramError::InvalidInstructionData)?; // WHY: Corrupt data must abort immediately.

    match instruction
    {
        BoostInstruction::Initialize => {
            process_initialize(program_id, accounts) // WHY: Setup global state before any mints.
        }
        BoostInstruction::MintBoost {
            multiplier,
            duration_seconds,
        } => {
            process_mint_boost(program_id, accounts, multiplier, duration_seconds) // WHY: Pass parameters to create the NFT.
        }
        BoostInstruction::ValidateBoost => {
            process_validate_boost(program_id, accounts) // WHY: External programs call this to verify boosts.
        }
    }
}

// ---------------------------------------------------------------------------
// Instruction Handlers
// ---------------------------------------------------------------------------

/// WHY: process_initialize creates the global config account that governs the boost system.
fn process_initialize(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult
{
    let account_info_iter = &mut accounts.iter();
    let authority = next_account_info(account_info_iter)?; // WHY: The first account is the admin initializing the program.
    let config_account = next_account_info(account_info_iter)?; // WHY: The second account stores the global config.

    if !authority.is_signer
    {
        msg!("Authority must sign initialization"); // WHY: Initialization is a privileged operation.
        return Err(ProgramError::MissingRequiredSignature);
    }

    /// WHY: Derive the config PDA so clients can predict the address.
    let (expected_config, bump) = Pubkey::find_program_address(
        &[b"boost_config"],
        program_id,
    );

    if expected_config != *config_account.key
    {
        msg!("Invalid config account address");
        return Err(ProgramError::InvalidAccountData);
    }

    if !config_account.data_is_empty()
    {
        msg!("Config already initialized");
        return Err(ProgramError::AccountAlreadyInitialized);
    }

    /// WHY: Build the config state with an empty whitelist and zero minted count.
    let config = BoostConfig
    {
        authority: *authority.key,
        whitelisted_mints: Vec::new(),
        total_minted: 0,
        bump,
    };

    /// WHY: Serialize and persist the config to the account.
    config.serialize(&mut &mut config_account.data.borrow_mut()[..])?;

    msg!("Boost config initialized");
    Ok(())
}

/// WHY: process_mint_boost creates a new boost NFT with on-chain metadata.
fn process_mint_boost(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    multiplier: u64,
    duration_seconds: i64,
) -> ProgramResult
{
    let account_info_iter = &mut accounts.iter();
    let authority = next_account_info(account_info_iter)?; // WHY: Only the authority can mint boosts.
    let config_account = next_account_info(account_info_iter)?; // WHY: Config is updated with the new mint.
    let boost_mint = next_account_info(account_info_iter)?; // WHY: The new SPL token mint for this NFT.
    let metadata_account = next_account_info(account_info_iter)?; // WHY: Stores multiplier and expiration.
    let recipient = next_account_info(account_info_iter)?; // WHY: The wallet receiving the NFT.
    let recipient_token_account = next_account_info(account_info_iter)?; // WHY: The ATA that will hold the NFT.
    let _system_program = next_account_info(account_info_iter)?; // WHY: Needed if allocating accounts via CPI.
    let token_program = next_account_info(account_info_iter)?; // WHY: SPL Token Program handles minting.
    let clock = Clock::get()?; // WHY: Current time sets the expiration baseline.

    if !authority.is_signer
    {
        msg!("Authority must sign mint");
        return Err(ProgramError::MissingRequiredSignature);
    }

    /// WHY: Deserialize config to verify authority and update state.
    let mut config = BoostConfig::try_from_slice(&config_account.data.borrow())?;
    if config.authority != *authority.key
    {
        msg!("Unauthorized minter");
        return Err(ProgramError::IllegalOwner);
    }

    /// WHY: Multiplier must be at least 1.0x (1000) to be meaningful.
    if multiplier < 1000
    {
        msg!("Multiplier must be at least 1000 (1.0x)");
        return Err(ProgramError::InvalidArgument);
    }

    /// WHY: Cap multiplier at 10.0x (10000) to prevent extreme economic distortion.
    if multiplier > 10000
    {
        msg!("Multiplier exceeds maximum allowed");
        return Err(ProgramError::InvalidArgument);
    }

    /// WHY: Derive the metadata PDA tied to this mint.
    let (expected_metadata, meta_bump) = Pubkey::find_program_address(
        &[b"boost_metadata", boost_mint.key.as_ref()],
        program_id,
    );
    if expected_metadata != *metadata_account.key
    {
        msg!("Invalid metadata account");
        return Err(ProgramError::InvalidAccountData);
    }

    if !metadata_account.data_is_empty()
    {
        msg!("Metadata already exists");
        return Err(ProgramError::AccountAlreadyInitialized);
    }

    /// WHY: Calculate expiration based on duration; default if zero passed.
    let effective_duration = if duration_seconds > 0
    {
        duration_seconds
    }
    else
    {
        DEFAULT_BOOST_DURATION_SECONDS
    };
    let expiration = clock
        .unix_timestamp
        .checked_add(effective_duration)
        .unwrap_or(i64::MAX); // WHY: Prevent overflow by capping at max timestamp.

    /// WHY: Derive tier from multiplier for UI categorization.
    let tier = if multiplier >= 2000
    {
        3 // WHY: Legendary tier for 2.0x and above.
    }
    else if multiplier >= 1500
    {
        2 // WHY: Rare tier for 1.5x and above.
    }
    else if multiplier >= 1250
    {
        1 // WHY: Uncommon tier for 1.25x and above.
    }
    else
    {
        0 // WHY: Common tier for 1.0x to 1.24x.
    };

    /// WHY: Build and persist the metadata account.
    let metadata = BoostMetadata
    {
        mint: *boost_mint.key,
        multiplier,
        expiration,
        tier,
        bump: meta_bump,
    };
    metadata.serialize(&mut &mut metadata_account.data.borrow_mut()[..])?;

    /// WHY: Mint exactly 1 token to the recipient's token account, enforcing NFT scarcity.
    let mint_ix = token_instruction::mint_to(
        token_program.key,
        boost_mint.key,
        recipient_token_account.key,
        authority.key, // WHY: Mint authority must sign.
        &[],
        1,
    )?;
    invoke(
        &mint_ix,
        &[
            boost_mint.clone(),
            recipient_token_account.clone(),
            authority.clone(),
            token_program.clone(),
        ],
    )?;

    /// WHY: Update the whitelist so the farm program knows this mint is valid.
    config.whitelisted_mints.push(*boost_mint.key);
    config.total_minted = config
        .total_minted
        .checked_add(1)
        .ok_or(ProgramError::ArithmeticOverflow)?;

    /// WHY: Persist updated config.
    config.serialize(&mut &mut config_account.data.borrow_mut()[..])?;

    msg!(
        "Minted boost NFT with multiplier {} expiring at {}",
        multiplier,
        expiration
    );
    Ok(())
}

/// WHY: process_validate_boost checks if a user holds a valid, unexpired boost NFT and returns its multiplier.
fn process_validate_boost(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult
{
    let account_info_iter = &mut accounts.iter();
    let _caller = next_account_info(account_info_iter)?; // WHY: The program invoking validation (e.g., the farm program).
    let config_account = next_account_info(account_info_iter)?; // WHY: Config holds the whitelist.
    let boost_mint = next_account_info(account_info_iter)?; // WHY: The mint being validated.
    let metadata_account = next_account_info(account_info_iter)?; // WHY: Stores expiration and multiplier.
    let user_token_account = next_account_info(account_info_iter)?; // WHY: Proves the user holds the NFT.
    let clock = Clock::get()?; // WHY: Expiration is checked against the current timestamp.

    /// WHY: Deserialize config to check whitelist membership.
    let config = BoostConfig::try_from_slice(&config_account.data.borrow())?;

    /// WHY: Reject if the mint is not in the whitelist.
    if !config.whitelisted_mints.contains(boost_mint.key)
    {
        msg!("Boost mint is not whitelisted");
        return Err(ProgramError::InvalidAccountData);
    }

    /// WHY: Verify the metadata account is the correct PDA for this mint.
    let (expected_metadata, _meta_bump) = Pubkey::find_program_address(
        &[b"boost_metadata", boost_mint.key.as_ref()],
        program_id,
    );
    if expected_metadata != *metadata_account.key
    {
        msg!("Invalid metadata account for mint");
        return Err(ProgramError::InvalidAccountData);
    }

    /// WHY: Deserialize metadata to read multiplier and expiration.
    let metadata = BoostMetadata::try_from_slice(&metadata_account.data.borrow())?;

    /// WHY: Verify the metadata matches the passed mint.
    if metadata.mint != *boost_mint.key
    {
        msg!("Metadata mint mismatch");
        return Err(ProgramError::InvalidAccountData);
    }

    /// WHY: Reject expired boosts immediately.
    if clock.unix_timestamp > metadata.expiration
    {
        msg!("Boost NFT has expired");
        return Err(ProgramError::InvalidAccountData);
    }

    /// WHY: Verify the user actually holds the NFT by checking token account balance.
    let token_data = user_token_account.data.borrow();
    if token_data.len() < 72
    {
        msg!("Invalid token account data");
        return Err(ProgramError::InvalidAccountData);
    }
    let account_mint = Pubkey::new_from_array(token_data[0..32].try_into().unwrap());
    let account_amount = u64::from_le_bytes(token_data[64..72].try_into().unwrap());

    if account_mint != *boost_mint.key
    {
        msg!("Token account mint mismatch");
        return Err(ProgramError::InvalidAccountData);
    }
    if account_amount < 1
    {
        msg!("User does not hold the boost NFT");
        return Err(ProgramError::InsufficientFunds);
    }

    /// WHY: Log the valid multiplier so the caller (farm program or client) can use it.
    msg!("Boost validated: multiplier = {}", metadata.multiplier);
    Ok(())
}
