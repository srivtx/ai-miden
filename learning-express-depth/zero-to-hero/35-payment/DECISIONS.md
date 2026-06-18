# The Decisions

> *"Stripe handles the card. We handle the subscription status. Webhooks connect them."*

## Decision 1: Stripe and not other processors

**Alternatives**:
- **Paddle** — Merchant of Record. Handles tax.
- **LemonSqueezy** — Similar to Paddle.
- **PayPal** — Older, more friction.
- **Braintree** — PayPal's developer-friendly product.

**Why Stripe: Standard. Best DX. Best docs. Best webhooks. Widest coverage. The de-facto choice for SaaS.

**Trade-off**: Vendor lock-in. We accept it.

## Decision 2: Checkout and not Elements

**Alternative**: Stripe Elements (embed card form in your site).

**Why Checkout: Hosted page. Simpler. We never see the card. PCI compliance is automatic.

**Trade-off**: Less control over the UI. We accept it.

## Decision 3: Subscriptions and not one-time payments

**Alternative**: One-time payments.

**Why subscriptions: SaaS model. Recurring revenue. Standard for our use case.

**Trade-off**: More complex lifecycle (active, past due, canceled, etc.). We handle it.

## Decision 4: Webhook for subscription events

**Alternative**: Poll Stripe's API to check the subscription status.

**Why webhook: Real-time. Efficient. Standard. We get events as they happen.

**Trade-off**: We need a webhook endpoint. We add it.

## Decision 5: Signature verification

**Alternative**: Trust the webhook without verification.

**Why verify: Security. Anyone can POST to our webhook URL. We verify the signature to ensure it's from Stripe.

**Trade-off**: Slightly more complex. We accept it.

## Decision 6: No customer portal link

**Alternative**: Add a `POST /subscriptions/portal` endpoint that returns a Stripe portal URL.

**Why no: Out of scope. The user can manage via the Stripe dashboard.

**Trade-off**: Slightly less convenient for the user. We accept it.

## Decision 7: No tax handling

**Alternative**: Configure Stripe Tax.

**Why no: Out of scope. Stripe Tax handles VAT, GST, etc. We don't configure it.

**Trade-off**: We might not be collecting the right amount of tax. Acceptable for the demo.

## Decision 8: No refunds endpoint

**Alternative**: Add a `POST /subscriptions/:id/refund` endpoint.

**Why no: Out of scope. Refunds are handled via the Stripe dashboard.

**Trade-off**: Refunds are manual. We accept this.

## Decision 9: No trials

**Alternative**: Free trials (Stripe supports them).

**Why no: Out of scope. We have one plan, no trial.

**Trade-off**: Users can't try before they buy. We accept this.

## Decision 10: No multiple plans

**Alternative**: Multiple price IDs (basic, pro, enterprise).

**Why no: Out of scope. We have one price.

**Trade-off**: Can't offer different tiers. We accept this.

---

## What We Did Not Decide

- **Multiple plans** — out of scope
- **Trials** — out of scope
- **Coupons** — out of scope
- **Customer portal link** — out of scope
- **Refunds endpoint** — out of scope
- **Tax handling** — out of scope
- **Invoicing** — out of scope
- **Per-seat pricing** — out of scope
- **Usage-based pricing** — out of scope
- **Multi-currency** — out of scope

Each is a future decision.

---

## The Meta-Decision: The Server Can Charge

For 34 projects, the app was free. No way to monetize.

Now the server can charge. Stripe Checkout handles the card. Webhooks update the subscription. The user can upgrade to premium.

This is the foundation of *payments*. From here, every project that needs to charge for features can use Stripe. The patterns (Checkout, webhooks, signature verification) are universal.

The next 5 projects will assume payments exist. The path diverges:

- **Tests** (project 36): automated
- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The server can charge. The path continues.
