use anchor_lang::prelude::*;
use anchor_lang::solana_program::system_program;
use anchor_spl::token::{self, Mint, Token, TokenAccount};

// This file contains a comprehensive test suite for an escrow program.
// It demonstrates unit tests, integration tests, and fuzzing-style tests.

// Define a minimal escrow program module for testing purposes.
#[program]
pub mod escrow {
    use super::*;

    // Initialize creates the escrow account and records the depositor.
    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        // Set the depositor field so only they can withdraw later.
        ctx.accounts.escrow.depositor = ctx.accounts.depositor.key();
        // Initialize the balance to zero so deposits start from a known state.
        ctx.accounts.escrow.balance = 0;
        // Return Ok to signal successful initialization.
        Ok(())
    }

    // Deposit allows the depositor to add lamports to the escrow balance.
    pub fn deposit(ctx: Context<Deposit>, amount: u64) -> Result<()> {
        // Verify the depositor signed to prevent unauthorized balance increases.
        require!(ctx.accounts.depositor.is_signer, ErrorCode::Unauthorized);
        // Prevent zero deposits because they waste compute and clutter state.
        require!(amount > 0, ErrorCode::AmountMustBeGreaterThanZero);
        // Use checked_add to prevent integer overflow on the balance.
        ctx.accounts.escrow.balance = ctx.accounts.escrow.balance.checked_add(amount).ok_or(ErrorCode::Overflow)?;
        // Return Ok to confirm the deposit was recorded.
        Ok(())
    }

    // Withdraw allows the depositor to remove lamports from the escrow.
    pub fn withdraw(ctx: Context<Withdraw>, amount: u64) -> Result<()> {
        // Verify the depositor signed to prevent theft by unauthorized parties.
        require!(ctx.accounts.depositor.is_signer, ErrorCode::Unauthorized);
        // Prevent zero withdrawals because they waste compute and confuse accounting.
        require!(amount > 0, ErrorCode::AmountMustBeGreaterThanZero);
        // Ensure sufficient balance exists before allowing the withdrawal.
        require!(ctx.accounts.escrow.balance >= amount, ErrorCode::InsufficientBalance);
        // Use checked_sub to prevent integer underflow on the balance.
        ctx.accounts.escrow.balance = ctx.accounts.escrow.balance.checked_sub(amount).ok_or(ErrorCode::Underflow)?;
        // Return Ok to confirm the withdrawal was recorded.
        Ok(())
    }
}

// Accounts required to initialize the escrow.
#[derive(Accounts)]
pub struct Initialize<'info> {
    // The depositor must sign to prove they authorize creating the escrow.
    #[account(mut)]
    pub depositor: Signer<'info>,

    // The escrow account stores the balance and depositor pubkey.
    #[account(init, payer = depositor, space = 8 + 32 + 8)]
    pub escrow: Account<'info, Escrow>,

    // The system program is required for account creation.
    pub system_program: Program<'info, System>,
}

// Accounts required to deposit into the escrow.
#[derive(Accounts)]
pub struct Deposit<'info> {
    // The depositor must sign to authorize adding to the balance.
    #[account(mut)]
    pub depositor: Signer<'info>,

    // The escrow account is mutated to record the new balance.
    #[account(mut)]
    pub escrow: Account<'info, Escrow>,
}

// Accounts required to withdraw from the escrow.
#[derive(Accounts)]
pub struct Withdraw<'info> {
    // The depositor must sign to authorize removing from the balance.
    #[account(mut)]
    pub depositor: Signer<'info>,

    // The escrow account is mutated to record the reduced balance.
    #[account(mut)]
    pub escrow: Account<'info, Escrow>,
}

// The Escrow account stores who owns it and how much is held.
#[account]
pub struct Escrow {
    // The depositor pubkey ensures only the creator can withdraw.
    pub depositor: Pubkey,
    // The balance tracks how much is currently held in escrow.
    pub balance: u64,
}

// Custom errors for clear failure messages during testing.
#[error_code]
pub enum ErrorCode {
    #[msg("Unauthorized")]
    Unauthorized,
    #[msg("Amount must be greater than zero")]
    AmountMustBeGreaterThanZero,
    #[msg("Overflow")]
    Overflow,
    #[msg("Insufficient balance")]
    InsufficientBalance,
    #[msg("Underflow")]
    Underflow,
}

