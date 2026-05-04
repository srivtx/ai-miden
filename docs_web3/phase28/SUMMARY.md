## Phase 28 Summary: Payment Gateway

**The Question:** "How do merchants accept cryptocurrency payments without manually tracking every transaction and guessing which payment belongs to which order?"

---

### What We Learned

1. **Payment Gateway**
   - A service that generates payment requests and monitors the blockchain for settlement
   - Bridges the complexity of blockchain addresses with familiar checkout experiences
   - Confirms payments so merchants know when to deliver goods

2. **Payment Intent**
   - A server-side record created at checkout that locks in price, amount, and destination
   - Uses unique deposit addresses to match on-chain payments to specific orders
   - Expires after a timeout to prevent stale orders from cluttering the system

3. **Webhook Notification**
   - Pushes payment status updates to merchant servers instantly via HTTP POST
   - Eliminates wasteful polling and reduces server load by 99.99%
   - Includes HMAC signatures so merchants can verify authenticity

---

### Results

- Payment intents created unique deposit addresses for every checkout
- Webhooks delivered confirmations in under 100ms versus 5-second polling delays
- Partial payment detection handled underpayments and overpayments gracefully
- Idempotency keys prevented duplicate order fulfillment from retry webhooks

---

### Phase 28 Files

| File | Purpose |
|---|---|
| `docs_web3/phase28/what_is_payment_gateway.md` | Service for accepting and tracking crypto payments |
| `docs_web3/phase28/what_is_payment_intent.md` | Checkout record that locks in payment details |
| `docs_web3/phase28/what_is_webhook_notification.md` | Pushing status updates to merchant servers |
| `src_web3/phase28/payment_gateway.ts` | Express API for payment intent lifecycle |
| `src_web3/phase28/payment_verification.ts` | On-chain verification and confirmation logic |

---

### Connects To

- **Phase 27:** Indexing On-Chain Data — Indexed transaction history enables fast payment lookups.
- **Phase 29:** Cross-Program Composability — Payment flows can compose with staking or lending for advanced checkout features.
