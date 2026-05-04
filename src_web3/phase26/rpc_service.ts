import express, { Request, Response } from 'express';
import { Connection, PublicKey, LAMPORTS_PER_SOL } from '@solana/web3.js';

/**
 * Phase 26: Custom RPC API Service
 *
 * Production-ready API that wraps Solana RPC with:
 * - Caching for frequently requested data
 * - Rate limiting
 * - Request batching
 * - Response formatting
 * - Error handling
 *
 * Run: npx ts-node src_web3/phase26/rpc_service.ts
 */

const app = express(); // Create the Express application to handle HTTP requests
app.use(express.json()); // Parse incoming JSON bodies so routes can read req.body

const PORT = 3007; // Use a fixed port so clients know where to connect

// ============================================================================
// CONFIGURATION
// ============================================================================
const RPC_URL = process.env.SOLANA_RPC || 'https://api.devnet.solana.com'; // Allow environment override so production can point to mainnet
const connection = new Connection(RPC_URL, 'confirmed'); // 'confirmed' commitment balances speed with finality for most reads

// Simple in-memory cache
const cache = new Map<string, { data: any; timestamp: number }>(); // Store results with timestamps so we know when they expire
const CACHE_TTL = 5000; // 5 seconds: balances change every slot but users rarely need millisecond precision

// Rate limiting
const requestCounts = new Map<string, { count: number; resetTime: number }>(); // Track per-client request counts to enforce fairness
const RATE_LIMIT = 100; // 100 requests per minute covers normal dashboard polling without allowing abuse
const RATE_WINDOW = 60000; // 1 minute in milliseconds so limits reset on a sensible interval

// ============================================================================
// MIDDLEWARE
// ============================================================================

// Rate limiting middleware
app.use((req: Request, res: Response, next: Function) => {
    const clientId = req.ip || 'unknown'; // Identify the caller so we can track usage per client
    const now = Date.now(); // Capture current time to compare against the client's window

    let clientData = requestCounts.get(clientId); // Look up whether this client has an active tracking entry
    if (!clientData || now > clientData.resetTime) {
        clientData = { count: 0, resetTime: now + RATE_WINDOW }; // Reset count for a new window or new client
        requestCounts.set(clientId, clientData); // Store the fresh tracking record
    }

    clientData.count++; // Increment the count because this request counts against the limit

    if (clientData.count > RATE_LIMIT) {
        return res.status(429).json({ // HTTP 429 tells the client they are sending too many requests
            error: 'Rate limit exceeded',
            limit: RATE_LIMIT,
            window: '1 minute',
            retryAfter: Math.ceil((clientData.resetTime - now) / 1000), // Help the client know when to retry
        });
    }

    next(); // Allow the request to proceed to the next middleware or route handler
});

// Request timing middleware
app.use((req: Request, res: Response, next: Function) => {
    const start = Date.now(); // Record start time so we can measure how long the request takes
    res.on('finish', () => {
        const duration = Date.now() - start; // Calculate duration after response is fully sent
        console.log(`[${new Date().toISOString()}] ${req.method} ${req.path} - ${res.statusCode} (${duration}ms)`); // Log for observability and debugging slow endpoints
    });
    next(); // Continue processing so the actual route handler executes
});

// ============================================================================
// CACHE HELPERS
// ============================================================================

function getCached(key: string): any | null {
    const cached = cache.get(key); // Retrieve the stored entry if it exists
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
        return cached.data; // Return cached data only if it has not expired
    }
    return null; // Signal a cache miss so the caller knows to fetch fresh data
}

function setCached(key: string, data: any): void {
    cache.set(key, { data, timestamp: Date.now() }); // Store the result with the current time so TTL checks work
}

// ============================================================================
// ROUTES
// ============================================================================

app.get('/health', async (_req: Request, res: Response) => {
    try {
        const slot = await connection.getSlot(); // Verify RPC connectivity by asking for the latest slot
        res.json({
            status: 'healthy',
            rpc: RPC_URL,
            slot,
            uptime: process.uptime(), // Show how long the server has been running for monitoring
            cacheSize: cache.size, // Expose cache size so operators can tune memory usage
        });
    } catch (error) {
        res.status(503).json({ status: 'unhealthy', error: String(error) }); // 503 signals the service is temporarily unable to handle requests
    }
});

