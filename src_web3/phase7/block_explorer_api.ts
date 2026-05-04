import express from 'express';
import cors from 'cors';
import {
  Connection,
  PublicKey,
  LAMPORTS_PER_SOL,
} from '@solana/web3.js';

/**
 * Phase 7: Block Explorer API
 *
 * This Express server wraps Solana RPC calls with an in-memory cache
 * and exposes them as developer-friendly REST endpoints. It demonstrates:
 * 1. Caching RPC responses to reduce rate-limit usage and latency
 * 2. Formatting raw blockchain data into human-readable JSON
 * 3. Supporting commitment level as a query parameter
 */

// WHY: Create the Express application.
const app = express();

// WHY: Parse JSON bodies for POST requests.
app.use(express.json());

// WHY: Allow cross-origin requests from frontend explorers.
app.use(cors());

// WHY: Connect to devnet. In production, you would use a paid RPC endpoint.
const connection = new Connection('https://api.devnet.solana.com', 'confirmed');

// WHY: Simple in-memory cache with TTL (time-to-live) to avoid hammering the RPC.
const cache = new Map<string, { data: any; expiresAt: number }>();
const CACHE_TTL_MS = 5000; // WHY: 5 seconds is short enough to stay fresh but reduces duplicate RPC calls.

// ============================================================================
// Helper: cachedRpcCall
// ============================================================================
// WHY: Deduplicate identical requests made within the TTL window.
async function cachedRpcCall(key: string, fetcher: () => Promise<any>) {
  // WHY: Check if a valid cached entry exists.
  const cached = cache.get(key);
  if (cached && cached.expiresAt > Date.now()) {
    return cached.data;
  }

  // WHY: Cache miss — call the RPC node.
  const data = await fetcher();

  // WHY: Store the result with an expiration timestamp.
  cache.set(key, { data, expiresAt: Date.now() + CACHE_TTL_MS });

  return data;
}

