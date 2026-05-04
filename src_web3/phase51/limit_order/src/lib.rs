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
use spl_token::state::Account as TokenAccount;
use borsh::{BorshDeserialize, BorshSerialize};

// WHY: This declares the entrypoint so the Solana runtime knows where to start executing our program.
entrypoint!(process_instruction);

// WHY: We use a fixed seed for the escrow authority PDA so the program can sign token transfers.
const ESCROW_AUTHORITY_SEED: &[u8] = b"escrow_authority";

// WHY: Each order is stored as a single account. This simplifies reads and makes cancellation atomic.
#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)]
pub struct Order {
    // WHY: We store the owner so only they can cancel the order.
    pub owner: Pubkey,
    // WHY: The input mint is the token the trader is selling.
    pub input_mint: Pubkey,
    // WHY: The output mint is the token the trader wants to receive.
    pub output_mint: Pubkey,
    // WHY: The input amount is how many tokens are locked in escrow.
    pub input_amount: u64,
    // WHY: The limit price defines the exchange rate the trader demands.
    pub limit_price: u64,
    // WHY: is_active prevents double execution or double cancellation.
    pub is_active: bool,
    // WHY: We store the escrow bump so we can recreate the PDA signer efficiently.
    pub escrow_bump: u8,
    // WHY: We store the slot the order was created in for potential time-based expiry logic.
    pub created_at_slot: u64,
}

// WHY: These instruction tags tell the program which function to run inside process_instruction.
#[repr(u8)]
enum Instruction {
    PlaceOrder = 0,
    CancelOrder = 1,
    ExecuteOrder = 2,
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
        0 => place_order(program_id, accounts, &instruction_data[1..]),
        1 => cancel_order(program_id, accounts),
        2 => execute_order(program_id, accounts, &instruction_data[1..]),
        // WHY: If the tag is unrecognized, we fail fast to avoid undefined behavior.
        _ => {
            msg!("ERROR: Unknown instruction tag");
            Err(ProgramError::InvalidInstructionData)
        }
    }
}