/**
 * GET /api/v1/balance/:pubkey
 * Get account balance with caching
 */
app.get('/api/v1/balance/:pubkey', async (req: Request, res: Response) => {
    try {
        const { pubkey } = req.params; // Extract the public key from the URL path
        const cacheKey = `balance_${pubkey}`; // Build a unique cache key so balances for different accounts do not collide

        const cached = getCached(cacheKey); // Check if we recently fetched this balance
        if (cached) {
            return res.json({ ...cached, cached: true }); // Return cached result immediately to save an RPC call
        }

        const publicKey = new PublicKey(pubkey); // Parse the string into a Solana PublicKey object
        const balance = await connection.getBalance(publicKey); // Query the blockchain for the current lamport balance

        const result = {
            pubkey,
            balance,
            sol: balance / LAMPORTS_PER_SOL, // Convert lamports to SOL so humans can read the value
            timestamp: new Date().toISOString(), // Include a timestamp so clients know when the data was fetched
        };

        setCached(cacheKey, result); // Store the result so the next identical request is instant
        res.json({ ...result, cached: false }); // Indicate this was a fresh fetch, not a cache hit
    } catch (error) {
        res.status(400).json({ error: `Invalid pubkey or RPC error: ${error}` }); // 400 means the client sent bad input
    }
});

/**
 * GET /api/v1/account/:pubkey
 * Get full account info
 */
app.get('/api/v1/account/:pubkey', async (req: Request, res: Response) => {
    try {
        const { pubkey } = req.params; // Read the account public key from the URL
        const publicKey = new PublicKey(pubkey); // Convert the string to a validated PublicKey
        const account = await connection.getAccountInfo(publicKey); // Fetch the full account structure from the chain

        if (!account) {
            return res.status(404).json({ error: 'Account not found' }); // Return 404 when the account does not exist on-chain
        }

        res.json({
            pubkey,
            lamports: account.lamports, // Raw balance in lamports for precision
            sol: account.lamports / LAMPORTS_PER_SOL, // Human-readable SOL amount
            owner: account.owner.toString(), // Program that owns this account, important for understanding account type
            executable: account.executable, // True for programs, false for user accounts
            rentEpoch: account.rentEpoch, // Metadata for rent exemption tracking
            dataSize: account.data.length, // Size of account data in bytes
            timestamp: new Date().toISOString(), // When this snapshot was taken
        });
    } catch (error) {
        res.status(400).json({ error: String(error) }); // Surface the error so the client can handle it
    }
});

/**
 * GET /api/v1/block/latest
 * Get latest block info
 */
app.get('/api/v1/block/latest', async (_req: Request, res: Response) => {
    try {
        const cacheKey = 'latest_block'; // Use a fixed key because there is only one latest block
        const cached = getCached(cacheKey); // Check cache to avoid repeated blockhash fetches
        if (cached) {
            return res.json({ ...cached, cached: true }); // Serve cached block info when available
        }

        const slot = await connection.getSlot(); // Ask the RPC for the current slot number
        const blockhash = await connection.getLatestBlockhash(); // Get a recent blockhash for transaction construction

        const result = {
            slot,
            blockhash: blockhash.blockhash, // The hash clients need to include in transactions
            lastValidBlockHeight: blockhash.lastValidBlockHeight, // Deadline after which the blockhash expires
            timestamp: new Date().toISOString(),
        };

        setCached(cacheKey, result); // Cache briefly because blockhashes expire quickly
        res.json({ ...result, cached: false });
    } catch (error) {
        res.status(500).json({ error: String(error) }); // 500 signals a server-side RPC failure
    }
});

/**
 * GET /api/v1/supply
 * Get token supply
 */
