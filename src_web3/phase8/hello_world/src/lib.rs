use solana_program::{
    account_info::AccountInfo,
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    pubkey::Pubkey,
};

/// Phase 8: Hello World Program
///
/// This is the simplest possible Solana program.
/// When invoked, it logs "Hello, Solana!" to the transaction log.
///
/// To deploy:
/// 1. Build: cargo build-bpf
/// 2. Deploy: solana program deploy target/deploy/hello_world.so
/// 3. Invoke: solana program call <PROGRAM_ID>

// WHY: The entrypoint! macro registers process_instruction as the function
// the Solana runtime calls when this program is invoked by a transaction.
entrypoint!(process_instruction);

/// The entrypoint is the function Solana calls when your program is invoked.
///
/// Parameters:
/// - program_id: The public key of this deployed program
/// - accounts: The accounts passed in the transaction (empty for this simple program)
/// - instruction_data: Custom data passed to the program (unused here)
fn process_instruction(
    _program_id: &Pubkey,
    _accounts: &[AccountInfo],
    _instruction_data: &[u8],
) -> ProgramResult {
    // WHY: msg!() logs to the transaction log. You can view logs with:
    // solana logs <PROGRAM_ID>
    msg!("Hello, Solana!");

    // WHY: Return Ok to indicate the instruction executed successfully.
    // If we returned Err, the entire transaction would fail.
    Ok(())
}

// WHY: Unit tests run locally without a validator to verify program logic.
#[cfg(test)]
mod tests {
    // WHY: Import everything from the parent module so tests can call process_instruction.
    use super::*;
    use solana_program::clock::Epoch;

    #[test]
    fn test_hello_world() {
        // WHY: Use the default Pubkey because this simple program does not use program_id.
        let program_id = Pubkey::default();

        // WHY: Pass an empty accounts vec because this program touches no accounts.
        let accounts: Vec<AccountInfo> = vec![];

        // WHY: Pass empty instruction_data because this program takes no parameters.
        let instruction_data: Vec<u8> = vec![];

        // WHY: Call the entrypoint directly to verify it returns Ok.
        let result = process_instruction(&program_id, &accounts, &instruction_data);

        // WHY: Assert success. If the program logic changes and returns Err, this test fails.
        assert!(result.is_ok());
    }
}
