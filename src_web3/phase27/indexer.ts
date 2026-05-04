import express, { Request, Response } from 'express';
import { Connection, PublicKey, ParsedTransactionWithMeta } from '@solana/web3.js';

/**
 * Phase 27: Indexing On-Chain Data
 *
 * Express API that demonstrates blockchain indexing:
 * - Polls Solana for new blocks and transactions
 * - Parses events from transaction logs
 * - Syncs parsed data to PostgreSQL schema (simulated with in-memory store)
 * - Provides REST endpoints for querying indexed history
 *
 * Run: npx ts-node src_web3/phase27/indexer.ts
 */

const app = express(); // Create the Express server to serve indexed data over HTTP
app.use(express.json()); // Parse JSON bodies so clients can send filter parameters

const PORT = 3009; // Unique port so this service runs alongside the RPC and webhook services

// ============================================================================
// CONFIGURATION
// ============================================================================
const RPC_URL = process.env.SOLANA_RPC || 'https://api.devnet.solana.com'; // Allow environment override for mainnet indexing
const connection = new Connection(RPC_URL, 'confirmed'); // Use confirmed commitment so indexed data reflects finalized state

const POLL_INTERVAL_MS = 5000; // Poll every 5 seconds to balance freshness with RPC quota usage

// ============================================================================
// TYPES
// ============================================================================
interface IndexedEvent {
    id: string; // Unique identifier for deduplication and lookups
    signature: string; // Transaction signature so users can verify on-chain
    slot: number; // Block slot for chronological ordering and reorg handling
    blockTime: number | null; // Unix timestamp for human-readable dates
    programId: string; // Which program emitted this event
    eventType: string; // Parsed event category like Transfer or Swap
    data: any; // Flexible structure to hold parsed event fields
    indexedAt: number; // When this record was written to the index
}

interface SyncCursor {
    id: string; // Single-row identifier since there is only one indexer cursor
    lastSlot: number; // The highest slot we have successfully processed
    updatedAt: number; // Timestamp for monitoring sync health
}

// ============================================================================
// SIMULATED DATABASE (replace with PostgreSQL in production)
// ============================================================================
const eventsDB: IndexedEvent[] = []; // In-memory array simulating a PostgreSQL events table
const syncCursor: SyncCursor = {
    id: 'main',
    lastSlot: 0, // Start from 0 so the first poll begins from the chain's current state
    updatedAt: Date.now(),
};

// ============================================================================
// EVENT PARSER
// ============================================================================

/**
 * Parse raw transaction logs to extract structured events.
 * In production this uses program IDLs. Here we simulate common patterns.
 */
function parseEvent(tx: ParsedTransactionWithMeta, signature: string): IndexedEvent[] {
    const results: IndexedEvent[] = []; // Collect all events found in this transaction
    const slot = tx.slot; // All events in a transaction share the same slot
    const blockTime = tx.blockTime; // All events share the same block timestamp

    if (!tx.meta || !tx.meta.logMessages) {
        return results; // Skip transactions with no logs since there is nothing to parse
    }

    for (const log of tx.meta.logMessages) {
        if (log.includes('Transfer')) {
            // Simulate parsing a transfer event from program logs
            const match = log.match(/Transfer (\d+) from (\S+) to (\S+)/); // Extract amount and addresses with regex
            if (match) {
                results.push({
                    id: `${signature}_transfer_${results.length}`, // Build a unique ID combining signature and index
                    signature,
                    slot,
                    blockTime,
                    programId: tx.transaction.message.accountKeys[0]?.pubkey.toString() || 'unknown', // Use the fee payer as a proxy for the program context
                    eventType: 'Transfer',
                    data: {
                        amount: parseInt(match[1], 10), // Convert matched string to integer
                        from: match[2], // Capture source address
                        to: match[3], // Capture destination address
                    },
                    indexedAt: Date.now(),
                });
            }
        }

        if (log.includes('Mint')) {
            const match = log.match(/Mint (\d+) to (\S+)/);
            if (match) {
                results.push({
                    id: `${signature}_mint_${results.length}`,
                    signature,
                    slot,
                    blockTime,
                    programId: tx.transaction.message.accountKeys[0]?.pubkey.toString() || 'unknown',
                    eventType: 'Mint',
                    data: {
                        amount: parseInt(match[1], 10),
                        to: match[2],
                    },
                    indexedAt: Date.now(),
                });
            }
        }

        if (log.includes('Swap')) {
            const match = log.match(/Swap (\d+) (\S+) for (\d+) (\S+)/);
            if (match) {
                results.push({
                    id: `${signature}_swap_${results.length}`,
                    signature,
                    slot,
                    blockTime,
                    programId: tx.transaction.message.accountKeys[0]?.pubkey.toString() || 'unknown',
                    eventType: 'Swap',
                    data: {
                        amountIn: parseInt(match[1], 10),
                        tokenIn: match[2],
                        amountOut: parseInt(match[3], 10),
                        tokenOut: match[4],
                    },
                    indexedAt: Date.now(),
                });
            }
        }
    }

    return results; // Return all parsed events for this transaction
}

