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
use spl_token::instruction as token_instruction;
use spl_token::state::Account as TokenAccount;
use borsh::{BorshDeserialize, BorshSerialize};

// WHY: This declares the entrypoint so the Solana runtime knows where to start executing our program.
entrypoint!(process_instruction);

// WHY: We use a fixed seed to derive a Program Derived Address (PDA) for the pool authority.
// This ensures only our program can sign transactions that move tokens out of the pool vaults.
const POOL_AUTHORITY_SEED: &[u8] = b"pool_authority";

// WHY: We represent the pool state as a struct so we can serialize it into a single account.
// Storing everything in one account makes reads simple and keeps the design atomic.
#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)]
pub struct PoolState {
    // WHY: We must know which two tokens this pool trades so we can validate deposits and swaps.
    pub token_a_mint: Pubkey,
    pub token_b_mint: Pubkey,
    // WHY: The vaults hold the actual tokens. The pool state account only holds pointers to them.
    pub token_a_vault: Pubkey,
    pub token_b_vault: Pubkey,
    // WHY: Total shares track the overall size of the pool so we can calculate proportional ownership.
    pub total_shares: u64,
    // WHY: A fee of 30 basis points (0.3%) is standard for constant product AMMs like Uniswap v2.
    pub fee_numerator: u64,
    pub fee_denominator: u64,
    // WHY: We store the authority bump so we can efficiently recreate the PDA signer when needed.
    pub authority_bump: u8,
}

// WHY: We track each liquidity provider individually so we know how many shares they own.
#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)]
pub struct LiquidityProvider {
    // WHY: We store the owner so only they can withdraw or modify this position.
    pub owner: Pubkey,
    // WHY: Shares are fungible within this pool but tracked per-account for simplicity in this example.
    pub shares: u64,
}

// WHY: These instruction tags tell the program which function to run inside process_instruction.
#[repr(u8)]
enum Instruction {
    InitializePool = 0,
    DepositLiquidity = 1,
    Swap = 2,
    WithdrawLiquidity = 3,
}

// WHY: The main entrypoint receives the program_id, accounts, and instruction data from the runtime.
pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    // WHY: We must have at least one byte to know which instruction is being called.
    if instruction_data.is_empty() {
        msg!("ERROR: Empty instruction data");
        return Err(ProgramError::InvalidInstructionData);
    }

    // WHY: We match on the first byte to dispatch to the correct handler.
    match instruction_data[0] {
        0 => initialize_pool(program_id, accounts),
        1 => deposit_liquidity(program_id, accounts, &instruction_data[1..]),
        2 => swap(program_id, accounts, &instruction_data[1..]),
        3 => withdraw_liquidity(program_id, accounts, &instruction_data[1..]),
        // WHY: If the tag is unrecognized, we fail fast to avoid undefined behavior.
        _ => {
            msg!("ERROR: Unknown instruction tag");
            Err(ProgramError::InvalidInstructionData)
        }
    }
}

