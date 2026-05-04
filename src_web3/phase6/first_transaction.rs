use solana_client::rpc_client::RpcClient;
use solana_sdk::{
    signature::{Keypair, Signer},
    transaction::Transaction,
    system_instruction,
    pubkey::Pubkey,
    commitment_config::CommitmentConfig,
};
use std::str::FromStr;

/// Phase 6: Your First Transaction
///
/// This demo shows how to:
/// 1. Connect to Solana devnet
/// 2. Create or load a wallet
/// 3. Request an airdrop (test SOL)
/// 4. Check balance
/// 5. Send a transfer transaction
/// 6. Verify the transaction
///
/// NOTE: This requires internet connection to devnet.
fn main() {
    // WHY: Print a header so the user knows which phase is running.
    println!("=== Phase 6: Your First Transaction ===\n");

    // =========================================================================
    // 1. CONNECT TO DEVNET
    // =========================================================================
    // WHY: Devnet is a public test network with free SOL.
    // Use it for development. Never use mainnet for testing.
    let rpc_url = "https://api.devnet.solana.com";

    // WHY: Create an RPC client with 'confirmed' commitment.
    // This balances speed with a strong guarantee the block will not be rolled back.
    let client = RpcClient::new_with_commitment(
        rpc_url.to_string(),
        CommitmentConfig::confirmed(),
    );

    // WHY: Print the RPC URL so the user knows which network is in use.
    println!("1. Connected to {}", rpc_url);

    // WHY: Query the current slot to prove the connection is alive.
    let slot = client.get_slot().expect("Failed to get slot");
    println!("   Current slot: {}\n", slot);

    // =========================================================================
    // 2. CREATE A NEW WALLET
    // =========================================================================
    // WHY: In production, you would load an existing keypair from a secure file.
    // For this demo, we generate a new one so it runs without setup.
    let sender = Keypair::new();
    println!("2. Created new wallet");

    // WHY: Print the public key so the user can view it on a block explorer.
    println!("   Public Key: {}", sender.pubkey());

    // WHY: Hide the private key in output to discourage copying it to logs.
    println!("   Private Key: [hidden]\n");

    // =========================================================================
    // 3. REQUEST AIRDROP
    // =========================================================================
    // WHY: Devnet provides free test SOL via airdrops so developers can experiment.
    // Mainnet requires purchasing SOL from an exchange.
    println!("3. Requesting airdrop of 2 SOL...");

    // WHY: 2 SOL = 2,000,000,000 lamports. The RPC works in lamports.
    match client.request_airdrop(&sender.pubkey(), 2_000_000_000) {
        Ok(signature) => {
            // WHY: Print the airdrop signature so the user can track it on an explorer.
            println!("   Airdrop transaction: {}", signature);

            // WHY: Wait for confirmation in a loop because airdrops are not instant.
            loop {
                // WHY: Check if the cluster has confirmed the airdrop transaction.
                match client.confirm_transaction(&signature) {
                    Ok(true) => {
                        // WHY: Confirmed means the funds are spendable.
                        println!("   Airdrop confirmed!\n");
                        break;
                    }
                    Ok(false) => {
                        // WHY: Sleep for 1 second before polling again to avoid rate limits.
                        std::thread::sleep(std::time::Duration::from_secs(1));
                        continue;
                    }
                    Err(e) => {
                        // WHY: Print the error and stop polling if something goes wrong.
                        println!("   Error confirming: {}\n", e);
                        break;
                    }
                }
            }
        }
        Err(e) => {
            // WHY: Airdrops can fail due to rate limits. Inform the user instead of panicking.
            println!("   Airdrop failed: {}", e);
            println!("   (This is normal if rate-limited. Try again later.)\n");
            return;
        }
    }

    // =========================================================================
    // 4. CHECK BALANCE
    // =========================================================================
    // WHY: Verify the airdrop succeeded by reading the on-chain balance.
    let balance = client.get_balance(&sender.pubkey()).unwrap_or(0);
    println!("4. Wallet Balance");

    // WHY: Print both lamports and SOL because different tools use different units.
    println!("   {} lamports ({} SOL)\n", balance, balance as f64 / 1_000_000_000.0);

    // =========================================================================
    // 5. CREATE RECIPIENT
    // =========================================================================
    // WHY: Generate a second wallet to act as the transfer destination.
    let recipient = Keypair::new();
    println!("5. Created recipient wallet");
    println!("   Public Key: {}\n", recipient.pubkey());

    // =========================================================================
    // 6. BUILD AND SEND TRANSACTION
    // =========================================================================
    // WHY: A transaction contains instructions. Here we have one instruction:
    // transfer SOL from sender to recipient using the System Program.
    let amount = 1_000_000_000; // WHY: 1 SOL in lamports.

    // WHY: Build a system transfer instruction specifying sender, recipient, and amount.
    let transfer_instruction = system_instruction::transfer(
        &sender.pubkey(),
        &recipient.pubkey(),
        amount,
    );

    // WHY: Fetch a recent blockhash to prevent replay and mark the transaction as current.
    let recent_blockhash = client.get_latest_blockhash().expect("Failed to get blockhash");

    // WHY: Construct a signed transaction containing the transfer instruction.
    let transaction = Transaction::new_signed_with_payer(
        &[transfer_instruction],
        Some(&sender.pubkey()),
        &[&sender],
        recent_blockhash,
    );

    println!("6. Sending transaction...");

    // WHY: Send the transaction and wait for confirmation in one call.
    match client.send_and_confirm_transaction(&transaction) {
        Ok(signature) => {
            println!("   Transaction sent: {}", signature);
            // WHY: Provide a direct link to the block explorer for visual verification.
            println!("   View on explorer: https://explorer.solana.com/tx/{}?cluster=devnet\n", signature);
        }
        Err(e) => {
            // WHY: Print the error and exit early if the transfer fails.
            println!("   Transaction failed: {}\n", e);
            return;
        }
    }

    // =========================================================================
    // 7. VERIFY BALANCES
    // =========================================================================
    // WHY: Read both balances to prove the transfer occurred and fees were deducted.
    let sender_balance = client.get_balance(&sender.pubkey()).unwrap_or(0);
    let recipient_balance = client.get_balance(&recipient.pubkey()).unwrap_or(0);

    println!("7. Final Balances");
    println!("   Sender:    {} lamports ({} SOL)", sender_balance, sender_balance as f64 / 1_000_000_000.0);
    println!("   Recipient: {} lamports ({} SOL)\n", recipient_balance, recipient_balance as f64 / 1_000_000_000.0);

    // WHY: Print a summary of what was learned in this phase.
    println!("=== Phase 6 Complete ===");
    println!("You have sent your first Solana transaction!");
    println!("Key concepts:");
    println!("- Transactions contain instructions");
    println!("- Instructions specify program, accounts, and data");
    println!("- Recent blockhash prevents replay attacks");
    println!("- Signatures prove authorization");
    println!("- All instructions in a transaction are atomic");
}