/**
 * Decode a specific transfer instruction from parsed transaction data.
 */
function decodeTransfer(tx: ParsedTransactionWithMeta): { from: string; to: string; amount: number } | null {
    if (!tx.meta) return null; // Cannot decode without transaction metadata

    const instructions = tx.transaction.message.instructions; // Access the top-level instructions
    for (const ix of instructions) {
        if ('parsed' in ix && ix.parsed.type === 'transfer') {
            return {
                from: ix.parsed.info.source, // Source account from the parsed instruction
                to: ix.parsed.info.destination, // Destination account from the parsed instruction
                amount: parseInt(ix.parsed.info.lamports, 10), // Amount in lamports
            };
        }
    }
    return null; // Return null if no transfer instruction is found
}

// ============================================================================
// DATABASE SYNC
// ============================================================================

/**
 * Write events to the database with idempotency checks.
 */
function syncEvents(events: IndexedEvent[]): void {
    for (const event of events) {
        const exists = eventsDB.find(e => e.id === event.id); // Check for duplicates using the unique event ID
        if (!exists) {
            eventsDB.push(event); // Insert only new events to maintain idempotency
        }
    }
}

/**
 * Update the sync cursor so the indexer knows where to resume after a restart.
 */
function updateCursor(slot: number): void {
    syncCursor.lastSlot = slot; // Persist the highest processed slot
    syncCursor.updatedAt = Date.now(); // Record the update time for health monitoring
}

// ============================================================================
// INDEXING LOOP
// ============================================================================

async function indexNewBlocks(): Promise<void> {
    try {
        const currentSlot = await connection.getSlot(); // Ask the RPC for the latest finalized slot
        const startSlot = syncCursor.lastSlot > 0 ? syncCursor.lastSlot + 1 : currentSlot - 10; // If starting fresh, index the last 10 blocks

        if (startSlot > currentSlot) {
            return; // Nothing new to index, so skip the rest of this cycle
        }

        console.log(`[Indexer] Processing slots ${startSlot} to ${currentSlot}`); // Log progress so operators can see activity

        for (let slot = startSlot; slot <= currentSlot; slot++) {
            try {
                const block = await connection.getBlock(slot, {
                    maxSupportedTransactionVersion: 0, // Request version 0 transactions for compatibility
                });

                if (!block) {
                    continue; // Skip empty slots since there are no transactions to index
                }

                for (const tx of block.transactions) {
                    const signature = tx.transaction.signatures[0]; // Use the first signature as the transaction identifier
                    if (!signature) continue; // Skip malformed transactions without signatures

                    const events = parseEvent(tx as ParsedTransactionWithMeta, signature); // Extract structured events from logs
                    if (events.length > 0) {
                        syncEvents(events); // Persist events to the database
                    }

                    const transfer = decodeTransfer(tx as ParsedTransactionWithMeta); // Also decode direct transfer instructions
                    if (transfer) {
                        syncEvents([{
                            id: `${signature}_transfer_decoded`,
                            signature,
                            slot,
                            blockTime: block.blockTime,
                            programId: 'system',
                            eventType: 'TransferDecoded',
                            data: transfer,
                            indexedAt: Date.now(),
                        }]);
                    }
                }

                updateCursor(slot); // Advance the cursor after successfully processing this slot
            } catch (err) {
                console.error(`[Indexer] Error processing slot ${slot}:`, err); // Log errors but continue so one bad slot does not stall everything
            }
        }
    } catch (error) {
        console.error('[Indexer] Polling error:', error); // Catch top-level errors to keep the loop alive
    }
}

