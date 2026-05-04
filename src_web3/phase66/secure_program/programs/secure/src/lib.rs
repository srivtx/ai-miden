use anchor_lang::prelude::*; // WHY: Importing Anchor framework prelude with common types and macros
use anchor_lang::solana_program::program::invoke; // WHY: Importing low-level CPI invocation for cross-program calls
use anchor_lang::solana_program::instruction::Instruction; // WHY: Importing Instruction struct to build CPI payloads

declare_id!("Hpy8x4n4vD8VLDx3v7b7j8k9L0m1n2o3p4q5r6s7t8u9"); // WHY: Declaring a different on-chain program ID for the secure program

const WHITELIST: [Pubkey; 1] = [pubkey!("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")]; // WHY: Hardcoding allowed CPI destination programs to prevent arbitrary calls

#[program] // WHY: Macro marking this module as the Solana program entry point
pub mod secure { // WHY: Defining the program module named secure
    use super::*; // WHY: Bringing parent scope declarations into the program module

    pub fn proxy_call(ctx: Context<ProxyCall>, ix_data: Vec<u8>) -> Result<()> { // WHY: Instruction forwarding raw calls to an external program via CPI
        // FIX: Added whitelist validation for arbitrary CPI vulnerability
        require!( // WHY: Enforcing that the target program is in the allowed whitelist
            WHITELIST.contains(ctx.accounts.target_program.key()), // WHY: Checking target program ID against hardcoded whitelist // FIX: Whitelist prevents arbitrary CPI to unknown programs
            ErrorCode::ProgramNotWhitelisted // WHY: Error to return if target is not approved
        ); // WHY: Closing the whitelist validation requirement
        let ix = Instruction { // WHY: Building a new Solana instruction for cross-program invocation
            program_id: *ctx.accounts.target_program.key(), // WHY: Dereferencing the now-whitelisted target program key // FIX: Target program validated before use
            accounts: vec![], // WHY: Passing empty account metas for the forwarded instruction
            data: ix_data, // WHY: Forwarding instruction data to the approved target program
        }; // WHY: Instruction constructed only after whitelist validation succeeds
        invoke( // WHY: Executing the cross-program invocation on the Solana runtime
            &ix, // WHY: Passing the validated instruction to the runtime
            &[ctx.accounts.target_program.to_account_info()], // WHY: Supplying target account info for CPI execution
        )?; // WHY: Propagating invocation errors to the caller
        Ok(()) // WHY: Returning success after safe CPI execution
    } // WHY: Closing proxy_call instruction handler

    pub fn close_user_account(_ctx: Context<CloseUserAccount>) -> Result<()> { // WHY: Instruction handler to close a user account securely
        // FIX: Using Anchor's close constraint to prevent closed account reuse
        Ok(()) // WHY: Anchor macro handles closure automatically via the close constraint // FIX: close = signer sets CLOSED_ACCOUNT_DISCRIMINATOR and transfers rent
    } // WHY: Closing close_user_account instruction handler

    pub fn withdraw_from_vault(ctx: Context<WithdrawFromVault>, amount: u64) -> Result<()> { // WHY: Instruction to withdraw tokens from a canonical vault PDA
        // FIX: PDA canonicalization enforced via Anchor seeds and bump constraints
        let vault = &mut ctx.accounts.vault; // WHY: Borrowing vault account mutably for balance updates // FIX: Vault address validated by Anchor constraint before handler execution
        if vault.balance < amount { // WHY: Checking if the vault has sufficient balance for the withdrawal
            return Err(ErrorCode::InsufficientFunds.into()); // WHY: Returning error if the vault balance is insufficient
        } // WHY: Fund check ensures no overdraft occurs
        vault.balance -= amount; // WHY: Deducting the withdrawn amount from the vault balance
        let destination = &mut ctx.accounts.user_token_account; // WHY: Borrowing destination account mutably
        destination.balance += amount; // WHY: Adding the withdrawn amount to the destination token account
        Ok(()) // WHY: Returning success after validated vault withdrawal
    } // WHY: Closing withdraw_from_vault instruction handler
} // WHY: Closing program module

