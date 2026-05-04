use std::collections::HashMap;
// We import HashMap to store accounts by their address for quick lookup during transaction execution.

// PHASE 4: Account Model Demo in Rust
// This file simulates Solana's account model with programs, data accounts, ownership, and rent.

/// Represents a generic Solana account with fields matching the runtime's account structure.
/// We use a struct because accounts have a fixed set of properties enforced by the system.
struct Account {
    /// The public key address that uniquely identifies this account on the ledger.
    address: String,
    /// Lamport balance used for rent exemption and transaction fee payment.
    lamports: u64,
    /// Mutable data payload that programs interpret according to their own schema.
    data: Vec<u8>,
    /// The program that owns this account and is allowed to modify its data.
    owner: String,
    /// Executable flag distinguishes program accounts from data accounts.
    executable: bool,
    /// Rent epoch tracks when the account was last charged rent.
    rent_epoch: u64,
}

/// Simulates the Solana runtime that enforces account rules during transaction execution.
/// We use a struct to encapsulate the ledger state and validation logic.
struct Runtime {
    /// Stores all accounts by address so transactions can look them up.
    accounts: HashMap<String, Account>,
    /// Rent rate in lamports per byte per epoch to calculate storage costs.
    rent_rate: u64,
}

impl Runtime {
    /// Creates a new runtime with a known rent rate so economic calculations are reproducible.
    fn new(rent_rate: u64) -> Self {
        Self {
            accounts: HashMap::new(),
            rent_rate,
        }
    }

    /// Creates a new account if the address does not already exist.
    fn create_account(&mut self, address: &str, lamports: u64, data_size: usize, owner: &str, executable: bool) {
        let account = Account {
            address: address.to_string(),
            lamports,
            data: vec![0u8; data_size],
            owner: owner.to_string(),
            executable,
            rent_epoch: 0,
        };
        self.accounts.insert(address.to_string(), account);
    }

    /// Computes the rent-exempt threshold for a given data size.
    /// Accounts above this balance avoid periodic rent charges and persist forever.
    fn rent_exempt_threshold(&self, data_size: usize) -> u64 {
        self.rent_rate * data_size as u64 * 24 // Roughly 2 years of rent.
    }

    /// Attempts to write data to an account, enforcing ownership rules.
    /// Only the owning program can mutate data, mirroring Solana's security boundary.
    fn write_data(&mut self, account_address: &str, caller_program: &str, data: &[u8]) -> Result<(), String> {
        let account = self.accounts.get_mut(account_address)
            .ok_or("Account not found")?;
        if account.owner != caller_program {
            return Err("Invalid owner: only the owning program can write".to_string());
        }
        if account.executable {
            return Err("Cannot write to executable account".to_string());
        }
        account.data = data.to_vec();
        Ok(())
    }

    /// Reads data from any account because reads do not require ownership.
    fn read_data(&self, account_address: &str) -> Option<&Vec<u8>> {
        self.accounts.get(account_address).map(|a| &a.data)
    }

    /// Transfers lamports between accounts to simulate rent payment or value transfer.
    fn transfer_lamports(&mut self, from: &str, to: &str, amount: u64) -> Result<(), String> {
        let from_account = self.accounts.get_mut(from)
            .ok_or("Source account not found")?;
        if from_account.lamports < amount {
            return Err("Insufficient balance".to_string());
        }
        from_account.lamports -= amount;
        let to_account = self.accounts.get_mut(to)
            .ok_or("Destination account not found")?;
        to_account.lamports += amount;
        Ok(())
    }
}

fn main() {
    // Initialize the runtime with a rent rate of 10 lamports per byte per epoch.
    let mut runtime = Runtime::new(10);

    // Create a program account to represent deployed bytecode.
    // Program accounts are executable and typically owned by the BPF loader.
    runtime.create_account("token_program", 0, 1024, "bpf_loader", true);

    // Create a data account owned by the token program to store a user's token balance.
    // Data accounts are non-executable and hold mutable state.
    runtime.create_account("alice_token_account", 5000, 165, "token_program", false);

    // Create another data account for Bob.
    runtime.create_account("bob_token_account", 5000, 165, "token_program", false);

    // Calculate rent-exempt threshold for a 165-byte account.
    let threshold = runtime.rent_exempt_threshold(165);
    println!("Rent-exempt threshold for 165 bytes: {} lamports", threshold);

    // Alice's account has 5000 lamports; check if it is rent-exempt.
    let alice_rent_exempt = 5000 >= threshold;
    println!("Alice account is rent-exempt: {}", alice_rent_exempt);

    // Write token balance data into Alice's account as the token program.
    // This succeeds because the caller matches the account owner.
    let alice_balance = 100u64.to_le_bytes();
    match runtime.write_data("alice_token_account", "token_program", &alice_balance) {
        Ok(()) => println!("Wrote Alice balance successfully"),
        Err(e) => println!("Write failed: {}", e),
    }

    // Attempt to write to Alice's account using the wrong program.
    // This MUST fail because the runtime enforces ownership boundaries.
    match runtime.write_data("alice_token_account", "malicious_program", &[255u8; 8]) {
        Ok(()) => println!("Unauthorized write succeeded (BUG!)"),
        Err(e) => println!("Unauthorized write blocked: {}", e),
    }

    // Transfer 50 lamports from Alice to Bob to simulate a fee or value transfer.
    match runtime.transfer_lamports("alice_token_account", "bob_token_account", 50) {
        Ok(()) => println!("Transferred 50 lamports"),
        Err(e) => println!("Transfer failed: {}", e),
    }

    // Read back Alice's data to verify the balance write persisted.
    if let Some(data) = runtime.read_data("alice_token_account") {
        let balance = u64::from_le_bytes(data[..8].try_into().unwrap_or([0; 8]));
        println!("Alice token balance: {}", balance);
    }

    // Print final balances to show the state transition.
    if let Some(acc) = runtime.accounts.get("alice_token_account") {
        println!("Alice lamports after transfer: {}", acc.lamports);
    }
    if let Some(acc) = runtime.accounts.get("bob_token_account") {
        println!("Bob lamports after transfer: {}", acc.lamports);
    }
}