// Start the indexing loop
setInterval(indexNewBlocks, POLL_INTERVAL_MS); // Poll on a fixed interval for simplicity; production uses Geyser or websockets

// ============================================================================
// API ROUTES
// ============================================================================

app.get('/health', (_req: Request, res: Response) => {
    res.json({
        status: 'healthy',
        lastIndexedSlot: syncCursor.lastSlot, // Expose sync progress for monitoring dashboards
        totalEvents: eventsDB.length, // Show how much data has been collected
        rpc: RPC_URL,
    });
});

/**
 * GET /events
 * Query indexed events with filters
 */
app.get('/events', (req: Request, res: Response) => {
    const { account, eventType, programId, limit = '50' } = req.query; // Read filter parameters from the query string
    let results = [...eventsDB]; // Copy the array so filters do not mutate the original database

    if (account) {
        results = results.filter(e =>
            JSON.stringify(e.data).includes(account as string) // Simple string search across event data for the account
        );
    }

    if (eventType) {
        results = results.filter(e => e.eventType === eventType); // Exact match on event type
    }

    if (programId) {
        results = results.filter(e => e.programId === programId); // Exact match on program ID
    }

    const limitNum = parseInt(limit as string, 10); // Convert the limit parameter to a number
    results = results.slice(-limitNum); // Return the most recent N events since newer data is usually more relevant

    res.json({
        count: results.length,
        filters: { account, eventType, programId }, // Echo filters back so clients know what was applied
        events: results,
    });
});

/**
 * GET /events/:id
 * Get a single event by ID
 */
app.get('/events/:id', (req: Request, res: Response) => {
    const event = eventsDB.find(e => e.id === req.params.id); // Lookup by primary key equivalent
    if (!event) {
        return res.status(404).json({ error: 'Event not found' });
    }
    res.json({ event });
});

/**
 * GET /accounts/:pubkey/history
 * Get all events related to an account
 */
app.get('/accounts/:pubkey/history', (req: Request, res: Response) => {
    const pubkey = req.params.pubkey; // Extract the account public key from the URL
    const history = eventsDB.filter(e =>
        JSON.stringify(e.data).includes(pubkey) // Search all event data fields for references to this account
    );

    res.json({
        account: pubkey,
        count: history.length,
        history: history.slice(-100), // Limit to the last 100 events to keep responses fast
    });
});

/**
 * GET /stats
 * Indexer statistics
 */
app.get('/stats', (_req: Request, res: Response) => {
    const eventTypes: Record<string, number> = {}; // Build a frequency map of event types
    for (const e of eventsDB) {
        eventTypes[e.eventType] = (eventTypes[e.eventType] || 0) + 1; // Increment count for this event type
    }

    res.json({
        totalEvents: eventsDB.length,
        lastSlot: syncCursor.lastSlot,
        eventTypeBreakdown: eventTypes, // Show distribution so operators understand what the chain is doing
        oldestEvent: eventsDB.length > 0 ? eventsDB[0].indexedAt : null, // First indexed timestamp
        newestEvent: eventsDB.length > 0 ? eventsDB[eventsDB.length - 1].indexedAt : null, // Latest indexed timestamp
    });
});

app.listen(PORT, () => {
    console.log(`=== Phase 27: Indexing On-Chain Data ===`);
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`Connected to: ${RPC_URL}`);
    console.log(`\nEndpoints:`);
    console.log(`  GET  /events              - Query indexed events with filters`);
    console.log(`  GET  /events/:id          - Get single event`);
    console.log(`  GET  /accounts/:pubkey/history - Account history`);
    console.log(`  GET  /stats               - Indexer statistics`);
    console.log(`\nPolling every ${POLL_INTERVAL_MS}ms for new blocks`);
});