#[derive(Accounts)] // WHY: Deriving Anchor account validation for the ProxyCall instruction context
pub struct ProxyCall<'info> { // WHY: Defining the accounts structure for proxy_call
    #[account(mut)] // WHY: Marking signer as mutable for transaction fee payment
    pub signer: Signer<'info>, // WHY: Transaction signer authorizing the CPI proxy
    /// CHECK: Validated against whitelist in instruction handler
    pub target_program: AccountInfo<'info>, // WHY: Target program validated via WHITELIST constant before CPI // FIX: Arbitrary CPI prevented by whitelist check
} // WHY: Closing ProxyCall accounts struct

#[derive(Accounts)] // WHY: Deriving Anchor account validation for the CloseUserAccount context
pub struct CloseUserAccount<'info> { // WHY: Defining accounts structure for close_user_account
    #[account(mut)] // WHY: Signer must be mutable to receive the rent lamports
    pub signer: Signer<'info>, // WHY: Account authorizing the closure and receiving lamports
    #[account(mut, close = signer)] // FIX: Anchor close constraint prevents closed account reuse by setting CLOSED_ACCOUNT_DISCRIMINATOR // WHY: Automatically invalidates account and transfers rent to signer
    pub user_account: Account<'info, UserAccount>, // WHY: Account being securely closed by Anchor
} // WHY: Closing CloseUserAccount accounts struct

#[derive(Accounts)] // WHY: Deriving Anchor account validation for the WithdrawFromVault context
pub struct WithdrawFromVault<'info> { // WHY: Defining accounts structure for withdraw_from_vault
    #[account(mut)] // WHY: Authority must be mutable if responsible for transaction fees
    pub authority: Signer<'info>, // WHY: Signer authorizing the vault withdrawal
    #[account( // WHY: Opening account constraints for the vault PDA
        mut, // WHY: Vault must be mutable for balance mutation
        seeds = [b"vault", authority.key().as_ref()], // FIX: Enforcing canonical seed prefix to prevent alternative PDA derivations // WHY: Hardcoded prefix ensures only expected vault PDAs are accepted
        bump // FIX: Enforcing canonical bump returned by find_program_address // WHY: Anchor validates the bump against the canonical derivation
    )] // WHY: Closing vault account constraints
    pub vault: Account<'info, Vault>, // WHY: Canonical vault PDA validated by Anchor constraints before handler runs
    #[account(mut)] // WHY: Destination must be mutable to receive withdrawn funds
    pub user_token_account: Account<'info, UserTokenAccount>, // WHY: Destination account for the withdrawn tokens
} // WHY: Closing WithdrawFromVault accounts struct

#[account] // WHY: Macro defining an Anchor account type with an 8-byte discriminator
pub struct UserAccount { // WHY: Data structure for user accounts stored on-chain
    pub owner: Pubkey, // WHY: Public key identifying the owner of this user account
    pub balance: u64, // WHY: Current token balance held in the user account
} // WHY: Closing UserAccount struct

#[account] // WHY: Macro defining an Anchor account type with an 8-byte discriminator
pub struct Vault { // WHY: Data structure for vault accounts stored on-chain
    pub authority: Pubkey, // WHY: Public key of the authority allowed to withdraw from this vault
    pub balance: u64, // WHY: Current token balance held in the vault
} // WHY: Closing Vault struct

#[account] // WHY: Macro defining an Anchor account type with an 8-byte discriminator
pub struct UserTokenAccount { // WHY: Data structure for user token destination accounts
    pub owner: Pubkey, // WHY: Public key of the owner of this token account
    pub balance: u64, // WHY: Current token balance held in the account
} // WHY: Closing UserTokenAccount struct

#[error_code] // WHY: Defining custom error codes for the program
pub enum ErrorCode { // WHY: Enumerating all possible program-specific errors
    #[msg("Program not whitelisted")] // WHY: Human-readable error message for unapproved CPI target
    ProgramNotWhitelisted, // WHY: Error returned when CPI target is not in the whitelist // FIX: Whitelist enforcement for arbitrary CPI
    #[msg("Insufficient funds")] // WHY: Human-readable error message for insufficient balance
    InsufficientFunds, // WHY: Error returned when vault balance is below requested amount
} // WHY: Closing ErrorCode enum
