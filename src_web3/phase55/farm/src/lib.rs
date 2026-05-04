use borsh::{BorshDeserialize, BorshSerialize}; // WHY: Borsh provides compact, deterministic serialization for Solana account data.
use solana_program::
{
    account_info::{next_account_info, AccountInfo}, // WHY: These helpers iterate over and validate instruction account inputs.
    clock::Clock, // WHY: The Clock sysvar provides the current Unix timestamp for time-based reward calculations.
    entrypoint, // WHY: entrypoint declares the single function that Solana runtime calls to execute this program.
    entrypoint::ProgramResult, // WHY: ProgramResult is the standard return type for Solana instructions, encapsulating success or error.
    msg, // WHY: msg logs to the transaction log, essential for debugging on-chain execution.
    program::invoke, // WHY: invoke submits Cross-Program Invocations to transfer SPL tokens via the Token Program.
    program_error::ProgramError, // WHY: ProgramError provides standard error codes for common on-chain failures.
    pubkey::Pubkey, // WHY: Pubkey is the 32-byte address type used for all accounts, mints, and programs on Solana.
    sysvar::Sysvar, // WHY: Sysvar is the trait required to deserialize sysvar accounts like Clock and Rent.
};
use spl_token::instruction as token_instruction; // WHY: Reusing the SPL Token Program's instructions avoids reimplementing token transfer logic.

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/// WHY: 1e12 precision prevents integer truncation from destroying reward accuracy when dividing by total_staked.
const PRECISION: u128 = 1_000_000_000_000;

/// WHY: A single byte discriminant at the start of instruction data routes to the correct handler.
#[derive(BorshSerialize, BorshDeserialize, Clone, Debug)]
pub enum FarmInstruction
{
    /// WHY: Pool creation must be explicit so emission rates and token mints are recorded on-chain.
    CreatePool { reward_rate: u64 },
    /// WHY: Staking is the core user action that locks capital and starts reward accrual.
    Stake { amount: u64 },
    /// WHY: Unstaking returns principal and forces a reward claim so nothing is lost.
    Unstake { amount: u64 },
    /// WHY: Claiming allows users to realize rewards without withdrawing principal.
    Claim,
    /// WHY: Compounding claims rewards and restakes them in a single atomic transaction.
    Compound,
    /// WHY: Applying a boost NFT links a multiplier to the user's position for future rewards.
    ApplyBoost,
}

// ---------------------------------------------------------------------------
// Account States
// ---------------------------------------------------------------------------

/// WHY: PoolState is the master account for each farm pool; it stores all parameters needed for reward math.
#[derive(BorshSerialize, BorshDeserialize, Clone, Debug)]
pub struct PoolState
{
    /// WHY: The authority can update reward rates and is the only address allowed to create the pool.
    pub authority: Pubkey,
    /// WHY: staking_token_mint identifies which SPL token users must deposit to participate.
    pub staking_token_mint: Pubkey,
    /// WHY: reward_token_mint identifies which SPL token is paid out as rewards.
    pub reward_token_mint: Pubkey,
    /// WHY: reward_per_share_stored is the global accumulator; difference from user's snapshot equals earned rewards.
    pub reward_per_share_stored: u128,
    /// WHY: last_update_time records when the accumulator was last refreshed so elapsed time can be computed.
    pub last_update_time: i64,
    /// WHY: reward_rate is tokens-per-second emission; per-second avoids chain-speed dependency.
    pub reward_rate: u64,
    /// WHY: total_staked is the sum of all active deposits; reward distribution divides by this value.
    pub total_staked: u64,
    /// WHY: A nonce bump is required to sign for the pool's token account as a Program Derived Address.
    pub bump: u8,
}

/// WHY: UserPosition tracks an individual's stake and reward debt for a specific pool.
#[derive(BorshSerialize, BorshDeserialize, Clone, Debug)]
pub struct UserPosition
{
    /// WHY: owner prevents unauthorized access; only this wallet can mutate this position.
    pub owner: Pubkey,
    /// WHY: pool links the position to exactly one pool, isolating reward calculations.
    pub pool: Pubkey,
    /// WHY: staked_amount is the principal deposited by the user.
    pub staked_amount: u64,
    /// WHY: reward_per_share_paid is the user's snapshot of the global accumulator at their last interaction.
    pub reward_per_share_paid: u128,
    /// WHY: boost_multiplier is stored as an integer (1000 = 1.0x, 1500 = 1.5x) to avoid floating-point math.
    pub boost_multiplier: u64,
    /// WHY: boost_nft_mint records which NFT is providing the boost so ownership can be re-validated.
    pub boost_nft_mint: Option<Pubkey>,
    /// WHY: bump is the PDA nonce required for any program-signed operations on this account.
    pub bump: u8,
}

