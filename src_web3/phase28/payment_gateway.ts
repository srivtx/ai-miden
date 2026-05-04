import express, { Request, Response } from 'express';
import { Connection, PublicKey, Keypair, LAMPORTS_PER_SOL } from '@solana/web3.js';
import crypto from 'crypto';

/**
 * Phase 28: Payment Gateway
 *
 * Express API for cryptocurrency payment processing:
 * - Creates payment intents with unique deposit addresses
 * - Monitors deposit addresses for incoming transactions
 * - Fires webhooks to merchants on confirmation
 * - Handles partial payments, overpayments, and expirations
 *
 * Run: npx ts-node src_web3/phase28/payment_gateway.ts
 */

const app = express(); // Create the Express application to handle merchant and customer requests
app.use(express.json()); // Parse JSON bodies so payment intent creation parameters are readable

const PORT = 3011; // Dedicated port for the payment gateway service

// ============================================================================
// CONFIGURATION
// ============================================================================
const RPC_URL = process.env.SOLANA_RPC || 'https://api.devnet.solana.com'; // Connect to Solana for transaction monitoring
const connection = new Connection(RPC_URL, 'confirmed'); // Confirmed commitment balances speed with finality

const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || 'gateway-secret-change-me'; // Shared secret to sign webhook payloads
const INTENT_EXPIRY_MS = 15 * 60 * 1000; // 15 minutes: enough time for a customer to complete a payment

// ============================================================================
// TYPES
// ============================================================================
interface PaymentIntent {
    id: string; // Unique identifier for the merchant to reference this order
    merchantId: string; // Which merchant created this intent for multi-tenant support
    amount: number; // Expected amount in SOL
    currency: string; // Currency code, typically SOL or USDC
    depositAddress: string; // Unique address where the customer must send payment
    status: 'pending' | 'partial' | 'paid' | 'overpaid' | 'expired' | 'failed'; // Lifecycle states
    receivedAmount: number; // How much has actually arrived on-chain
    customerEmail?: string; // Optional metadata for merchant CRM systems
    orderId?: string; // Merchant's internal order identifier
    callbackUrl?: string; // Where to POST webhook notifications
    createdAt: number; // When the intent was created
    expiresAt: number; // Deadline after which the intent is considered stale
    confirmedAt?: number; // When the payment was fully confirmed
    transactions: string[]; // List of transaction signatures that contributed to this payment
}

interface Merchant {
    id: string; // Merchant identifier
    name: string; // Display name
    callbackUrl: string; // Default webhook URL if not overridden per intent
    apiKey: string; // Simple API key for authentication
}

// ============================================================================
// STORAGE
// ============================================================================
const intents: Map<string, PaymentIntent> = new Map(); // In-memory store for payment intents
const merchants: Map<string, Merchant> = new Map(); // In-memory store for registered merchants

// Seed with a demo merchant so the API works out of the box
merchants.set('merchant_001', {
    id: 'merchant_001',
    name: 'Demo Store',
    callbackUrl: 'https://httpbin.org/post', // Public endpoint for testing webhook delivery
    apiKey: 'demo-api-key-123',
});

// ============================================================================
// HELPERS
// ============================================================================

/**
 * Generate a unique deposit address for each payment intent.
 * In production this derives from an HD wallet. Here we simulate with Keypair.
 */
function generateDepositAddress(): string {
    const keypair = Keypair.generate(); // Generate a new keypair to act as a unique deposit address
    return keypair.publicKey.toString(); // Return the public key as the deposit address
}

/**
 * Sign a webhook payload so the merchant can verify it came from the gateway.
 */
function signWebhookPayload(payload: any): string {
    const hmac = crypto.createHmac('sha256', WEBHOOK_SECRET); // Use HMAC-SHA256 for integrity and authenticity
    hmac.update(JSON.stringify(payload)); // Sign the serialized payload
    return hmac.digest('hex'); // Return hex string for easy HTTP header transmission
}

/**
 * Deliver a webhook notification to the merchant's callback URL.
 */
