use anchor_lang::prelude::*; // WHY: Import the Anchor framework macros and types needed for Solana program development.
use spl_transfer_hook_interface; // WHY: Import the transfer hook interface crate so this program is linked to the expected Token-2022 hook standard.
declare_id!("Hook111111111111111111111111111111111111111"); // WHY: Declare the program ID that the Token-2022 mint will reference as its hook authority.
#[program] // WHY: Mark this module as an Anchor program containing the on-chain instruction handlers.
pub mod hook { // WHY: Define the program module named hook to group all instruction logic together.
    use super::*; // WHY: Bring all parent scope imports into this module so types and macros are available.
    pub fn execute_hook(ctx: Context<ExecuteHook>) -> Result<()> { // WHY: Define the hook execution handler that Token-2022 calls automatically on every transfer.
        let sender = ctx.accounts.sender.key(); // WHY: Load the sender pubkey so we can check it against the blacklist.
        require!(sender != ctx.accounts.blacklist.key(), HookError::Blacklisted); // WHY: Revert the transaction if the sender address matches the blacklisted address.
        Ok(()) // WHY: Return success so the underlying Token-2022 transfer can proceed.
    } // WHY: Close the execute_hook function scope.
} // WHY: Close the hook program module scope.
#[derive(Accounts)] // WHY: Tell Anchor to generate the account validation struct for the execute hook instruction.
pub struct ExecuteHook<'info> { // WHY: Define the account constraints struct that maps the accounts passed by Token-2022 during transfer.
    pub sender: AccountInfo<'info>, // WHY: Include the sender account so the hook can inspect who is initiating the transfer.
    pub recipient: AccountInfo<'info>, // WHY: Include the recipient account because Token-2022 passes it even if we do not validate it here.
    pub blacklist: AccountInfo<'info>, // WHY: Include the blacklisted address account used as a constant reference for comparison.
} // WHY: Close the ExecuteHook accounts struct scope.
#[error_code] // WHY: Mark this enum as an Anchor custom error code for descriptive on-chain failures.
pub enum HookError { // WHY: Define the custom error enum so failed transactions return a specific error identifier.
    #[msg("Sender is blacklisted")] // WHY: Attach a human-readable message to the error for debugging and client feedback.
    Blacklisted, // WHY: Declare the Blacklisted variant used when a sender matches the forbidden address.
} // WHY: Close the HookError enum scope.