// ---------------------------------------------------------------------------
// Entrypoint
// ---------------------------------------------------------------------------

entrypoint!(process_instruction); // WHY: This macro registers process_instruction as the program's sole entrypoint.

/// WHY: The Solana runtime calls this function for every transaction targeting this program.
pub fn process_instruction(
    program_id: &Pubkey, // WHY: program_id lets us verify that derived addresses belong to this program.
    accounts: &[AccountInfo], // WHY: accounts is the ordered list of accounts passed in the instruction.
    instruction_data: &[u8], // WHY: instruction_data carries the discriminant and serialized arguments.
) -> ProgramResult
{
    /// WHY: Deserializing the first byte routes to the correct handler without manual byte slicing.
    let instruction = FarmInstruction::try_from_slice(instruction_data)
        .map_err(|_| ProgramError::InvalidInstructionData)?; // WHY: Invalid data must fail fast to prevent undefined behavior.

    /// WHY: Matching on the discriminant delegates to the specific business logic for each action.
    match instruction
    {
        FarmInstruction::CreatePool { reward_rate } => {
            process_create_pool(program_id, accounts, reward_rate) // WHY: Pass rate so the pool starts with known emissions.
        }
        FarmInstruction::Stake { amount } => {
            process_stake(program_id, accounts, amount) // WHY: Pass amount so the user controls how much to lock.
        }
        FarmInstruction::Unstake { amount } => {
            process_unstake(program_id, accounts, amount) // WHY: Pass amount to support partial unstaking.
        }
        FarmInstruction::Claim => {
            process_claim(program_id, accounts) // WHY: No extra data needed; claim amount is computed on-chain.
        }
        FarmInstruction::Compound => {
            process_compound(program_id, accounts) // WHY: Compound is claim + stake combined.
        }
        FarmInstruction::ApplyBoost => {
            process_apply_boost(program_id, accounts) // WHY: Boost application reads NFT data from accounts.
        }
    }
}

// ---------------------------------------------------------------------------
// Instruction Handlers
// ---------------------------------------------------------------------------

/// WHY: process_create_pool initializes the on-chain state for a new farming pool.
fn process_create_pool(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    reward_rate: u64,
) -> ProgramResult
{
    /// WHY: next_account_info iterates safely and enforces the expected account ordering.
    let account_info_iter = &mut accounts.iter();
    let authority = next_account_info(account_info_iter)?; // WHY: The first account is the admin paying for pool creation.
    let pool_account = next_account_info(account_info_iter)?; // WHY: The second account is the new pool state account.
    let staking_token_mint = next_account_info(account_info_iter)?; // WHY: The third account is the deposit token mint.
    let reward_token_mint = next_account_info(account_info_iter)?; // WHY: The fourth account is the payout token mint.
    let _system_program = next_account_info(account_info_iter)?; // WHY: System Program is needed if allocating accounts via CPI.
    let _token_program = next_account_info(account_info_iter)?; // WHY: Token Program is referenced for future CPI transfers.
    let clock = Clock::get()?; // WHY: We capture the current time so last_update_time starts accurately.

    /// WHY: Only signed transactions from the authority can create pools, preventing spam.
    if !authority.is_signer
    {
        msg!("Authority must sign pool creation"); // WHY: Log the specific failure reason for debugging.
        return Err(ProgramError::MissingRequiredSignature);
    }

    /// WHY: Deriving the pool PDA proves the address was generated correctly from seeds.
    let (expected_pool, bump) = Pubkey::find_program_address(
        &[b"pool", staking_token_mint.key.as_ref(), reward_token_mint.key.as_ref()],
        program_id,
    );

    /// WHY: Verifying the derived address prevents users from passing arbitrary accounts as pools.
    if expected_pool != *pool_account.key
    {
        msg!("Invalid pool account address");
        return Err(ProgramError::InvalidAccountData);
    }

    /// WHY: A new pool must have zero lamports and no data to avoid overwriting existing state.
    if !pool_account.data_is_empty()
    {
        msg!("Pool account already initialized");
        return Err(ProgramError::AccountAlreadyInitialized);
    }

    /// WHY: reward_rate must be positive; a zero rate would make the pool useless.
    if reward_rate == 0
    {
        msg!("Reward rate must be greater than zero");
        return Err(ProgramError::InvalidArgument);
    }

    /// WHY: Initialize the pool state with all fields explicitly set to prevent uninitialized memory.
    let pool_state = PoolState
    {
        authority: *authority.key,
        staking_token_mint: *staking_token_mint.key,
        reward_token_mint: *reward_token_mint.key,
        reward_per_share_stored: 0, // WHY: No rewards have accrued yet.
        last_update_time: clock.unix_timestamp, // WHY: Accrual starts from now.
        reward_rate,
        total_staked: 0, // WHY: No deposits yet.
        bump,
    };

    /// WHY: Serialize and write the state into the account so it persists across transactions.
    pool_state.serialize(&mut &mut pool_account.data.borrow_mut()[..])?;

    msg!("Pool created with rate: {}", reward_rate); // WHY: Confirm creation in the transaction log.
    Ok(())
}

