# 02 — Customers (Payments)

Customer records. Save payment methods for future use.

**What's new:**
- `customers` table: id, email, name
- `payment_methods` table: card_last4, brand, exp, is_default
- `POST /customers` — create
- `POST /customers/:id/payment-methods` — add a card
- Card brand detection (Visa, Mastercard, Amex, Discover)

**Why save cards?** Customer adds a card once. They can pay with one click later. Without saving, they'd re-enter their card every purchase.

**Why last 4 + brand?** Display "Visa ending in 4242" — enough to identify. We can't store full numbers (PCI compliance).

**Why a default?** A customer might have multiple cards. The default is used for subscriptions and one-click checkout.

**Brand detection:** Visa starts with 4, Mastercard with 51-55, Amex with 34/37, Discover with 6. The first digits (BIN) tell you the brand.

## Run
```bash
npm install && node server.js
```

```bash
# Create customer
curl -X POST http://localhost:3000/customers -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "name": "Alice"}'
# 201

# Add a Visa
curl -X POST http://localhost:3000/customers/cus_xxx/payment-methods -H "Content-Type: application/json" \
  -d '{"card_number": "4242424242424242", "exp_month": 12, "exp_year": 2025}'
# 201 { brand: "visa", last4: "4242", is_default: true }

# Add an Amex
curl -X POST http://localhost:3000/customers/cus_xxx/payment-methods -H "Content-Type: application/json" \
  -d '{"card_number": "378282246310005", "exp_month": 6, "exp_year": 2026}'
# 201 { brand: "amex", last4: "0005", is_default: false }
```

## What we learned
- Customer records
- Saved payment methods
- Card brand detection (BIN)
- Default payment method
- Last 4 storage

## Next
**03-subscriptions** — recurring charges. Monthly/yearly plans.
