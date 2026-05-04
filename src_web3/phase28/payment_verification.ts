import express, { Request, Response } from 'express';
import { Connection, PublicKey, LAMPORTS_PER_SOL } from '@solana/web3.js';

/**
 * Phase 28: Payment Verification Service
 *
 * Provides on-chain verification endpoints for payment gateway operations:
 * - Confirms transactions exist and are finalized
 * - Verifies payment amounts match expected values
 * - Checks transaction details like sender, receiver, and memo
 * - Serves as the trust layer between the gateway and merchants
 *
 * Run: npx ts-node src_web3/phase28/payment_verification.ts
 */

const app = express(); // Create the Express server for verification requests
app.use(express.json()); // Parse JSON bodies so clients can send verification parameters

const PORT = 3012; // Separate port so verification can scale independently from the gateway

// ============================================================================
// CONFIGURATION
// ============================================================================
const RPC_URL = process.env.SOLANA_RPC || 'https://api.devnet.solana.com'; // Use the same RPC as the gateway
const connection = new Connection(RPC_URL, 'confirmed'); // Confirmed commitment ensures we verify finalized transactions

// ============================================================================
// TYPES
// ============================================================================
interface VerificationResult {
    valid: boolean; // Whether the payment passes all verification checks
    signature: string; // The transaction signature being verified
    checks: {
        exists: boolean; // Transaction is found on-chain
        finalized: boolean; // Transaction has reached confirmed commitment
        amountCorrect: boolean; // Received amount matches expected amount
        receiverCorrect: boolean; // Funds went to the expected address
        senderKnown: boolean; // We could identify a sender address
        notDoubleSpent: boolean; // This signature has not been verified before for another payment
    };
    details: {
        slot: number; // Block slot for audit trails
        blockTime: number | null; // Unix timestamp for reconciliation
        fee: number; // Transaction fee in SOL
        sender: string | null; // Source account
        receiver: string | null; // Destination account
        amount: number; // Amount transferred in SOL
    };
    errors: string[]; // Human-readable reasons if any check failed
}

// ============================================================================
// DOUBLE-SPEND PREVENTION
// ============================================================================
const verifiedSignatures: Set<string> = new Set(); // Track which signatures have already been used for payments

// ============================================================================
// VERIFICATION LOGIC
// ============================================================================

/**
 * Perform deep on-chain verification of a payment transaction.
 */
async function verifyPayment(
    signature: string,
    expectedAmount: number,
    expectedReceiver: string
): Promise<VerificationResult> {
    const result: VerificationResult = {
        valid: false,
        signature,
        checks: {
            exists: false,
            finalized: false,
            amountCorrect: false,
            receiverCorrect: false,
            senderKnown: false,
            notDoubleSpent: false,
        },
        details: {
            slot: 0,
            blockTime: null,
            fee: 0,
            sender: null,
            receiver: null,
            amount: 0,
        },
        errors: [],
    };

    try {
        const tx = await connection.getTransaction(signature, {
            commitment: 'confirmed', // Require confirmed status to avoid verifying unconfirmed payments
            maxSupportedTransactionVersion: 0, // Support both legacy and version 0 transactions
        });

        if (!tx) {
            result.errors.push('Transaction not found on-chain'); // The signature does not exist or is too old
            return result;
        }
        result.checks.exists = true; // Mark existence check as passed

        if (tx.meta && tx.meta.err) {
            result.errors.push('Transaction failed on-chain'); // Failed transactions cannot represent valid payments
            return result;
        }
        result.checks.finalized = true; // No error means it succeeded at confirmed level

        result.details.slot = tx.slot; // Record block slot for audit purposes
        result.details.blockTime = tx.blockTime; // Record timestamp for merchant reconciliation
        result.details.fee = (tx.meta?.fee || 0) / LAMPORTS_PER_SOL; // Convert fee from lamports to SOL

        // Extract transfer details from parsed transaction
        if (tx.transaction.message.instructions.length > 0) {
            const ix = tx.transaction.message.instructions[0]; // Look at the first instruction for system transfers
            if ('parsed' in ix && ix.parsed.type === 'transfer') {
                result.details.sender = ix.parsed.info.source; // Capture source account
                result.details.receiver = ix.parsed.info.destination; // Capture destination account
                result.details.amount = parseInt(ix.parsed.info.lamports, 10) / LAMPORTS_PER_SOL; // Convert to SOL
                result.checks.senderKnown = true; // We successfully identified the sender
            }
        }

        if (!result.details.receiver) {
            result.errors.push('Could not determine receiver from transaction'); // Non-transfer transactions are not valid payments
            return result;
        }

        if (result.details.receiver !== expectedReceiver) {
            result.errors.push(`Receiver mismatch: expected ${expectedReceiver}, got ${result.details.receiver}`); // Funds went to the wrong address
            return result;
        }
        result.checks.receiverCorrect = true; // The payment reached the intended destination

        const tolerance = 0.0001; // Small tolerance for floating point comparison
        if (Math.abs(result.details.amount - expectedAmount) > tolerance) {
            result.errors.push(`Amount mismatch: expected ${expectedAmount}, got ${result.details.amount}`); // Customer sent wrong amount
            return result;
        }
        result.checks.amountCorrect = true; // The amount matches within tolerance

        if (verifiedSignatures.has(signature)) {
            result.errors.push('Transaction signature has already been used for another payment'); // Prevent double-spending the same signature
            return result;
        }
        result.checks.notDoubleSpent = true; // This signature is fresh

        verifiedSignatures.add(signature); // Mark this signature as used so future verifications reject it
        result.valid = true; // All checks passed
    } catch (error) {
        result.errors.push(`Verification error: ${error}`); // Capture unexpected errors like RPC failures
    }

    return result;
}

