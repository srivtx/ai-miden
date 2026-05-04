use solana_program::{
    // WHY: Import AccountInfo so the program can read and write on-chain account data.
    account_info::{next_account_info, AccountInfo},
    // WHY: Import Clock to read the current block timestamp for interest accrual.
    clock::Clock,
    // WHY: Import the entrypoint macro so the Solana runtime knows where execution begins.
    entrypoint,
    // WHY: Import ProgramResult as the standard return type for Solana instructions.
    entrypoint::ProgramResult,
    // WHY: Import msg so the program can emit logs for debugging and indexing.
    msg,
    // WHY: Import invoke to call external programs like the SPL Token program.
    program::invoke,
    // WHY: Import invoke_signed so a PDA can sign cross-program invocations.
    program::invoke_signed,
    // WHY: Import ProgramError for standardized error codes.
    program_error::ProgramError,
    // WHY: Import Pubkey to represent addresses and derive PDAs.
    pubkey::Pubkey,
    // WHY: Import Sysvar so Clock can be deserialized from a sysvar account.
    sysvar::Sysvar,
};
// WHY: Import Borsh for compact binary serialization of account state.
use borsh::{BorshDeserialize, BorshSerialize};
// WHY: Import Error from thiserror to define readable custom errors with minimal code.
use thiserror::Error;

// WHY: Register process_instruction as the entrypoint so every transaction starts here.
entrypoint!(process_instruction);

// WHY: Define custom errors so failed transactions return human-readable messages.
#[derive(Error, Debug, Copy, Clone, PartialEq)]
pub enum LendingError {
    // WHY: Prevent initializing the same market twice.
    #[error("Already initialized")]
    AlreadyInitialized,
    // WHY: Ensure instructions only run after initialization.
    #[error("Not initialized")]
    NotInitialized,
    // WHY: Reject zero or nonsensical amounts.
    #[error("Invalid amount")]
    InvalidAmount,
    // WHY: Catch any arithmetic that exceeds u64 bounds.
    #[error("Math overflow")]
    MathOverflow,
    // WHY: Block borrowing when collateral is too low.
    #[error("Insufficient collateral")]
    InsufficientCollateral,
    // WHY: Block borrows that exceed the collateral factor limit.
    #[error("Borrow amount too large")]
    BorrowTooLarge,
    // WHY: Prevent repaying more than the current debt.
    #[error("Repay amount too large")]
    RepayTooLarge,
    // WHY: Prevent withdrawing more collateral than was deposited.
    #[error("Withdraw amount too large")]
    WithdrawTooLarge,
    // WHY: Reject withdrawals that would make the position unsafe.
    #[error("Health factor too low")]
    HealthFactorTooLow,
    // WHY: Ensure liquidations only target underwater positions.
    #[error("Position not liquidatable")]
    NotLiquidatable,
    // WHY: Cap how much of a debt a single liquidation can clear.
    #[error("Close factor exceeded")]
    CloseFactorExceeded,
}

// WHY: Map LendingError into ProgramError so the runtime understands the failure.
impl From<LendingError> for ProgramError {
    fn from(e: LendingError) -> Self {
        ProgramError::Custom(e as u32)
    }
}

// WHY: Enumerate all supported instructions so the entrypoint can route correctly.
#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)]
pub enum LendingInstruction {
    // WHY: InitializeMarket sets global parameters once before any user interacts.
    InitializeMarket {
        collateral_factor: u64,
        liquidation_bonus: u64,
        close_factor: u64,
        base_rate: u64,
        slope1: u64,
        slope2: u64,
        optimal_utilization: u64,
        reserve_factor: u64,
    },
    // WHY: Deposit allows users to lock collateral into the protocol.
    Deposit { amount: u64 },
    // WHY: Borrow lets users withdraw loan tokens against their collateral.
    Borrow { amount: u64 },
    // WHY: Repay returns loan tokens and reduces debt.
    Repay { amount: u64 },
    // WHY: Withdraw returns collateral after debt is reduced.
    Withdraw { amount: u64 },
    // WHY: Liquidate clears underwater debt in exchange for discounted collateral.
    Liquidate { repay_amount: u64 },
}

