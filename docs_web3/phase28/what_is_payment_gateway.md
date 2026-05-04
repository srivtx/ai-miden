# What is a Payment Gateway?

## Why It Exists

Merchants and applications want to accept cryptocurrency payments, but blockchain infrastructure is complex.
Customers do not want to manually copy addresses, calculate amounts, or wait uncertain confirmation times.
A payment gateway bridges the gap between traditional checkout flows and blockchain settlements.
It handles address generation, amount tracking, and confirmation logic.
Without a gateway, merchants would manually check explorers and guess which payment belongs to which order.
This manual process is error-prone and does not scale.

## Definition

A payment gateway is a service that generates payment requests, monitors the blockchain for incoming transactions that match those requests, and confirms settlement to the merchant so goods or services can be delivered.
The gateway acts as an automated cashier for blockchain payments.
It translates the chaos of blockchain transactions into orderly business events.
It is the bridge between e-commerce and decentralized finance.
A well-designed gateway makes crypto payments feel as seamless as credit card transactions.

## Real-Life Analogy

Imagine paying at a restaurant.
Instead of walking into the kitchen to hand cash directly to the chef, you tell the waiter what you want.
The waiter writes an order, brings you a bill with a specific table number, and checks the register to confirm your payment.
Only then does the kitchen start cooking.

The payment gateway is the waiter.
It takes the order, presents a clear bill, watches for payment, and tells the merchant when it is safe to proceed.
The customer never interacts directly with the kitchen.
The waiter ensures the right meal goes to the right table.
Without the waiter, the kitchen would be chaos.
The waiter also handles special requests and resolves payment disputes.

## Tiny Numeric Example

A customer buys an NFT for 2.5 SOL.

| Step | Gateway Action | Time |
|---|---|---|
| 1. Create payment intent | Generate unique deposit address | 50ms |
| 2. Customer pays | Send 2.5 SOL to address | 2-5s |
| 3. Detect on-chain | Poll RPC for transaction | 5s |
| 4. Confirm | 1 confirmation received | 400ms |
| 5. Notify merchant | Webhook fired | 100ms |
| Total | | ~8 seconds |

Without a gateway, the merchant would manually check an explorer, guess which payment belongs to which order, and risk delivering goods to the wrong customer.
The gateway automates this entire flow.
It also handles partial payments and overpayments gracefully.
The merchant receives a clean API notification instead of raw blockchain data.
This abstraction lets merchants focus on their business rather than blockchain mechanics.
A mature payment gateway handles edge cases that would overwhelm manual processing.

## Common Confusion

- **"Isn't this just a wallet?"** No. A wallet holds keys and signs transactions. A gateway generates addresses, tracks payments, and notifies merchants.
- **"Does the gateway hold funds?"** Non-custodial gateways do not hold funds. They only monitor and confirm. Custodial gateways hold funds temporarily.
- **"Why not just share a static address?"** Static addresses make it impossible to match payments to specific orders. Unique addresses per payment solve this.
- **"Is this centralized?"** The gateway service is centralized, but settlement happens on the decentralized chain. Users can always verify on-chain.
- **"What if the customer sends the wrong amount?"** Good gateways detect partial payments, overpayments, and underpayments, then notify both parties.
- **"Do I need this for peer-to-peer payments?"** No. P2P payments work fine with direct wallet transfers. Gateways help merchants processing many orders.
- **"How is this different from a payment processor like Stripe?"** Stripe handles fiat. Crypto payment gateways handle on-chain assets while providing similar developer APIs.
- **"Can gateways handle refunds?"** Yes, but refunds require the merchant to send funds back to the customer, usually through a separate transaction.
- **"What about multi-currency support?"** Advanced gateways support SOL, USDC, USDT, and even multiple chains, converting everything to the merchant's preferred currency.

## Key Properties

- **Address Generation:** Creates unique deposit addresses for each payment to prevent order confusion and enable precise matching.
- **Transaction Monitoring:** Continuously polls the blockchain to detect incoming payments against open payment intents.
- **Confirmation Logic:** Waits for configurable confirmation levels before marking a payment as complete and triggering fulfillment.
- **Webhook Delivery:** Pushes real-time notifications to merchant systems so they can ship goods instantly upon confirmation.
- **Expiry Handling:** Automatically cancels stale payment intents and releases addresses after a defined timeout period.
- **Observability:** Provides logging, metrics, and health checks for monitoring system behavior and debugging issues.
- **Composability:** Works seamlessly with other infrastructure components like load balancers, databases, and messaging queues.
- **Extensibility:** Supports plugins and middleware so developers can customize behavior without modifying core code.

## Key Properties
## Where It Appears in Our Code

`src_web3/phase28/payment_gateway.ts` implements an Express API that creates payment intents, monitors deposit addresses, and fires webhooks on confirmation.
It includes merchant authentication and expiry handling.