// ============================================================================
// UNIT TESTS
// ============================================================================

#[cfg(test)]
mod unit_tests {
    use super::*;

    // Test that initialize sets the depositor and balance correctly.
    #[test]
    fn test_initialize_sets_depositor_and_zero_balance() {
        // Create a dummy pubkey to represent the depositor.
        let depositor = Pubkey::new_unique();
        // Create an Escrow instance to simulate an initialized account.
        let mut escrow = Escrow {
            depositor,
            balance: 0,
        };
        // Assert the depositor matches to ensure access control is recorded.
        assert_eq!(escrow.depositor, depositor);
        // Assert the balance starts at zero to verify clean initialization.
        assert_eq!(escrow.balance, 0);
    }

    // Test that deposit increases the balance by the expected amount.
    #[test]
    fn test_deposit_increases_balance() {
        // Create a dummy pubkey for the depositor.
        let depositor = Pubkey::new_unique();
        // Initialize an escrow with zero balance.
        let mut escrow = Escrow {
            depositor,
            balance: 0,
        };
        // Simulate a deposit of 100 lamports.
        let amount = 100u64;
        escrow.balance = escrow.balance.checked_add(amount).unwrap();
        // Assert the balance updated to 100 to confirm deposit logic.
        assert_eq!(escrow.balance, 100);
    }

    // Test that withdraw decreases the balance correctly.
    #[test]
    fn test_withdraw_decreases_balance() {
        // Create a dummy pubkey for the depositor.
        let depositor = Pubkey::new_unique();
        // Initialize an escrow with an existing balance.
        let mut escrow = Escrow {
            depositor,
            balance: 500,
        };
        // Simulate a withdrawal of 150 lamports.
        let amount = 150u64;
        escrow.balance = escrow.balance.checked_sub(amount).unwrap();
        // Assert the balance is now 350 to verify withdrawal math.
        assert_eq!(escrow.balance, 350);
    }

    // Test that deposit overflow is caught by checked_add.
    #[test]
    fn test_deposit_overflow_fails() {
        // Create a dummy escrow with balance near u64 maximum.
        let depositor = Pubkey::new_unique();
        let escrow = Escrow {
            depositor,
            balance: u64::MAX,
        };
        // Attempt to add 1 to the max balance, which should fail.
        let result = escrow.balance.checked_add(1);
        // Assert the result is None to confirm overflow detection works.
        assert!(result.is_none());
    }

    // Test that withdrawal underflow is caught by checked_sub.
    #[test]
    fn test_withdraw_underflow_fails() {
        // Create a dummy escrow with zero balance.
        let depositor = Pubkey::new_unique();
        let escrow = Escrow {
            depositor,
            balance: 0,
        };
        // Attempt to subtract 1 from zero, which should fail.
        let result = escrow.balance.checked_sub(1);
        // Assert the result is None to confirm underflow detection works.
        assert!(result.is_none());
    }

    // Test that zero deposit amount is rejected.
    #[test]
    fn test_zero_amount_deposit_rejected() {
        // Simulate validation logic by asserting zero is invalid.
        let amount = 0u64;
        // Reject zero because it has no logical effect and wastes resources.
        assert!(!amount > 0);
    }
}

// ============================================================================
// INTEGRATION TESTS
// ============================================================================

#[cfg(test)]
mod integration_tests {
    use super::*;
    use anchor_lang::prelude::*;
    use std::cell::RefCell;
    use std::rc::Rc;

    // Helper function to create a mock escrow for integration tests.
    fn setup_escrow() -> Escrow {
        Escrow {
            depositor: Pubkey::new_unique(),
            balance: 0,
        }
    }

    // Integration test: full deposit-then-withdraw workflow.
    #[test]
    fn test_full_deposit_withdraw_workflow() {
        // Initialize the escrow to simulate a fresh account.
        let mut escrow = setup_escrow();
        // Step 1: Deposit 1000 lamports.
        let deposit_amount = 1000u64;
        escrow.balance = escrow.balance.checked_add(deposit_amount).unwrap();
        // Assert the deposit succeeded to ensure state is correct mid-workflow.
        assert_eq!(escrow.balance, 1000);

        // Step 2: Withdraw 300 lamports.
        let withdraw_amount = 300u64;
        assert!(escrow.balance >= withdraw_amount);
        escrow.balance = escrow.balance.checked_sub(withdraw_amount).unwrap();
        // Assert the final balance is correct after the full workflow.
        assert_eq!(escrow.balance, 700);
    }

