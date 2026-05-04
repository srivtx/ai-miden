import express from 'express';
import cors from 'cors';
import {
  Connection,
  Keypair,
  PublicKey,
  Transaction,
  SystemProgram,
  LAMPORTS_PER_SOL,
} from '@solana/web3.js';
import * as borsh from 'borsh';

/**
 * Phase 10: PDA API
 *
 * This Express server demonstrates Program Derived Addresses:
 * 1. Derive a PDA from seeds and a program ID
 * 2. Create a PDA account via Cross-Program Invocation
 * 3. Increment state stored inside a PDA
 * 4. Read PDA state from the blockchain
 */

// WHY: Create the Express application.
const app = express();

// WHY: Parse JSON bodies and enable cross-origin requests.
app.use(express.json());
app.use(cors());

// WHY: Connect to devnet for all blockchain operations.
const connection = new Connection('https://api.devnet.solana.com', 'confirmed');

// WHY: In a real scenario, this would be your deployed PDA demo program.
const PDA_PROGRAM_ID = new PublicKey('PdaDemoDevnet111111111111111111111111111111');

// ============================================================================
// Borsh Schemas
// ============================================================================
const InstructionSchema = new Map([
  [Object, { kind: 'struct', fields: [['discriminant', 'u8']] }],
]);

const UserCounterSchema = new Map([
  [Object, { kind: 'struct', fields: [['count', 'u64']] }],
]);

// ============================================================================
// GET /derive-pda
// ============================================================================
// WHY: Clients need to know the deterministic address before creating it.
// This endpoint replicates the Rust find_program_address logic.
app.get('/derive-pda', async (req, res) => {
  try {
    // WHY: Read the user's public key and optional seed from query params.
    const userAddress = req.query.user as string;
    const seed = (req.query.seed as string) || 'counter';

    if (!userAddress) {
      return res.status(400).json({ error: 'Missing user query parameter' });
    }

    // WHY: Parse the user's public key.
    const userPubkey = new PublicKey(userAddress);

    // WHY: Convert the seed string to bytes.
    const seedBytes = Buffer.from(seed);

    // WHY: Use Solana web3.js to derive the PDA and bump.
    // This runs the same algorithm as Pubkey::find_program_address in Rust.
    const [pda, bump] = await PublicKey.findProgramAddress(
      [userPubkey.toBuffer(), seedBytes],
      PDA_PROGRAM_ID
    );

    return res.json({
      user: userPubkey.toString(),
      seed,
      programId: PDA_PROGRAM_ID.toString(),
      pda: pda.toString(),
      bump,
    });
  } catch (error: any) {
    return res.status(500).json({ error: error.message || 'PDA derivation failed' });
  }
});

// ============================================================================
// POST /create-pda
// ============================================================================
// WHY: Creating a PDA requires the program to sign via invoke_signed.
// The client builds the transaction that triggers this CPI.
app.post('/create-pda', async (req, res) => {
  try {
    const { payerSecretKey, userAddress, seed } = req.body;

    // WHY: Reconstruct the payer who funds the PDA account.
    const payer = Keypair.fromSecretKey(Buffer.from(payerSecretKey, 'base58'));
    const userPubkey = new PublicKey(userAddress);
    const seedBytes = Buffer.from(seed || 'counter');

    // WHY: Derive the PDA and bump so we can pass them in the transaction.
    const [pda, bump] = await PublicKey.findProgramAddress(
      [userPubkey.toBuffer(), seedBytes],
      PDA_PROGRAM_ID
    );

    // WHY: Serialize the Initialize instruction (discriminant 0).
    const instructionData = borsh.serialize(InstructionSchema, { discriminant: 0 });

    // WHY: Fetch a fresh blockhash.
    const { blockhash } = await connection.getLatestBlockhash('confirmed');

    // WHY: Build the transaction with the program invocation.
    // The program will use invoke_signed with the seeds + bump to create the account.
    const transaction = new Transaction().add({
      keys: [
        {
          pubkey: payer.publicKey,
          isSigner: true,
          isWritable: true,
        },
        {
          pubkey: userPubkey,
          isSigner: false,
          isWritable: false,
        },
        {
          pubkey: pda,
          isSigner: false,
          isWritable: true,
        },
        {
          pubkey: SystemProgram.programId,
          isSigner: false,
          isWritable: false,
        },
      ],
      programId: PDA_PROGRAM_ID,
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
      pda: pda.toString(),
      bump,
      user: userPubkey.toString(),
      action: 'create-pda',
    });
  } catch (error: any) {
    return res.status(500).json({ error: error.message || 'PDA creation failed' });
  }
});

// ============================================================================
// POST /increment-pda
// ============================================================================
// WHY: After creation, the PDA holds state that can be incremented.
// The program signs for the PDA during the state update.
app.post('/increment-pda', async (req, res) => {
  try {
    const { payerSecretKey, userAddress, seed } = req.body;

    const payer = Keypair.fromSecretKey(Buffer.from(payerSecretKey, 'base58'));
    const userPubkey = new PublicKey(userAddress);
    const seedBytes = Buffer.from(seed || 'counter');

    // WHY: Re-derive the PDA so we know which account to target.
    const [pda, bump] = await PublicKey.findProgramAddress(
      [userPubkey.toBuffer(), seedBytes],
      PDA_PROGRAM_ID
    );

    // WHY: Serialize the Increment instruction (discriminant 1).
    const instructionData = borsh.serialize(InstructionSchema, { discriminant: 1 });

    const { blockhash } = await connection.getLatestBlockhash('confirmed');

    const transaction = new Transaction().add({
      keys: [
        {
          pubkey: payer.publicKey,
          isSigner: true,
          isWritable: false,
        },
        {
          pubkey: userPubkey,
          isSigner: false,
          isWritable: false,
        },
        {
          pubkey: pda,
          isSigner: false,
          isWritable: true,
        },
      ],
      programId: PDA_PROGRAM_ID,
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
      pda: pda.toString(),
      bump,
      action: 'increment-pda',
    });
  } catch (error: any) {
    return res.status(500).json({ error: error.message || 'PDA increment failed' });
  }
});

// ============================================================================
// GET /pda-state/:pda
// ============================================================================
// WHY: Clients need to read the counter value stored inside the PDA.
app.get('/pda-state/:pda', async (req, res) => {
  try {
    const pdaPubkey = new PublicKey(req.params.pda);

    // WHY: Fetch the raw account data for the PDA.
    const accountInfo = await connection.getAccountInfo(pdaPubkey);

    if (!accountInfo) {
      return res.status(404).json({ error: 'PDA account not found' });
    }

    // WHY: Deserialize the u64 count using Borsh.
    const decoded = borsh.deserialize(UserCounterSchema, accountInfo.data) as any;

    return res.json({
      pda: pdaPubkey.toString(),
      count: decoded.count.toString(),
      owner: accountInfo.owner.toString(),
      lamports: accountInfo.lamports,
      dataSize: accountInfo.data.length,
    });
  } catch (error: any) {
    return res.status(500).json({ error: error.message || 'Failed to read PDA state' });
  }
});

// ============================================================================
// START SERVER
// ============================================================================
const PORT = 3010;
app.listen(PORT, () => {
  console.log(`Phase 10 PDA API running on http://localhost:${PORT}`);
  console.log('Endpoints:');
  console.log(`  GET  http://localhost:${PORT}/derive-pda?user=<pubkey>&seed=counter`);
  console.log(`  POST http://localhost:${PORT}/create-pda`);
  console.log(`  POST http://localhost:${PORT}/increment-pda`);
  console.log(`  GET  http://localhost:${PORT}/pda-state/:pda`);
});
