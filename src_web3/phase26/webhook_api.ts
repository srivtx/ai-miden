import express, { Request, Response } from 'express';
import { Connection } from '@solana/web3.js';
import crypto from 'crypto';

/**
 * Phase 26: Webhook API Service
 *
 * Provides event-driven notifications for on-chain events:
 * - Clients register webhooks for specific program addresses or account changes
 * - The service polls the blockchain and POSTs to registered URLs when events match
 * - Includes signature verification so receivers can trust the payload
 *
 * Run: npx ts-node src_web3/phase26/webhook_api.ts
 */

const app = express(); // Initialize Express to handle HTTP requests for webhook registration and delivery
app.use(express.json()); // Enable JSON parsing so webhook payloads and registrations are readable

const PORT = 3008; // Separate port from the RPC service so each service can scale independently

// ============================================================================
// CONFIGURATION
// ============================================================================
const RPC_URL = process.env.SOLANA_RPC || 'https://api.devnet.solana.com'; // Connect to the same RPC as the main service
const connection = new Connection(RPC_URL, 'confirmed'); // Use confirmed commitment so webhooks fire on finalized changes

const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || 'dev-secret-change-in-production'; // Shared secret to sign payloads so receivers verify authenticity

// ============================================================================
// TYPES
// ============================================================================
interface WebhookSubscription {
    id: string; // Unique identifier so clients can manage specific subscriptions
    url: string; // Where to POST event data when a match is found
    account?: string; // Optional filter: only notify when this specific account changes
    programId?: string; // Optional filter: notify for any account owned by this program
    eventType: 'accountChange' | 'programLog' | 'signature'; // What kind of on-chain event to watch
    createdAt: number; // Timestamp for subscription lifecycle tracking
    active: boolean; // Allow pausing without deleting
}

interface WebhookDelivery {
    id: string; // Unique delivery attempt ID for tracing
    subscriptionId: string; // Link back to the subscription that triggered this
    payload: any; // The actual event data sent to the client
    status: 'pending' | 'delivered' | 'failed'; // Track whether the POST succeeded
    attemptedAt: number; // When the delivery was attempted
    responseStatus?: number; // HTTP status from the client's server
}

// ============================================================================
// STORAGE
// ============================================================================
const subscriptions: Map<string, WebhookSubscription> = new Map(); // In-memory store for active webhook registrations
const deliveries: Map<string, WebhookDelivery> = new Map(); // Log of every delivery attempt for debugging and retry logic

// ============================================================================
// HELPERS
// ============================================================================

/**
 * Generate a signature for webhook payloads so receivers can verify the sender.
 */
function signPayload(payload: any): string {
    const hmac = crypto.createHmac('sha256', WEBHOOK_SECRET); // Use HMAC-SHA256 for integrity and authenticity
    hmac.update(JSON.stringify(payload)); // Sign the serialized payload so tampering invalidates the signature
    return hmac.digest('hex'); // Return hex string for easy inclusion in HTTP headers
}

/**
 * Attempt to POST a webhook payload to a subscriber URL.
 */
async function deliverWebhook(subscription: WebhookSubscription, eventData: any): Promise<void> {
    const deliveryId = `dlv_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`; // Generate a unique delivery ID for tracing
    const payload = {
        subscriptionId: subscription.id, // Let the receiver know which subscription triggered this
        eventType: subscription.eventType, // Include the event type so receivers can route internally
        data: eventData, // The actual on-chain event details
        timestamp: new Date().toISOString(), // Precise delivery time for idempotency checks
    };

    const delivery: WebhookDelivery = {
        id: deliveryId,
        subscriptionId: subscription.id,
        payload,
        status: 'pending',
        attemptedAt: Date.now(),
    };
    deliveries.set(deliveryId, delivery); // Record the attempt before sending so failures are logged

    try {
        const signature = signPayload(payload); // Sign the payload so the receiver can verify it came from us

        const response = await fetch(subscription.url, {
            method: 'POST', // POST is the standard method for webhook delivery
            headers: {
                'Content-Type': 'application/json', // Tell the receiver to parse the body as JSON
                'X-Webhook-Signature': signature, // Include signature so the receiver verifies authenticity
                'X-Webhook-ID': deliveryId, // Include delivery ID so the receiver can deduplicate
            },
            body: JSON.stringify(payload), // Serialize the event data for transmission
        });

        delivery.status = response.ok ? 'delivered' : 'failed'; // Mark success only if the receiver responded with 2xx
        delivery.responseStatus = response.status; // Record the exact status for debugging
    } catch (error) {
        delivery.status = 'failed'; // Network errors or DNS failures land here
        console.error(`[Webhook] Delivery failed: ${subscription.url}`, error);
    }

    deliveries.set(deliveryId, delivery); // Update the delivery record with the final status
}

// ============================================================================
// ROUTES
// ============================================================================

/**
 * POST /webhooks
 * Register a new webhook subscription
 */
app.post('/webhooks', (req: Request, res: Response) => {
    const { url, account, programId, eventType } = req.body; // Extract registration parameters from the request body

    if (!url || !eventType) {
        return res.status(400).json({ error: 'url and eventType are required' }); // Reject incomplete registrations immediately
    }

    const id = `wh_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`; // Generate a unique subscription ID
    const subscription: WebhookSubscription = {
        id,
        url,
        account,
        programId,
        eventType,
        createdAt: Date.now(),
        active: true, // Activate immediately so events start flowing
    };

    subscriptions.set(id, subscription); // Store the subscription for the polling loop to evaluate
    res.status(201).json({ success: true, subscription }); // 201 signals successful resource creation
});

/**
 * GET /webhooks
 * List all webhook subscriptions
 */
