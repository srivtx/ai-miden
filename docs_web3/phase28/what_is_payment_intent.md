# What is a Payment Intent?

## Why It Exists

When a customer decides to pay, the merchant needs a temporary record that locks in the price, amount, and destination before the blockchain transaction is broadcast.
Without this record, exchange rate fluctuations, duplicate payments, and timing confusion create chaos at checkout.
The intent serves as the contract between buyer and seller before any blockchain activity begins.
It is the anchor that prevents payments from drifting into ambiguity.
Without intents, merchants would have no way to correlate on-chain payments with specific orders.

## Definition

A payment intent is a server-side object created at checkout that captures the expected payment amount, currency, destination address, expiration time, and order metadata.
It serves as the source of truth while the customer completes the on-chain transfer.
The intent exists independently of the blockchain transaction.
It is the bridge between the shopping cart and the blockchain.
The intent transforms a volatile payment process into a structured workflow.
This structure is what makes automated payment processing possible at scale.
Payment intents are the foundational data model for any serious crypto commerce platform.

## Real-Life Analogy

Imagine ordering a custom cake.
The bakery writes an order slip with your name, cake flavor, price, and pickup time.
That slip is your payment intent.
It exists before you hand over cash.
If chocolate prices spike an hour later, the slip still says $30.
If someone else walks in asking for the same cake, they get a new slip with a new number.

The slip keeps everything organized and prevents arguments about what was promised.
Without the slip, the bakery would have no idea who ordered what.
The slip is the source of truth.
The baker can reference it at any time to verify your order.
When you pay, the cashier matches your cash to the slip, not to your face.

## Tiny Numeric Example

Three customers check out simultaneously.

| Customer | Amount | Address | Status | Expires In |
|---|---|---|---|---|
| Alice | 1.5 SOL | Gx7a... | pending | 15 min |
| Bob | 2.0 SOL | Ht9b... | pending | 15 min |
| Carol | 1.5 SOL | Jk3c... | pending | 15 min |

Each gets a unique address even though Alice and Carol pay the same amount.
The gateway matches transactions to intents by address, not by amount alone.
This prevents the common problem of matching the wrong payment to the wrong order.
The unique address acts as a receipt number.
Merchants can trace every payment back to its originating order with complete certainty.
This traceability is essential for accounting, refunds, and customer support.
If Alice pays from an exchange that deducts fees, the gateway detects the partial payment.

## Common Confusion

- **"Is a payment intent a transaction?"** No. The intent is a database record. The transaction is the on-chain transfer that fulfills the intent.
- **"Does creating an intent cost money?"** No. It is a free database operation. Only the customer's on-chain transaction pays fees.
- **"What happens when the intent expires?"** The address is released, the order is marked expired, and the merchant knows not to expect payment.
- **"Can I reuse an address from an expired intent?"** In production, addresses are single-use for privacy. Reusing them links customer payments together.
- **"Why not just use the customer's wallet address as the identifier?"** Multiple payments from the same customer would be indistinguishable. Unique destination addresses solve this.
- **"Does the intent lock the exchange rate?"** It can. The intent records the expected amount in SOL. If the merchant prices in USD, the intent captures the SOL equivalent at checkout time.
- **"What if the customer sends from an exchange?"** Exchanges sometimes send from different addresses or deduct fees from the amount. The gateway must handle these edge cases.
- **"Can intents be cancelled?"** Yes. Merchants can cancel pending intents, which stops monitoring and frees the address.
- **"What metadata can an intent store?"** Order ID, customer email, product SKU, callback URL, and custom fields for CRM integration.

## Key Properties

- **Immutability:** Once created, the intent locks in the expected amount and currency to prevent price drift during payment.
- **Uniqueness:** Generates a one-time deposit address so each payment can be matched to exactly one order.
- **Expiration:** Defines a deadline after which the intent is void and the address is recycled.
- **Traceability:** Links on-chain transactions to off-chain orders through signatures and metadata.
- **Flexibility:** Supports partial payments, overpayments, and underpayments with clear status transitions.
- **Observability:** Provides logging, metrics, and health checks for monitoring system behavior and debugging issues.
- **Composability:** Works seamlessly with other infrastructure components like load balancers, databases, and messaging queues.
- **Extensibility:** Supports plugins and middleware so developers can customize behavior without modifying core code.

## Key Properties
## Where It Appears in Our Code

`src_web3/phase28/payment_gateway.ts` defines the `PaymentIntent` interface and implements POST /intents to create new payment intents with unique deposit addresses.
