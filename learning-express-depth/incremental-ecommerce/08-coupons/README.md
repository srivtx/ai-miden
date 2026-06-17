# 08 — Coupons

Discount codes. Apply at checkout, redeem after order, track usage.

**What's new:**
- `coupons` table: code, type (percent or fixed), value, min order, max uses, expires
- `coupon_redemptions` table: who used what
- `POST /coupons/apply` calculates the discount
- `POST /coupons/:code/redeem` confirms the redemption
- Validation: not expired, not exhausted, not used by this user before

**Why two steps (apply then redeem)?** The cart total might change between applying the coupon and the order being placed. We want to verify the discount at apply time, then commit it at order time.

**Percent vs fixed:** `10% off` vs `$5 off`. We support both.

## Run
```bash
npm install && node server.js
```

```bash
# Create coupons
curl -X POST http://localhost:3000/coupons -H "Content-Type: application/json" \
  -d '{"code": "SAVE10", "type": "percent", "value": 10}'
curl -X POST http://localhost:3000/coupons -H "Content-Type: application/json" \
  -d '{"code": "FIVEOFF", "type": "fixed", "value": 500, "min_order_cents": 5000}'

# Apply a coupon
curl -X POST http://localhost:3000/coupons/apply -H "Content-Type: application/json" \
  -d '{"code": "SAVE10", "subtotal_cents": 10000, "user_id": "alice"}'
# { discount_cents: 1000, total_cents: 9000 }

# Apply with min order not met
curl -X POST http://localhost:3000/coupons/apply -H "Content-Type: application/json" \
  -d '{"code": "FIVEOFF", "subtotal_cents": 1000, "user_id": "alice"}'
# 422 order below minimum

# Confirm the redemption
curl -X POST http://localhost:3000/coupons/SAVE10/redeem -H "Content-Type: application/json" \
  -d '{"user_id": "alice", "order_id": "ord_001"}'

# Try to use again
curl -X POST http://localhost:3000/coupons/apply -H "Content-Type: application/json" \
  -d '{"code": "SAVE10", "subtotal_cents": 10000, "user_id": "alice"}'
# Still works (apply doesn't redeem)
curl -X POST http://localhost:3000/coupons/SAVE10/redeem -H "Content-Type: application/json" \
  -d '{"user_id": "alice", "order_id": "ord_002"}'
# 409 already redeemed
```

## What this stage teaches
- Coupon types (percent, fixed)
- Min order requirement
- Max uses and expiration
- Per-user redemption
- Two-phase: apply + redeem

## Next
**09-shipping** — shipping methods, costs, tracking integration.
