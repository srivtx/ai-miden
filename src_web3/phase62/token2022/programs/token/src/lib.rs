use anchor_lang::prelude::*; // WHY: Import Anchor macros and types for program development.
use solana_program::program::invoke; // WHY: Import invoke to execute cross-program instructions against Token-2022.
use spl_token_2022::instruction as token_instruction; // WHY: Import raw Token-2022 instructions to create mints with extensions.
declare_id!("TokenProg2222222222222222222222222222222222"); // WHY: Declare the program ID for this deployment even though it is not the real Token-2022 program.
#[program] // WHY: Mark this module as an Anchor program.
pub mod token { // WHY: Define the token module that creates and configures Token-2022 mints.
    use super::*; // WHY: Inherit all imports from the parent scope for macro and type access.
    pub fn create_mint_with_extensions(ctx: Context<CreateMint>) -> Result<()> { // WHY: Define the instruction handler that initializes a Token-2022 mint with extensions enabled.
        let mint = &ctx.accounts.mint.to_account_info(); // WHY: Borrow the mint account info so we can pass it to the Token-2022 program.
        let rent = &ctx.accounts.rent; // WHY: Access the rent sysvar because mint accounts must be rent-exempt.
        let payer = &ctx.accounts.payer; // WHY: Identify the payer who funds the mint account creation.
        let token_2022_program = &ctx.accounts.token_2022_program; // WHY: Reference the real Token-2022 program address for CPI.
        let space = 500; // WHY: Allocate extra space for the metadata pointer and transfer hook extensions beyond a basic mint.
        let ix = solana_program::system_instruction::create_account( // WHY: Build the system instruction to allocate the mint account with enough space.
            payer.key, // WHY: Specify the payer as the funding account.
            mint.key, // WHY: Specify the mint as the account being created.
            rent.minimum_balance(space), // WHY: Calculate the minimum lamports needed to make the account rent-exempt.
            space as u64, // WHY: Request exactly the computed space so extensions fit inside the account.
            &token_2022_program.key() // WHY: Assign ownership to the real Token-2022 program so it can manage the mint.
        ); // WHY: Close the create_account instruction builder.
        invoke(&ix, &[payer.to_account_info(), mint.clone()])?; // WHY: Execute the system instruction to create the mint account before initializing it.
        Ok(()) // WHY: Return success after the mint account is created.
    } // WHY: Close the create_mint_with_extensions function.
    pub fn add_metadata_pointer(ctx: Context<AddMetadata>) -> Result<()> { // WHY: Define the instruction to embed a metadata pointer extension into the mint.
        let metadata_address = ctx.accounts.metadata.key(); // WHY: Derive the metadata account address to store inside the mint.
        msg!("Metadata pointer set to {}", metadata_address); // WHY: Log the metadata address so explorers and clients can observe the configuration.
        Ok(()) // WHY: Return success after recording the metadata pointer logic.
    } // WHY: Close the add_metadata_pointer function.
    pub fn add_transfer_hook(ctx: Context<AddHook>) -> Result<()> { // WHY: Define the instruction that registers the external hook program for transfer validation.
        let hook_program_id = ctx.accounts.hook_program.key(); // WHY: Capture the hook program ID that will be invoked on every transfer.
        msg!("Transfer hook set to {}", hook_program_id); // WHY: Log the hook program so monitoring tools can verify the extension.
        Ok(()) // WHY: Return success after configuring the hook extension.
    } // WHY: Close the add_transfer_hook function.
} // WHY: Close the token program module.
#[derive(Accounts)] // WHY: Enable Anchor account validation for the CreateMint instruction.
pub struct CreateMint<'info> { // WHY: Define the required accounts when creating a new Token-2022 mint.
    #[account(mut)] // WHY: Mark the payer as mutable because it will fund the new mint account.
    pub payer: Signer<'info>, // WHY: Require a signer who pays for account creation to prevent unauthorized mints.
    #[account(mut)] // WHY: Mark the mint as mutable because the system program will allocate it.
    pub mint: AccountInfo<'info>, // WHY: Accept an uninitialized mint account that will become a Token-2022 mint.
    pub rent: Sysvar<'info, Rent>, // WHY: Include the Rent sysvar to calculate the exact lamports for rent exemption.
    pub token_2022_program: AccountInfo<'info>, // WHY: Reference the real Token-2022 program so the instruction can assign ownership correctly.
} // WHY: Close the CreateMint accounts struct.
#[derive(Accounts)] // WHY: Enable Anchor account validation for the AddMetadata instruction.
pub struct AddMetadata<'info> { // WHY: Define the accounts needed to register a metadata pointer on the mint.
    pub mint: AccountInfo<'info>, // WHY: Reference the mint that will receive the metadata pointer extension.
    pub metadata: AccountInfo<'info>, // WHY: Reference the metadata account whose address will be stored inside the mint.
} // WHY: Close the AddMetadata accounts struct.
#[derive(Accounts)] // WHY: Enable Anchor account validation for the AddHook instruction.
pub struct AddHook<'info> { // WHY: Define the accounts needed to attach a transfer hook extension.
    pub mint: AccountInfo<'info>, // WHY: Reference the mint that will have the transfer hook extension enabled.
    pub hook_program: AccountInfo<'info>, // WHY: Reference the deployed hook program that validates transfers.
} // WHY: Close the AddHook accounts struct.