app.get('/webhooks', (_req: Request, res: Response) => {
    const list = Array.from(subscriptions.values()); // Convert the Map to an array for JSON serialization
    res.json({ count: list.length, subscriptions: list }); // Include count so dashboards show summary stats
});

/**
 * GET /webhooks/:id
 * Get a single subscription
 */
app.get('/webhooks/:id', (req: Request, res: Response) => {
    const sub = subscriptions.get(req.params.id); // Look up the subscription by its ID
    if (!sub) {
        return res.status(404).json({ error: 'Subscription not found' }); // Return 404 for unknown IDs
    }
    res.json({ subscription: sub });
});

/**
 * DELETE /webhooks/:id
 * Remove a subscription
 */
app.delete('/webhooks/:id', (req: Request, res: Response) => {
    const deleted = subscriptions.delete(req.params.id); // Remove the subscription from the active set
    if (!deleted) {
        return res.status(404).json({ error: 'Subscription not found' });
    }
    res.json({ success: true, message: 'Subscription deleted' });
});

/**
 * POST /webhooks/:id/pause
 * Pause a subscription without deleting it
 */
app.post('/webhooks/:id/pause', (req: Request, res: Response) => {
    const sub = subscriptions.get(req.params.id);
    if (!sub) {
        return res.status(404).json({ error: 'Subscription not found' });
    }
    sub.active = false; // Set active to false so the polling loop skips this subscription
    res.json({ success: true, subscription: sub });
});

/**
 * POST /webhooks/:id/resume
 * Resume a paused subscription
 */
app.post('/webhooks/:id/resume', (req: Request, res: Response) => {
    const sub = subscriptions.get(req.params.id);
    if (!sub) {
        return res.status(404).json({ error: 'Subscription not found' });
    }
    sub.active = true; // Re-enable the subscription so events resume
    res.json({ success: true, subscription: sub });
});

/**
 * GET /webhooks/deliveries
 * View delivery history
 */
app.get('/webhooks/deliveries', (_req: Request, res: Response) => {
    const list = Array.from(deliveries.values());
    const summary = {
        total: list.length,
        delivered: list.filter(d => d.status === 'delivered').length, // Count successes for health metrics
        failed: list.filter(d => d.status === 'failed').length, // Count failures so operators can investigate
    };
    res.json({ summary, deliveries: list.slice(-50) }); // Return the most recent 50 to keep the response small
});

/**
 * POST /webhooks/test/:id
 * Send a test event to a subscription
 */
app.post('/webhooks/test/:id', async (req: Request, res: Response) => {
    const sub = subscriptions.get(req.params.id);
    if (!sub) {
        return res.status(404).json({ error: 'Subscription not found' });
    }

    const testEvent = {
        test: true,
        message: 'This is a test webhook delivery',
        customData: req.body || {}, // Allow the client to include custom test data
    };

    await deliverWebhook(sub, testEvent); // Reuse the real delivery function so tests exercise the same code path
    res.json({ success: true, message: 'Test delivery sent' });
});

// ============================================================================
// POLLING LOOP (simplified; production would use websockets or geyser)
// ============================================================================

let lastProcessedSlot = 0; // Track the last slot we checked to avoid duplicate notifications

async function pollForEvents(): Promise<void> {
    try {
        const currentSlot = await connection.getSlot(); // Ask the RPC for the latest slot
        if (currentSlot <= lastProcessedSlot) {
            return; // Skip if no new blocks have been produced since the last poll
        }

        lastProcessedSlot = currentSlot; // Advance the pointer so we only process new slots

        for (const sub of subscriptions.values()) {
            if (!sub.active) {
                continue; // Skip paused subscriptions to respect user preferences
            }

            if (sub.eventType === 'accountChange' && sub.account) {
                try {
                    const accountInfo = await connection.getAccountInfo(new (await import('@solana/web3.js')).PublicKey(sub.account)); // Fetch the latest account state
                    if (accountInfo) {
                        await deliverWebhook(sub, {
                            account: sub.account,
                            lamports: accountInfo.lamports,
                            owner: accountInfo.owner.toString(),
                            slot: currentSlot,
                        }); // Notify the subscriber with the current account snapshot
                    }
                } catch (e) {
                    console.error(`[Poll] Error checking account ${sub.account}:`, e); // Log but do not crash the polling loop
                }
            }

            if (sub.eventType === 'programLog' && sub.programId) {
                await deliverWebhook(sub, {
                    programId: sub.programId,
                    slot: currentSlot,
                    message: `Program activity detected at slot ${currentSlot}`, // Simplified; real implementation would parse logs
                });
            }
        }
    } catch (error) {
        console.error('[Poll] Polling error:', error); // Catch top-level errors so the loop keeps running
    }
}

// Start polling every 10 seconds
setInterval(pollForEvents, 10000); // 10 seconds is a balance between responsiveness and RPC usage

app.listen(PORT, () => {
    console.log(`=== Phase 26: Webhook API Service ===`);
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`Connected to: ${RPC_URL}`);
    console.log(`\nEndpoints:`);
    console.log(`  POST /webhooks              - Register a webhook`);
    console.log(`  GET  /webhooks              - List subscriptions`);
    console.log(`  GET  /webhooks/:id          - Get subscription`);
    console.log(`  DELETE /webhooks/:id        - Delete subscription`);
    console.log(`  POST /webhooks/:id/pause    - Pause subscription`);
    console.log(`  POST /webhooks/:id/resume   - Resume subscription`);
    console.log(`  GET  /webhooks/deliveries   - Delivery history`);
    console.log(`  POST /webhooks/test/:id     - Send test event`);
    console.log(`\nPolling every 10s for account and program events`);
});
