use solana_client::rpc_client::RpcClient;
use solana_sdk::{
    pubkey::Pubkey,
    commitment_config::CommitmentConfig,
};
use std::str::FromStr;

/// Phase 7: Reading Blockchain Data
///
/// This demo shows how to query the Solana blockchain using RPC:
/// 1. Get account balance
/// 2. Get account info
/// 3. Get latest slot
/// 4. Get block height
/// 5. Get transaction count
fn main() {
    // WHY: Print a header so the user knows which phase is running.
    println!("=== Phase 7: Reading Blockchain Data ===\n");

    // WHY: Create an RPC client connected to devnet with confirmed commitment.
    // Confirmed commitment is the standard for reliable queries.
    let client = RpcClient::new_with_commitment(
        "https://api.devnet.solana.com".to_string(),
        CommitmentConfig::confirmed(),
    );

    // =========================================================================
    // 1. GET LATEST SLOT
    // =========================================================================
    // WHY: The slot is like a block number. It tells you where the blockchain currently is.
    match client.get_slot() {
        Ok(slot) => println!("1. Latest Slot: {}\n", slot),
        Err(e) => println!("1. Error getting slot: {}\n", e),
    }

    // =========================================================================
    // 2. GET BLOCK HEIGHT
    // =========================================================================
    // WHY: Block height counts only finalized blocks, which is useful for progress tracking.
    match client.get_block_height() {
        Ok(height) => println!("2. Block Height: {}\n", height),
        Err(e) => println!("2. Error getting block height: {}\n", e),
    }

    // =========================================================================
    // 3. GET TRANSACTION COUNT
    // =========================================================================
    // WHY: This gives a rough sense of network activity and total historical throughput.
    match client.get_transaction_count() {
        Ok(count) => println!("3. Transaction Count: {}\n", count),
        Err(e) => println!("3. Error getting transaction count: {}\n", e),
    }

    // =========================================================================
    // 4. GET ACCOUNT BALANCE (Serum Program)
    // =========================================================================
    // WHY: We use a well-known devnet account for demonstration so the example works reliably.
    let serum_program = Pubkey::from_str("9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin").unwrap_or_else(|_| Pubkey::new_unique());

    // WHY: Query the balance to show how to read a specific account's lamports.
    match client.get_balance(&serum_program) {
        Ok(balance) => {
            println!("4. Serum Program Balance");
            println!("   Account: {}", serum_program);
            // WHY: Print both lamports and SOL for clarity.
            println!("   Balance: {} lamports ({:.6} SOL)\n", balance, balance as f64 / 1_000_000_000.0);
        }
        Err(e) => println!("4. Error getting balance: {}\n", e),
    }

    // =========================================================================
    // 5. GET ACCOUNT INFO
    // =========================================================================
    // WHY: Account info reveals ownership, executable status, data size, and rent epoch.
    match client.get_account(&serum_program) {
        Ok(account) => {
            println!("5. Serum Program Account Info");
            println!("   Lamports:   {}", account.lamports);
            println!("   Data size:  {} bytes", account.data.len());
            println!("   Owner:      {}", account.owner);
            println!("   Executable: {}", account.executable);
            println!("   Rent Epoch: {}\n", account.rent_epoch);
        }
        Err(e) => println!("5. Error getting account info: {}\n", e),
    }

    // =========================================================================
    // 6. GET SUPPLY
    // =========================================================================
    // WHY: Total supply information is important for understanding tokenomics and inflation.
    match client.get_supply() {
        Ok(supply) => {
            println!("6. Total Supply");
            println!("   Total:      {} SOL", supply.total as f64 / 1_000_000_000.0);
            println!("   Circulating: {} SOL", supply.circulating as f64 / 1_000_000_000.0);
            println!("   Non-circulating: {} SOL\n", supply.non_circulating as f64 / 1_000_000_000.0);
        }
        Err(e) => println!("6. Error getting supply: {}\n", e),
    }

    // =========================================================================
    // 7. GET RECENT BLOCKHASH
    // =========================================================================
    // WHY: Recent blockhashes are required for building transactions.
    match client.get_latest_blockhash() {
        Ok(blockhash) => {
            println!("7. Recent Blockhash");
            println!("   {}\n", blockhash);
        }
        Err(e) => println!("7. Error getting blockhash: {}\n", e),
    }

    // WHY: Print a summary of what was learned.
    println!("=== Phase 7 Complete ===");
    println!("You can now query any data from the Solana blockchain.");
    println!("Key RPC methods:");
    println!("- get_balance: Account balance");
    println!("- get_account: Full account info");
    println!("- get_slot: Current block number");
    println!("- get_transaction_count: Total transactions");
    println!("- get_supply: Total SOL supply");
    println!("- get_latest_blockhash: For building transactions");
}