app.get('/api/v1/supply', async (_req: Request, res: Response) => {
    try {
        const cacheKey = 'supply'; // Single key because there is one network supply
        const cached = getCached(cacheKey); // Reuse recent supply data since it changes slowly
        if (cached) {
            return res.json({ ...cached, cached: true });
        }

        const supply = await connection.getSupply(); // Query total and circulating SOL supply

        const result = {
            total: supply.value.total / LAMPORTS_PER_SOL, // Convert from lamports to SOL for readability
            circulating: supply.value.circulating / LAMPORTS_PER_SOL,
            nonCirculating: supply.value.nonCirculating / LAMPORTS_PER_SOL,
            timestamp: new Date().toISOString(),
        };

        setCached(cacheKey, result); // Cache for longer because supply rarely changes
        res.json({ ...result, cached: false });
    } catch (error) {
        res.status(500).json({ error: String(error) });
    }
});

/**
 * POST /api/v1/batch
 * Batch multiple requests
 */
app.post('/api/v1/batch', async (req: Request, res: Response) => {
    try {
        const { requests } = req.body; // Expect an array of sub-requests in the body

        if (!Array.isArray(requests) || requests.length > 10) {
            return res.status(400).json({ error: 'Max 10 requests per batch' }); // Limit batch size to prevent resource exhaustion
        }

        const results = await Promise.all(
            requests.map(async (request: any) => {
                const { method, params } = request; // Destructure each sub-request into method name and parameters

                switch (method) {
                    case 'getBalance':
                        try {
                            const balance = await connection.getBalance(new PublicKey(params.pubkey)); // Fetch balance for the given pubkey
                            return { method, success: true, result: { balance, sol: balance / LAMPORTS_PER_SOL } }; // Normalize result shape
                        } catch (e) {
                            return { method, success: false, error: String(e) }; // Capture errors per sub-request so one failure does not kill the batch
                        }
                    case 'getSlot':
                        try {
                            const slot = await connection.getSlot(); // Fetch current slot
                            return { method, success: true, result: { slot } };
                        } catch (e) {
                            return { method, success: false, error: String(e) };
                        }
                    case 'getBlockHeight':
                        try {
                            const height = await connection.getBlockHeight(); // Fetch current block height
                            return { method, success: true, result: { height } };
                        } catch (e) {
                            return { method, success: false, error: String(e) };
                        }
                    default:
                        return { method, success: false, error: 'Unknown method' }; // Reject unsupported methods gracefully
                }
            })
        );

        res.json({
            batchSize: requests.length, // Include metadata so clients can verify all requests were processed
            results,
        });
    } catch (error) {
        res.status(500).json({ error: String(error) });
    }
});

/**
 * GET /api/v1/cache/stats
 * Cache statistics
 */
app.get('/api/v1/cache/stats', (_req: Request, res: Response) => {
    const stats = Array.from(cache.entries()).map(([key, value]) => ({
        key,
        age: Date.now() - value.timestamp, // How old each entry is in milliseconds
        expired: Date.now() - value.timestamp > CACHE_TTL, // Whether the entry is past its TTL
    }));

    res.json({
        cacheSize: cache.size, // Total number of cached entries
        ttl: CACHE_TTL, // Current TTL setting for transparency
        entries: stats, // Detailed per-entry status for debugging
    });
});

/**
 * POST /api/v1/cache/clear
 * Clear cache
 */
app.post('/api/v1/cache/clear', (_req: Request, res: Response) => {
    cache.clear(); // Remove all entries to force fresh fetches, useful after configuration changes
    res.json({ success: true, message: 'Cache cleared' });
});

app.listen(PORT, () => {
    console.log(`=== Phase 26: Custom RPC API Service ===`);
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`Connected to: ${RPC_URL}`);
    console.log(`\nFeatures:`);
    console.log(`  - Caching (5s TTL)`);
    console.log(`  - Rate limiting (100 req/min)`);
    console.log(`  - Request batching`);
    console.log(`  - Request timing`);
    console.log(`\nEndpoints:`);
    console.log(`  GET  /api/v1/balance/:pubkey`);
    console.log(`  GET  /api/v1/account/:pubkey`);
    console.log(`  GET  /api/v1/block/latest`);
    console.log(`  GET  /api/v1/supply`);
    console.log(`  POST /api/v1/batch`);
    console.log(`  GET  /api/v1/cache/stats`);
    console.log(`  POST /api/v1/cache/clear`);
});