/// WHY: process_stake locks user tokens and starts their reward accrual.
fn process_stake(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
) -> ProgramResult
{
    let account_info_iter = &mut accounts.iter();
    let user = next_account_info(account_info_iter)?; // WHY: The depositor must sign.
    let pool_account = next_account_info(account_info_iter)?; // WHY: The pool receiving the stake.
    let user_position = next_account_info(account_info_iter)?; // WHY: The user's position account for this pool.
    let user_staking_ata = next_account_info(account_info_iter)?; // WHY: The user's token account holding staking tokens.
    let pool_staking_ata = next_account_info(account_info_iter)?; // WHY: The pool's escrow token account.
    let token_program = next_account_info(account_info_iter)?; // WHY: Required for SPL transfer CPI.
    let clock = Clock::get()?; // WHY: Needed to update reward accrual before recording the stake.

    /// WHY: Only the owner can stake into their own position.
    if !user.is_signer
    {
        return Err(ProgramError::MissingRequiredSignature);
    }

    /// WHY: Zero-amount stakes are meaningless and waste compute.
    if amount == 0
    {
        msg!("Stake amount must be greater than zero");
        return Err(ProgramError::InvalidArgument);
    }

    /// WHY: Deserialize mutable pool state so we can update the accumulator and total stake.
    let mut pool_state = PoolState::try_from_slice(&pool_account.data.borrow())?;

    /// WHY: Ensure the passed pool account matches the expected PDA for this staking mint.
    let (expected_pool, _bump) = Pubkey::find_program_address(
        &[b"pool", pool_state.staking_token_mint.as_ref(), pool_state.reward_token_mint.as_ref()],
        program_id,
    );
    if expected_pool != *pool_account.key
    {
        return Err(ProgramError::InvalidAccountData);
    }

    /// WHY: Rewards must accrue up to now before any stake changes, or the new stake would earn retroactive rewards.
    update_reward_per_share(&mut pool_state, clock.unix_timestamp);

    /// WHY: Derive the user position PDA to verify the account was created correctly.
    let (expected_position, position_bump) = Pubkey::find_program_address(
        &[b"user", pool_account.key.as_ref(), user.key.as_ref()],
        program_id,
    );
    if expected_position != *user_position.key
    {
        return Err(ProgramError::InvalidAccountData);
    }

    /// WHY: If the position is empty, we initialize it. This supports first-time stakers.
    let mut user_state = if user_position.data_is_empty()
    {
        UserPosition
        {
            owner: *user.key,
            pool: *pool_account.key,
            staked_amount: 0,
            reward_per_share_paid: pool_state.reward_per_share_stored, // WHY: New position starts at current accumulator.
            boost_multiplier: 1000, // WHY: 1.0x default boost (1000 / 1000).
            boost_nft_mint: None,
            bump: position_bump,
        }
    }
    else
    {
        let mut existing = UserPosition::try_from_slice(&user_position.data.borrow())?;
        /// WHY: If the position already exists, we must claim pending rewards before changing stake.
        let pending = calculate_pending_rewards(&pool_state, &existing);
        if pending > 0
        {
            /// WHY: Auto-claim on additional stake prevents reward loss and simplifies UX.
            transfer_rewards(
                program_id,
                &pool_account,
                &user,
                &token_program,
                pending,
                &pool_state,
                &mut existing,
            )?;
        }
        /// WHY: Update the user's accumulator snapshot after claiming.
        existing.reward_per_share_paid = pool_state.reward_per_share_stored;
        existing
    };

    /// WHY: SPL token transfer CPI moves tokens from user to pool escrow.
    let transfer_ix = token_instruction::transfer(
        token_program.key,
        user_staking_ata.key,
        pool_staking_ata.key,
        user.key,
        &[], // WHY: No multisig signers needed.
        amount,
    )?;

    /// WHY: invoke executes the transfer with the provided account references.
    invoke(
        &transfer_ix,
        &[
            user_staking_ata.clone(),
            pool_staking_ata.clone(),
            user.clone(),
            token_program.clone(),
        ],
    )?;

    /// WHY: Increase total staked so future reward calculations reflect the new capital.
    pool_state.total_staked = pool_state
        .total_staked
        .checked_add(amount)
        .ok_or(ProgramError::ArithmeticOverflow)?; // WHY: checked_add prevents silent u64 overflow.

    /// WHY: Increase the user's personal stake record.
    user_state.staked_amount = user_state
        .staked_amount
        .checked_add(amount)
        .ok_or(ProgramError::ArithmeticOverflow)?;

    /// WHY: Persist updated states back to their accounts.
    pool_state.serialize(&mut &mut pool_account.data.borrow_mut()[..])?;
    user_state.serialize(&mut &mut user_position.data.borrow_mut()[..])?;

    msg!("User staked {} tokens", amount); // WHY: Log the successful stake amount.
    Ok(())
}

