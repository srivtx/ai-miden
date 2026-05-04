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
import * as borsh from 'borsh';

/**
 * Phase 9: State API
 *
 * This Express server demonstrates how to read and write program state
 * through on-chain accounts. It uses the Counter program concepts:
 * 1. Create a data account owned by the program
 * 2. Serialize instruction data using Borsh
 * 3. Send transactions that mutate state
 * 4. Deserialize account data to read the current state
 */

// WHY: Create the Express application.
const app = express();

// WHY: Parse JSON request bodies.
app.use(express.json());

// WHY: Enable CORS for frontend access.
app.use(cors());

// WHY: Connect to devnet for testing.
const connection = new Connection('https://api.devnet.solana.com', 'confirmed');

// WHY: A devnet program ID that accepts Borsh-encoded instructions.
// In a real app, this would be your deployed Counter program.
const COUNTER_PROGRAM_ID = new PublicKey('CounterDevnet111111111111111111111111111111');

// ============================================================================
// Borsh Schema
// ============================================================================
// WHY: The Counter program expects instruction data as a Borsh-encoded enum.
// Discriminant 0 = Initialize, Discriminant 1 = Increment.
const InstructionSchema = new Map([
  [
    Object,
    {
      kind: 'struct',
      fields: [['discriminant', 'u8']],
    },
  ],
]);

// WHY: The account data is a single u64 count serialized with Borsh.
const CounterSchema = new Map([
  [
    Object,
    {
      kind: 'struct',
      fields: [['count', 'u64']],
    },
  ],
]);

// ============================================================================
// POST /create-account
// ============================================================================
// WHY: Before a program can store state, a data account must exist.
// This endpoint creates an account and funds it with rent-exempt lamports.
app.post('/create-account', async (req, res) => {
  try {
    const { payerSecretKey, accountSecretKey, space } = req.body;

    // WHY: Reconstruct the payer who will fund the new account.
    const payer = Keypair.fromSecretKey(Buffer.from(payerSecretKey, 'base58'));

    // WHY: Reconstruct the new account keypair that will hold the state.
    const newAccount = Keypair.fromSecretKey(Buffer.from(accountSecretKey, 'base58'));

    // WHY: Calculate rent-exempt minimum so the account persists without being garbage-collected.
    const lamports = await connection.getMinimumBalanceForRentExemption(space || 8);

    // WHY: Fetch a fresh blockhash for the transaction.
    const { blockhash } = await connection.getLatestBlockhash('confirmed');

    // WHY: Build a transaction that creates the account via the System Program.
    const transaction = new Transaction().add(
      SystemProgram.createAccount({
        fromPubkey: payer.publicKey,
        newAccountPubkey: newAccount.publicKey,
        lamports,
        space: space || 8,
        programId: COUNTER_PROGRAM_ID,
      })
    );

    // WHY: Set blockhash and fee payer.
    transaction.recentBlockhash = blockhash;
    transaction.feePayer = payer.publicKey;

    // WHY: Sign with both payer and new account. The new account must sign
    // to prove ownership of the public key being created.
    transaction.sign(payer, newAccount);

    // WHY: Send and confirm the transaction.
    const signature = await connection.sendRawTransaction(transaction.serialize());
    await connection.confirmTransaction(signature, 'confirmed');

    return res.json({
      success: true,
      signature,
      account: newAccount.publicKey.toString(),
      space: space || 8,
      lamports,
    });
  } catch (error: any) {
    return res.status(500).json({ error: error.message || 'Account creation failed' });
  }
});

