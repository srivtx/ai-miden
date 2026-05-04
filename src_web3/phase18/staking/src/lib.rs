use solana_program::{ // Import the Solana program SDK for building on-chain programs
    account_info::{next_account_info, AccountInfo}, // Import utilities to iterate and validate transaction accounts
    entrypoint, // Import the macro to register the program's main entry point
    entrypoint::ProgramResult, // Import the typed result for success and error returns
    msg, // Import the logging utility to emit debug messages during execution
    program_error::ProgramError, // Import standard error types for clean failure reporting
    pubkey::Pubkey, // Import the Pubkey type for Solana address handling
    clock::Clock, // Import the Clock struct to access on-chain time
    sysvar::Sysvar, // Import the Sysvar trait to load system variables like Clock
};
use borsh::{BorshDeserialize, BorshSerialize}; // Import Borsh traits to serialize and deserialize account data

/// Phase 18: Staking Program
///
/// This program manages token staking with time-based rewards:
/// - InitializePool: Creates a staking pool with a reward rate
/// - Stake: Locks tokens and starts tracking time
/// - ClaimRewards: Calculates and pays out accumulated rewards
/// - Unstake: Returns staked tokens and optionally claims rewards

entrypoint!(process_instruction); // Register process_instruction as the function the Solana runtime invokes

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Enable serialization and debugging for pool state
pub struct StakingPool { // Define the on-chain data structure representing the staking pool
    pub reward_rate: u64, // Rewards per second per staked token, scaled for integer math
    pub total_staked: u64, // Total number of tokens currently locked across all stakers
    pub reward_pool_balance: u64, // Remaining tokens available to pay future rewards
}

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Enable serialization and debugging for staker state
pub struct StakerPosition { // Define the on-chain data structure tracking an individual staker
    pub amount: u64, // Number of tokens this user has staked
    pub staked_at: i64, // Unix timestamp of the last stake or claim to calculate elapsed time
    pub total_claimed: u64, // Lifetime rewards this user has already withdrawn
}

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Enable serialization and debugging for instructions
pub enum StakingInstruction { // Enumerate every instruction this program supports
    InitializePool { reward_rate: u64, initial_rewards: u64 }, // Create a pool with a reward rate and seed the reward treasury
    Stake { amount: u64 }, // Lock tokens into the pool and start the reward timer
    ClaimRewards, // Calculate and pay out rewards earned since the last claim or stake
    Unstake { amount: u64 }, // Unlock tokens and return them to the user
}