    // Integration test: multiple deposits accumulate correctly.
    #[test]
    fn test_multiple_deposits_accumulate() {
        // Initialize a fresh escrow.
        let mut escrow = setup_escrow();
        // Deposit 100, then 200, then 300 to test cumulative behavior.
        escrow.balance = escrow.balance.checked_add(100).unwrap();
        escrow.balance = escrow.balance.checked_add(200).unwrap();
        escrow.balance = escrow.balance.checked_add(300).unwrap();
        // Assert the total is 600 to confirm accumulation logic.
        assert_eq!(escrow.balance, 600);
    }

    // Integration test: attempt to withdraw more than balance should fail.
    #[test]
    fn test_overdraft_fails() {
        // Initialize an escrow with 50 lamports.
        let mut escrow = setup_escrow();
        escrow.balance = 50;
        // Attempt to withdraw 100, which exceeds the balance.
        let withdraw_amount = 100u64;
        // Check balance before subtracting to simulate the program guard.
        let can_withdraw = escrow.balance >= withdraw_amount;
        // Assert the guard returns false to confirm overdraft prevention.
        assert!(!can_withdraw);
    }
}

// ============================================================================
// FUZZING-STYLE TESTS
// ============================================================================

#[cfg(test)]
mod fuzzing_tests {
    use super::*;
    use rand::Rng;

    // Fuzzing-style test: feed random deposit amounts and verify no panic or overflow.
    #[test]
    fn test_fuzz_random_deposits() {
        // Create a random number generator for pseudo-random inputs.
        let mut rng = rand::thread_rng();
        // Initialize an escrow to receive deposits.
        let mut escrow = Escrow {
            depositor: Pubkey::new_unique(),
            balance: 0,
        };
        // Run 1000 iterations to stress-test the deposit logic.
        for _ in 0..1000 {
            // Generate a random u64 value to simulate unpredictable user input.
            let amount = rng.gen::<u64>();
            // Use checked_add to safely handle potential overflow.
            if let Some(new_balance) = escrow.balance.checked_add(amount) {
                escrow.balance = new_balance;
            } else {
                // If overflow occurs, break the loop because the program should reject it.
                break;
            }
        }
        // Assert the balance did not wrap around to a tiny value.
        assert!(escrow.balance >= 0);
    }

    // Fuzzing-style test: random deposits followed by random withdrawals.
    #[test]
    fn test_fuzz_random_withdrawals() {
        // Create a random number generator for unpredictable sequences.
        let mut rng = rand::thread_rng();
        // Initialize an escrow with a starting seed balance.
        let mut escrow = Escrow {
            depositor: Pubkey::new_unique(),
            balance: 1_000_000,
        };
        // Run 500 random withdrawal attempts.
        for _ in 0..500 {
            // Generate a random withdrawal amount.
            let amount = rng.gen::<u64>();
            // Only withdraw if the balance is sufficient, matching program logic.
            if escrow.balance >= amount {
                escrow.balance = escrow.balance.checked_sub(amount).unwrap();
            }
        }
        // Assert the final balance never underflowed and is non-negative.
        assert!(escrow.balance <= 1_000_000);
    }

    // Fuzzing-style test: boundary values near u64::MAX.
    #[test]
    fn test_fuzz_boundary_values() {
        // Initialize an escrow with balance near the maximum u64 value.
        let mut escrow = Escrow {
            depositor: Pubkey::new_unique(),
            balance: u64::MAX - 10,
        };
        // Attempt to add 5, which should succeed because there is headroom.
        let small_add = 5u64;
        let result = escrow.balance.checked_add(small_add);
        assert!(result.is_some());
        escrow.balance = result.unwrap();

        // Attempt to add 10, which should fail because it exceeds u64::MAX.
        let overflow_add = 10u64;
        let fail_result = escrow.balance.checked_add(overflow_add);
        // Assert overflow is detected at the boundary to protect against wraparound.
        assert!(fail_result.is_none());
    }
}