// WHY: This function creates an order account, locks input tokens in escrow, and records the intent.
fn place_order(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    data: &[u8],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let trader = next_account_info(account_info_iter)?; // WHY: The user placing the order and paying for the account.
    let order_account = next_account_info(account_info_iter)?; // WHY: The account that will store the Order struct.
    let trader_input_token_account = next_account_info(account_info_iter)?; // WHY: Source of the tokens to escrow.
    let escrow_token_account = next_account_info(account_info_iter)?; // WHY: Program-owned vault holding the tokens.
    let escrow_authority = next_account_info(account_info_iter)?; // WHY: PDA that owns the escrow vault.
    let input_mint = next_account_info(account_info_iter)?; // WHY: Needed to validate the token account mint.
    let output_mint = next_account_info(account_info_iter)?; // WHY: Stored in the order so executors know what to return.
    let token_program = next_account_info(account_info_iter)?; // WHY: Required for SPL token transfers.
    let system_program = next_account_info(account_info_iter)?; // WHY: Required to create the order account.
    let rent_sysvar = next_account_info(account_info_iter)?; // WHY: Required to ensure rent exemption.
    let clock_sysvar = next_account_info(account_info_iter)?; // WHY: To record the creation slot.

    if !trader.is_signer {
        msg!("ERROR: Trader must sign");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // WHY: We verify the escrow authority PDA to prevent anyone from creating a fake escrow.
    let (expected_escrow_authority, escrow_bump) =
        Pubkey::find_program_address(&[ESCROW_AUTHORITY_SEED], program_id);
    if expected_escrow_authority != *escrow_authority.key {
        msg!("ERROR: Invalid escrow authority PDA");
        return Err(ProgramError::InvalidAccountData);
    }

    // WHY: We deserialize the instruction data to get amount and price.
    if data.len() < 16 {
        msg!("ERROR: Insufficient place_order data");
        return Err(ProgramError::InvalidInstructionData);
    }
    let input_amount = u64::from_le_bytes(data[0..8].try_into().unwrap());
    let limit_price = u64::from_le_bytes(data[8..16].try_into().unwrap());

    // WHY: We allocate space for the Order struct so it can persist on-chain.
    let order_size = std::mem::size_of::<Order>() as u64;
    let rent = Rent::from_account_info(rent_sysvar)?;
    let required_lamports = rent.minimum_balance(order_size as usize);

    // WHY: We create the order account using a system instruction, funded by the trader.
    invoke(
        &system_instruction::create_account(
            trader.key,
            order_account.key,
            required_lamports,
            order_size,
            program_id,
        ),
        &[
            trader.clone(),
            order_account.clone(),
            system_program.clone(),
        ],
    )?;

    // WHY: We read the current slot to timestamp the order.
    let clock = Clock::from_account_info(clock_sysvar)?;

    // WHY: We initialize the order struct with all parameters.
    let order = Order {
        owner: *trader.key,
        input_mint: *input_mint.key,
        output_mint: *output_mint.key,
        input_amount,
        limit_price,
        is_active: true,
        escrow_bump,
        created_at_slot: clock.slot,
    };

    // WHY: We serialize the order into the account so it persists.
    order.serialize(&mut &mut order_account.data.borrow_mut()[..])?;

    // WHY: We transfer the input tokens from the trader to the escrow account.
    invoke(
        &token_instruction::transfer(
            token_program.key,
            trader_input_token_account.key,
            escrow_token_account.key,
            trader.key,
            &[],
            input_amount,
        )?,
        &[
            trader_input_token_account.clone(),
            escrow_token_account.clone(),
            trader.clone(),
            token_program.clone(),
        ],
    )?;

    msg!("Order placed: amount={}, price={}", input_amount, limit_price);
    Ok(())
}

// WHY: This function allows the owner to cancel an unexecuted order and reclaim their tokens.
fn cancel_order(program_id: &Pubkey, accounts: &[AccountInfo]) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let owner = next_account_info(account_info_iter)?; // WHY: Must be the original trader.
    let order_account = next_account_info(account_info_iter)?; // WHY: The account holding the order data.
    let owner_output_token_account = next_account_info(account_info_iter)?; // WHY: Destination for refunded tokens.
    let escrow_token_account = next_account_info(account_info_iter)?; // WHY: Source of the locked tokens.
    let escrow_authority = next_account_info(account_info_iter)?; // WHY: PDA signer for the escrow vault.
    let token_program = next_account_info(account_info_iter)?; // WHY: SPL Token program.

    if !owner.is_signer {
        msg!("ERROR: Owner must sign cancellation");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // WHY: We load the order to verify ownership and active status.
    let mut order = Order::try_from_slice(&order_account.data.borrow())?;
    if order.owner != *owner.key {
        msg!("ERROR: Only the order owner can cancel");
        return Err(ProgramError::IllegalOwner);
    }
    if !order.is_active {
        msg!("ERROR: Order is not active");
        return Err(ProgramError::InvalidAccountData);
    }

    // WHY: We verify the escrow authority PDA to ensure the refund is legitimate.
    let (expected_escrow_authority, _bump) =
        Pubkey::find_program_address(&[ESCROW_AUTHORITY_SEED], program_id);
    if expected_escrow_authority != *escrow_authority.key {
        msg!("ERROR: Invalid escrow authority");
        return Err(ProgramError::InvalidAccountData);
    }

    // WHY: We read the escrow balance to know exactly how much to refund.
    let escrow_data = TokenAccount::unpack(&escrow_token_account.data.borrow())?;
    let refund_amount = escrow_data.amount;

    // WHY: We transfer the escrowed tokens back to the owner.
    invoke_signed(
        &token_instruction::transfer(
            token_program.key,
            escrow_token_account.key,
            owner_output_token_account.key,
            escrow_authority.key,
            &[],
            refund_amount,
        )?,
        &[
            escrow_token_account.clone(),
            owner_output_token_account.clone(),
            escrow_authority.clone(),
            token_program.clone(),
        ],
        &[&[ESCROW_AUTHORITY_SEED, &[order.escrow_bump]]],
    )?;

    // WHY: We mark the order inactive and re-serialize so it cannot be executed or cancelled again.
    order.is_active = false;
    order.serialize(&mut &mut order_account.data.borrow_mut()[..])?;

    msg!("Order cancelled and {} tokens refunded", refund_amount);
    Ok(())
}

// WHY: This function allows anyone (a keeper) to execute an order when the market price crosses the limit.
fn execute_order(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    data: &[u8],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let executor = next_account_info(account_info_iter)?; // WHY: The keeper triggering execution.
    let order_account = next_account_info(account_info_iter)?; // WHY: The order to execute.
    let executor_input_token_account = next_account_info(account_info_iter)?; // WHY: The keeper pays the output token here.
    let executor_output_token_account = next_account_info(account_info_iter)?; // WHY: The keeper receives the input token here.
    let trader_output_token_account = next_account_info(account_info_iter)?; // WHY: The original trader receives the bought tokens.
    let escrow_token_account = next_account_info(account_info_iter)?; // WHY: Source of the trader's locked tokens.
    let escrow_authority = next_account_info(account_info_iter)?; // WHY: PDA signer for escrow.
    let token_program = next_account_info(account_info_iter)?; // WHY: SPL Token program.

    // WHY: Execution does not require the trader to sign because they pre-authorized it by placing the order.
    // However, we do require the executor to sign to prevent spam.
    if !executor.is_signer {
        msg!("ERROR: Executor must sign");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // WHY: We load the order to check its status and parameters.
    let mut order = Order::try_from_slice(&order_account.data.borrow())?;
    if !order.is_active {
        msg!("ERROR: Order is not active");
        return Err(ProgramError::InvalidAccountData);
    }

    // WHY: We verify the escrow authority PDA.
    let (expected_escrow_authority, _bump) =
        Pubkey::find_program_address(&[ESCROW_AUTHORITY_SEED], program_id);
    if expected_escrow_authority != *escrow_authority.key {
        msg!("ERROR: Invalid escrow authority");
        return Err(ProgramError::InvalidAccountData);
    }

    // WHY: The instruction data contains the current market price provided by the executor.
    // In a production system, you might read this from an oracle or an on-chain pool account.
    if data.len() < 8 {
        msg!("ERROR: Insufficient execute_order data");
        return Err(ProgramError::InvalidInstructionData);
    }
    let current_price = u64::from_le_bytes(data[0..8].try_into().unwrap());

    // WHY: We check if the market price satisfies the limit condition.
    // For a buy order (trader sells input for output), we require current_price <= limit_price.
    if current_price > order.limit_price {
        msg!("ERROR: Current price {} is above limit {}", current_price, order.limit_price);
        return Err(ProgramError::Custom(2));
    }

    // WHY: We calculate how many output tokens the trader should receive.
    // amount_out = input_amount * limit_price (assuming price is in integer form with implied decimals).
    let output_amount = (order.input_amount as u128)
        .checked_mul(order.limit_price as u128)
        .ok_or(ProgramError::Overflow)? as u64;

    // WHY: We read the escrow balance to know how much to transfer out.
    let escrow_data = TokenAccount::unpack(&escrow_token_account.data.borrow())?;
    let escrow_amount = escrow_data.amount;

    // WHY: We transfer the trader's locked input tokens from escrow to the executor.
    invoke_signed(
        &token_instruction::transfer(
            token_program.key,
            escrow_token_account.key,
            executor_output_token_account.key,
            escrow_authority.key,
            &[],
            escrow_amount,
        )?,
        &[
            escrow_token_account.clone(),
            executor_output_token_account.clone(),
            escrow_authority.clone(),
            token_program.clone(),
        ],
        &[&[ESCROW_AUTHORITY_SEED, &[order.escrow_bump]]],
    )?;

    // WHY: We transfer the output tokens from the executor to the trader.
    invoke(
        &token_instruction::transfer(
            token_program.key,
            executor_input_token_account.key,
            trader_output_token_account.key,
            executor.key,
            &[],
            output_amount,
        )?,
        &[
            executor_input_token_account.clone(),
            trader_output_token_account.clone(),
            executor.clone(),
            token_program.clone(),
        ],
    )?;

    // WHY: We mark the order as inactive so it cannot be executed again.
    order.is_active = false;
    order.serialize(&mut &mut order_account.data.borrow_mut()[..])?;

    msg!("Order executed at price {}. Trader received {}", current_price, output_amount);
    Ok(())
}
