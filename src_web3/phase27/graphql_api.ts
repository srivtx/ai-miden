import express, { Request, Response } from 'express';
import { graphqlHTTP } from 'express-graphql';
import { buildSchema } from 'graphql';

/**
 * Phase 27: GraphQL API for Indexed Data
 *
 * Serves indexed blockchain data through a GraphQL interface:
 * - Clients request exactly the fields they need
 * - Single endpoint replaces multiple REST endpoints
 * - Supports filtering, pagination, and nested queries
 *
 * Run: npx ts-node src_web3/phase27/graphql_api.ts
 */

const app = express(); // Initialize Express to handle HTTP requests
app.use(express.json()); // Parse JSON bodies for any non-GraphQL routes

const PORT = 3010; // Unique port so this runs alongside the indexer REST API

// ============================================================================
// SIMULATED INDEXED DATA STORE
// ============================================================================
interface IndexedEvent {
    id: string; // Primary key for lookups
    signature: string; // Transaction signature for on-chain verification
    slot: number; // Block slot for chronological queries
    blockTime: number; // Unix timestamp for date filtering
    programId: string; // Program that emitted the event
    eventType: string; // Category like Transfer, Mint, or Swap
    data: any; // Parsed event payload
}

// Seed with simulated data so the GraphQL API has content to serve
const eventsDB: IndexedEvent[] = [
    {
        id: 'evt_001',
        signature: '5x...abc',
        slot: 250000000,
        blockTime: 1700000000,
        programId: 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',
        eventType: 'Transfer',
        data: { amount: 1000000, from: 'Alice', to: 'Bob' },
    },
    {
        id: 'evt_002',
        signature: '3y...def',
        slot: 250000001,
        blockTime: 1700000010,
        programId: 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',
        eventType: 'Transfer',
        data: { amount: 500000, from: 'Bob', to: 'Carol' },
    },
    {
        id: 'evt_003',
        signature: '9z...ghi',
        slot: 250000002,
        blockTime: 1700000020,
        programId: 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4',
        eventType: 'Swap',
        data: { amountIn: 2000000, tokenIn: 'SOL', amountOut: 1800000, tokenOut: 'USDC' },
    },
    {
        id: 'evt_004',
        signature: '1a...jkl',
        slot: 250000003,
        blockTime: 1700000030,
        programId: 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',
        eventType: 'Mint',
        data: { amount: 10000000, to: 'Alice' },
    },
];

// ============================================================================
// GRAPHQL SCHEMA
// ============================================================================

const schema = buildSchema(`
    type Event {
        id: String!
        signature: String!
        slot: Int!
        blockTime: Int!
        programId: String!
        eventType: String!
        data: EventData!
    }

    type EventData {
        amount: Int
        amountIn: Int
        amountOut: Int
        tokenIn: String
        tokenOut: String
        from: String
        to: String
    }

    type Query {
        events(eventType: String, programId: String, limit: Int): [Event!]!
        event(id: String!): Event
        eventsByAccount(account: String!, limit: Int): [Event!]!
        stats: IndexerStats!
    }

    type IndexerStats {
        totalEvents: Int!
        eventTypes: [String!]!
        programs: [String!]!
    }
`); // Define the schema so clients know what queries and types are available

// ============================================================================
// RESOLVERS
// ============================================================================

const root = {
    events: (args: { eventType?: string; programId?: string; limit?: number }) => {
        let results = [...eventsDB]; // Copy the array to avoid mutating the source data during filtering

        if (args.eventType) {
            results = results.filter(e => e.eventType === args.eventType); // Filter by exact event type match
        }

        if (args.programId) {
            results = results.filter(e => e.programId === args.programId); // Filter by exact program ID match
        }

        const limit = args.limit || 50; // Default to 50 events to keep response sizes reasonable
        return results.slice(-limit); // Return the most recent events since newer data is usually more relevant
    },

    event: (args: { id: string }) => {
        return eventsDB.find(e => e.id === args.id) || null; // Return the matching event or null if not found
    },

    eventsByAccount: (args: { account: string; limit?: number }) => {
        const results = eventsDB.filter(e =>
            JSON.stringify(e.data).includes(args.account) // Search all event data for references to the requested account
        );
        const limit = args.limit || 50;
        return results.slice(-limit);
    },

    stats: () => {
        const eventTypes = Array.from(new Set(eventsDB.map(e => e.eventType))); // Deduplicate event types for the stats view
        const programs = Array.from(new Set(eventsDB.map(e => e.programId))); // Deduplicate program IDs
        return {
            totalEvents: eventsDB.length, // Total count for dashboard summaries
            eventTypes,
            programs,
        };
    },
};

// ============================================================================
// MIDDLEWARE AND ROUTES
// ============================================================================

app.use('/graphql', graphqlHTTP({
    schema: schema, // Attach the schema so GraphQL validates queries against it
    rootValue: root, // Attach resolvers so GraphQL knows how to fetch data for each field
    graphiql: true, // Enable GraphiQL interface so developers can explore the API in a browser
}));

/**
 * GET /health
 * Health check for load balancers
 */
app.get('/health', (_req: Request, res: Response) => {
    res.json({
        status: 'healthy',
        endpoint: '/graphql',
        totalEvents: eventsDB.length, // Include data volume in health checks for monitoring
    });
});

/**
 * GET /schema
 * Return the schema as text for client generation tools
 */
app.get('/schema', (_req: Request, res: Response) => {
    res.type('text/plain').send(schema.toString()); // Expose the schema so frontend tools can generate types automatically
});

app.listen(PORT, () => {
    console.log(`=== Phase 27: GraphQL API for Indexed Data ===`);
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`GraphiQL available at http://localhost:${PORT}/graphql`);
    console.log(`\nExample queries:`);
    console.log(`  { events(eventType: "Transfer", limit: 10) { id signature data { amount from to } } }`);
    console.log(`  { event(id: "evt_001") { slot programId data } }`);
    console.log(`  { eventsByAccount(account: "Alice") { id eventType data } }`);
    console.log(`  { stats { totalEvents eventTypes programs } }`);
});