// WHY: MarketState is the global account that tracks pool-wide metrics.
#[derive(BorshSerialize, BorshDeserialize, Debug, Clone, Default)]
pub struct MarketState {
    // WHY: A flag prevents reading uninitialized account data as valid state.
    pub is_initialized: bool,
    // WHY: total_deposits is the sum of all collateral tokens held by the protocol.
    pub total_deposits: u64,
    // WHY: total_borrows is the sum of all outstanding debt in borrow-token units.
    pub total_borrows: u64,
    // WHY: collateral_factor limits how much can be borrowed against each unit of collateral.
    pub collateral_factor: u64,
    // WHY: liquidation_bonus incentivizes third parties to liquidate bad debt.
    pub liquidation_bonus: u64,
    // WHY: close_factor caps the percentage of debt liquidated in one transaction.
    pub close_factor: u64,
    // WHY: base_rate is the minimum borrow rate when utilization is zero.
    pub base_rate: u64,
    // WHY: slope1 controls how fast rates rise below the optimal utilization point.
    pub slope1: u64,
    // WHY: slope2 controls how fast rates rise above the optimal utilization point.
    pub slope2: u64,
    // WHY: optimal_utilization is the kink point between the two rate slopes.
    pub optimal_utilization: u64,
    // WHY: reserve_factor is the protocol fee taken from borrower interest.
    pub reserve_factor: u64,
    // WHY: borrow_index accumulates interest over time for all borrowers.
    pub borrow_index: u128,
    // WHY: last_update_time stores the last Unix timestamp when interest was accrued.
    pub last_update_time: i64,
}

// WHY: UserPosition stores each borrower's isolated collateral and debt state.
#[derive(BorshSerialize, BorshDeserialize, Debug, Clone, Default)]
pub struct UserPosition {
    // WHY: A flag prevents reading an account that has never been used.
    pub is_initialized: bool,
    // WHY: collateral_deposited tracks how much collateral the user has locked.
    pub collateral_deposited: u64,
    // WHY: borrow_principal is the debt amount scaled to the borrow_index snapshot.
    pub borrow_principal: u64,
    // WHY: borrow_index_snapshot records the global index when the user last interacted.
    pub borrow_index_snapshot: u128,
}

// WHY: OracleState is a lightweight copy of the oracle account layout so the lending program can deserialize it.
#[derive(BorshSerialize, BorshDeserialize, Debug, Clone, Default)]
pub struct OracleState {
    // WHY: price is the current market price of the collateral asset.
    pub price: u64,
    // WHY: decimals tells the program how many decimal places the price carries.
    pub decimals: u8,
}

// WHY: INDEX_SCALE represents 1.0 as a u128 so interest can compound without floating point.
const INDEX_SCALE: u128 = 1_000_000_000_000_000_000;
// WHY: SECONDS_PER_YEAR normalizes annual rates into per-second rates.
const SECONDS_PER_YEAR: u64 = 31_536_000;
// WHY: BASIS_POINTS lets the protocol express percentages as integers to avoid floats.
const BASIS_POINTS: u64 = 10_000;

// WHY: The main entrypoint deserializes the instruction and routes to the correct handler.
fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    // WHY: Deserialize the instruction payload so we know which operation to perform.
    let instruction = LendingInstruction::try_from_slice(instruction_data)
        .map_err(|_| ProgramError::InvalidInstructionData)?;
    // WHY: Match each variant to its processor so every instruction has dedicated logic.
    match instruction {
        LendingInstruction::InitializeMarket {
            collateral_factor,
            liquidation_bonus,
            close_factor,
            base_rate,
            slope1,
            slope2,
            optimal_utilization,
            reserve_factor,
        } => process_initialize_market(
            program_id,
            accounts,
            collateral_factor,
            liquidation_bonus,
            close_factor,
            base_rate,
            slope1,
            slope2,
            optimal_utilization,
            reserve_factor,
        ),
        LendingInstruction::Deposit { amount } => process_deposit(program_id, accounts, amount),
        LendingInstruction::Borrow { amount } => process_borrow(program_id, accounts, amount),
        LendingInstruction::Repay { amount } => process_repay(program_id, accounts, amount),
        LendingInstruction::Withdraw { amount } => process_withdraw(program_id, accounts, amount),
        LendingInstruction::Liquidate { repay_amount } => {
            process_liquidate(program_id, accounts, repay_amount)
        }
    }
}