// WHY: This function sets up the pool state account and associated token vaults.
fn initialize_pool(program_id: &Pubkey, accounts: &[AccountInfo]) -> ProgramResult {
    // WHY: We iterate through the account list in a defined order so we know what each account represents.
    let account_info_iter = &mut accounts.iter();
    let initializer = next_account_info(account_info_iter)?; // WHY: The person paying for account creation.
    let pool_state_account = next_account_info(account_info_iter)?; // WHY: The account that will hold our PoolState struct.
    let token_a_mint = next_account_info(account_info_iter)?; // WHY: We need the mint to create a vault for token A.
    let token_b_mint = next_account_info(account_info_iter)?; // WHY: We need the mint to create a vault for token B.
    let token_a_vault = next_account_info(account_info_iter)?; // WHY: This account will hold the actual token A reserves.
    let token_b_vault = next_account_info(account_info_iter)?; // WHY: This account will hold the actual token B reserves.
    let pool_authority = next_account_info(account_info_iter)?; // WHY: The PDA that will own the vaults.
    let token_program = next_account_info(account_info_iter)?; // WHY: Required to invoke SPL Token instructions.
    let system_program = next_account_info(account_info_iter)?; // WHY: Required to create new accounts.
    let rent_sysvar = next_account_info(account_info_iter)?; // WHY: Required to ensure accounts are rent-exempt.

    // WHY: Only the initializer should pay for and control the creation of the pool.
    if !initializer.is_signer {
        msg!("ERROR: Initializer must sign");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // WHY: We derive the PDA so it is deterministic and program-controlled.
    let (expected_authority, authority_bump) =
        Pubkey::find_program_address(&[POOL_AUTHORITY_SEED], program_id);
    if expected_authority != *pool_authority.key {
        msg!("ERROR: Invalid pool authority PDA");
        return Err(ProgramError::InvalidAccountData);
    }

    // WHY: We must allocate space for the PoolState struct so the account can hold our data.
    let pool_state_size = std::mem::size_of::<PoolState>() as u64;
    let rent = Rent::from_account_info(rent_sysvar)?;
    let required_lamports = rent.minimum_balance(pool_state_size as usize);

    // WHY: We create the pool state account using a system instruction, funded by the initializer.
    invoke(
        &system_instruction::create_account(
            initializer.key,
            pool_state_account.key,
            required_lamports,
            pool_state_size,
            program_id,
        ),
        &[
            initializer.clone(),
            pool_state_account.clone(),
            system_program.clone(),
        ],
    )?;

    // WHY: We initialize the pool state with the provided mints and empty reserves.
    let pool_state = PoolState {
        token_a_mint: *token_a_mint.key,
        token_b_mint: *token_b_mint.key,
        token_a_vault: *token_a_vault.key,
        token_b_vault: *token_b_vault.key,
        total_shares: 0,
        fee_numerator: 3,
        fee_denominator: 1000,
        authority_bump,
    };

    // WHY: We serialize the state into the account so it persists on-chain.
    pool_state.serialize(&mut &mut pool_state_account.data.borrow_mut()[..])?;

    msg!("Pool initialized successfully");
    Ok(())
}

// WHY: This function allows users to deposit both tokens and receive LP shares representing their ownership.
fn deposit_liquidity(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    _data: &[u8],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let depositor = next_account_info(account_info_iter)?; // WHY: The user providing liquidity.
    let pool_state_account = next_account_info(account_info_iter)?; // WHY: To read current reserves and update total shares.
    let depositor_a_account = next_account_info(account_info_iter)?; // WHY: The user's token A account to pull from.
    let depositor_b_account = next_account_info(account_info_iter)?; // WHY: The user's token B account to pull from.
    let token_a_vault = next_account_info(account_info_iter)?; // WHY: The pool's token A vault to deposit into.
    let token_b_vault = next_account_info(account_info_iter)?; // WHY: The pool's token B vault to deposit into.
    let pool_authority = next_account_info(account_info_iter)?; // WHY: Needed as a signer for PDA-owned vaults.
    let token_program = next_account_info(account_info_iter)?; // WHY: To invoke SPL token transfers.

    if !depositor.is_signer {
        msg!("ERROR: Depositor must sign");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // WHY: We load the existing pool state to calculate shares proportionally.
    let mut pool_state = PoolState::try_from_slice(&pool_state_account.data.borrow())?;

    // WHY: In a real implementation, the amounts would be passed in instruction data.
    // Here we use dummy amounts for clarity, assuming the caller has prepared them.
    let amount_a: u64 = 1000;
    let amount_b: u64 = 1000;

    // WHY: We calculate shares. If the pool is empty, shares equal the geometric mean or sum.
    // For simplicity, we use the sum of deposits as initial shares.
    let shares_to_mint = if pool_state.total_shares == 0 {
        amount_a.checked_add(amount_b).ok_or(ProgramError::Overflow)?
    } else {
        // WHY: If the pool already has liquidity, shares must be proportional to preserve fairness.
        let a_shares = amount_a
            .checked_mul(pool_state.total_shares)
            .ok_or(ProgramError::Overflow)?
            .checked_div(1000)
            .ok_or(ProgramError::Overflow)?;
        a_shares
    };

    // WHY: We transfer token A from the user to the pool vault.
    invoke(
        &token_instruction::transfer(
            token_program.key,
            depositor_a_account.key,
            token_a_vault.key,
            depositor.key,
            &[],
            amount_a,
        )?,
        &[
            depositor_a_account.clone(),
            token_a_vault.clone(),
            depositor.clone(),
            token_program.clone(),
        ],
    )?;

    // WHY: We transfer token B from the user to the pool vault.
    invoke(
        &token_instruction::transfer(
            token_program.key,
            depositor_b_account.key,
            token_b_vault.key,
            depositor.key,
            &[],
            amount_b,
        )?,
        &[
            depositor_b_account.clone(),
            token_b_vault.clone(),
            depositor.clone(),
            token_program.clone(),
        ],
    )?;

    // WHY: We update the pool state to reflect the new total shares.
    pool_state.total_shares = pool_state
        .total_shares
        .checked_add(shares_to_mint)
        .ok_or(ProgramError::Overflow)?;
    pool_state.serialize(&mut &mut pool_state_account.data.borrow_mut()[..])?;

    msg!("Deposited {} A, {} B, minted {} shares", amount_a, amount_b, shares_to_mint);
    Ok(())
}

// WHY: This function executes a trade against the pool using the constant product formula.
fn swap(program_id: &Pubkey, accounts: &[AccountInfo], data: &[u8]) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let swapper = next_account_info(account_info_iter)?; // WHY: The user initiating the swap.
    let pool_state_account = next_account_info(account_info_iter)?; // WHY: To read reserves and fee settings.
    let swapper_source_account = next_account_info(account_info_iter)?; // WHY: User's account for the token they are selling.
    let swapper_dest_account = next_account_info(account_info_iter)?; // WHY: User's account for the token they are buying.
    let token_a_vault = next_account_info(account_info_iter)?; // WHY: Pool vault for token A.
    let token_b_vault = next_account_info(account_info_iter)?; // WHY: Pool vault for token B.
    let pool_authority = next_account_info(account_info_iter)?; // WHY: PDA signer to transfer out of pool vaults.
    let token_program = next_account_info(account_info_iter)?; // WHY: SPL Token program for transfers.

    if !swapper.is_signer {
        msg!("ERROR: Swapper must sign");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // WHY: We verify the pool authority PDA to prevent unauthorized token movements.
    let (expected_authority, authority_bump) =
        Pubkey::find_program_address(&[POOL_AUTHORITY_SEED], program_id);
    if expected_authority != *pool_authority.key {
        msg!("ERROR: Invalid pool authority");
        return Err(ProgramError::InvalidAccountData);
    }

    // WHY: We load pool state to know the fee parameters.
    let mut pool_state = PoolState::try_from_slice(&pool_state_account.data.borrow())?;

    // WHY: The instruction data contains amount_in and min_amount_out to prevent frontrunning.
    if data.len() < 16 {
        msg!("ERROR: Insufficient swap data");
        return Err(ProgramError::InvalidInstructionData);
    }
    let amount_in = u64::from_le_bytes(data[0..8].try_into().unwrap());
    let min_amount_out = u64::from_le_bytes(data[8..16].try_into().unwrap());

    // WHY: We read vault balances to get the current reserves x and y.
    let vault_a_data = TokenAccount::unpack(&token_a_vault.data.borrow())?;
    let vault_b_data = TokenAccount::unpack(&token_b_vault.data.borrow())?;
    let reserve_in = vault_a_data.amount;
    let reserve_out = vault_b_data.amount;

    // WHY: We calculate the amount after fees. Fees stay in the pool, increasing k over time.
    let amount_in_with_fee = (amount_in as u128)
        .checked_mul(pool_state.fee_numerator as u128)
        .ok_or(ProgramError::Overflow)?
        .checked_div(pool_state.fee_denominator as u128)
        .ok_or(ProgramError::InvalidArgument)?;

    // WHY: Constant product formula: (reserve_in + amount_in_with_fee) * (reserve_out - amount_out) = reserve_in * reserve_out
    // Rearranged: amount_out = reserve_out - (reserve_in * reserve_out) / (reserve_in + amount_in_with_fee)
    let numerator = (reserve_in as u128)
        .checked_mul(reserve_out as u128)
        .ok_or(ProgramError::Overflow)?;
    let denominator = (reserve_in as u128)
        .checked_add(amount_in_with_fee)
        .ok_or(ProgramError::Overflow)?;
    let amount_out = reserve_out - (numerator / denominator) as u64;

    // WHY: We enforce the slippage limit. If the output is too low, the transaction reverts.
    if amount_out < min_amount_out {
        msg!("ERROR: Slippage exceeded. Expected at least {}, got {}", min_amount_out, amount_out);
        return Err(ProgramError::Custom(1));
    }

    // WHY: We transfer the input token from the user to the pool vault.
    invoke(
        &token_instruction::transfer(
            token_program.key,
            swapper_source_account.key,
            token_a_vault.key,
            swapper.key,
            &[],
            amount_in,
        )?,
        &[
            swapper_source_account.clone(),
            token_a_vault.clone(),
            swapper.clone(),
            token_program.clone(),
        ],
    )?;

    // WHY: We transfer the output token from the pool vault to the user, signed by the PDA.
    invoke_signed(
        &token_instruction::transfer(
            token_program.key,
            token_b_vault.key,
            swapper_dest_account.key,
            pool_authority.key,
            &[],
            amount_out,
        )?,
        &[
            token_b_vault.clone(),
            swapper_dest_account.clone(),
            pool_authority.clone(),
            token_program.clone(),
        ],
        &[&[POOL_AUTHORITY_SEED, &[authority_bump]]],
    )?;

    // WHY: We re-serialize pool state even if values haven't changed, to keep the pattern consistent.
    pool_state.serialize(&mut &mut pool_state_account.data.borrow_mut()[..])?;

    msg!("Swapped {} in for {} out", amount_in, amount_out);
    Ok(())
}

// WHY: This function lets users burn their LP shares and withdraw their proportional reserves.
fn withdraw_liquidity(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    data: &[u8],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let withdrawer = next_account_info(account_info_iter)?; // WHY: The user requesting withdrawal.
    let pool_state_account = next_account_info(account_info_iter)?; // WHY: To read reserves and total shares.
    let withdrawer_a_account = next_account_info(account_info_iter)?; // WHY: Destination for token A.
    let withdrawer_b_account = next_account_info(account_info_iter)?; // WHY: Destination for token B.
    let token_a_vault = next_account_info(account_info_iter)?; // WHY: Source of token A.
    let token_b_vault = next_account_info(account_info_iter)?; // WHY: Source of token B.
    let pool_authority = next_account_info(account_info_iter)?; // WHY: PDA signer for vault transfers.
    let token_program = next_account_info(account_info_iter)?; // WHY: SPL Token program.

    if !withdrawer.is_signer {
        msg!("ERROR: Withdrawer must sign");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // WHY: We verify the PDA to ensure the vault transfer is legitimate.
    let (expected_authority, authority_bump) =
        Pubkey::find_program_address(&[POOL_AUTHORITY_SEED], program_id);
    if expected_authority != *pool_authority.key {
        msg!("ERROR: Invalid pool authority");
        return Err(ProgramError::InvalidAccountData);
    }

    // WHY: We load pool state to calculate the proportional withdrawal amounts.
    let mut pool_state = PoolState::try_from_slice(&pool_state_account.data.borrow())?;

    // WHY: In a full implementation, the LP account would be parsed here to verify shares.
    // We assume the instruction data contains the number of shares to burn.
    if data.len() < 8 {
        msg!("ERROR: Insufficient withdraw data");
        return Err(ProgramError::InvalidInstructionData);
    }
    let shares_to_burn = u64::from_le_bytes(data[0..8].try_into().unwrap());

    // WHY: We read current vault balances to know the exact reserves at withdrawal time.
    let vault_a_data = TokenAccount::unpack(&token_a_vault.data.borrow())?;
    let vault_b_data = TokenAccount::unpack(&token_b_vault.data.borrow())?;
    let reserve_a = vault_a_data.amount;
    let reserve_b = vault_b_data.amount;

    // WHY: The amount returned is proportional to shares owned divided by total shares.
    let amount_a = (shares_to_burn as u128)
        .checked_mul(reserve_a as u128)
        .ok_or(ProgramError::Overflow)?
        .checked_div(pool_state.total_shares as u128)
        .ok_or(ProgramError::InvalidArgument)? as u64;

    let amount_b = (shares_to_burn as u128)
        .checked_mul(reserve_b as u128)
        .ok_or(ProgramError::Overflow)?
        .checked_div(pool_state.total_shares as u128)
        .ok_or(ProgramError::InvalidArgument)? as u64;

    // WHY: We transfer token A from the pool vault to the user.
    invoke_signed(
        &token_instruction::transfer(
            token_program.key,
            token_a_vault.key,
            withdrawer_a_account.key,
            pool_authority.key,
            &[],
            amount_a,
        )?,
        &[
            token_a_vault.clone(),
            withdrawer_a_account.clone(),
            pool_authority.clone(),
            token_program.clone(),
        ],
        &[&[POOL_AUTHORITY_SEED, &[authority_bump]]],
    )?;

    // WHY: We transfer token B from the pool vault to the user.
    invoke_signed(
        &token_instruction::transfer(
            token_program.key,
            token_b_vault.key,
            withdrawer_b_account.key,
            pool_authority.key,
            &[],
            amount_b,
        )?,
        &[
            token_b_vault.clone(),
            withdrawer_b_account.clone(),
            pool_authority.clone(),
            token_program.clone(),
        ],
        &[&[POOL_AUTHORITY_SEED, &[authority_bump]]],
    )?;

    // WHY: We reduce total shares to reflect the burned position.
    pool_state.total_shares = pool_state
        .total_shares
        .checked_sub(shares_to_burn)
        .ok_or(ProgramError::InsufficientFunds)?;
    pool_state.serialize(&mut &mut pool_state_account.data.borrow_mut()[..])?;

    msg!("Withdrew {} A, {} B, burned {} shares", amount_a, amount_b, shares_to_burn);
    Ok(())
}
