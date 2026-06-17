# 05 — Orders

Order lifecycle. Status transitions, history, tracking.

**What's new:**
- Full order state machine: `pending` → `paid` → `shipped` → `delivered` (or `cancelled`/`refunded`)
- Each transition is checked: only valid transitions allowed
- `order_events` log: every transition is recorded
- Tracking number generated when shipped
- 409 Conflict for invalid transitions

**The state machine:**
```
pending → paid → shipped → delivered
   ↓       ↓
cancelled  cancelled / refunded
                  ↓
              returned
```

**Why a state machine?** Without it, an order could go from "pending" to "delivered" without being paid or shipped. The state machine prevents that.

## Run
```bash
npm install && node server.js
```

```bash
# See the seeded order
curl http://localhost:3000/orders/ord_001

# Pay it
curl -X POST http://localhost:3000/orders/ord_001/pay
# { status: "paid" }

# Try to pay again (fails, already paid)
curl -X POST http://localhost:3000/orders/ord_001/pay
# 409 cannot transition

# Ship it
curl -X POST http://localhost:3000/orders/ord_001/ship
# { status: "shipped", tracking: "TRK..." }

# Try to cancel after shipping (fails)
curl -X POST http://localhost:3000/orders/ord_001/cancel
# 409 cannot cancel

# Deliver
curl -X POST http://localhost:3000/orders/ord_001/deliver

# See the full history
curl http://localhost:3000/orders/ord_001
# Includes events: pending → paid → shipped → delivered
```

## What this stage teaches
- State machines
- Valid transitions only
- Order event log
- Tracking numbers
- 409 for invalid state changes

## Next
**06-inventory** — track stock. Don't oversell. Decrement on order, restore on cancel.
