import express from 'express';
import cors from 'cors';
import {
  Connection,
  Keypair,
  PublicKey,
  Transaction,
  SystemProgram,
  sendAndConfirmTransaction,
  LAMPORTS_PER_SOL,
} from '@solana/web3.js';

/**
 * Phase 8: Program Deploy API
 *
 * This Express server demonstrates how to:
 * 1. Prepare a program deployer wallet with devnet SOL
 * 2. Build a transaction that invokes the Hello World program
 * 3. Monitor program invocation via transaction logs
 *
 * WHY: In a real deployment pipeline, you compile BPF bytecode,
 * upload it to a buffer, and deploy it. This API simulates the
 * invocation side of that pipeline using a known devnet program.
 */

// WHY: Create the Express application.
const app = express();

// WHY: Parse JSON bodies.
app.use(express.json());

// WHY: Allow cross-origin requests.
app.use(cors());

// WHY: Connect to devnet for all RPC operations.
const connection = new Connection('https://api.devnet.solana.com', 'confirmed');

// WHY: A well-known devnet Memo program that logs messages.
// We use this as a stand-in for a custom Hello World program
// because deploying custom programs requires compiled .so files.
const MEMO_PROGRAM_ID = new PublicKey('MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr');

// ============================================================================
// POST /fund-wallet
// ============================================================================
// WHY: Before deploying or invoking programs, the wallet needs SOL for fees.
app.post('/fund-wallet', async (req, res) => {
  try {
    // WHY: Accept a secret key so the user controls which wallet gets funded.
    const { secretKey } = req.body;
    let keypair: Keypair;

    if (secretKey) {
      // WHY: Decode the base58-encoded secret key to reconstruct the Keypair.
      keypair = Keypair.fromSecretKey(Buffer.from(secretKey, 'base58'));
    } else {
      // WHY: Generate a new keypair if none is provided for quick testing.
      keypair = Keypair.generate();
    }

    // WHY: Request 2 SOL from the devnet faucet.
    const signature = await connection.requestAirdrop(keypair.publicKey, 2 * LAMPORTS_PER_SOL);

    // WHY: Wait for confirmation so the wallet has spendable balance.
    await connection.confirmTransaction(signature, 'confirmed');

    return res.json({
      success: true,
      publicKey: keypair.publicKey.toString(),
      secretKey: Buffer.from(keypair.secretKey).toString('base58'),
      airdropSignature: signature,
    });
  } catch (error: any) {
    return res.status(500).json({ error: error.message || 'Funding failed' });
  }
});

// ============================================================================
// POST /invoke-hello
// ============================================================================
// WHY: This endpoint simulates invoking a "Hello World" program by sending
// a memo instruction. The concept is identical: build a transaction with
// an instruction targeting a program, sign it, and submit it.
app.post('/invoke-hello', async (req, res) => {
  try {
    // WHY: Read the caller's secret key and optional message from the body.
    const { secretKey, message } = req.body;

    // WHY: Reconstruct the caller's Keypair from the secret key.
    const keypair = Keypair.fromSecretKey(Buffer.from(secretKey, 'base58'));

    // WHY: Fetch a fresh blockhash for the transaction.
    const { blockhash } = await connection.getLatestBlockhash('confirmed');

    // WHY: Build a new transaction.
    const transaction = new Transaction();

    // WHY: Add a memo instruction. The Memo program logs the message to
    // the transaction log, similar to how our Hello World program logs
    // "Hello, Solana!". Both require a program ID and instruction data.
    transaction.add(
      new Transaction().add({
        keys: [
          {
            pubkey: keypair.publicKey,
            isSigner: true,
            isWritable: false,
          },
        ],
        programId: MEMO_PROGRAM_ID,
        data: Buffer.from(message || 'Hello, Solana!'),
      } as any)
    );

    // WHY: Set the blockhash and fee payer.
    transaction.recentBlockhash = blockhash;
    transaction.feePayer = keypair.publicKey;

    // WHY: Sign the transaction with the caller's key.
    transaction.sign(keypair);

    // WHY: Send the signed transaction and wait for confirmation.
    const signature = await connection.sendRawTransaction(transaction.serialize());
    await connection.confirmTransaction(signature, 'confirmed');

    // WHY: Fetch the transaction logs so the client can see the program output.
    const txInfo = await connection.getParsedTransaction(signature, { commitment: 'confirmed', maxSupportedTransactionVersion: 0 });

    return res.json({
      success: true,
      signature,
      message: message || 'Hello, Solana!',
      explorerUrl: `https://explorer.solana.com/tx/${signature}?cluster=devnet`,
      // WHY: Return the raw logs so the user sees the program's "Hello" message.
      logs: txInfo?.meta?.logMessages || [],
    });
  } catch (error: any) {
    return res.status(500).json({ error: error.message || 'Invocation failed' });
  }
});

// ============================================================================
// GET /program-info/:programId
// ============================================================================
// WHY: After deploying a program, you need to verify it exists on-chain.
// This endpoint returns the executable account metadata.
app.get('/program-info/:programId', async (req, res) => {
  try {
    // WHY: Parse the program ID from the URL.
    const programId = new PublicKey(req.params.programId);

    // WHY: Query the account info for this program address.
    const accountInfo = await connection.getAccountInfo(programId);

    if (!accountInfo) {
      return res.status(404).json({ error: 'Program not found on devnet' });
    }

    // WHY: Verify that the account is actually executable (a program).
    if (!accountInfo.executable) {
      return res.status(400).json({ error: 'Account is not a program' });
    }

    return res.json({
      programId: programId.toString(),
      executable: accountInfo.executable,
      owner: accountInfo.owner.toString(),
      lamports: accountInfo.lamports,
      dataSize: accountInfo.data.length,
    });
  } catch (error: any) {
    return res.status(400).json({ error: error.message || 'Invalid program ID' });
  }
});

// ============================================================================
// START SERVER
// ============================================================================
const PORT = 3008;
app.listen(PORT, () => {
  console.log(`Phase 8 Program Deploy API running on http://localhost:${PORT}`);
  console.log('Endpoints:');
  console.log(`  POST http://localhost:${PORT}/fund-wallet`);
  console.log(`  POST http://localhost:${PORT}/invoke-hello`);
  console.log(`  GET  http://localhost:${PORT}/program-info/:programId`);
});
