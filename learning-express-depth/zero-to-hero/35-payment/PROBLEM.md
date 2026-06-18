# The Problem

> *"Free is great. Premium is better. Stripe makes it easy."*

## Why Payment Is Hard

Online payment involves:

- **PCI compliance**: handling card data directly requires rigorous security audits
- **Fraud detection**: distinguishing legitimate from fraudulent transactions
- **Subscriptions**: handling recurring billing, upgrades, downgrades, cancellations
- **International**: different currencies, tax rules, regulations
- **Disputes**: handling chargebacks and refunds

Building all this from scratch is impractical for most apps. We use a **payment processor** — a service that handles all of this for us.

## What Pain Is This Solving?

The alternative to a payment processor is to handle card data ourselves. We'd need:

- PCI-DSS certification (expensive, ongoing audits)
- Tokenization (storing card numbers securely)
- Fraud detection (manual or via a service)
- Recurring billing (complex logic)
- Webhook handling (for async events)

A payment processor handles all of this. We just integrate.

**Stripe** is the standard. It handles:

- Card collection (PCI-DSS compliant, we never see the card number)
- Subscriptions (recurring billing)
- Payment intents (one-time payments)
- Webhooks (for events like `payment_succeeded`, `subscription_canceled`)
- International (135+ currencies, 40+ countries)
- Fraud detection (Stripe Radar)
- Disputes (chargebacks)

We use Stripe. We never see the card. Stripe handles the compliance.

## The Deeper Problem: The Payment Flow

The standard flow for a subscription:

1. **User clicks "Upgrade"** on our site
2. **We create a Stripe Checkout session** and return the URL
3. **User is redirected to Stripe** (stripe.com/pay/...)
4. **User enters card details** on Stripe's hosted page
5. **Stripe charges the card**
6. **Stripe sends a webhook** to our server (`checkout.session.completed`)
7. **We update the user's subscription status** in our database
8. **User is redirected back** to our site (to /success or /cancel)

Stripe handles the UI for card entry. We never see the card. We get a webhook when the payment succeeds. We update our database.

## What This Project Will Solve

This project will:

1. Add a `subscriptions` table
2. Add a `POST /subscriptions/checkout` endpoint (creates a Stripe Checkout session)
3. Add a `POST /subscriptions/webhook` endpoint (receives Stripe webhooks)
4. Add a `GET /subscriptions/me` endpoint (returns the user's subscription status)
5. Use the webhook from project 34 to receive Stripe webhooks (with signature verification)

By the end, users can upgrade to premium. We charge their card. The subscription is managed.

## What This Project Will *Not* Solve

- **Customer portal** — Stripe provides a hosted portal for users to manage their subscription. We link to it.
- **Multiple plans** — we have one price ID. Multiple plans are out of scope.
- **Trials** — Stripe supports free trials. We don't use them.
- **Coupons** — Stripe supports discount codes. We don't use them.
- **Invoicing** — out of scope.
- **Tax** — Stripe handles tax via Stripe Tax. We don't configure it.
- **Refunds** — handled via the Stripe dashboard.

## The Question This Project Answers

> *"How do I charge for premium features?"*

If you can answer: "use Stripe Checkout for hosted payment, receive webhooks for events, update the user's subscription status in our database," you are ready for project 36.
