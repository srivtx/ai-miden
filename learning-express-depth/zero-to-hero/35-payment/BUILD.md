# The Build

> *"Stripe handles the card. We handle the subscription status. Webhooks connect them."*

We are going to add Stripe payments. The change from project 34: add a `subscriptions` table, Stripe Checkout, and Stripe webhook handling.

## Setup

```bash
npm install stripe

# Set environment variables
export STRIPE_SECRET_KEY=sk_test_...
export STRIPE_PRICE_ID=price_...
export STRIPE_WEBHOOK_SECRET=whsec_...
```

You get these from the Stripe dashboard. For testing, use the test keys (Stripe provides test mode).

## The Code

### The Migration

```js
{
  version: 9,
  up: `
    CREATE TABLE IF NOT EXISTS subscriptions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      stripe_customer_id TEXT NOT NULL,
      stripe_subscription_id TEXT NOT NULL,
      status TEXT NOT NULL,
      current_period_end INTEGER NOT NULL,
      created_at INTEGER NOT NULL,
      updated_at INTEGER NOT NULL
    );
  `,
},
```

### The Stripe Client

```js
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
```

### The Checkout Endpoint

```js
app.post('/subscriptions/checkout', authMiddleware, asyncHandler(async (req, res) => {
  const session = await stripe.checkout.sessions.create({
    mode: 'subscription',
    line_items: [{ price: process.env.STRIPE_PRICE_ID, quantity: 1 }],
    success_url: `${process.env.APP_URL}/subscriptions/success`,
    cancel_url: `${process.env.APP_URL}/subscriptions/cancel`,
    customer_email: req.user.email,
    client_reference_id: req.user.userId.toString(),
  });
  res.json({ url: session.url });
}));
```

### The Webhook Endpoint

```js
app.post('/subscriptions/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  const sig = req.headers['stripe-signature'];
  let event;
  try {
    event = stripe.webhooks.constructEvent(req.body, sig, process.env.STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    req.log.error({ err: err.message }, 'Stripe webhook signature verification failed');
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;
    const userId = parseInt(session.client_reference_id);
    const subscription = await stripe.subscriptions.retrieve(session.subscription);
    await db('subscriptions').insert({
      user_id: userId,
      stripe_customer_id: session.customer,
      stripe_subscription_id: session.subscription,
      status: subscription.status,
      current_period_end: subscription.current_period_end * 1000,
      created_at: Date.now(),
      updated_at: Date.now(),
    }).onConflict('user_id').merge();
  } else if (event.type === 'customer.subscription.updated' || event.type === 'customer.subscription.deleted') {
    const subscription = event.data.object;
    await db('subscriptions').where({ stripe_subscription_id: subscription.id }).update({
      status: subscription.status,
      current_period_end: subscription.current_period_end * 1000,
      updated_at: Date.now(),
    });
  }

  res.json({ received: true });
}));
```

### The Status Endpoint

```js
app.get('/subscriptions/me', authMiddleware, asyncHandler(async (req, res) => {
  const sub = await db('subscriptions').where({ user_id: req.user.userId }).first();
  res.json(sub || { status: 'inactive' });
}));
```

## Run It

```bash
# Start the server
STRIPE_SECRET_KEY=sk_test_... STRIPE_PRICE_ID=price_... STRIPE_WEBHOOK_SECRET=whsec_... node server.js

# Create a Checkout session
curl -X POST http://localhost:3000/subscriptions/checkout \
  -H "Authorization: Bearer $TOKEN"
# {"url":"https://checkout.stripe.com/..."}

# Open the URL in a browser. Use Stripe's test card: 4242 4242 4242 4242.

# After payment, Stripe sends a webhook. Our server updates the database.

# Check the subscription status
curl http://localhost:3000/subscriptions/me \
  -H "Authorization: Bearer $TOKEN"
# {"id":1,"user_id":1,"stripe_customer_id":"cus_...","stripe_subscription_id":"sub_...","status":"active","current_period_end":...}
```

The pain of "I can't charge for premium" is solved. We integrate Stripe. Users can upgrade.

---

## Experiments

### Experiment 1: Test the webhook locally

Use the Stripe CLI to forward webhooks to localhost:

```bash
stripe listen --forward-to localhost:3000/subscriptions/webhook
```

The CLI prints the webhook secret. Use it in `STRIPE_WEBHOOK_SECRET`. Now you can test webhooks locally.

### Experiment 2: Handle subscription cancellation

Add a handler for `customer.subscription.deleted`:

```js
} else if (event.type === 'customer.subscription.deleted') {
  const subscription = event.data.object;
  await db('subscriptions').where({ stripe_subscription_id: subscription.id }).update({
    status: 'canceled',
    updated_at: Date.now(),
  });
}
```

### Experiment 3: Add a customer portal link

```js
app.post('/subscriptions/portal', authMiddleware, asyncHandler(async (req, res) => {
  const sub = await db('subscriptions').where({ user_id: req.user.userId }).first();
  if (!sub) throw new NotFoundError('No subscription');
  const session = await stripe.billingPortal.sessions.create({
    customer: sub.stripe_customer_id,
    return_url: `${process.env.APP_URL}/account`,
  });
  res.json({ url: session.url });
}));
```

### Experiment 4: Premium features

Add a middleware that checks the subscription status:

```js
function requirePremium(req, res, next) {
  db('subscriptions').where({ user_id: req.user.userId, status: 'active' }).first()
    .then((sub) => {
      if (!sub) throw new ForbiddenError('Premium required');
      next();
    })
    .catch(next);
}

app.post('/posts/premium', authMiddleware, requirePremium, validate(postCreateSchema), ...);
```

---

## Summary

You now have Stripe payments. Users can upgrade to premium. We charge their card. The subscription is managed.

This is the foundation of *payments*. From here, every project that needs to charge for features can use Stripe. The patterns (Checkout, webhooks, signature verification) are universal.

In project 36, we will add **tests**. We will write unit tests and integration tests to verify everything works automatically.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.