// ============================================================================
// POST /initialize
// ============================================================================
// WHY: After creating the account, the program must write the initial state.
// This endpoint sends an Initialize instruction with discriminant 0.
app.post('/initialize', async (req, res) => {
  try {
    const { payerSecretKey, counterAccount } = req.body;

    // WHY: Reconstruct the payer keypair.
    const payer = Keypair.fromSecretKey(Buffer.from(payerSecretKey, 'base58'));

    // WHY: Parse the counter account address that was created earlier.
    const counterPubkey = new PublicKey(counterAccount);

    // WHY: Serialize the Initialize instruction as a single byte: [0].
    const instructionData = borsh.serialize(InstructionSchema, { discriminant: 0 });

    // WHY: Fetch a fresh blockhash.
    const { blockhash } = await connection.getLatestBlockhash('confirmed');

    // WHY: Build the transaction with a program invocation instruction.
    const transaction = new Transaction().add({
      keys: [
        {
          pubkey: counterPubkey,
          isSigner: false,
          isWritable: true,
        },
      ],
      programId: COUNTER_PROGRAM_ID,
      data: Buffer.from(instructionData),
    } as any);

    transaction.recentBlockhash = blockhash;
    transaction.feePayer = payer.publicKey;
    transaction.sign(payer);

    const signature = await connection.sendRawTransaction(transaction.serialize());
    await connection.confirmTransaction(signature, 'confirmed');

    return res.json({
      success: true,
      signature,
      action: 'initialize',
      account: counterPubkey.toString(),
    });
  } catch (error: any) {
    return res.status(500).json({ error: error.message || 'Initialize failed' });
  }
});

// ============================================================================
// POST /increment
// ============================================================================
// WHY: This endpoint sends an Increment instruction (discriminant 1)
// to mutate the counter state stored in the account.
app.post('/increment', async (req, res) => {
  try {
    const { payerSecretKey, counterAccount } = req.body;

    const payer = Keypair.fromSecretKey(Buffer.from(payerSecretKey, 'base58'));
    const counterPubkey = new PublicKey(counterAccount);

    // WHY: Serialize the Increment instruction as a single byte: [1].
    const instructionData = borsh.serialize(InstructionSchema, { discriminant: 1 });

    const { blockhash } = await connection.getLatestBlockhash('confirmed');

    const transaction = new Transaction().add({
      keys: [
        {
          pubkey: counterPubkey,
          isSigner: false,
          isWritable: true,
        },
      ],
      programId: COUNTER_PROGRAM_ID,
      data: Buffer.from(instructionData),
    } as any);

    transaction.recentBlockhash = blockhash;
    transaction.feePayer = payer.publicKey;
    transaction.sign(payer);

    const signature = await connection.sendRawTransaction(transaction.serialize());
    await connection.confirmTransaction(signature, 'confirmed');

    return res.json({
      success: true,
      signature,
      action: 'increment',
      account: counterPubkey.toString(),
    });
  } catch (error: any) {
    return res.status(500).json({ error: error.message || 'Increment failed' });
  }
});

// ============================================================================
// GET /state/:account
// ============================================================================
// WHY: Clients need to read the current counter value without sending a transaction.
// This endpoint deserializes the on-chain account data.
app.get('/state/:account', async (req, res) => {
  try {
    const pubkey = new PublicKey(req.params.account);

    // WHY: Fetch the raw account data from the RPC node.
    const accountInfo = await connection.getAccountInfo(pubkey);

    if (!accountInfo) {
      return res.status(404).json({ error: 'Account not found' });
    }

    // WHY: Deserialize the 8-byte account data into a JavaScript object.
    // Borsh u64 maps to a BN (BigNumber) in JavaScript.
    const decoded = borsh.deserialize(CounterSchema, accountInfo.data) as any;

    return res.json({
      account: pubkey.toString(),
      count: decoded.count.toString(),
      rawData: Array.from(accountInfo.data),
      owner: accountInfo.owner.toString(),
      lamports: accountInfo.lamports,
    });
  } catch (error: any) {
    return res.status(500).json({ error: error.message || 'Failed to read state' });
  }
});

// ============================================================================
// START SERVER
// ============================================================================
const PORT = 3009;
app.listen(PORT, () => {
  console.log(`Phase 9 State API running on http://localhost:${PORT}`);
  console.log('Endpoints:');
  console.log(`  POST http://localhost:${PORT}/create-account`);
  console.log(`  POST http://localhost:${PORT}/initialize`);
  console.log(`  POST http://localhost:${PORT}/increment`);
  console.log(`  GET  http://localhost:${PORT}/state/:account`);
});
