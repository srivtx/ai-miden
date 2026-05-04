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
 * Phase 6: Transaction API
 *
 * This Express server exposes REST endpoints to:
 * 1. Create and fund a wallet via airdrop
 * 2. Check a wallet balance
 * 3. Build, sign, and send a SOL transfer transaction
 * 4. Monitor a transaction's confirmation status
 *
 * WHY: Wrapping blockchain operations in an API makes them accessible
 * to frontend applications, mobile clients, and other services that
 * do not run Solana client libraries directly.
 */

// WHY: Create the Express application instance.
const app = express();

// WHY: Parse incoming JSON request bodies so we can read parameters.
app.use(express.json());

// WHY: Enable CORS so browsers from different origins can call this API.
app.use(cors());

// WHY: Connect to devnet using 'confirmed' commitment for reliable reads.
const connection = new Connection('https://api.devnet.solana.com', 'confirmed');

// WHY: In-memory cache for transaction statuses so clients can poll.
const txCache: Map<string, { status: string; slot?: number; err?: any }> = new Map();

// ============================================================================
// POST /airdrop
// ============================================================================
// WHY: Developers need test SOL to experiment. This endpoint funds any
// address with devnet SOL so they can build transactions immediately.
app.post('/airdrop', async (req, res) => {
  try {
    // WHY: Read the target address from the request body.
    const { address, amount } = req.body;

    // WHY: Validate that the client provided a valid Solana public key string.
    let pubkey: PublicKey;
    try {
      pubkey = new PublicKey(address);
    } catch {
      // WHY: Return 400 so the client knows their input is malformed.
      return res.status(400).json({ error: 'Invalid public key' });
    }

    // WHY: Default to 2 SOL if no amount is provided.
    const solAmount = amount || 2;

    // WHY: Convert SOL to lamports because the RPC works in lamports.
    const lamports = solAmount * LAMPORTS_PER_SOL;

    // WHY: Request the airdrop from devnet's faucet.
    const signature = await connection.requestAirdrop(pubkey, lamports);

    // WHY: Wait for confirmation so the client knows the funds are spendable.
    await connection.confirmTransaction(signature, 'confirmed');

    // WHY: Return the signature so the client can view it on a block explorer.
    return res.json({
      success: true,
      signature,
      amount: solAmount,
      address: pubkey.toString(),
    });
  } catch (error: any) {
    // WHY: Catch any RPC or network errors and return them clearly.
    return res.status(500).json({ error: error.message || 'Airdrop failed' });
  }
});

// ============================================================================
// GET /balance/:address
// ============================================================================
// WHY: Before sending a transaction, you must know if the sender has
// enough funds. This endpoint exposes balance queries over HTTP.
app.get('/balance/:address', async (req, res) => {
  try {
    // WHY: Parse the route parameter into a PublicKey object.
    const pubkey = new PublicKey(req.params.address);

    // WHY: Query the balance from the RPC node.
    const balance = await connection.getBalance(pubkey);

    // WHY: Return both lamports and SOL for developer convenience.
    return res.json({
      address: pubkey.toString(),
      balanceLamports: balance,
      balanceSOL: balance / LAMPORTS_PER_SOL,
    });
  } catch (error: any) {
    // WHY: Handle invalid addresses or RPC failures gracefully.
    return res.status(400).json({ error: error.message || 'Invalid address' });
  }
});