// WHY: accrue_interest updates the global borrow_index and total_borrows before any state change.
fn accrue_interest(market: &mut MarketState, clock: &Clock) -> Result<(), ProgramError> {
    // WHY: Read the current on-chain timestamp to calculate elapsed time.
    let current_time = clock.unix_timestamp;
    // WHY: Compute how many seconds have passed since the last accrual.
    let elapsed = (current_time - market.last_update_time) as u64;
    // WHY: Skip expensive math if no time has passed or the pool is empty.
    if elapsed == 0 || market.total_borrows == 0 || market.total_deposits == 0 {
        market.last_update_time = current_time;
        return Ok(());
    }
    // WHY: Compute utilization so the correct rate can be selected from the piecewise curve.
    let utilization = get_utilization(market)?;
    // WHY: Fetch the borrow rate from the model based on current utilization.
    let borrow_rate = get_borrow_rate(utilization, market)?;
    // WHY: Calculate total interest = total_borrows * rate * elapsed / (seconds_per_year * basis_points).
    let interest = market
        .total_borrows
        .checked_mul(borrow_rate)
        .ok_or(LendingError::MathOverflow)?
        .checked_mul(elapsed)
        .ok_or(LendingError::MathOverflow)?
        .checked_div(SECONDS_PER_YEAR)
        .ok_or(LendingError::MathOverflow)?
        .checked_div(BASIS_POINTS)
        .ok_or(LendingError::MathOverflow)?;
    // WHY: If rounding produced zero interest, avoid unnecessary state writes.
    if interest == 0 {
        market.last_update_time = current_time;
        return Ok(());
    }
    // WHY: Increase total_borrows by the accrued interest so lender yields are tracked.
    let new_total_borrows = market
        .total_borrows
        .checked_add(interest)
        .ok_or(LendingError::MathOverflow)?;
    // WHY: Update the borrow index proportionally so every borrower's debt scales correctly.
    let index_increment = market
        .borrow_index
        .checked_mul(interest as u128)
        .ok_or(LendingError::MathOverflow)?
        .checked_div(market.total_borrows as u128)
        .ok_or(LendingError::MathOverflow)?;
    market.borrow_index = market
        .borrow_index
        .checked_add(index_increment)
        .ok_or(LendingError::MathOverflow)?;
    market.total_borrows = new_total_borrows;
    market.last_update_time = current_time;
    Ok(())
}

// WHY: get_utilization divides borrows by deposits so the rate model has a demand signal.
fn get_utilization(market: &MarketState) -> Result<u64, ProgramError> {
    if market.total_deposits == 0 {
        return Ok(0);
    }
    market
        .total_borrows
        .checked_mul(BASIS_POINTS)
        .ok_or(LendingError::MathOverflow)?
        .checked_div(market.total_deposits)
        .ok_or(LendingError::MathOverflow.into())
}

// WHY: get_borrow_rate implements the piecewise linear model with a kink at optimal utilization.
fn get_borrow_rate(utilization: u64, market: &MarketState) -> Result<u64, ProgramError> {
    if utilization <= market.optimal_utilization {
        // WHY: Below the kink, rates rise slowly using slope1.
        let extra = utilization
            .checked_mul(market.slope1)
            .ok_or(LendingError::MathOverflow)?
            .checked_div(market.optimal_utilization)
            .ok_or(LendingError::MathOverflow)?;
        market.base_rate.checked_add(extra).ok_or(LendingError::MathOverflow.into())
    } else {
        // WHY: Above the kink, rates rise sharply using slope2 to discourage bank runs.
        let extra1 = market.slope1;
        let extra2 = (utilization - market.optimal_utilization)
            .checked_mul(market.slope2)
            .ok_or(LendingError::MathOverflow)?
            .checked_div(BASIS_POINTS - market.optimal_utilization)
            .ok_or(LendingError::MathOverflow)?;
        market
            .base_rate
            .checked_add(extra1)
            .ok_or(LendingError::MathOverflow)?
            .checked_add(extra2)
            .ok_or(LendingError::MathOverflow.into())
    }
}

// WHY: get_current_borrow_balance scales the user's principal by the global borrow_index.
fn get_current_borrow_balance(
    user: &UserPosition,
    market: &MarketState,
) -> Result<u64, ProgramError> {
    if user.borrow_principal == 0 {
        return Ok(0);
    }
    // WHY: Multiply principal by the current index, then divide by the snapshot to get current debt.
    let scaled = (user.borrow_principal as u128)
        .checked_mul(market.borrow_index)
        .ok_or(LendingError::MathOverflow)?
        .checked_div(user.borrow_index_snapshot)
        .ok_or(LendingError::MathOverflow)?;
    // WHY: Convert back to u64 because token amounts fit in u64.
    scaled.try_into().map_err(|_| LendingError::MathOverflow.into())
}

// WHY: get_health_factor computes collateral value weighted by factor, divided by debt.
fn get_health_factor(
    user: &UserPosition,
    market: &MarketState,
    oracle: &OracleState,
) -> Result<u64, ProgramError> {
    // WHY: Multiply raw collateral by the oracle price to get dollar-denominated value.
    let collateral_value = user
        .collateral_deposited
        .checked_mul(oracle.price)
        .ok_or(LendingError::MathOverflow)?;
    // WHY: Adjust for oracle decimals so the value is in base units.
    let collateral_value_adj = if oracle.decimals > 0 {
        collateral_value
            .checked_div(10u64.pow(oracle.decimals as u32))
            .ok_or(LendingError::MathOverflow)?
    } else {
        collateral_value
    };
    // WHY: Apply the collateral factor to find the effective borrowing power.
    let weighted_collateral = collateral_value_adj
        .checked_mul(market.collateral_factor)
        .ok_or(LendingError::MathOverflow)?
        .checked_div(BASIS_POINTS)
        .ok_or(LendingError::MathOverflow)?;
    // WHY: Fetch the current debt including accrued interest.
    let borrow_balance = get_current_borrow_balance(user, market)?;
    if borrow_balance == 0 {
        // WHY: Return max when there is no debt so the position is always safe.
        return Ok(u64::MAX);
    }
    // WHY: Health factor is weighted collateral divided by debt, scaled by BASIS_POINTS.
    weighted_collateral
        .checked_mul(BASIS_POINTS)
        .ok_or(LendingError::MathOverflow)?
        .checked_div(borrow_balance)
        .ok_or(LendingError::MathOverflow.into())
}