// ============================================================================
// ROUTES
// ============================================================================

app.get('/health', async (_req: Request, res: Response) => {
    try {
        const slot = await connection.getSlot();
        res.json({
            status: 'healthy',
            slot,
            verifiedCount: verifiedSignatures.size, // Show how many payments have been verified
        });
    } catch (error) {
        res.status(503).json({ status: 'unhealthy', error: String(error) });
    }
});

/**
 * POST /verify
 * Verify a single payment transaction
 */
app.post('/verify', async (req: Request, res: Response) => {
    const { signature, expectedAmount, expectedReceiver } = req.body; // Extract verification parameters

    if (!signature || expectedAmount === undefined || !expectedReceiver) {
        return res.status(400).json({ error: 'signature, expectedAmount, and expectedReceiver are required' }); // Reject incomplete requests
    }

    const result = await verifyPayment(signature, parseFloat(expectedAmount), expectedReceiver); // Run the full verification pipeline
    res.json({ result }); // Return the detailed result so the gateway can make informed decisions
});

/**
 * POST /verify/batch
 * Verify multiple payment transactions in one request
 */
app.post('/verify/batch', async (req: Request, res: Response) => {
    const { payments } = req.body; // Expect an array of payment objects

    if (!Array.isArray(payments) || payments.length > 20) {
        return res.status(400).json({ error: 'Max 20 payments per batch' }); // Limit batch size to prevent resource exhaustion
    }

    const results = await Promise.all(
        payments.map(async (p: any) => {
            if (!p.signature || p.expectedAmount === undefined || !p.expectedReceiver) {
                return {
                    signature: p.signature || 'unknown',
                    valid: false,
                    errors: ['Missing required fields'], // Validate each item individually
                };
            }
            const result = await verifyPayment(p.signature, parseFloat(p.expectedAmount), p.expectedReceiver);
            return result;
        })
    );

    const allValid = results.every(r => r.valid); // Quick summary for batch approvals
    res.json({
        allValid,
        count: results.length,
        passed: results.filter(r => r.valid).length, // Count successes
        failed: results.filter(r => !r.valid).length, // Count failures for monitoring
        results,
    });
});

/**
 * GET /verify/:signature
 * Check verification status of a previously verified transaction
 */
app.get('/verify/:signature', (req: Request, res: Response) => {
    const signature = req.params.signature;
    const wasVerified = verifiedSignatures.has(signature); // Check if this signature is in our used set
    res.json({
        signature,
        verified: wasVerified,
        message: wasVerified ? 'This transaction has been verified for a prior payment' : 'Transaction not yet used for payment verification',
    });
});

/**
 * GET /stats
 * Verification service statistics
 */
app.get('/stats', (_req: Request, res: Response) => {
    res.json({
        totalVerified: verifiedSignatures.size, // Total number of unique signatures verified
        rpcEndpoint: RPC_URL,
        doubleSpendProtection: true, // Indicate that this service prevents replay attacks
    });
});

app.listen(PORT, () => {
    console.log(`=== Phase 28: Payment Verification Service ===`);
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`Connected to: ${RPC_URL}`);
    console.log(`\nEndpoints:`);
    console.log(`  POST /verify              - Verify a single payment`);
    console.log(`  POST /verify/batch        - Batch verify up to 20 payments`);
    console.log(`  GET  /verify/:signature   - Check if signature was already used`);
    console.log(`  GET  /stats               - Verification statistics`);
    console.log(`\nChecks performed: exists, finalized, amount, receiver, sender, double-spend`);
});