// ============================================================================
// GET /slot
// ============================================================================
// WHY: Frontends need to know the current block height for pagination or freshness checks.
app.get('/slot', async (_req, res) => {
  try {
    // WHY: Use the cache so rapid reloads do not spam the RPC.
    const slot = await cachedRpcCall('slot', () => connection.getSlot());
    return res.json({ slot });
  } catch (error: any) {
    return res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// GET /block-height
// ============================================================================
// WHY: Block height is slightly different from slot; some apps need this specifically.
app.get('/block-height', async (_req, res) => {
  try {
    const height = await cachedRpcCall('blockHeight', () => connection.getBlockHeight());
    return res.json({ blockHeight: height });
  } catch (error: any) {
    return res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// GET /supply
// ============================================================================
// WHY: Tokenomics dashboards and educational tools need to display total supply.
app.get('/supply', async (_req, res) => {
  try {
    const supply = await cachedRpcCall('supply', () => connection.getSupply());
    return res.json({
      total: supply.value.total / LAMPORTS_PER_SOL,
      circulating: supply.value.circulating / LAMPORTS_PER_SOL,
      nonCirculating: supply.value.nonCirculating / LAMPORTS_PER_SOL,
    });
  } catch (error: any) {
    return res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// GET /balance/:address
// ============================================================================
// WHY: This is the most common query. We allow commitment as a query param
// so the client can choose between speed and finality.
app.get('/balance/:address', async (req, res) => {
  try {
    // WHY: Parse the address from the URL route parameter.
    const pubkey = new PublicKey(req.params.address);

    // WHY: Read optional commitment level from query string (?commitment=processed).
    const commitment = (req.query.commitment as any) || 'confirmed';

    // WHY: Build a cache key that includes commitment so different levels do not collide.
    const cacheKey = `balance:${pubkey.toString()}:${commitment}`;

    // WHY: Fetch balance with the requested commitment level.
    const balance = await cachedRpcCall(cacheKey, () =>
      connection.getBalance(pubkey, commitment)
    );

    return res.json({
      address: pubkey.toString(),
      balanceLamports: balance,
      balanceSOL: balance / LAMPORTS_PER_SOL,
      commitment,
    });
  } catch (error: any) {
    return res.status(400).json({ error: error.message || 'Invalid address' });
  }
});

// ============================================================================
// GET /account/:address
// ============================================================================
// WHY: Power users and debuggers need the full account info: owner, executable flag, data size.
app.get('/account/:address', async (req, res) => {
  try {
    const pubkey = new PublicKey(req.params.address);
    const commitment = (req.query.commitment as any) || 'confirmed';
    const cacheKey = `account:${pubkey.toString()}:${commitment}`;

    const accountInfo = await cachedRpcCall(cacheKey, () =>
      connection.getAccountInfo(pubkey, commitment)
    );

    if (!accountInfo) {
      // WHY: Return 404 when the account does not exist on-chain.
      return res.status(404).json({ error: 'Account not found' });
    }

    // WHY: Format the raw account into a friendly JSON shape.
    return res.json({
      address: pubkey.toString(),
      lamports: accountInfo.lamports,
      owner: accountInfo.owner.toString(),
      executable: accountInfo.executable,
      rentEpoch: accountInfo.rentEpoch,
      dataSize: accountInfo.data.length,
      commitment,
    });
  } catch (error: any) {
    return res.status(400).json({ error: error.message || 'Invalid address' });
  }
});

// ============================================================================
// GET /transaction/:signature
// ============================================================================
// WHY: Explorers need to show what happened inside a transaction: instructions, accounts, logs.
app.get('/transaction/:signature', async (req, res) => {
  try {
    const { signature } = req.params;
    const commitment = (req.query.commitment as any) || 'confirmed';
    const cacheKey = `tx:${signature}:${commitment}`;

    // WHY: getParsedTransaction returns human-readable instruction data instead of raw bytes.
    const tx = await cachedRpcCall(cacheKey, () =>
      connection.getParsedTransaction(signature, { commitment: commitment as any, maxSupportedTransactionVersion: 0 })
    );

    if (!tx) {
      return res.status(404).json({ error: 'Transaction not found' });
    }

    // WHY: Extract the most useful fields for a lightweight explorer view.
    return res.json({
      signature,
      slot: tx.slot,
      blockTime: tx.blockTime,
      fee: tx.meta?.fee,
      status: tx.meta?.err ? 'failed' : 'success',
      err: tx.meta?.err,
      // WHY: Show simplified instruction names so the frontend does not need to parse raw data.
      instructions: tx.transaction.message.instructions.map((ix: any) => ({
        programId: ix.programId?.toString?.() || ix.programId,
        // WHY: For parsed instructions, include the friendly type and info.
        parsed: ix.parsed,
        data: ix.data,
      })),
      commitment,
    });
  } catch (error: any) {
    return res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// GET /recent-blockhash
// ============================================================================
// WHY: Clients building their own transactions need a fresh blockhash.
app.get('/recent-blockhash', async (_req, res) => {
  try {
    const blockhash = await cachedRpcCall('blockhash', () => connection.getLatestBlockhash());
    return res.json({
      blockhash: blockhash.blockhash,
      lastValidBlockHeight: blockhash.lastValidBlockHeight,
    });
  } catch (error: any) {
    return res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// GET /epoch
// ============================================================================
// WHY: Staking and governance tools need to know the current epoch and progress.
app.get('/epoch', async (_req, res) => {
  try {
    const epochInfo = await cachedRpcCall('epoch', () => connection.getEpochInfo());
    return res.json({
      epoch: epochInfo.epoch,
      slotIndex: epochInfo.slotIndex,
      slotsInEpoch: epochInfo.slotsInEpoch,
      absoluteSlot: epochInfo.absoluteSlot,
      percentComplete: ((epochInfo.slotIndex / epochInfo.slotsInEpoch) * 100).toFixed(2) + '%',
    });
  } catch (error: any) {
    return res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// START SERVER
// ============================================================================
const PORT = 3007;
app.listen(PORT, () => {
  console.log(`Phase 7 Block Explorer API running on http://localhost:${PORT}`);
  console.log('Endpoints:');
  console.log(`  GET http://localhost:${PORT}/slot`);
  console.log(`  GET http://localhost:${PORT}/block-height`);
  console.log(`  GET http://localhost:${PORT}/supply`);
  console.log(`  GET http://localhost:${PORT}/balance/:address?commitment=confirmed`);
  console.log(`  GET http://localhost:${PORT}/account/:address?commitment=confirmed`);
  console.log(`  GET http://localhost:${PORT}/transaction/:signature`);
  console.log(`  GET http://localhost:${PORT}/recent-blockhash`);
  console.log(`  GET http://localhost:${PORT}/epoch`);
});