// WHY: process_initialize_market sets up the global state with rate curve parameters.
fn process_initialize_market(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    collateral_factor: u64,
    liquidation_bonus: u64,
    close_factor: u64,
    base_rate: u64,
    slope1: u64,
    slope2: u64,
    optimal_utilization: u64,
    reserve_factor: u64,
) -> ProgramResult {
    // WHY: Iterate over the ordered account list so each account is assigned to the correct role.
    let account_info_iter = &mut accounts.iter();
    let market_account = next_account_info(account_info_iter)?;
    let authority = next_account_info(account_info_iter)?;
    let clock_info = next_account_info(account_info_iter)?;
    // WHY: Require the authority to sign so unauthorized actors cannot create markets.
    if !authority.is_signer {
        return Err(ProgramError::MissingRequiredSignature);
    }
    // WHY: Verify the market account is owned by this program so data is trusted.
    if market_account.owner != program_id {
        return Err(ProgramError::IncorrectProgramId);
    }
    // WHY: Deserialize existing data to check the initialization flag.
    let mut market = MarketState::try_from_slice(&market_account.data.borrow())?;
    if market.is_initialized {
        return Err(LendingError::AlreadyInitialized.into());
    }
    // WHY: Load the clock so the market records its birth timestamp.
    let clock = Clock::from_account_info(clock_info)?;
    // WHY: Set the initialization flag so subsequent instructions treat this account as valid.
    market.is_initialized = true;
    market.collateral_factor = collateral_factor;
    market.liquidation_bonus = liquidation_bonus;
    market.close_factor = close_factor;
    market.base_rate = base_rate;
    market.slope1 = slope1;
    market.slope2 = slope2;
    market.optimal_utilization = optimal_utilization;
    market.reserve_factor = reserve_factor;
    // WHY: Start borrow_index at 1.0 represented by INDEX_SCALE.
    market.borrow_index = INDEX_SCALE;
    market.last_update_time = clock.unix_timestamp;
    market.total_deposits = 0;
    market.total_borrows = 0;
    // WHY: Serialize the updated state back into the account so it persists.
    market.serialize(&mut *market_account.data.borrow_mut())?;
    msg!("Market initialized");
    Ok(())
}

// WHY: process_deposit transfers user collateral into the protocol and updates balances.
fn process_deposit(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let market_account = next_account_info(account_info_iter)?;
    let user_position_account = next_account_info(account_info_iter)?;
    let user_wallet = next_account_info(account_info_iter)?;
    let user_collateral_token_account = next_account_info(account_info_iter)?;
    let protocol_collateral_token_account = next_account_info(account_info_iter)?;
    let token_program = next_account_info(account_info_iter)?;
    let clock_info = next_account_info(account_info_iter)?;
    // WHY: The user must sign to authorize spending their tokens.
    if !user_wallet.is_signer {
        return Err(ProgramError::MissingRequiredSignature);
    }
    // WHY: Verify program ownership so malicious accounts cannot spoof state.
    if market_account.owner != program_id {
        return Err(ProgramError::IncorrectProgramId);
    }
    if user_position_account.owner != program_id {
        return Err(ProgramError::IncorrectProgramId);
    }
    // WHY: Load and validate the market is initialized.
    let mut market = MarketState::try_from_slice(&market_account.data.borrow())?;
    if !market.is_initialized {
        return Err(LendingError::NotInitialized.into());
    }
    // WHY: Load the clock and accrue interest so all balances are current.
    let clock = Clock::from_account_info(clock_info)?;
    accrue_interest(&mut market, &clock)?;
    // WHY: Load the user position, or initialize it on first deposit.
    let mut user = UserPosition::try_from_slice(&user_position_account.data.borrow())?;
    if !user.is_initialized {
        user.is_initialized = true;
        user.collateral_deposited = 0;
        user.borrow_principal = 0;
        user.borrow_index_snapshot = INDEX_SCALE;
    }
    // WHY: Reject zero deposits to prevent spam and wasted compute.
    if amount == 0 {
        return Err(LendingError::InvalidAmount.into());
    }
    // WHY: Build an SPL Token transfer instruction to move collateral from user to protocol.
    let transfer_instruction = spl_token::instruction::transfer(
        token_program.key,
        user_collateral_token_account.key,
        protocol_collateral_token_account.key,
        user_wallet.key,
        &[],
        amount,
    )?;
    // WHY: Invoke the transfer with the user's signature.
    invoke(
        &transfer_instruction,
        &[
            user_collateral_token_account.clone(),
            protocol_collateral_token_account.clone(),
            user_wallet.clone(),
            token_program.clone(),
        ],
    )?;
    // WHY: Credit the user's on-chain collateral balance.
    user.collateral_deposited = user
        .collateral_deposited
        .checked_add(amount)
        .ok_or(LendingError::MathOverflow)?;
    // WHY: Increase global deposits so utilization is computed correctly.
    market.total_deposits = market
        .total_deposits
        .checked_add(amount)
        .ok_or(LendingError::MathOverflow)?;
    // WHY: Persist user and market state.
    user.serialize(&mut *user_position_account.data.borrow_mut())?;
    market.serialize(&mut *market_account.data.borrow_mut())?;
    msg!("Deposited {}", amount);
    Ok(())
}

