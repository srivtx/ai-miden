import { Connection, PublicKey, LAMPORTS_PER_SOL } from '@solana/web3.js';

/**
 * Phase 7: RPC Client (TypeScript)
 *
 * Demonstrates querying Solana blockchain data using @solana/web3.js
 */

async function main() {
    // WHY: Print a header so the user knows which demo is running.
    console.log('=== Phase 7: RPC Client (TypeScript) ===\n');

    // ============================================================================
    // 1. CONNECT TO DEVNET
    // ============================================================================
    // WHY: Create a Connection to devnet with confirmed commitment for reliable reads.
    const connection = new Connection('https://api.devnet.solana.com', 'confirmed');
    console.log('1. Connected to devnet\n');

    // ============================================================================
    // 2. GET LATEST SLOT
    // ============================================================================
    // WHY: The slot is the current block number. It proves the connection is alive.
    const slot = await connection.getSlot();
    console.log(`2. Latest Slot: ${slot}\n`);

    // ============================================================================
    // 3. GET BLOCK HEIGHT
    // ============================================================================
    // WHY: Block height counts finalized blocks, useful for measuring chain progress.
    const blockHeight = await connection.getBlockHeight();
    console.log(`3. Block Height: ${blockHeight}\n`);

    // ============================================================================
    // 4. GET VERSION
    // ============================================================================
    // WHY: Knowing the Solana version helps debug compatibility issues.
    const version = await connection.getVersion();
    console.log(`4. Solana Version: ${version['solana-core']}\n`);

    // ============================================================================
    // 5. GET SUPPLY
    // ============================================================================
    // WHY: Total supply metrics are essential for understanding network tokenomics.
    const supply = await connection.getSupply();
    console.log('5. Total Supply');
    console.log(`   Total:      ${(supply.value.total / LAMPORTS_PER_SOL).toLocaleString()} SOL`);
    console.log(`   Circulating: ${(supply.value.circulating / LAMPORTS_PER_SOL).toLocaleString()} SOL`);
    console.log(`   Non-Circulating: ${(supply.value.nonCirculating / LAMPORTS_PER_SOL).toLocaleString()} SOL\n`);

    // ============================================================================
    // 6. GET FEE FOR RECENT BLOCKHASH
    // ============================================================================
    // WHY: Fee estimation helps users understand the cost of their transaction before sending.
    const recentBlockhash = await connection.getLatestBlockhash();
    console.log('6. Recent Blockhash');
    console.log(`   Blockhash: ${recentBlockhash.blockhash}`);

    // WHY: Dynamically import TransactionMessage to estimate fees without a real transaction.
    const { TransactionMessage } = await import('@solana/web3.js');
    const message = new TransactionMessage({
        payerKey: new PublicKey('11111111111111111111111111111111'),
        recentBlockhash: recentBlockhash.blockhash,
        instructions: [],
    }).compileToLegacyMessage();

    const fee = await connection.getFeeForMessage(message);
    console.log(`   Fee: ~${fee.value || 0} lamports\n`);

    // ============================================================================
    // 7. GET EPOCH INFO
    // ============================================================================
    // WHY: Epochs define staking reward periods. Validators and stakers need this data.
    const epochInfo = await connection.getEpochInfo();
    console.log('7. Epoch Info');
    console.log(`   Epoch: ${epochInfo.epoch}`);
    console.log(`   Slot Index: ${epochInfo.slotIndex}`);
    console.log(`   Slots in Epoch: ${epochInfo.slotsInEpoch}`);
    console.log(`   Absolute Slot: ${epochInfo.absoluteSlot}\n`);

    // ============================================================================
    // 8. GET PERFORMANCE SAMPLES
    // ============================================================================
    // WHY: TPS metrics show how heavily the network is being used.
    const perfSamples = await connection.getRecentPerformanceSamples(5);
    console.log('8. Performance Samples (last 5)');
    perfSamples.forEach((sample, i) => {
        const tps = Math.round(sample.numTransactions / sample.samplePeriodSecs);
        console.log(`   Sample ${i + 1}: ${sample.numTransactions} tx in ${sample.samplePeriodSecs}s (${tps} TPS)`);
    });
    console.log();

    // WHY: Print completion summary.
    console.log('=== Phase 7 Complete ===');
    console.log('You can query any Solana data using @solana/web3.js');
    console.log('Key methods: getBalance, getAccountInfo, getTransaction, getBlock');
}

// WHY: Execute the main function and catch any errors.
main().catch(console.error);