// ============================================================================
// POST /transfer
// ============================================================================
// WHY: This is the core endpoint. It constructs a transaction containing
// a single transfer instruction, signs it, and broadcasts it to the network.
app.post('/transfer', async (req, res) => {
  try {
    // WHY: Read sender secret key, recipient address, and amount from body.
    const { fromSecretKey, toAddress, amountSOL } = req.body;

    // WHY: Reconstruct the sender's Keypair from the base58 secret key.
    const fromKeypair = Keypair.fromSecretKey(Buffer.from(fromSecretKey, 'base58'));

    // WHY: Parse the recipient address into a PublicKey.
    const toPubkey = new PublicKey(toAddress);

    // WHY: Convert the human-friendly SOL amount to lamports.
    const lamports = (amountSOL || 0.1) * LAMPORTS_PER_SOL;

    // WHY: Fetch a recent blockhash to include in the transaction.
    // Without this, the transaction would be invalid or replayable.
    const { blockhash } = await connection.getLatestBlockhash('confirmed');

    // WHY: Build a new Transaction object.
    const transaction = new Transaction();

    // WHY: Attach a transfer instruction that moves lamports from sender to recipient.
    transaction.add(
      SystemProgram.transfer({
        fromPubkey: fromKeypair.publicKey,
        toPubkey: toPubkey,
        lamports,
      })
    );

    // WHY: Set the recent blockhash so validators know this transaction is current.
    transaction.recentBlockhash = blockhash;

    // WHY: Set the fee payer. Usually the sender pays the transaction fee.
    transaction.feePayer = fromKeypair.publicKey;

    // WHY: Sign the transaction with the sender's private key.
    // Unsigned transactions are rejected by the network.
    transaction.sign(fromKeypair);

    // WHY: Serialize the signed transaction into raw bytes for transmission.
    const rawTransaction = transaction.serialize();

    // WHY: Send the raw transaction and wait for confirmation.
    const signature = await connection.sendRawTransaction(rawTransaction);

    // WHY: Cache the pending status so the /status endpoint can report it.
    txCache.set(signature, { status: 'pending' });

    // WHY: Start a background confirmation monitor without blocking the response.
    connection.confirmTransaction(signature, 'confirmed').then((result) => {
      if (result.value.err) {
        txCache.set(signature, { status: 'failed', err: result.value.err });
      } else {
        txCache.set(signature, { status: 'confirmed', slot: result.context?.slot });
      }
    }).catch((err) => {
      txCache.set(signature, { status: 'error', err: err.message });
    });

    // WHY: Return the signature immediately so the client can track progress.
    return res.json({
      success: true,
      signature,
      from: fromKeypair.publicKey.toString(),
      to: toPubkey.toString(),
      amountSOL: amountSOL || 0.1,
      explorerUrl: `https://explorer.solana.com/tx/${signature}?cluster=devnet`,
    });
  } catch (error: any) {
    // WHY: Return detailed error information so developers can debug.
    return res.status(500).json({ error: error.message || 'Transfer failed' });
  }
});

// ============================================================================
// GET /status/:signature
// ============================================================================
// WHY: Clients need to poll for confirmation after submission.
// This endpoint checks both the local cache and the RPC node.
app.get('/status/:signature', async (req, res) => {
  try {
    // WHY: Read the transaction signature from the URL.
    const { signature } = req.params;

    // WHY: Check the local cache first for fast responses.
    const cached = txCache.get(signature);
    if (cached && cached.status !== 'pending') {
      return res.json({ signature, ...cached });
    }

    // WHY: If not cached or still pending, query the RPC node directly.
    const status = await connection.getSignatureStatus(signature);

    // WHY: Build a consistent response shape regardless of source.
    const response: any = { signature };

    if (status.value) {
      // WHY: Map the on-chain confirmation status to a simple string.
      if (status.value.err) {
        response.status = 'failed';
        response.err = status.value.err;
      } else if (status.value.confirmationStatus === 'finalized') {
        response.status = 'finalized';
        response.slot = status.value.slot;
      } else if (status.value.confirmationStatus === 'confirmed') {
        response.status = 'confirmed';
        response.slot = status.value.slot;
      } else {
        response.status = 'processed';
        response.slot = status.value.slot;
      }
    } else {
      // WHY: If the RPC has never seen it, report it as not found.
      response.status = 'not_found';
    }

    // WHY: Update the cache with the latest status.
    txCache.set(signature, response);

    return res.json(response);
  } catch (error: any) {
    return res.status(500).json({ error: error.message || 'Status check failed' });
  }
});

// ============================================================================
// GET /recent-blockhash
// ============================================================================
// WHY: Advanced clients may want to build transactions locally.
// This endpoint provides a fresh blockhash for them to use.
app.get('/recent-blockhash', async (_req, res) => {
  try {
    // WHY: Fetch the latest blockhash from the RPC node.
    const { blockhash, lastValidBlockHeight } = await connection.getLatestBlockhash('confirmed');

    // WHY: Return both the blockhash and its expiration height.
    return res.json({ blockhash, lastValidBlockHeight });
  } catch (error: any) {
    return res.status(500).json({ error: error.message || 'Failed to get blockhash' });
  }
});

// ============================================================================
// START SERVER
// ============================================================================
// WHY: Bind to port 3006 to match the phase number and avoid collisions.
const PORT = 3006;
app.listen(PORT, () => {
  console.log(`Phase 6 Transaction API running on http://localhost:${PORT}`);
  console.log('Endpoints:');
  console.log(`  POST http://localhost:${PORT}/airdrop`);
  console.log(`  GET  http://localhost:${PORT}/balance/:address`);
  console.log(`  POST http://localhost:${PORT}/transfer`);
  console.log(`  GET  http://localhost:${PORT}/status/:signature`);
  console.log(`  GET  http://localhost:${PORT}/recent-blockhash`);
});
