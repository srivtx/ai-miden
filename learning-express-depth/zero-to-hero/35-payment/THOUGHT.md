# The Thought

> *"Stripe handles the card. We handle the subscription status. Webhooks connect them."*

## How Stripe Checkout Works

Stripe Checkout is a *hosted payment page*. The user is redirected to Stripe's site, enters card details, and Stripe handles everything. We never see the card.

The flow:

1. Our server creates a "Checkout session" via Stripe's API:

```js
const session = await stripe.checkout.sessions.create({
  mode: 'subscription', // or 'payment' for one-time
  line_items: [{ price: 'price_xxx', quantity: 1 }],
  success_url: 'https://yourapp.com/success',
  cancel_url: 'https://yourapp.com/cancel',
  customer_email: 'alice@example.com',
  client_reference_id: '1', // our user ID
});
```

The `price_xxx` is a Stripe price ID (created in the Stripe dashboard). The `client_reference_id` is our user ID — we'll use it to update the right user when the webhook arrives.

2. Stripe returns a session with a `url`. The user is redirected to this URL.

3. The user enters card details on Stripe's hosted page.

4. Stripe charges the card.

5. Stripe sends a webhook to our server. The webhook event is `checkout.session.completed`. The event includes the `client_reference_id` (our user ID) and the `subscription` ID (Stripe's subscription ID).

6. Our server receives the webhook, verifies the signature, and updates our database:

```js
await db('subscriptions').insert({
  user_id: parseInt(session.client_reference_id),
  stripe_customer_id: session.customer,
  stripe_subscription_id: session.subscription,
  status: 'active',
  current_period_end: ...,
});
```

7. Stripe redirects the user back to our `success_url`.

## The Subscription Lifecycle

A subscription has a lifecycle:

1. **Created** — user signs up, Stripe creates the subscription
2. **Active** — payment succeeds, subscription is active
3. **Past due** — payment fails (e.g., expired card), Stripe retries
4. **Canceled** — user cancels, or we cancel
5. **Ended** — subscription period is over, no more renewals

Stripe sends webhooks for each transition:
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`

We listen for these and update our database accordingly.

## Webhook Signature Verification

Stripe webhooks are signed. We verify the signature to ensure the webhook is from Stripe:

```js
const event = stripe.webhooks.constructEvent(
  req.body, // raw body
  req.headers['stripe-signature'],
  process.env.STRIPE_WEBHOOK_SECRET
);
```

If the signature is invalid, we reject. This is the same pattern as our outgoing webhooks (project 34), but in reverse.

## The Raw Body Requirement

Stripe's signature verification requires the *raw* request body. Express's `express.json()` middleware parses the body as JSON, which changes the bytes. We need the raw body.

```js
app.post('/subscriptions/webhook', express.raw({ type: 'application/json' }), (req, res) => {
  // req.body is a Buffer
});
```

We use `express.raw()` for this endpoint. The rest of the app uses `express.json()`.

## The Customer Portal

Stripe provides a hosted customer portal where users can manage their subscription (cancel, update payment method, see invoices). We link to it:

```js
const session = await stripe.billingPortal.sessions.create({
  customer: stripeCustomerId,
  return_url: 'https://yourapp.com/account',
});
// Redirect to session.url
```

For this project, we don't add the portal link. The user can manage via the Stripe dashboard.

## Common Confusions (read these)

**Confusion 1: "Why not handle cards directly?"**
PCI compliance. Expensive. Risky. Use Stripe.

**Confusion 2: "Why Checkout and not Elements?"**
Checkout is a hosted page (simpler). Elements is embedded in your site (more control). For most apps, Checkout is enough.

**Confusion 3: "What if the webhook fails?"**
Stripe retries the webhook for up to 3 days. We should always return 200 quickly and process asynchronously.

**Confusion 4: "What if the user pays but the webhook doesn't arrive?"**
Stripe's idempotency key prevents double-charging. We can also fetch the subscription from Stripe's API to verify.

**Confusion 5: "What about refunds?"**
Handled via the Stripe dashboard. We could add a refund endpoint, but for now, it's manual.

**Confusion 6: "What about taxes?"**
Stripe Tax handles VAT, GST, etc. We don't configure it for this project.

**Confusion 7: "What about multiple plans?"**
Out of scope. We have one price ID. Multiple plans would require more logic.

**Confusion 8: "What about trials?"**
Stripe supports free trials. We don't use them.

## What We Are About to Build

A ~800-line Express app that:

1. Has a `subscriptions` table
2. Has a `POST /subscriptions/checkout` endpoint (Stripe Checkout)
3. Has a `POST /subscriptions/webhook` endpoint (Stripe webhooks)
4. Has a `GET /subscriptions/me` endpoint
5. Verifies webhook signatures
6. Updates the database on subscription events

The handlers are extended. The new piece is the payment flow.

In [BUILD.md](./BUILD.md) we will go line by line.
