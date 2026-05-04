use anchor_lang::prelude::*; // WHY: Importing Anchor framework prelude with common types and macros
use anchor_lang::solana_program::program::invoke; // WHY: Importing low-level CPI invocation for cross-program calls
use anchor_lang::solana_program::instruction::Instruction; // WHY: Importing Instruction struct to build CPI payloads

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS"); // WHY: Declaring on-chain program ID for runtime validation and IDL

#[program] // WHY: Macro marking this module as the Solana program entry point
pub mod vulnerable { // WHY: Defining the program module named vulnerable
    use super::*; // WHY: Bringing parent scope declarations into the program module

    pub fn proxy_call(ctx: Context<ProxyCall>, ix_data: Vec<u8>) -> Result<()> { // WHY: Instruction forwarding raw calls to an external program via CPI
        // VULNERABLE: No program ID whitelist validation before constructing CPI
        let ix = Instruction { // WHY: Building a new Solana instruction for cross-program invocation
            program_id: *ctx.accounts.target_program.key(), // VULNERABLE: Using arbitrary unchecked account as the CPI destination program // WHY: Dereferencing target key for Instruction without whitelist check
            accounts: vec![], // WHY: Passing empty account metas for the forwarded instruction
            data: ix_data, // WHY: Forwarding raw instruction data from the caller to the target program unchecked
        }; // WHY: Instruction fully constructed without verifying the destination program identity
        invoke( // WHY: Executing the cross-program invocation on the Solana runtime
            &ix, // WHY: Passing the unvalidated instruction to the runtime
            &[ctx.accounts.target_program.to_account_info()], // WHY: Supplying target account info without ownership or whitelist checks
        )?; // WHY: Propagating invocation errors without additional safety validation
        Ok(()) // WHY: Returning success after potentially executing a malicious CPI
    } // WHY: Closing proxy_call instruction handler

    pub fn close_user_account(ctx: Context<CloseUserAccount>) -> Result<()> { // WHY: Instruction handler to close a user account and recover rent
        let account_info = ctx.accounts.user_account.to_account_info(); // WHY: Extracting AccountInfo for manual lamport manipulation
        let signer_info = ctx.accounts.signer.to_account_info(); // WHY: Extracting signer AccountInfo to receive the rent lamports
        let lamports = account_info.lamports(); // WHY: Reading the current lamport balance of the account being closed
        **signer_info.try_borrow_mut_lamports()? += lamports; // WHY: Transferring all lamports from the account to the signer
        **account_info.try_borrow_mut_lamports()? = 0; // WHY: Zeroing the account lamports but leaving data and discriminator intact
        // VULNERABLE: No discriminator invalidation to CLOSED_ACCOUNT_DISCRIMINATOR // WHY: Skipping the step that prevents account reuse after closure
        // VULNERABLE: Account data remains valid, allowing the closed account to be reused in other instructions // WHY: Data persistence enables closed account reuse attacks
        Ok(()) // WHY: Returning success while the account remains deserializable as UserAccount
    } // WHY: Closing close_user_account instruction handler

    pub fn withdraw_from_vault(ctx: Context<WithdrawFromVault>, amount: u64, bump: u8, seed_prefix: Vec<u8>) -> Result<()> { // WHY: Instruction to withdraw tokens from a vault PDA
        let derived = Pubkey::create_program_address( // WHY: Deriving PDA from potentially non-canonical seeds and bump
            &[ // WHY: Building seed slice for manual PDA derivation
                &seed_prefix[..], // VULNERABLE: Accepting attacker-controlled seed prefix instead of a hardcoded constant // WHY: Allowing caller to specify arbitrary seed components
                ctx.accounts.authority.key().as_ref(), // WHY: Using authority pubkey as a seed component
                &[bump], // VULNERABLE: Accepting any bump from the caller without canonical validation // WHY: Using user-provided bump without verifying it is the canonical one
            ], // WHY: Seed construction allows attacker-controlled alternative PDA derivations
            ctx.program_id, // WHY: Deriving relative to the current program ID
        ).map_err(|_| ErrorCode::InvalidPda)?; // WHY: Mapping derivation failure to a program error
        // VULNERABLE: Only checking address equality, not verifying canonical bump or fixed seeds
        if derived != ctx.accounts.vault.key() { // WHY: Verifying the derived address matches the provided vault account
            return Err(ErrorCode::InvalidPda.into()); // WHY: Returning error if the PDA address does not match
        } // WHY: This check still permits alternative valid PDAs with different seed combinations
        // VULNERABLE: Proceeding without ensuring the canonical bump or seed prefix is enforced
        let vault = &mut ctx.accounts.vault; // WHY: Borrowing vault account mutably for balance updates
        if vault.balance < amount { // WHY: Checking if the vault has sufficient balance for the withdrawal
            return Err(ErrorCode::InsufficientFunds.into()); // WHY: Returning error if the vault balance is insufficient
        } // WHY: Fund check occurs after vulnerable PDA validation
        vault.balance -= amount; // WHY: Deducting the withdrawn amount from the vault balance
        let destination = &mut ctx.accounts.user_token_account; // WHY: Borrowing destination account mutably
        destination.balance += amount; // WHY: Adding the withdrawn amount to the destination token account
        Ok(()) // WHY: Returning success after potentially unauthorized vault access
    } // WHY: Closing withdraw_from_vault instruction handler
} // WHY: Closing program module

#[derive(Accounts)] // WHY: Deriving Anchor account validation for the ProxyCall instruction context
pub struct ProxyCall<'info> { // WHY: Defining the accounts structure for proxy_call
    #[account(mut)] // WHY: Marking signer as mutable for transaction fee payment
    pub signer: Signer<'info>, // WHY: Transaction signer authorizing the CPI proxy
    /// CHECK: No validation is performed on this account
    pub target_program: AccountInfo<'info>, // VULNERABLE: Unchecked AccountInfo allows any program to be invoked via CPI // WHY: Permitting arbitrary program as CPI target without restriction
} // WHY: Closing ProxyCall accounts struct

#[derive(Accounts)] // WHY: Deriving Anchor account validation for the CloseUserAccount context
pub struct CloseUserAccount<'info> { // WHY: Defining accounts structure for close_user_account
    #[account(mut)] // WHY: Signer must be mutable to receive the rent lamports
    pub signer: Signer<'info>, // WHY: Account authorizing the closure and receiving lamports
    #[account(mut)] // WHY: Target account must be mutable for lamport transfer
    pub user_account: Account<'info, UserAccount>, // VULNERABLE: Account type validated but not marked for proper Anchor closure // WHY: Using Account without close constraint leaves discriminator intact
} // WHY: Closing CloseUserAccount accounts struct

#[derive(Accounts)] // WHY: Deriving Anchor account validation for the WithdrawFromVault context
pub struct WithdrawFromVault<'info> { // WHY: Defining accounts structure for withdraw_from_vault
    #[account(mut)] // WHY: Authority must be mutable if responsible for transaction fees
    pub authority: Signer<'info>, // WHY: Signer authorizing the vault withdrawal
    #[account(mut)] // WHY: Vault must be mutable for balance mutation
    pub vault: Account<'info, Vault>, // WHY: Vault account whose balance is deducted without seed constraint validation
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
    #[msg("Invalid PDA")] // WHY: Human-readable error message for invalid PDA derivation
    InvalidPda, // WHY: Error returned when PDA validation fails
    #[msg("Insufficient funds")] // WHY: Human-readable error message for insufficient balance
    InsufficientFunds, // WHY: Error returned when vault balance is below requested amount
} // WHY: Closing ErrorCode enum