async function notifyMerchant(intent: PaymentIntent, event: string): Promise<void> {
    if (!intent.callbackUrl) {
        return; // Skip if no callback URL was provided during intent creation
    }

    const payload = {
        event, // e.g., 'payment.confirmed', 'payment.partial', 'payment.expired'
        intentId: intent.id, // Let the merchant know which order this concerns
        merchantId: intent.merchantId,
        status: intent.status,
        expectedAmount: intent.amount,
        receivedAmount: intent.receivedAmount,
        depositAddress: intent.depositAddress,
        orderId: intent.orderId,
        timestamp: new Date().toISOString(),
    };

    try {
        const signature = signWebhookPayload(payload); // Sign so the merchant can verify authenticity
        const response = await fetch(intent.callbackUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Webhook-Signature': signature, // Include signature for verification
                'X-Webhook-Event': event, // Include event type so merchants can route internally
                'X-Idempotency-Key': `${intent.id}_${event}`, // Prevent duplicate processing
            },
            body: JSON.stringify(payload),
        });

        console.log(`[Webhook] ${event} for intent ${intent.id} -> ${response.status}`); // Log delivery status for observability
    } catch (error) {
        console.error(`[Webhook] Failed to notify merchant for intent ${intent.id}:`, error); // Log failures for retry logic
    }
}

/**
 * Check if an intent has expired and update its status.
 */
function checkExpiry(intent: PaymentIntent): boolean {
    if (intent.status === 'expired' || intent.status === 'paid') {
        return false; // Already finalized, no need to check again
    }
    if (Date.now() > intent.expiresAt) {
        intent.status = 'expired'; // Mark as expired when the deadline passes
        notifyMerchant(intent, 'payment.expired'); // Notify the merchant that this order timed out
        return true;
    }
    return false;
}

// ============================================================================
// AUTH MIDDLEWARE
// ============================================================================

function authMiddleware(req: Request, res: Response, next: Function): void {
    const apiKey = req.headers['x-api-key'] as string; // Read the API key from the header
    if (!apiKey) {
        res.status(401).json({ error: 'Missing API key' }); // Reject requests without authentication
        return;
    }

    const merchant = Array.from(merchants.values()).find(m => m.apiKey === apiKey); // Look up the merchant by API key
    if (!merchant) {
        res.status(403).json({ error: 'Invalid API key' }); // Reject requests with unknown keys
        return;
    }

    (req as any).merchant = merchant; // Attach the merchant object to the request for downstream handlers
    next(); // Proceed to the route handler
}

// ============================================================================
// ROUTES
// ============================================================================

app.get('/health', async (_req: Request, res: Response) => {
    try {
        const slot = await connection.getSlot(); // Verify RPC connectivity
        res.json({
            status: 'healthy',
            slot,
            intents: intents.size,
            merchants: merchants.size,
        });
    } catch (error) {
        res.status(503).json({ status: 'unhealthy', error: String(error) });
    }
});

/**
 * POST /intents
 * Create a new payment intent
 */
app.post('/intents', authMiddleware, (req: Request, res: Response) => {
    const merchant = (req as any).merchant; // Retrieve the authenticated merchant from the middleware
    const { amount, currency = 'SOL', customerEmail, orderId, callbackUrl } = req.body; // Extract payment details

    if (!amount || amount <= 0) {
        return res.status(400).json({ error: 'Amount must be greater than 0' }); // Validate input to prevent invalid intents
    }

    const id = `pi_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`; // Generate a unique payment intent ID
    const depositAddress = generateDepositAddress(); // Create a unique address for this payment

    const intent: PaymentIntent = {
        id,
        merchantId: merchant.id,
        amount,
        currency,
        depositAddress,
        status: 'pending',
        receivedAmount: 0,
        customerEmail,
        orderId,
        callbackUrl: callbackUrl || merchant.callbackUrl, // Fallback to merchant default if not specified
        createdAt: Date.now(),
        expiresAt: Date.now() + INTENT_EXPIRY_MS, // Set deadline based on configured expiry
        transactions: [],
    };

    intents.set(id, intent); // Store the intent for monitoring and lookup
    res.status(201).json({
        success: true,
        intent: {
            id: intent.id,
            depositAddress: intent.depositAddress, // Tell the customer exactly where to send funds
            amount: intent.amount,
            currency: intent.currency,
            expiresAt: new Date(intent.expiresAt).toISOString(), // Human-readable deadline
            status: intent.status,
        },
    });
});

/**
 * GET /intents/:id
 * Retrieve a payment intent
 */
