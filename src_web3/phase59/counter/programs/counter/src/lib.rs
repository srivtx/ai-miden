use anchor_lang::prelude::*;                            // WHY: Imports all Anchor core types, macros, and traits needed for program development.

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS"); // WHY: Hardcodes the program's public key so Anchor can verify the deployed binary matches this ID.

#[program]                                              // WHY: Marks the module as an Anchor program, generating the BPF entrypoint and instruction dispatcher.
pub mod counter {                                       // WHY: Declares the program module name which becomes part of the instruction discriminator hash.
    use super::*;                                       // WHY: Brings the parent scope types into this module so CounterAccount and contexts are visible.

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> { // WHY: Defines the initialize instruction handler that creates and sets up a new counter account.
        let counter = &mut ctx.accounts.counter;        // WHY: Obtains a mutable reference to the counter account so we can write its initial state.
        counter.bump = ctx.bumps.counter;               // WHY: Stores the canonical bump seed in the account data so future instructions can verify the PDA.
        counter.count = 0;                              // WHY: Sets the initial count to zero because the account was just created and has no prior state.
        msg!("Counter initialized with count: {}", counter.count); // WHY: Logs the initialization event to the transaction log for debugging and indexing.
        Ok(())                                          // WHY: Returns success so the Solana runtime commits the account state changes.
    }

    pub fn increment(ctx: Context<Update>) -> Result<()> { // WHY: Defines the increment instruction handler that increases the counter by one.
        let counter = &mut ctx.accounts.counter;        // WHY: Obtains a mutable reference to the counter account because increment modifies stored data.
        counter.count = counter.count.checked_add(1).unwrap(); // WHY: Safely adds one using checked arithmetic to prevent overflow, then unwraps because overflow is impossible here.
        msg!("Counter incremented to: {}", counter.count); // WHY: Logs the new count value to the transaction log for off-chain observation.
        Ok(())                                          // WHY: Returns success so the runtime persists the updated count to the blockchain.
    }

    pub fn decrement(ctx: Context<Update>) -> Result<()> { // WHY: Defines the decrement instruction handler that decreases the counter by one.
        let counter = &mut ctx.accounts.counter;        // WHY: Obtains a mutable reference because decrementing is a state mutation on the account.
        counter.count = counter.count.checked_sub(1).unwrap(); // WHY: Safely subtracts one using checked arithmetic to prevent underflow on unsigned integers.
        msg!("Counter decremented to: {}", counter.count); // WHY: Logs the new count so clients and explorers can verify the operation succeeded.
        Ok(())                                          // WHY: Returns success so the transaction is finalized with the new counter value.
    }

    pub fn close(ctx: Context<Close>) -> Result<()> {   // WHY: Defines the close instruction handler that destroys the counter account and refunds rent.
        let counter = &ctx.accounts.counter;            // WHY: Obtains an immutable reference because we only read the account address before closing it.
        msg!("Closing counter account: {}", counter.key()); // WHY: Logs the public key of the account being closed for audit trails and debugging.
        Ok(())                                          // WHY: Returns success so Anchor's close constraint can execute and refund lamports to the payer.
    }
}

#[derive(Accounts)]                                     // WHY: Generates the Accounts trait implementation for deserialization and validation of the initialize instruction.
pub struct Initialize<'info> {                          // WHY: Defines the account structure for the initialize instruction with a lifetime tied to the transaction.
    #[account(                                           // WHY: Opens the account constraint attribute that tells Anchor how to validate and create the counter account.
        init,                                           // WHY: Instructs Anchor to create this account via a CPI to the System Program before running the handler.
        seeds = [b"counter", payer.key().as_ref()],     // WHY: Derives the account address as a PDA from the static seed and the payer's public key for deterministic addressing.
        bump,                                           // WHY: Tells Anchor to find and store the canonical bump seed so the PDA is valid and off-curve.
        payer = payer,                                  // WHY: Specifies which account pays the rent lamports required to create the counter account on-chain.
        space = 8 + 8                                   // WHY: Allocates 8 bytes for the account discriminator plus 8 bytes for the u64 count field.
    )]
    pub counter: Account<'info, CounterAccount>,        // WHY: Declares the counter as an Anchor account of type CounterAccount, enabling typed deserialization.
    #[account(mut)]                                     // WHY: Marks the payer as mutable because creating the counter account deducts lamports for rent.
    pub payer: Signer<'info>,                           // WHY: Requires the payer to sign the transaction to authorize the deduction of lamports and account creation.
    pub system_program: Program<'info, System>,         // WHY: Provides access to the System Program which is required by Anchor to create new accounts.
}

#[derive(Accounts)]                                     // WHY: Generates the Accounts trait for the increment and decrement instructions which share the same account layout.
pub struct Update<'info> {                              // WHY: Defines a reusable account struct for any instruction that modifies an existing counter account.
    #[account(                                           // WHY: Opens the constraint attribute for the existing counter account that will be mutated.
        mut,                                            // WHY: Marks the counter account as mutable so the runtime permits writing the updated count value.
        seeds = [b"counter", payer.key().as_ref()],     // WHY: Re-derives the PDA using the same seeds as initialization to verify this is the correct counter account.
        bump = counter.bump                             // WHY: Verifies the bump seed stored in the account matches the derived bump, preventing address forgery.
    )]
    pub counter: Account<'info, CounterAccount>,        // WHY: Declares the counter as a typed Anchor account so the count field is automatically deserialized.
    #[account(mut)]                                     // WHY: Marks the payer as mutable because future versions might refund or charge the payer on updates.
    pub payer: Signer<'info>,                           // WHY: Requires the payer to sign to prove they own this counter and are authorized to modify it.
}

#[derive(Accounts)]                                     // WHY: Generates the Accounts trait for the close instruction which destroys the counter account.
pub struct Close<'info> {                               // WHY: Defines the account structure for closing a counter and refunding its rent to the payer.
    #[account(                                           // WHY: Opens the constraint attribute for the counter account that will be destroyed.
        mut,                                            // WHY: Marks the account as mutable because closing it drains lamports and zeros data.
        seeds = [b"counter", payer.key().as_ref()],     // WHY: Derives the PDA to ensure only the correct counter account associated with this payer can be closed.
        bump = counter.bump,                            // WHY: Validates the bump seed to confirm the account address was legitimately derived.
        close = payer                                   // WHY: Instructs Anchor to close the account and send its rent lamports back to the payer after the handler.
    )]
    pub counter: Account<'info, CounterAccount>,        // WHY: Declares the counter as a typed account so Anchor can verify ownership before closing it.
    #[account(mut)]                                     // WHY: Marks the payer as mutable because they will receive the refunded rent lamports.
    pub payer: Signer<'info>,                           // WHY: Requires the payer to sign to authorize the destruction of their own counter account.
}

#[account]                                              // WHY: Marks the struct as an Anchor account type, adding an 8-byte discriminator and ownership checks.
pub struct CounterAccount {                             // WHY: Defines the on-chain data schema for the counter program's state.
    pub bump: u8,                                       // WHY: Stores the canonical PDA bump seed so future instructions can validate the address without recomputing.
    pub count: u64,                                     // WHY: Stores the current counter value as a 64-bit unsigned integer to support large counts.
}