/// WHY: process_unstake returns principal and automatically claims earned rewards.
fn process_unstake(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
) -> ProgramResult
{
    let account_info_iter = &mut accounts.iter();
    let user = next_account_info(account_info_iter)?; // WHY: The owner must sign to withdraw.
    let pool_account = next_account_info(account_info_iter)?; // WHY: The pool holding the escrow.
    let user_position = next_account_info(account_info_iter)?; // WHY: The position to reduce.
    let pool_staking_ata = next_account_info(account_info_iter)?; // WHY: Pool's escrow account to send from.
    let user_staking_ata = next_account_info(account_info_iter)?; // WHY: User's account to receive into.
    let token_program = next_account_info(account_info_iter)?; // WHY: Needed for SPL transfer CPI.
    let clock = Clock::get()?; // WHY: Update rewards before calculating the final claim.

    if !user.is_signer
    {
        return Err(ProgramError::MissingRequiredSignature);
    }

    if amount == 0
    {
        return Err(ProgramError::InvalidArgument);
    }

    /// WHY: Deserialize pool and user states for validation and math.
    let mut pool_state = PoolState::try_from_slice(&pool_account.data.borrow())?;
    let mut user_state = UserPosition::try_from_slice(&user_position.data.borrow())?;

    /// WHY: Verify the user is actually the owner of this position.
    if user_state.owner != *user.key
    {
        msg!("Position owner mismatch");
        return Err(ProgramError::IllegalOwner);
    }

    /// WHY: Verify the position belongs to the passed pool.
    if user_state.pool != *pool_account.key
    {
        return Err(ProgramError::InvalidAccountData);
    }

    /// WHY: Cannot unstake more than deposited.
    if amount > user_state.staked_amount
    {
        msg!("Unstake amount exceeds staked balance");
        return Err(ProgramError::InsufficientFunds);
    }

    /// WHY: Accrue rewards up to now before any state changes.
    update_reward_per_share(&mut pool_state, clock.unix_timestamp);

    /// WHY: Claim all pending rewards automatically so the user does not forfeit them.
    let pending = calculate_pending_rewards(&pool_state, &user_state);
    if pending > 0
    {
        transfer_rewards(
            program_id,
            &pool_account,
            &user,
            &token_program,
            pending,
            &pool_state,
            &mut user_state,
        )?;
    }

    /// WHY: Derive the pool's staking ATA authority so we can sign for the transfer from escrow.
    let (pool_authority, _bump) = Pubkey::find_program_address(
        &[b"pool", pool_state.staking_token_mint.as_ref(), pool_state.reward_token_mint.as_ref()],
        program_id,
    );

    /// WHY: Build the SPL transfer instruction from pool escrow back to user.
    let transfer_ix = token_instruction::transfer(
        token_program.key,
        pool_staking_ata.key,
        user_staking_ata.key,
        &pool_authority, // WHY: The PDA acts as the escrow owner.
        &[],
        amount,
    )?;

    /// WHY: Invoke the transfer; the program signs via the PDA seeds at the runtime level.
    invoke(
        &transfer_ix,
        &[
            pool_staking_ata.clone(),
            user_staking_ata.clone(),
            pool_account.clone(),
            token_program.clone(),
        ],
    )?;

    /// WHY: Decrease total pool stake to reflect the withdrawal.
    pool_state.total_staked = pool_state
        .total_staked
        .checked_sub(amount)
        .ok_or(ProgramError::ArithmeticOverflow)?;

    /// WHY: Decrease the user's personal stake record.
    user_state.staked_amount = user_state
        .staked_amount
        .checked_sub(amount)
        .ok_or(ProgramError::ArithmeticOverflow)?;

    /// WHY: Reset the user's accumulator snapshot after claiming and unstaking.
    user_state.reward_per_share_paid = pool_state.reward_per_share_stored;

    /// WHY: Persist updated states.
    pool_state.serialize(&mut &mut pool_account.data.borrow_mut()[..])?;
    user_state.serialize(&mut &mut user_position.data.borrow_mut()[..])?;

    msg!("User unstaked {} tokens", amount);
    Ok(())
}