app.get('/intents/:id', authMiddleware, (req: Request, res: Response) => {
    const intent = intents.get(req.params.id); // Look up the intent by ID
    if (!intent) {
        return res.status(404).json({ error: 'Intent not found' });
    }

    const merchant = (req as any).merchant;
    if (intent.merchantId !== merchant.id) {
        return res.status(403).json({ error: 'Not authorized to view this intent' }); // Prevent merchants from viewing each other's data
    }

    checkExpiry(intent); // Update status if the intent has passed its deadline
    res.json({ intent });
});

/**
 * GET /intents
 * List payment intents for the authenticated merchant
 */
app.get('/intents', authMiddleware, (req: Request, res: Response) => {
    const merchant = (req as any).merchant;
    const merchantIntents = Array.from(intents.values())
        .filter(i => i.merchantId === merchant.id) // Only return intents belonging to this merchant
        .map(i => {
            checkExpiry(i); // Refresh expiry status before returning
            return i;
        });

    res.json({ count: merchantIntents.length, intents: merchantIntents });
});

/**
 * POST /intents/:id/cancel
 * Cancel a pending payment intent
 */
app.post('/intents/:id/cancel', authMiddleware, (req: Request, res: Response) => {
    const intent = intents.get(req.params.id);
    if (!intent) {
        return res.status(404).json({ error: 'Intent not found' });
    }

    const merchant = (req as any).merchant;
    if (intent.merchantId !== merchant.id) {
        return res.status(403).json({ error: 'Not authorized' });
    }

    if (intent.status !== 'pending') {
        return res.status(400).json({ error: `Cannot cancel intent with status: ${intent.status}` }); // Only cancel pending intents
    }

    intent.status = 'failed'; // Mark as failed to stop monitoring
    notifyMerchant(intent, 'payment.cancelled'); // Inform the merchant of the cancellation
    res.json({ success: true, intent });
});

// ============================================================================
// MONITORING LOOP
// ============================================================================

async function monitorPayments(): Promise<void> {
    for (const intent of intents.values()) {
        if (intent.status === 'paid' || intent.status === 'expired' || intent.status === 'failed') {
            continue; // Skip finalized intents since they do not need monitoring
        }

        if (checkExpiry(intent)) {
            continue; // Skip if the intent just expired in checkExpiry
        }

        try {
            const balance = await connection.getBalance(new PublicKey(intent.depositAddress)); // Check current balance of the deposit address
            const received = balance / LAMPORTS_PER_SOL; // Convert lamports to SOL for comparison

            if (received > intent.receivedAmount) {
                intent.receivedAmount = received; // Update received amount if new funds arrived

                // Find new transaction signatures for this address
                const signatures = await connection.getSignaturesForAddress(
                    new PublicKey(intent.depositAddress),
                    { limit: 10 }
                );
                intent.transactions = signatures.map(s => s.signature); // Record contributing signatures

                if (received >= intent.amount * 0.99 && received <= intent.amount * 1.01) {
                    intent.status = 'paid'; // Mark paid if within 1% tolerance for network fees
                    intent.confirmedAt = Date.now();
                    notifyMerchant(intent, 'payment.confirmed'); // Fire webhook so merchant ships the product
                } else if (received < intent.amount) {
                    intent.status = 'partial'; // Customer sent less than expected
                    notifyMerchant(intent, 'payment.partial'); // Alert merchant so they can contact the customer
                } else if (received > intent.amount) {
                    intent.status = 'overpaid'; // Customer sent more than expected
                    notifyMerchant(intent, 'payment.overpaid'); // Alert merchant so they can refund the excess
                }
            }
        } catch (error) {
            console.error(`[Monitor] Error checking intent ${intent.id}:`, error); // Log but do not stop monitoring other intents
        }
    }
}

setInterval(monitorPayments, 10000); // Check every 10 seconds to balance responsiveness with RPC usage

app.listen(PORT, () => {
    console.log(`=== Phase 28: Payment Gateway ===`);
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`Connected to: ${RPC_URL}`);
    console.log(`\nEndpoints (requires x-api-key header):`);
    console.log(`  POST /intents           - Create payment intent`);
    console.log(`  GET  /intents           - List merchant intents`);
    console.log(`  GET  /intents/:id       - Get intent details`);
    console.log(`  POST /intents/:id/cancel - Cancel pending intent`);
    console.log(`\nDemo merchant API key: demo-api-key-123`);
    console.log(`Monitoring every 10s for incoming payments`);
});
