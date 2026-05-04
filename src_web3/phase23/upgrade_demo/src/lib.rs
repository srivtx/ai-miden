use anchor_lang::prelude::*;

// Declare the program ID so Solana routes calls to this deployed program.
declare_id!("Upgrade33333333333333333333333333333333333333");

// Define the program module containing all upgrade demo instructions.
#[program]
pub mod upgrade_demo {
    use super::*;

    // The initialize instruction sets up a counter account to demonstrate state persistence.
    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        // Create a new counter account to track how many times increment is called.
        let counter = &mut ctx.accounts.counter;
        counter.count = 0; // Start at zero so subsequent increments are predictable.
        counter.version = 1; // Track the program version that created this counter.
        // Return Ok to confirm initialization succeeded.
        Ok(())
    }

    // The increment instruction increases the counter, useful for verifying behavior after upgrade.
    pub fn increment(ctx: Context<Increment>) -> Result<()> {
        // Load the counter account mutably so we can modify its state.
        let counter = &mut ctx.accounts.counter;
        // Increase count by one to demonstrate stateful program interaction.
        counter.count = counter.count.checked_add(1).unwrap();
        // Return Ok to confirm the increment was recorded.
        Ok(())
    }

    // The get_version instruction returns the current program version stored in counter.
    pub fn get_version(ctx: Context<GetVersion>) -> Result<u64> {
        // Load the counter account to read its version field.
        let counter = &ctx.accounts.counter;
        // Return the version so clients can verify which program revision is active.
        Ok(counter.version)
    }
}

// Accounts required to initialize the counter.
#[derive(Accounts)]
pub struct Initialize<'info> {
    // The payer must sign and fund the creation of the counter account.
    #[account(mut)]
    pub payer: Signer<'info>,

    // The counter account is initialized here and persists across program upgrades.
    #[account(
        init,
        payer = payer,
        space = 8 + 8 + 8 // discriminator + u64 count + u64 version
    )]
    pub counter: Account<'info, Counter>,

    // The system program is required for account creation.
    pub system_program: Program<'info, System>,
}

// Accounts required to increment the counter.
#[derive(Accounts)]
pub struct Increment<'info> {
    // The user must sign to authorize the increment operation.
    pub user: Signer<'info>,

    // The counter account is modified by the increment instruction.
    #[account(mut)]
    pub counter: Account<'info, Counter>,
}

// Accounts required to read the version.
#[derive(Accounts)]
pub struct GetVersion<'info> {
    // The counter account is read without modification.
    pub counter: Account<'info, Counter>,
}

// The Counter account stores state that survives program upgrades.
#[account]
pub struct Counter {
    // The current count value, incremented by users.
    pub count: u64,
    // The version field helps clients detect if the program logic has changed.
    pub version: u64,
}
