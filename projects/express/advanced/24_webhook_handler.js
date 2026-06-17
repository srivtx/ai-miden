// 24_webhook_handler.js — Receive webhooks, verify HMAC signature, idempotency, queue.
const express = require('express');
const crypto = require('crypto');
const app = express();

// Store processed webhook IDs to prevent duplicate processing
const processed = new Set();

// Raw body for signature verification (express.json parses before we can hash)
app.use('/webhooks', express.raw({ type: 'application/json' }));
app.use(express.json());

// Generic webhook verifier (Stripe/GitHub/Paddle pattern — all use HMAC-SHA256)
function verifySignature(secret) {
  return (req, res, next) => {
    const sig = req.headers['x-signature'] || req.headers['x-hub-signature-256'];
    if (!sig) return res.status(401).json({ error: 'Missing signature' });
    const computed = crypto.createHmac('sha256', secret).update(req.body).digest('hex');
    const expected = sig.replace('sha256=', ''); // GitHub format: sha256=xxx
    if (!crypto.timingSafeEqual(Buffer.from(computed), Buffer.from(expected))) {
      return res.status(401).json({ error: 'Invalid signature' });
    }
    req.body = JSON.parse(req.body.toString()); // Parse after verification
    next();
  };
}

// Idempotency: track processed event IDs
function idempotent(req, res, next) {
  const eventId = req.body.id || req.headers['x-event-id'];
  if (!eventId) return next();
  if (processed.has(eventId)) return res.status(200).json({ msg: 'Already processed', id: eventId });
  processed.add(eventId);
  req.eventId = eventId;
  next();
}

const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || 'whsec_test';

// Stripe-style webhook
app.post('/webhooks/stripe', verifySignature(WEBHOOK_SECRET), idempotent, (req, res) => {
  const { type, data } = req.body;
  console.log(`[Stripe] ${type}:`, data.object.id);

  switch (type) {
    case 'payment_intent.succeeded':
      // Fulfill order, send email, update DB
      console.log('  -> Processing payment:', data.object.amount);
      break;
    case 'customer.subscription.deleted':
      console.log('  -> Cancel subscription for:', data.object.customer);
      break;
    default:
      console.log('  -> Unhandled event:', type);
  }

  res.json({ received: true, type, id: req.eventId });
});

// GitHub-style webhook
app.post('/webhooks/github', verifySignature(WEBHOOK_SECRET), idempotent, (req, res) => {
  const event = req.headers['x-github-event'];
  console.log(`[GitHub] ${event}:`, req.body.action || req.body.ref);

  if (event === 'push') {
    console.log(`  -> New commits to ${req.body.ref}:`, req.body.commits?.map(c => c.message));
  } else if (event === 'pull_request' && req.body.action === 'opened') {
    console.log(`  -> PR #${req.body.number}: ${req.body.pull_request.title}`);
  }

  res.json({ received: true, event, id: req.eventId });
});

app.get('/webhooks/processed', (req, res) => res.json({ count: processed.size }));

app.listen(3000, () => {
  console.log('Webhook server :3000');
  console.log('Test:');
  console.log('  curl -X POST localhost:3000/webhooks/stripe \\');
  console.log('    -H "Content-Type: application/json" \\');
  console.log('    -H "X-Signature: sha256=WRONG" \\');
  console.log('    -d \'{"type":"payment_intent.succeeded","data":{"object":{"id":"pi_123"}}}\'');
  console.log('  (Will 401 — use correct signature from a real webhook provider)');
});