fn process_instruction( // Define the main instruction handler invoked by the Solana runtime
    _program_id: &Pubkey, // Accept the program ID even though this simple demo does not use it
    accounts: &[AccountInfo], // Receive the ordered array of accounts passed by the transaction
    instruction_data: &[u8], // Receive the raw binary payload that encodes the instruction
) -> ProgramResult { // Return a typed result so the runtime knows if execution succeeded
    let instruction = StakingInstruction::try_from_slice(instruction_data) // Deserialize the instruction bytes into a typed enum
        .map_err(|_| ProgramError::InvalidInstructionData)?; // If deserialization fails, abort with a clear error code

    let account_info_iter = &mut accounts.iter(); // Create a mutable iterator to consume accounts in order
    let pool_account = next_account_info(account_info_iter)?; // Fetch the pool account because it holds global state
    let user = next_account_info(account_info_iter)?; // Fetch the user account to verify transaction authorization

    if !user.is_signer { // Reject the transaction if the user did not sign because state changes require permission
        msg!("User must sign"); // Log the failure so developers can debug signature issues
        return Err(ProgramError::MissingRequiredSignature); // Return the standard missing-signature error
    } // Close the signature check

    let mut pool = StakingPool::try_from_slice(&pool_account.data.borrow()) // Attempt to load existing pool state from account data
        .unwrap_or(StakingPool { reward_rate: 0, total_staked: 0, reward_pool_balance: 0 }); // Default to zeros if uninitialized

    match instruction { // Branch execution based on which instruction variant was deserialized
        StakingInstruction::InitializePool { reward_rate, initial_rewards } => { // Handle pool creation and treasury seeding
            if pool.reward_rate != 0 { // Prevent overwriting an existing pool to avoid destroying staker data
                msg!("Pool already initialized"); // Log the conflict so operators understand the failure
                return Err(ProgramError::AccountAlreadyInitialized); // Return the standard already-initialized error
            } // Close the duplicate guard
            pool.reward_rate = reward_rate; // Store the reward rate that determines how fast stakers earn
            pool.reward_pool_balance = initial_rewards; // Seed the treasury with tokens available for distribution
            pool.total_staked = 0; // Explicitly start with zero staked tokens
            pool.serialize(&mut &mut pool_account.data.borrow_mut()[..])?; // Persist the new pool state to the account
            msg!("Pool initialized: rate={}, rewards={}", reward_rate, initial_rewards); // Log the initialization parameters
        } // Close the InitializePool arm
        StakingInstruction::Stake { amount } => { // Handle a user locking tokens into the staking pool
            let staker_account = next_account_info(account_info_iter)?; // Fetch the user's staker account to store their position
            let clock = Clock::get()?; // Load the on-chain clock to record the exact time of the stake

            let mut staker = StakerPosition::try_from_slice(&staker_account.data.borrow()) // Attempt to load the user's existing position
                .unwrap_or(StakerPosition { amount: 0, staked_at: clock.unix_timestamp, total_claimed: 0 }); // Default to zero with current time

            staker.amount = staker.amount.checked_add(amount) // Increase the staked amount by the deposit
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort if the addition overflows u64
            staker.staked_at = clock.unix_timestamp; // Reset the timer to now because the staked amount changed
            staker.serialize(&mut &mut staker_account.data.borrow_mut()[..])?; // Persist the updated staker position

            pool.total_staked = pool.total_staked.checked_add(amount) // Increase the global staked total
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on overflow
            pool.serialize(&mut &mut pool_account.data.borrow_mut()[..])?; // Persist the updated pool totals
            msg!("Staked {} tokens at timestamp {}", amount, clock.unix_timestamp); // Log the stake event with time
        } // Close the Stake arm
        StakingInstruction::ClaimRewards => { // Handle a user requesting their accumulated reward payout
            let staker_account = next_account_info(account_info_iter)?; // Fetch the user's staker account to read their position
            let clock = Clock::get()?; // Load the on-chain clock to calculate elapsed time since the last claim

            let mut staker = StakerPosition::try_from_slice(&staker_account.data.borrow())?; // Deserialize the staker position
            let elapsed = clock.unix_timestamp.checked_sub(staker.staked_at) // Calculate how many seconds have passed since stake or last claim
                .ok_or(ProgramError::ArithmeticOverflow)? as u64; // Convert to u64 for multiplication

            let rewards = (staker.amount as u128) // Use u128 to prevent overflow during multiplication
                .checked_mul(pool.reward_rate as u128) // Multiply staked amount by the per-second reward rate
                .and_then(|v| v.checked_mul(elapsed as u128)) // Multiply by elapsed seconds to get total earned
                .and_then(|v| v.checked_div(1_000_000)) // Divide by a scaling factor because reward_rate uses fixed-point math
                .ok_or(ProgramError::ArithmeticOverflow)? as u64; // Cast back to u64 for storage

            if rewards > pool.reward_pool_balance { // Ensure the treasury can cover the payout
                msg!("Insufficient reward pool balance"); // Log the shortfall for debugging
                return Err(ProgramError::InsufficientFunds); // Return the standard insufficient funds error
            } // Close the treasury balance check

            pool.reward_pool_balance = pool.reward_pool_balance.checked_sub(rewards) // Decrease the treasury by the paid amount
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort if subtraction underflows
            staker.total_claimed = staker.total_claimed.checked_add(rewards) // Increase the lifetime claimed counter
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on overflow
            staker.staked_at = clock.unix_timestamp; // Reset the timer to now so future rewards start from zero
            staker.serialize(&mut &mut staker_account.data.borrow_mut()[..])?; // Persist the updated staker position
            pool.serialize(&mut &mut pool_account.data.borrow_mut()[..])?; // Persist the updated pool treasury
            msg!("Claimed {} rewards at timestamp {}", rewards, clock.unix_timestamp); // Log the claim event
        } // Close the ClaimRewards arm
        StakingInstruction::Unstake { amount } => { // Handle a user withdrawing their staked tokens
            let staker_account = next_account_info(account_info_iter)?; // Fetch the user's staker account
            let clock = Clock::get()?; // Load the on-chain clock to update timing after unstaking

            let mut staker = StakerPosition::try_from_slice(&staker_account.data.borrow())?; // Deserialize the staker position
            if amount > staker.amount { // Reject if the user tries to unstake more than they have locked
                msg!("Insufficient staked amount"); // Log the overdraft attempt
                return Err(ProgramError::InsufficientFunds); // Return the standard insufficient funds error
            } // Close the balance check

            let elapsed = clock.unix_timestamp.checked_sub(staker.staked_at) // Calculate seconds since last claim or stake
                .ok_or(ProgramError::ArithmeticOverflow)? as u64; // Convert to u64 for reward math
            let pending_rewards = (staker.amount as u128) // Use u128 for safe intermediate math
                .checked_mul(pool.reward_rate as u128) // Apply the per-token reward rate
                .and_then(|v| v.checked_mul(elapsed as u128)) // Multiply by elapsed time
                .and_then(|v| v.checked_div(1_000_000)) // Apply the fixed-point scaling factor
                .ok_or(ProgramError::ArithmeticOverflow)? as u64; // Cast back to u64

            if pending_rewards > 0 && pending_rewards <= pool.reward_pool_balance { // Auto-claim pending rewards before unstaking
                pool.reward_pool_balance = pool.reward_pool_balance.checked_sub(pending_rewards) // Deduct rewards from treasury
                    .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on underflow
                staker.total_claimed = staker.total_claimed.checked_add(pending_rewards) // Add to lifetime claimed
                    .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on overflow
                msg!("Auto-claimed {} rewards on unstake", pending_rewards); // Log the auto-claim for transparency
            } // Close the auto-claim block

            staker.amount = staker.amount.checked_sub(amount) // Reduce the staked amount by the withdrawal
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort if subtraction underflows
            staker.staked_at = clock.unix_timestamp; // Reset the timer because the staked amount changed
            staker.serialize(&mut &mut staker_account.data.borrow_mut()[..])?; // Persist the updated staker position

            pool.total_staked = pool.total_staked.checked_sub(amount) // Reduce the global staked total
                .ok_or(ProgramError::ArithmeticOverflow)?; // Abort on underflow
            pool.serialize(&mut &mut pool_account.data.borrow_mut()[..])?; // Persist the updated pool totals
            msg!("Unstaked {} tokens at timestamp {}", amount, clock.unix_timestamp); // Log the unstake event
        } // Close the Unstake arm
    } // Close the match block

    Ok(()) // Return success so the runtime finalizes the transaction
} // Close the process_instruction function