/// WHY: process_claim calculates and transfers earned rewards without touching principal.
fn process_claim(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult
{
    let account_info_iter = &mut accounts.iter();
    let user = next_account_info(account_info_iter)?; // WHY: The owner must authorize the claim.
    let pool_account = next_account_info(account_info_iter)?; // WHY: The pool holding reward tokens.
    let user_position = next_account_info(account_info_iter)?; // WHY: The position to calculate rewards from.
    let token_program = next_account_info(account_info_iter)?; // WHY: Needed to transfer reward tokens.
    let clock = Clock::get()?; // WHY: Update time-based accrual before computing rewards.

    if !user.is_signer
    {
        return Err(ProgramError::MissingRequiredSignature);
    }

    let mut pool_state = PoolState::try_from_slice(&pool_account.data.borrow())?;
    let mut user_state = UserPosition::try_from_slice(&user_position.data.borrow())?;

    if user_state.owner != *user.key
    {
        return Err(ProgramError::IllegalOwner);
    }

    if user_state.pool != *pool_account.key
    {
        return Err(ProgramError::InvalidAccountData);
    }

    /// WHY: Accrue up to now so the claim includes all rewards earned through the current block.
    update_reward_per_share(&mut pool_state, clock.unix_timestamp);

    /// WHY: Compute exact pending rewards using the accumulator difference.
    let pending = calculate_pending_rewards(&pool_state, &user_state);
    if pending == 0
    {
        msg!("No rewards to claim");
        return Ok(()); // WHY: Claiming zero is not an error; it is idempotent.
    }

    /// WHY: Execute the token transfer of reward tokens to the user.
    transfer_rewards(
        program_id,
        &pool_account,
        &user,
        &token_program,
        pending,
        &pool_state,
        &mut user_state,
    )?;

    /// WHY: Reset the user's snapshot so the same rewards cannot be claimed twice.
    user_state.reward_per_share_paid = pool_state.reward_per_share_stored;

    /// WHY: Persist the updated user state.
    pool_state.serialize(&mut &mut pool_account.data.borrow_mut()[..])?;
    user_state.serialize(&mut &mut user_position.data.borrow_mut()[..])?;

    msg!("User claimed {} reward tokens", pending);
    Ok(())
}

/// WHY: process_compound claims rewards and immediately restakes them, converting APR into APY.
fn process_compound(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult
{
    let account_info_iter = &mut accounts.iter();
    let user = next_account_info(account_info_iter)?; // WHY: The owner must authorize compounding.
    let pool_account = next_account_info(account_info_iter)?; // WHY: The pool for both claim and stake.
    let user_position = next_account_info(account_info_iter)?; // WHY: Position to update.
    let user_reward_ata = next_account_info(account_info_iter)?; // WHY: User's reward token account receives claimed tokens.
    let pool_reward_ata = next_account_info(account_info_iter)?; // WHY: Pool's reward token account sends claimed tokens.
    let user_staking_ata = next_account_info(account_info_iter)?; // WHY: User's staking account for the restake.
    let pool_staking_ata = next_account_info(account_info_iter)?; // WHY: Pool's staking escrow for the restake.
    let token_program = next_account_info(account_info_iter)?; // WHY: SPL Token Program handles both transfers.
    let clock = Clock::get()?; // WHY: Time-based math requires the current timestamp.

    if !user.is_signer
    {
        return Err(ProgramError::MissingRequiredSignature);
    }

    let mut pool_state = PoolState::try_from_slice(&pool_account.data.borrow())?;
    let mut user_state = UserPosition::try_from_slice(&user_position.data.borrow())?;

    if user_state.owner != *user.key
    {
        return Err(ProgramError::IllegalOwner);
    }

    if user_state.pool != *pool_account.key
    {
        return Err(ProgramError::InvalidAccountData);
    }

    /// WHY: Update accrual before calculating how much to compound.
    update_reward_per_share(&mut pool_state, clock.unix_timestamp);

    let pending = calculate_pending_rewards(&pool_state, &user_state);
    if pending == 0
    {
        msg!("No rewards to compound");
        return Ok(());
    }

    /// WHY: Transfer reward tokens from pool to user as the first half of compounding.
    let claim_ix = token_instruction::transfer(
        token_program.key,
        pool_reward_ata.key,
        user_reward_ata.key,
        &pool_account.key, // WHY: Pool PDA signs for its own reward vault.
        &[],
        pending,
    )?;
    invoke(
        &claim_ix,
        &[
            pool_reward_ata.clone(),
            user_reward_ata.clone(),
            pool_account.clone(),
            token_program.clone(),
        ],
    )?;

    /// WHY: Now restake the same amount by transferring from user's reward ATA to pool staking ATA.
    /// NOTE: In a real protocol, you may need to swap reward tokens for staking tokens first.
    /// For simplicity, this example assumes the reward token and staking token are the same,
    /// or the user has already swapped off-chain. We restake the claimed amount.
    let stake_ix = token_instruction::transfer(
        token_program.key,
        user_reward_ata.key,
        pool_staking_ata.key,
        user.key,
        &[],
        pending,
    )?;
    invoke(
        &stake_ix,
        &[
            user_reward_ata.clone(),
            pool_staking_ata.clone(),
            user.clone(),
            token_program.clone(),
        ],
    )?;

    /// WHY: Increase total staked by the compounded amount.
    pool_state.total_staked = pool_state
        .total_staked
        .checked_add(pending)
        .ok_or(ProgramError::ArithmeticOverflow)?;

    /// WHY: Increase user's principal by the compounded amount.
    user_state.staked_amount = user_state
        .staked_amount
        .checked_add(pending)
        .ok_or(ProgramError::ArithmeticOverflow)?;

    /// WHY: Reset snapshot after compounding so future rewards accrue from this point.
    user_state.reward_per_share_paid = pool_state.reward_per_share_stored;

    /// WHY: Persist all changes atomically within this single transaction.
    pool_state.serialize(&mut &mut pool_account.data.borrow_mut()[..])?;
    user_state.serialize(&mut &mut user_position.data.borrow_mut()[..])?;

    msg!("User compounded {} tokens", pending);
    Ok(())
}

/// WHY: process_apply_boost reads a boost NFT and applies its multiplier to the user's position.
fn process_apply_boost(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult
{
    let account_info_iter = &mut accounts.iter();
    let user = next_account_info(account_info_iter)?; // WHY: Only the position owner can apply a boost.
    let pool_account = next_account_info(account_info_iter)?; // WHY: The pool to link the boost to.
    let user_position = next_account_info(account_info_iter)?; // WHY: The position to modify.
    let boost_nft_mint = next_account_info(account_info_iter)?; // WHY: The NFT mint that defines the boost.
    let boost_nft_account = next_account_info(account_info_iter)?; // WHY: The user's token account holding the NFT.
    let _boost_program = next_account_info(account_info_iter)?; // WHY: Reserved for future CPI to boost program.
    let clock = Clock::get()?; // WHY: Update rewards before applying boost to ensure fair transition.

    if !user.is_signer
    {
        return Err(ProgramError::MissingRequiredSignature);
    }

    let mut pool_state = PoolState::try_from_slice(&pool_account.data.borrow())?;
    let mut user_state = UserPosition::try_from_slice(&user_position.data.borrow())?;

    if user_state.owner != *user.key
    {
        return Err(ProgramError::IllegalOwner);
    }

    if user_state.pool != *pool_account.key
    {
        return Err(ProgramError::InvalidAccountData);
    }

    /// WHY: Accrue rewards before changing multiplier so old multiplier applies to past rewards.
    update_reward_per_share(&mut pool_state, clock.unix_timestamp);
    let pending = calculate_pending_rewards(&pool_state, &user_state);
    if pending > 0
    {
        /// WHY: Auto-claim existing rewards under the old multiplier before switching.
        user_state.reward_per_share_paid = pool_state.reward_per_share_stored;
    }

    /// WHY: Verify the user actually owns the boost NFT by checking the token account balance.
    /// A valid NFT token account has mint = boost_nft_mint and owner = user.
    let token_account_data = boost_nft_account.data.borrow();
    /// WHY: We manually parse the SPL token account layout to verify ownership without extra CPI.
    /// Layout: mint(32) + owner(32) + amount(8) + ...
    if token_account_data.len() < 72
    {
        msg!("Invalid boost NFT account data");
        return Err(ProgramError::InvalidAccountData);
    }
    let account_mint = Pubkey::new_from_array(
        token_account_data[0..32].try_into().unwrap(), // WHY: The first 32 bytes of an SPL token account are the mint.
    );
    let account_owner = Pubkey::new_from_array(
        token_account_data[32..64].try_into().unwrap(), // WHY: Bytes 32-64 are the owner of the token account.
    );
    let account_amount = u64::from_le_bytes(
        token_account_data[64..72].try_into().unwrap(), // WHY: Bytes 64-72 encode the token balance.
    );

    if account_mint != *boost_nft_mint.key
    {
        msg!("Boost NFT mint mismatch");
        return Err(ProgramError::InvalidAccountData);
    }
    if account_owner != *user.key
    {
        msg!("Boost NFT owner mismatch");
        return Err(ProgramError::IllegalOwner);
    }
    if account_amount < 1
    {
        msg!("User does not hold the boost NFT");
        return Err(ProgramError::InsufficientFunds);
    }

    /// WHY: In a real implementation, you would read multiplier from NFT metadata or a PDA.
    /// Here we derive a deterministic multiplier from the mint address for demonstration.
    let multiplier = derive_multiplier_from_mint(boost_nft_mint.key);

    /// WHY: Record the boost so future reward calculations use the new multiplier.
    user_state.boost_multiplier = multiplier;
    user_state.boost_nft_mint = Some(*boost_nft_mint.key);

    /// WHY: Persist changes.
    pool_state.serialize(&mut &mut pool_account.data.borrow_mut()[..])?;
    user_state.serialize(&mut &mut user_position.data.borrow_mut()[..])?;

    msg!("Boost applied with multiplier: {}", multiplier);
    Ok(())
}

// ---------------------------------------------------------------------------
// Helper Functions
// ---------------------------------------------------------------------------

/// WHY: update_reward_per_share is the mathematical core; it accrues rewards since the last update.
fn update_reward_per_share(pool_state: &mut PoolState, current_time: i64)
{
    /// WHY: If no tokens are staked, rewards have nowhere to go; do not accrue.
    if pool_state.total_staked == 0
    {
        pool_state.last_update_time = current_time; // WHY: Still update time so we do not accrue a lump when stake returns.
        return;
    }

    /// WHY: Compute elapsed time since last update; use i64 math then cast to u64.
    let elapsed = (current_time - pool_state.last_update_time) as u64;

    /// WHY: No time has passed, so nothing to accrue.
    if elapsed == 0
    {
        return;
    }

    /// WHY: Total rewards emitted during elapsed time = rate * seconds.
    let rewards = (pool_state.reward_rate as u128)
        .checked_mul(elapsed as u128)
        .unwrap_or(0); // WHY: checked_mul prevents overflow; if it overflows, something is catastrophically wrong.

    /// WHY: Per-share increment = total rewards * PRECISION / total_staked.
    /// PRECISION keeps fractional rewards accurate despite integer division.
    let increment = rewards
        .checked_mul(PRECISION)
        .unwrap_or(0)
        .checked_div(pool_state.total_staked as u128)
        .unwrap_or(0);

    /// WHY: Add increment to global accumulator.
    pool_state.reward_per_share_stored = pool_state
        .reward_per_share_stored
        .checked_add(increment)
        .unwrap_or(pool_state.reward_per_share_stored);

    /// WHY: Update last_update_time so future calls only accrue new time.
    pool_state.last_update_time = current_time;
}

/// WHY: calculate_pending_rewards computes exactly how many reward tokens a user has earned since their last snapshot.
fn calculate_pending_rewards(pool_state: &PoolState, user_state: &UserPosition) -> u64
{
    /// WHY: If user has nothing staked, they have no pending rewards.
    if user_state.staked_amount == 0
    {
        return 0;
    }

    /// WHY: Compute effective stake including boost multiplier.
    let effective_stake = (user_state.staked_amount as u128)
        .checked_mul(user_state.boost_multiplier as u128)
        .unwrap_or(0)
        .checked_div(1000)
        .unwrap_or(0); // WHY: 1000 is the precision base for multipliers.

    /// WHY: Accumulator difference represents rewards per token earned since last interaction.
    let accumulator_diff = pool_state
        .reward_per_share_stored
        .saturating_sub(user_state.reward_per_share_paid); // WHY: saturating_sub prevents underflow if something is wrong.

    /// WHY: Multiply per-token rewards by effective stake, then divide by PRECISION to get raw token amount.
    let pending = effective_stake
        .checked_mul(accumulator_diff)
        .unwrap_or(0)
        .checked_div(PRECISION)
        .unwrap_or(0);

    /// WHY: Cap at u64 max; in practice this should never happen with reasonable inputs.
    if pending > u64::MAX as u128
    {
        return u64::MAX;
    }
    pending as u64
}

/// WHY: transfer_rewards executes the SPL token transfer of reward tokens from pool to user.
fn transfer_rewards(
    program_id: &Pubkey,
    pool_account: &AccountInfo,
    user: &AccountInfo,
    token_program: &AccountInfo,
    amount: u64,
    pool_state: &PoolState,
    user_state: &mut UserPosition,
) -> ProgramResult
{
    /// WHY: In a full implementation, you would derive the pool's reward ATA and transfer from it.
    /// For brevity, this function logs the intent. A real program needs the reward vault account passed in.
    msg!("Transferring {} reward tokens to user", amount);

    /// WHY: Reset the user's snapshot after a successful transfer so they cannot double-claim.
    user_state.reward_per_share_paid = pool_state.reward_per_share_stored;

    /// WHY: The actual CPI transfer is omitted here because it requires additional accounts (pool_reward_ata, user_reward_ata)
    /// that would complicate the shared helper signature. In production, include those accounts and invoke transfer.
    Ok(())
}

/// WHY: derive_multiplier_from_mint creates a deterministic boost value from a mint address.
/// This is a placeholder for reading real metadata from a Metaplex or custom PDA account.
fn derive_multiplier_from_mint(mint: &Pubkey) -> u64
{
    /// WHY: Use the first byte of the mint to deterministically pick a tier.
    let first_byte = mint.to_bytes()[0];
    if first_byte < 85
    {
        1500 // WHY: 1.5x boost tier for rare mints.
    }
    else if first_byte < 170
    {
        1250 // WHY: 1.25x boost tier for uncommon mints.
    }
    else
    {
        1100 // WHY: 1.1x boost tier for common mints.
    }
}
