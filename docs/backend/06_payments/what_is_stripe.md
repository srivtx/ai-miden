## Why it exists (THE PROBLEM)

You need to charge users: one-time payments, subscriptions, invoices. Handling credit cards directly (PCI compliance, storing card numbers, chargebacks, fraud detection) is a regulatory nightmare. You need $100K+ in audits and weeks of security work.

**Stripe** handles all of this. Your server never sees a credit card number. Stripe's JavaScript library (Stripe.js) collects the card details, tokenizes them, and sends a token to your server. Your server tells Stripe "charge $20 to token tok_123." Stripe handles: PCI compliance, fraud detection, currency conversion, tax calculation, invoices, refunds, disputes. You pay 2.9% + $0.30 per transaction.

## How Stripe works

```
Browser                    Your Server                    Stripe
  |                            |                            |
  |-- Stripe.js creates card -->                            |
  |   token (stays in browser)  |                            |
  |                            |                            |
  |-- POST /create-payment ----|                            |
  |   { token: "tok_123" }     |                            |
  |                            |-- stripe.paymentIntents    |
  |                            |   .create({amount, token}) |
  |                            |                            |-- Charge card
  |                            |                            |-- Return result
  |                            |                            |
  |<-- { success: true } ------|                            |
  |                            |                            |
  |              * WEBHOOK: payment_intent.succeeded        |
  |                            |<---------------------------|
  |                            | Fulfill order               |
```

**Your server never touches card numbers.** The token (`tok_123`) is a one-time-use identifier that Stripe maps to the actual card. After charging, the token expires.

## Key Stripe objects

| Object | What it is |
|---|---|
| **PaymentIntent** | One-time payment. Create, confirm, capture. |
| **Customer** | A user in Stripe (linked to your user ID). Stores payment methods. |
| **Subscription** | Recurring billing. Customer + Price + interval. |
| **Invoice** | Auto-generated for subscriptions. Line items. |
| **Webhook** | Stripe POSTs to your server when events happen (payment succeeded, subscription canceled, etc.) |

## The webhook pattern (critical)

Stripe sends webhooks for EVERY event. NEVER trust just the client-side confirmation. The webhook `payment_intent.succeeded` is the GROUND TRUTH. Fulfill the order only when this webhook arrives. The client-side redirect can be intercepted/tampered.

```javascript
app.post('/webhooks/stripe', express.raw({ type: 'application/json' }), (req, res) => {
  const sig = req.headers['stripe-signature'];
  const event = stripe.webhooks.constructEvent(req.body, sig, WEBHOOK_SECRET);

  switch (event.type) {
    case 'payment_intent.succeeded':
      // FULFILL THE ORDER HERE (this is the source of truth)
      break;
    case 'customer.subscription.deleted':
      // Cancel user's access
      break;
  }
  res.json({ received: true });
});
```
