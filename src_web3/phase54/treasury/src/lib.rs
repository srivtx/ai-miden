use solana_program::{ // Import the Solana runtime API so the treasury program can manage funds and validate accounts.
    account_info::{next_account_info, AccountInfo}, // next_account_info iterates safely over the accounts slice; AccountInfo holds all on-chain account metadata.
    entrypoint, // entrypoint macro marks the function Solana calls when this program is invoked.
    entrypoint::ProgramResult, // ProgramResult is the standard return type that maps to Solana success or error codes.
    msg, // msg logs to the transaction log so developers and auditors can trace execution.
    program_error::ProgramError, // ProgramError enumerates common on-chain failures so callers receive meaningful error codes.
    pubkey::Pubkey, // Pubkey is the 32-byte address type used to identify accounts and programs.
    program_pack::{Pack, Sealed}, // Pack defines serialization for account state; Sealed marks a type with a fixed size.
    borsh0_10::try_from_slice_unchecked, // try_from_slice_unchecked deserializes Borsh without length checks for known-size account data.
};
use borsh::{BorshDeserialize, BorshSerialize}; // Borsh provides compact binary serialization used by Solana account state.

entrypoint!(process_instruction); // Register process_instruction as the BPF entrypoint so the runtime knows where to begin.

pub fn process_instruction( // process_instruction is the single entry function that dispatches to handlers based on instruction data.
    program_id: &Pubkey, // program_id is the address of this treasury program; we use it to verify ownership of vault accounts.
    accounts: &[AccountInfo], // accounts holds all accounts passed by the client; order matters and must match the instruction definition.
    instruction_data: &[u8], // instruction_data is the payload that tells us which instruction to run and what parameters it carries.
) -> ProgramResult { // Return ProgramResult so Solana knows whether to commit or roll back the transaction.
    msg!("Treasury program entrypoint invoked"); // Log entry so explorers and debuggers can confirm the program started.
    let instruction = TreasuryInstruction::try_from_slice(instruction_data) // Deserialize the raw bytes into a typed instruction so we can match on it safely.
        .map_err(|_| ProgramError::InvalidInstructionData)?; // Reject the transaction if the payload is malformed to prevent undefined behavior.
    match instruction { // Match on the deserialized instruction to route to the correct handler.
        TreasuryInstruction::Deposit { amount } => { // Route to deposit when a member wants to add funds to the treasury.
            process_deposit(program_id, accounts, amount) // Forward the amount to the handler that credits the vault.
        }
        TreasuryInstruction::Withdraw { amount } => { // Route to withdraw when governance approves a fund release.
            process_withdraw(program_id, accounts, amount) // Forward the amount to the handler that debits the vault after multi-sig checks.
        }
    }
}

#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)] // Derive traits so instructions can be serialized across the wire and cloned in memory.
pub enum TreasuryInstruction { // Enumerate all possible instructions so the program has a closed set of operations.
    Deposit { amount: u64 }, // Deposit credits the vault with funds from a member.
    Withdraw { amount: u64 }, // Withdraw debits the vault after verifying governance approval and multi-sig thresholds.
}

#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)] // Derive traits so TreasuryConfig can be saved to and loaded from account data.
pub struct TreasuryConfig { // TreasuryConfig is the global settings account that controls spending rules and authorization.
    pub governance_program: Pubkey, // governance_program is the only program allowed to trigger withdrawals so the treasury cannot be drained arbitrarily.
    pub spending_limit: u64, // spending_limit caps any single withdrawal to contain damage from a single rogue proposal.
    pub required_signers: u8, // required_signers is the minimum number of trusted signers needed to approve a withdrawal.
    pub signers: Vec<Pubkey>, // signers is the list of authorized addresses that can contribute signatures toward the threshold.
    pub vault_bump: u8, // vault_bump stores the program-derived address bump for the vault account.
}

#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)] // Derive traits so WithdrawalRecord can be saved to and loaded from account data.
pub struct WithdrawalRecord { // WithdrawalRecord prevents double spending by marking each approved withdrawal as executed.
    pub proposal_id: u64, // proposal_id links the withdrawal to the governance proposal that authorized it.
    pub amount: u64, // amount stores the exact withdrawal quantity for auditing.
    pub recipient: Pubkey, // recipient identifies the destination so the record is complete and traceable.
    pub executed: bool, // executed is a flag that blocks any attempt to replay the same withdrawal.
}