// WHY: process_borrow checks collateral, accrues interest, and transfers loan tokens.
fn process_borrow(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let market_account = next_account_info(account_info_iter)?;
    let user_position_account = next_account_info(account_info_iter)?;
    let user_wallet = next_account_info(account_info_iter)?;
    let oracle_account = next_account_info(account_info_iter)?;
    let protocol_borrow_token_account = next_account_info(account_info_iter)?;
    let user_borrow_token_account = next_account_info(account_info_iter)?;
    let protocol_authority = next_account_info(account_info_iter)?;
    let token_program = next_account_info(account_info_iter)?;
    let clock_info = next_account_info(account_info_iter)?;
    if !user_wallet.is_signer {
        return Err(ProgramError::MissingRequiredSignature);
    }
    if market_account.owner != program_id {
        return Err(ProgramError::IncorrectProgramId);
    }
    if user_position_account.owner != program_id {
        return Err(ProgramError::IncorrectProgramId);
    }
    let mut market = MarketState::try_from_slice(&market_account.data.borrow())?;
    if !market.is_initialized {
        return Err(LendingError::NotInitialized.into());
    }
    let clock = Clock::from_account_info(clock_info)?;
    accrue_interest(&mut market, &clock)?;
    let mut user = UserPosition::try_from_slice(&user_position_account.data.borrow())?;
    if !user.is_initialized {
        return Err(LendingError::NotInitialized.into());
    }
    let oracle = OracleState::try_from_slice(&oracle_account.data.borrow())?;
    if amount == 0 {
        return Err(LendingError::InvalidAmount.into());
    }
    // WHY: Compute the user's current debt after interest.
    let current_debt = get_current_borrow_balance(&user, &market)?;
    let new_debt = current_debt
        .checked_add(amount)
        .ok_or(LendingError::MathOverflow)?;
    // WHY: Compute collateral value in borrow-token units.
    let collateral_value = user
        .collateral_deposited
        .checked_mul(oracle.price)
        .ok_or(LendingError::MathOverflow)?;
    let collateral_value_adj = if oracle.decimals > 0 {
        collateral_value
            .checked_div(10u64.pow(oracle.decimals as u32))
            .ok_or(LendingError::MathOverflow)?
    } else {
        collateral_value
    };
    // WHY: Apply collateral factor to determine maximum borrow power.
    let max_borrow = collateral_value_adj
        .checked_mul(market.collateral_factor)
        .ok_or(LendingError::MathOverflow)?
        .checked_div(BASIS_POINTS)
        .ok_or(LendingError::MathOverflow)?;
    // WHY: Reject borrows that would exceed the user's collateral backing.
    if new_debt > max_borrow {
        return Err(LendingError::BorrowTooLarge.into());
    }
    // WHY: Derive the protocol PDA so it can sign the outgoing token transfer.
    let (expected_pda, bump) = Pubkey::find_program_address(&[b"protocol"], program_id);
    if expected_pda != *protocol_authority.key {
        return Err(ProgramError::InvalidSeeds);
    }
    let seeds = &[b"protocol".as_ref(), &[bump]];
    // WHY: Build an SPL Token transfer from the protocol to the user.
    let transfer_instruction = spl_token::instruction::transfer(
        token_program.key,
        protocol_borrow_token_account.key,
        user_borrow_token_account.key,
        protocol_authority.key,
        &[],
        amount,
    )?;
    // WHY: Invoke signed with the PDA seeds so the SPL Token program accepts the transfer.
    invoke_signed(
        &transfer_instruction,
        &[
            protocol_borrow_token_account.clone(),
            user_borrow_token_account.clone(),
            protocol_authority.clone(),
            token_program.clone(),
        ],
        &[seeds],
    )?;
    // WHY: Update the user's borrow principal and snapshot the current borrow index.
    let new_principal = if market.borrow_index == INDEX_SCALE {
        new_debt
    } else {
        (new_debt as u128)
            .checked_mul(INDEX_SCALE)
            .ok_or(LendingError::MathOverflow)?
            .checked_div(market.borrow_index)
            .ok_or(LendingError::MathOverflow)?
            .try_into()
            .map_err(|_| LendingError::MathOverflow)?
    };
    user.borrow_principal = new_principal;
    user.borrow_index_snapshot = market.borrow_index;
    // WHY: Increase global borrows so utilization rises and rates adjust.
    market.total_borrows = market
        .total_borrows
        .checked_add(amount)
        .ok_or(LendingError::MathOverflow)?;
    user.serialize(&mut *user_position_account.data.borrow_mut())?;
    market.serialize(&mut *market_account.data.borrow_mut())?;
    msg!("Borrowed {}", amount);
    Ok(())
}

