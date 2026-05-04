import { Connection, Keypair, PublicKey, Transaction, SystemProgram, sendAndConfirmTransaction } from '@solana/web3.js';

/**
 * Phase 6: First Transaction (TypeScript)
 *
 * This script demonstrates how to:
 * 1. Connect to devnet
 * 2. Create a new wallet
 * 3. Request an airdrop
 * 4. Check balance
 * 5. Send SOL to another wallet
 * 6. Verify the transaction
 */

// WHY: Define the constant for lamports per SOL because TypeScript needs it explicitly.
const LAMPORTS_PER_SOL = 1000000000;

async function main() {
    // WHY: Print a header so the user knows which demo is running.
    console.log('=== Phase 6: First Transaction (TypeScript) ===\n');

    // ============================================================================
    // 1. CONNECT TO DEVNET
    // ============================================================================
    // WHY: Create a Connection to the devnet RPC endpoint with 'confirmed' commitment.
    // This ensures balance reads reflect confirmed blocks, not just processed ones.
    const connection = new Connection('https://api.devnet.solana.com', 'confirmed');
    console.log('1. Connected to https://api.devnet.solana.com\n');

    // ============================================================================
    // 2. CREATE A NEW WALLET
    // ============================================================================
    // WHY: Generate a fresh keypair to act as the sender for this demo.
    const sender = Keypair.generate();
    console.log('2. Created new wallet');
    console.log(`   Public Key: ${sender.publicKey.toString()}`);
    console.log(`   Secret Key: [hidden]\n`);

    // ============================================================================
    // 3. REQUEST AIRDROP
    // ============================================================================
    // WHY: Devnet provides free SOL via airdrops so developers can test without spending money.
    console.log('3. Requesting airdrop of 2 SOL...');
    try {
        // WHY: Request 2 SOL converted to lamports. The RPC expects lamports.
        const signature = await connection.requestAirdrop(sender.publicKey, 2 * LAMPORTS_PER_SOL);
        console.log(`   Airdrop transaction: ${signature}`);

        // WHY: Wait for confirmation before proceeding. Unconfirmed airdrops are not spendable.
        await connection.confirmTransaction(signature, 'confirmed');
        console.log('   Airdrop confirmed!\n');
    } catch (e) {
        // WHY: Airdrops can fail due to rate limits. Catch and explain instead of crashing.
        console.log(`   Airdrop failed: ${e}`);
        console.log('   (Rate-limited. Try again later.)\n');
        return;
    }

    // ============================================================================
    // 4. CHECK BALANCE
    // ============================================================================
    // WHY: Verify the airdrop by reading the on-chain balance.
    const balance = await connection.getBalance(sender.publicKey);
    console.log(`4. Wallet Balance: ${balance / LAMPORTS_PER_SOL} SOL\n`);

    // ============================================================================
    // 5. CREATE RECIPIENT
    // ============================================================================
    // WHY: Generate a second wallet to receive the transfer.
    const recipient = Keypair.generate();
    console.log(`5. Created recipient wallet: ${recipient.publicKey.toString()}\n`);

    // ============================================================================
    // 6. BUILD AND SEND TRANSACTION
    // ============================================================================
    // WHY: Construct a transaction that transfers 1 SOL from sender to recipient.
    console.log('6. Sending transaction...');

    // WHY: Create a new Transaction object.
    const transaction = new Transaction();

    // WHY: Add a System Program transfer instruction to the transaction.
    transaction.add(
        SystemProgram.transfer({
            fromPubkey: sender.publicKey,
            toPubkey: recipient.publicKey,
            lamports: LAMPORTS_PER_SOL, // WHY: Transfer exactly 1 SOL.
        })
    );

    // WHY: sendAndConfirmTransaction handles fetching the blockhash, signing, sending, and polling.
    const txSignature = await sendAndConfirmTransaction(connection, transaction, [sender]);
    console.log(`   Transaction sent: ${txSignature}`);
    console.log(`   View on explorer: https://explorer.solana.com/tx/${txSignature}?cluster=devnet\n`);

    // ============================================================================
    // 7. VERIFY BALANCES
    // ============================================================================
    // WHY: Query both balances to confirm the transfer and show the fee deduction.
    const senderBalance = await connection.getBalance(sender.publicKey);
    const recipientBalance = await connection.getBalance(recipient.publicKey);

    console.log('7. Final Balances');
    console.log(`   Sender:    ${senderBalance / LAMPORTS_PER_SOL} SOL`);
    console.log(`   Recipient: ${recipientBalance / LAMPORTS_PER_SOL} SOL`);
    console.log(`   Fees paid: ~0.000005 SOL\n`);

    console.log('=== Phase 6 Complete ===');
    console.log('You sent your first Solana transaction!');
}

// WHY: Run the main function and print any unhandled errors to the console.
main().catch(console.error);
