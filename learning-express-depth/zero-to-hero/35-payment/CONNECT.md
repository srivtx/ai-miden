# The Connect

> *"The server can charge. Now we need tests, Docker, CI/CD, observability, and microservices."*

This project added Stripe payments. The pain of "I can't charge for premium" is solved. Stripe Checkout handles the card. Webhooks update the subscription. The user can upgrade to premium.

The next 5 projects complete Phase 6 (Production):

| # | Project | Pain Answered |
|---|---------|---------------|
| 36 | Tests | "I want to verify everything works automatically." |
| 37 | Container | "I want to deploy reproducibly with Docker." |
| 38 | Pipeline | "I want CI/CD." |
| 39 | Observability | "I want to see metrics." |
| 40 | Microservice | "I want to split into services." |

After these, the server is a production-ready, real-time, role-based, tested, deployed, observed, distributed system. The complete backend for the final artifact.

## What Works

- Stripe Checkout for hosted payment
- Webhook signature verification
- `subscriptions` table
- Status endpoint (`GET /subscriptions/me`)

## What Doesn't Work

### 1. No tests

We can't verify anything works automatically.

**The pain**: Tests. Project 36.

### 2. No Docker

We can't deploy reproducibly.

**The pain**: Container. Project 37.

### 3. No CI/CD

We can't run tests automatically on every commit.

**The pain**: Pipeline. Project 38.

### 4. No observability

We can't see metrics.

**The pain**: Observability. Project 39.

### 5. No microservices

One big monolith.

**The pain**: Microservices. Project 40.

### 6. No customer portal link

The user can't manage their subscription from our app.

**The pain**: Customer portal. Out of scope.

### 7. No refunds endpoint

Refunds are manual via the Stripe dashboard.

**The pain**: Refunds endpoint. Out of scope.

### 8. No tax handling

We might not collect the right amount of tax.

**The pain**: Tax handling. Out of scope (use Stripe Tax).

### 9. No multiple plans

We have one price. Can't offer different tiers.

**The pain**: Multiple plans. Out of scope.

### 10. No trials

Users can't try before they buy.

**The pain**: Trials. Out of scope.

---

## What This Project Forbids Us From Doing

This server can:

- Charge for premium features via Stripe
- Receive webhooks for subscription events
- Verify webhook signatures
- Update the subscription status in the database

It cannot:

- Be tested automatically
- Be deployed reproducibly
- Be observed in production
- Be split into microservices
- Allow users to manage subscriptions from the app
- Issue refunds
- Handle taxes
- Offer multiple plans
- Offer trials

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 36 | Tests | "I want to verify everything works automatically." |
| 37 | Container | "I want to deploy reproducibly with Docker." |

Project 36 is the natural next step. We have a working server. Now we need to verify it works automatically.

---

## What You Should Do Now

1. **Read the code.** Notice the Stripe client, the Checkout endpoint, the webhook handler, the signature verification. The HTTP handlers are extended.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Set up Stripe test mode.** Get the test keys.
4. **Create a Checkout session.** Open the URL. Use a test card.
5. **Verify the webhook.** Use the Stripe CLI to forward webhooks to localhost.
6. **When you are ready**, move to [Project 36: Tests](../36-tests/).
7. **If anything is unclear**, do not proceed. Payments are the foundation of monetization. They must be solid.

---

## A Note on the Bigger Picture

You now have a server that can charge for premium features. The app is monetizable. The integration is real, secure, and reliable.

From here, the path diverges into the final 5 projects of Phase 6 (Production):

- **Tests** (project 36): automated
- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The server can charge. The path continues.