// WHY: process_repay transfers loan tokens back and reduces debt.
fn process_repay(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let market_account = next_account_info(account_info_iter)?;
    let user_position_account = next_account_info(account_info_iter)?;
    let user_wallet = next_account_info(account_info_iter)?;
    let user_borrow_token_account = next_account_info(account_info_iter)?;
    let protocol_borrow_token_account = next_account_info(account_info_iter)?;
    let token_program = next_account_info(account_info_iter)?;
    let clock_info = next_account_info(account_info_iter)?;
    if !user_wallet.is_signer {
        return Err(ProgramError::MissingRequiredSignature);
    }
    if market_account.owner != program_id {
        return Err(ProgramError::IncorrectProgramId);
    }
    if user_position_account.owner != program_id {
        return Err(ProgramError::IncorrectProgramId);
    }
    let mut market = MarketState::try_from_slice(&market_account.data.borrow())?;
    if !market.is_initialized {
        return Err(LendingError::NotInitialized.into());
    }
    let clock = Clock::from_account_info(clock_info)?;
    accrue_interest(&mut market, &clock)?;
    let mut user = UserPosition::try_from_slice(&user_position_account.data.borrow())?;
    if !user.is_initialized {
        return Err(LendingError::NotInitialized.into());
    }
    if amount == 0 {
        return Err(LendingError::InvalidAmount.into());
    }
    // WHY: Load the current debt to prevent over-repayment.
    let current_debt = get_current_borrow_balance(&user, &market)?;
    if amount > current_debt {
        return Err(LendingError::RepayTooLarge.into());
    }
    // WHY: Transfer repay tokens from user back to the protocol.
    let transfer_instruction = spl_token::instruction::transfer(
        token_program.key,
        user_borrow_token_account.key,
        protocol_borrow_token_account.key,
        user_wallet.key,
        &[],
        amount,
    )?;
    invoke(
        &transfer_instruction,
        &[
            user_borrow_token_account.clone(),
            protocol_borrow_token_account.clone(),
            user_wallet.clone(),
            token_program.clone(),
        ],
    )?;
    // WHY: Reduce the user's borrow principal proportionally to the repayment.
    let remaining_debt = current_debt - amount;
    let new_principal = if market.borrow_index == INDEX_SCALE {
        remaining_debt
    } else {
        (remaining_debt as u128)
            .checked_mul(INDEX_SCALE)
            .ok_or(LendingError::MathOverflow)?
            .checked_div(market.borrow_index)
            .ok_or(LendingError::MathOverflow)?
            .try_into()
            .map_err(|_| LendingError::MathOverflow)?
    };
    user.borrow_principal = new_principal;
    user.borrow_index_snapshot = market.borrow_index;
    // WHY: Reduce global borrows so utilization falls and rates adjust downward.
    market.total_borrows = market
        .total_borrows
        .checked_sub(amount)
        .ok_or(LendingError::MathOverflow)?;
    user.serialize(&mut *user_position_account.data.borrow_mut())?;
    market.serialize(&mut *market_account.data.borrow_mut())?;
    msg!("Repaid {}", amount);
    Ok(())
}

