# 38 — Inventory Tracker

Inventory with a quantity field. Add stock (positive delta) or remove (negative delta). New thing: **delta operations** (add/subtract by a number) and a **low-stock alert**.

## Run it

```bash
npm install
node server.js
```

```bash
# Add an item
curl -X POST http://localhost:3000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Widget", "sku": "W-001", "quantity": 100}'

# Add 50 more
curl -X PATCH http://localhost:3000/items/1/adjust \
  -H "Content-Type: application/json" \
  -d '{"delta": 50}'

# Remove 30
curl -X PATCH http://localhost:3000/items/1/adjust \
  -H "Content-Type: application/json" \
  -d '{"delta": -30}'

# Low stock check
curl 'http://localhost:3000/low-stock?threshold=20'
```

## How to think about it

When a number can go up and down, we use a delta (the change) instead of a replacement (the new value). `quantity: 50` says "the new value is 50." `delta: -30` says "subtract 30 from the current value."

This is how every "add to cart" or "increment" works behind the scenes.

## How to build it (line by line)

```js
item.quantity += delta;
if (item.quantity < 0) item.quantity = 0; // Never negative
```

**Lines 23-24.** Apply the delta. Then cap at 0 — quantity can't go below 0.

**Why cap?** Removing stock below 0 is a bug. We protect the data.

## What we learned

1. Delta operations: change by a number, not replace
2. We protect data integrity (no negative quantities)
3. Threshold queries: find items below X
4. We've now seen 5+ different aggregation patterns

## What's next

In **39-resume-builder** we build a resume. Has sections: experience, education, skills. New thing: replacing the whole resume (PUT).