impl Sealed for TreasuryConfig {} // Sealed tells the Pack trait that TreasuryConfig has a fixed upper size bound.
impl Pack for TreasuryConfig { // Pack defines how TreasuryConfig is serialized into and deserialized from account bytes.
    const LEN: usize = 32 + 8 + 1 + 4 + (5 * 32) + 1; // LEN is the maximum account size reserved for TreasuryConfig.
    fn pack_into_slice(&self, dst: &mut [u8]) { // pack_into_slice writes the struct into the account buffer.
        let mut data = dst; // Create a mutable borrow so Borsh can write into it.
        self.serialize(&mut data).unwrap(); // Serialize with Borsh; unwrap is safe because the buffer is pre-allocated to LEN.
    }
    fn unpack_from_slice(src: &[u8]) -> Result<Self, ProgramError> { // unpack_from_slice reads the struct from the account buffer.
        try_from_slice_unchecked(src).map_err(|_| ProgramError::InvalidAccountData) // Return an error if the bytes do not match the expected schema.
    }
}

impl Sealed for WithdrawalRecord {} // Sealed tells the Pack trait that WithdrawalRecord has a fixed upper size bound.
impl Pack for WithdrawalRecord { // Pack defines how WithdrawalRecord is serialized into and deserialized from account bytes.
    const LEN: usize = 8 + 8 + 32 + 1; // LEN is the maximum account size reserved for a WithdrawalRecord.
    fn pack_into_slice(&self, dst: &mut [u8]) { // pack_into_slice writes the struct into the account buffer.
        let mut data = dst; // Create a mutable borrow so Borsh can write into it.
        self.serialize(&mut data).unwrap(); // Serialize with Borsh; unwrap is safe because the buffer is pre-allocated to LEN.
    }
    fn unpack_from_slice(src: &[u8]) -> Result<Self, ProgramError> { // unpack_from_slice reads the struct from the account buffer.
        try_from_slice_unchecked(src).map_err(|_| ProgramError::InvalidAccountData) // Return an error if the bytes do not match the expected schema.
    }
}

fn process_deposit( // process_deposit credits the treasury vault with funds from a member.
    _program_id: &Pubkey, // program_id is unused because deposit validation relies on signatures and lamport math.
    accounts: &[AccountInfo], // accounts contains the depositor and the vault.
    amount: u64, // amount is the quantity of lamports to move into the treasury.
) -> ProgramResult { // Return ProgramResult so the deposit is either fully credited or fully rejected.
    let accounts_iter = &mut accounts.iter(); // Create an iterator to consume accounts in order.
    let depositor = next_account_info(accounts_iter)?; // Extract the depositor because they must sign and supply funds.
    let vault = next_account_info(accounts_iter)?; // Extract the vault because it receives the deposited lamports.
    if !depositor.is_signer { // Require depositor signature so anonymous accounts cannot debit others.
        msg!("Depositor must sign to prevent unauthorized debits from their account"); // Explain the authorization requirement.
        return Err(ProgramError::MissingRequiredSignature); // Abort if the depositor did not sign.
    }
    if amount == 0 { // Reject zero deposits because they waste block space and create meaningless records.
        msg!("Zero amount deposits are rejected to avoid spam transactions"); // Explain the spam prevention.
        return Err(ProgramError::InvalidInstructionData); // Abort because the amount is invalid.
    }
    **depositor.try_borrow_mut_lamports()? -= amount; // Debit the depositor's account atomically; fail if balance is insufficient.
    **vault.try_borrow_mut_lamports()? += amount; // Credit the vault atomically so the total money supply is conserved.
    msg!("Deposited {} lamports into treasury vault", amount); // Log success for transparency.
    Ok(()) // Return success so the transaction is committed.
}