// WHY: process_withdraw checks health factor before returning collateral.
fn process_withdraw(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let market_account = next_account_info(account_info_iter)?;
    let user_position_account = next_account_info(account_info_iter)?;
    let user_wallet = next_account_info(account_info_iter)?;
    let oracle_account = next_account_info(account_info_iter)?;
    let protocol_collateral_token_account = next_account_info(account_info_iter)?;
    let user_collateral_token_account = next_account_info(account_info_iter)?;
    let protocol_authority = next_account_info(account_info_iter)?;
    let token_program = next_account_info(account_info_iter)?;
    let clock_info = next_account_info(account_info_iter)?;
    if !user_wallet.is_signer {
        return Err(ProgramError::MissingRequiredSignature);
    }
    if market_account.owner != program_id {
        return Err(ProgramError::IncorrectProgramId);
    }
    if user_position_account.owner != program_id {
        return Err(ProgramError::IncorrectProgramId);
    }
    let mut market = MarketState::try_from_slice(&market_account.data.borrow())?;
    if !market.is_initialized {
        return Err(LendingError::NotInitialized.into());
    }
    let clock = Clock::from_account_info(clock_info)?;
    accrue_interest(&mut market, &clock)?;
    let mut user = UserPosition::try_from_slice(&user_position_account.data.borrow())?;
    if !user.is_initialized {
        return Err(LendingError::NotInitialized.into());
    }
    let oracle = OracleState::try_from_slice(&oracle_account.data.borrow())?;
    if amount == 0 {
        return Err(LendingError::InvalidAmount.into());
    }
    if amount > user.collateral_deposited {
        return Err(LendingError::WithdrawTooLarge.into());
    }
    // WHY: Pre-compute the post-withdrawal collateral to simulate the new health factor.
    let future_collateral = user.collateral_deposited - amount;
    let mut simulated_user = user.clone();
    simulated_user.collateral_deposited = future_collateral;
    let future_hf = get_health_factor(&simulated_user, &market, &oracle)?;
    // WHY: Reject withdrawals that would drop health factor below 1.0.
    if future_hf < BASIS_POINTS {
        return Err(LendingError::HealthFactorTooLow.into());
    }
    // WHY: Derive the protocol PDA to authorize the outgoing collateral transfer.
    let (expected_pda, bump) = Pubkey::find_program_address(&[b"protocol"], program_id);
    if expected_pda != *protocol_authority.key {
        return Err(ProgramError::InvalidSeeds);
    }
    let seeds = &[b"protocol".as_ref(), &[bump]];
    let transfer_instruction = spl_token::instruction::transfer(
        token_program.key,
        protocol_collateral_token_account.key,
        user_collateral_token_account.key,
        protocol_authority.key,
        &[],
        amount,
    )?;
    invoke_signed(
        &transfer_instruction,
        &[
            protocol_collateral_token_account.clone(),
            user_collateral_token_account.clone(),
            protocol_authority.clone(),
            token_program.clone(),
        ],
        &[seeds],
    )?;
    // WHY: Debit the user's collateral and global deposits.
    user.collateral_deposited = user
        .collateral_deposited
        .checked_sub(amount)
        .ok_or(LendingError::MathOverflow)?;
    market.total_deposits = market
        .total_deposits
        .checked_sub(amount)
        .ok_or(LendingError::MathOverflow)?;
    user.serialize(&mut *user_position_account.data.borrow_mut())?;
    market.serialize(&mut *market_account.data.borrow_mut())?;
    msg!("Withdrew {}", amount);
    Ok(())
}

