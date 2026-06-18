# Project 35: The Payment

> *"Free is great. Premium is better. Stripe makes it easy."*

In projects 01-34, our app is free. Anyone can sign up, create posts, etc. But real apps have premium tiers. "Pay $10/month to unlock advanced features."

We use **Stripe** — the standard for online payments. Stripe handles:

- Card collection (via Stripe Checkout or Elements)
- Subscription management
- Payment intents
- Webhooks for payment events

We add:

1. A `subscriptions` table (user, stripe_customer_id, stripe_subscription_id, status, current_period_end)
2. A `POST /subscriptions/checkout` endpoint that creates a Stripe Checkout session and returns the URL
3. A `POST /subscriptions/webhook` endpoint that receives Stripe webhooks (using the webhook from project 34, but for *incoming* webhooks from Stripe)
4. A `GET /subscriptions/me` endpoint that returns the user's subscription status

The flow:
1. User clicks "Upgrade"
2. Server creates a Stripe Checkout session, returns the URL
3. User is redirected to Stripe, enters card details
4. Stripe charges the card, sends a webhook to our server
5. Server updates the user's subscription status
6. User is redirected back to our app

By the end, users can upgrade to premium. We charge their card. The subscription is managed.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is payment hard? What is Stripe?
2. [The Thought](./THOUGHT.md) — How does Stripe Checkout work? What are webhooks for?
3. [The Build](./BUILD.md) — Line-by-line construction of the payment flow
4. [The Decisions](./DECISIONS.md) — Why Stripe? Why Checkout? Why subscriptions?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

Stripe is the standard for online payments. We add a `subscriptions` table, a `POST /subscriptions/checkout` endpoint that creates a Stripe Checkout session and returns the URL, a `POST /subscriptions/webhook` endpoint that receives Stripe webhooks, and a `GET /subscriptions/me` endpoint that returns the user's subscription status. The flow: user clicks "Upgrade," server creates a Checkout session, user enters card details, Stripe charges, Stripe sends a webhook, server updates the subscription.

---

## The Code

```js
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

// Create a Checkout session
app.post('/subscriptions/checkout', authMiddleware, asyncHandler(async (req, res) => {
  const session = await stripe.checkout.sessions.create({
    mode: 'subscription',
    line_items: [{ price: process.env.STRIPE_PRICE_ID, quantity: 1 }],
    success_url: 'https://yourapp.com/success',
    cancel_url: 'https://yourapp.com/cancel',
    customer_email: req.user.email,
    client_reference_id: req.user.userId.toString(),
  });
  res.json({ url: session.url });
}));

// Stripe webhook
app.post('/subscriptions/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  const sig = req.headers['stripe-signature'];
  let event;
  try {
    event = stripe.webhooks.constructEvent(req.body, sig, process.env.STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;
    const userId = parseInt(session.client_reference_id);
    await db('subscriptions').insert({
      user_id: userId,
      stripe_customer_id: session.customer,
      stripe_subscription_id: session.subscription,
      status: 'active',
      current_period_end: Date.now() + 30 * 24 * 60 * 60 * 1000,
    });
  }

  res.json({ received: true });
}));

// Get subscription status
app.get('/subscriptions/me', authMiddleware, asyncHandler(async (req, res) => {
  const sub = await db('subscriptions').where({ user_id: req.user.userId }).first();
  res.json(sub || { status: 'inactive' });
}));
```

The pain of "I can't charge for premium" is solved. We integrate Stripe. Users can upgrade.

---

## What You Will Have Learned

- What Stripe is (the standard for online payments)
- How Stripe Checkout works (hosted payment page)
- How to create a Checkout session from the server
- How to receive Stripe webhooks (signature verification)
- How to update the user's subscription status
- How to expose the subscription status to the client

These are the foundations of *payments*. From here, every project that needs to charge for features can use Stripe.