fn process_withdraw( // process_withdraw debits the treasury vault after verifying governance approval and multi-sig thresholds.
    program_id: &Pubkey, // program_id is used to verify vault ownership.
    accounts: &[AccountInfo], // accounts contains the governance program, config, vault, recipient, record, and multi-sig signers.
    amount: u64, // amount is the quantity of lamports to release from the treasury.
) -> ProgramResult { // Return ProgramResult so the withdrawal is either fully executed or fully rejected.
    let accounts_iter = &mut accounts.iter(); // Create an iterator to consume accounts in order.
    let governance_program = next_account_info(accounts_iter)?; // Extract the governance program account to verify it is the authorized caller.
    let config_account = next_account_info(accounts_iter)?; // Extract the config account to read spending limits and signer list.
    let vault = next_account_info(accounts_iter)?; // Extract the vault because it will be debited.
    let recipient = next_account_info(accounts_iter)?; // Extract the recipient because they will receive the funds.
    let withdrawal_record = next_account_info(accounts_iter)?; // Extract the record account to prevent double spending.
    let mut signer_count = 0; // Initialize a counter to track how many valid multi-sig signers are present.
    let required = { // Open a block to load config and perform initial validation.
        let config = TreasuryConfig::unpack(&config_account.data.borrow())?; // Load treasury settings so we can enforce rules.
        if *governance_program.key != config.governance_program { // Reject if the calling program is not the authorized governance program.
            msg!("Withdrawal must be triggered by the authorized governance program"); // Explain the authorization failure.
            return Err(ProgramError::IllegalOwner); // Abort because the caller is not trusted.
        }
        if amount > config.spending_limit { // Reject if the requested amount exceeds the per-proposal cap.
            msg!("Withdrawal exceeds spending limit; proposal must respect treasury constraints"); // Explain the limit violation.
            return Err(ProgramError::InvalidInstructionData); // Abort because the amount is too large.
        }
        if amount > vault.lamports() { // Reject if the treasury does not have enough funds to fulfill the request.
            msg!("Insufficient treasury balance to cover the requested withdrawal"); // Explain the balance failure.
            return Err(ProgramError::InsufficientFunds); // Abort because the vault is underfunded.
        }
        config.required_signers // Return the threshold so we can count signers after this block.
    };
    for account in accounts_iter { // Iterate over any remaining accounts to find multi-sig signers.
        if account.is_signer { // Only consider accounts that actually signed the transaction.
            let config = TreasuryConfig::unpack(&config_account.data.borrow())?; // Reload config to access the authorized signer list.
            if config.signers.contains(account.key) { // Check if this signer is in the approved list.
                signer_count += 1; // Increment the valid signer count.
                msg!("Valid signer {} counted toward multi-sig threshold", account.key); // Log each valid signer for auditing.
            } else { // If the signer is not in the list.
                msg!("Signer {} is not in the authorized signer list", account.key); // Log the invalid signer for debugging.
            }
        }
    }
    if signer_count < required { // Reject if the number of valid signers is below the threshold.
        msg!("Not enough valid signers; required {} but found {}", required, signer_count); // Explain the multi-sig failure.
        return Err(ProgramError::MissingRequiredSignature); // Abort because the security threshold was not met.
    }
    let mut record = WithdrawalRecord::unpack(&withdrawal_record.data.borrow())?; // Load the withdrawal record to check for replays.
    if record.executed { // Reject if this record has already been used to withdraw funds.
        msg!("This withdrawal record has already been executed; double spending is blocked"); // Explain the replay prevention.
        return Err(ProgramError::AccountAlreadyInitialized); // Abort because the same proposal cannot be executed twice.
    }
    record.executed = true; // Mark the record as executed so future attempts will fail.
    record.amount = amount; // Store the amount for auditing.
    record.recipient = *recipient.key; // Store the recipient for auditing.
    WithdrawalRecord::pack(record, &mut withdrawal_record.data.borrow_mut())?; // Save the updated record to block replays.
    **vault.try_borrow_mut_lamports()? -= amount; // Debit the vault atomically; fail if balance is insufficient.
    **recipient.try_borrow_mut_lamports()? += amount; // Credit the recipient atomically so funds arrive in full or not at all.
    msg!("Withdrew {} lamports to {} after multi-sig verification", amount, recipient.key); // Log success for transparency.
    Ok(()) // Return success so the transaction is committed.
}