// WHY: process_liquidate allows anyone to repay bad debt and seize collateral at a discount.
fn process_liquidate(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    repay_amount: u64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let market_account = next_account_info(account_info_iter)?;
    let borrower_position_account = next_account_info(account_info_iter)?;
    let liquidator_wallet = next_account_info(account_info_iter)?;
    let oracle_account = next_account_info(account_info_iter)?;
    let liquidator_repay_token_account = next_account_info(account_info_iter)?;
    let protocol_borrow_token_account = next_account_info(account_info_iter)?;
    let protocol_collateral_token_account = next_account_info(account_info_iter)?;
    let liquidator_collateral_token_account = next_account_info(account_info_iter)?;
    let protocol_authority = next_account_info(account_info_iter)?;
    let token_program = next_account_info(account_info_iter)?;
    let clock_info = next_account_info(account_info_iter)?;
    // WHY: The liquidator must sign to authorize spending their own tokens.
    if !liquidator_wallet.is_signer {
        return Err(ProgramError::MissingRequiredSignature);
    }
    if market_account.owner != program_id {
        return Err(ProgramError::IncorrectProgramId);
    }
    if borrower_position_account.owner != program_id {
        return Err(ProgramError::IncorrectProgramId);
    }
    let mut market = MarketState::try_from_slice(&market_account.data.borrow())?;
    if !market.is_initialized {
        return Err(LendingError::NotInitialized.into());
    }
    let clock = Clock::from_account_info(clock_info)?;
    accrue_interest(&mut market, &clock)?;
    let mut borrower = UserPosition::try_from_slice(&borrower_position_account.data.borrow())?;
    if !borrower.is_initialized {
        return Err(LendingError::NotInitialized.into());
    }
    let oracle = OracleState::try_from_slice(&oracle_account.data.borrow())?;
    if repay_amount == 0 {
        return Err(LendingError::InvalidAmount.into());
    }
    // WHY: Compute the borrower's current debt to enforce the close factor.
    let current_debt = get_current_borrow_balance(&borrower, &market)?;
    let max_repay = current_debt
        .checked_mul(market.close_factor)
        .ok_or(LendingError::MathOverflow)?
        .checked_div(BASIS_POINTS)
        .ok_or(LendingError::MathOverflow)?;
    if repay_amount > max_repay {
        return Err(LendingError::CloseFactorExceeded.into());
    }
    // WHY: Verify the position is actually underwater before allowing liquidation.
    let health = get_health_factor(&borrower, &market, &oracle)?;
    if health >= BASIS_POINTS {
        return Err(LendingError::NotLiquidatable.into());
    }
    // WHY: Calculate collateral seized = repay * (1 + bonus) / price.
    let collateral_to_seize = (repay_amount as u128)
        .checked_mul((market.liquidation_bonus as u128) + (BASIS_POINTS as u128))
        .ok_or(LendingError::MathOverflow)?
        .checked_div(BASIS_POINTS as u128)
        .ok_or(LendingError::MathOverflow)?
        .checked_mul(10u128.pow(oracle.decimals as u32))
        .ok_or(LendingError::MathOverflow)?
        .checked_div(oracle.price as u128)
        .ok_or(LendingError::MathOverflow)?
        .try_into()
        .map_err(|_| LendingError::MathOverflow)?;
    if collateral_to_seize > borrower.collateral_deposited {
        return Err(LendingError::MathOverflow.into());
    }
    // WHY: Derive the protocol PDA to authorize collateral transfers out.
    let (expected_pda, bump) = Pubkey::find_program_address(&[b"protocol"], program_id);
    if expected_pda != *protocol_authority.key {
        return Err(ProgramError::InvalidSeeds);
    }
    let seeds = &[b"protocol".as_ref(), &[bump]];
    // WHY: Transfer repay tokens from liquidator into the protocol borrow account.
    let repay_transfer = spl_token::instruction::transfer(
        token_program.key,
        liquidator_repay_token_account.key,
        protocol_borrow_token_account.key,
        liquidator_wallet.key,
        &[],
        repay_amount,
    )?;
    invoke(
        &repay_transfer,
        &[
            liquidator_repay_token_account.clone(),
            protocol_borrow_token_account.clone(),
            liquidator_wallet.clone(),
            token_program.clone(),
        ],
    )?;
    // WHY: Transfer seized collateral from the protocol to the liquidator.
    let seize_transfer = spl_token::instruction::transfer(
        token_program.key,
        protocol_collateral_token_account.key,
        liquidator_collateral_token_account.key,
        protocol_authority.key,
        &[],
        collateral_to_seize,
    )?;
    invoke_signed(
        &seize_transfer,
        &[
            protocol_collateral_token_account.clone(),
            liquidator_collateral_token_account.clone(),
            protocol_authority.clone(),
            token_program.clone(),
        ],
        &[seeds],
    )?;
    // WHY: Reduce the borrower's debt by the repaid amount.
    let remaining_debt = current_debt - repay_amount;
    let new_principal = if market.borrow_index == INDEX_SCALE {
        remaining_debt
    } else {
        (remaining_debt as u128)
            .checked_mul(INDEX_SCALE)
            .ok_or(LendingError::MathOverflow)?
            .checked_div(market.borrow_index)
            .ok_or(LendingError::MathOverflow)?
            .try_into()
            .map_err(|_| LendingError::MathOverflow)?
    };
    borrower.borrow_principal = new_principal;
    borrower.borrow_index_snapshot = market.borrow_index;
    // WHY: Reduce the borrower's collateral by the seized amount.
    borrower.collateral_deposited = borrower
        .collateral_deposited
        .checked_sub(collateral_to_seize)
        .ok_or(LendingError::MathOverflow)?;
    // WHY: Reduce global borrows because debt was cleared.
    market.total_borrows = market
        .total_borrows
        .checked_sub(repay_amount)
        .ok_or(LendingError::MathOverflow)?;
    // WHY: Reduce global deposits because collateral left the protocol.
    market.total_deposits = market
        .total_deposits
        .checked_sub(collateral_to_seize)
        .ok_or(LendingError::MathOverflow)?;
    borrower.serialize(&mut *borrower_position_account.data.borrow_mut())?;
    market.serialize(&mut *market_account.data.borrow_mut())?;
    msg!(
        "Liquidated debt {} for collateral {}",
        repay_amount,
        collateral_to_seize
    );
    Ok(())
}
