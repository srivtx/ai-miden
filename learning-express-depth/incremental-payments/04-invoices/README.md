# 04 — Invoices (Payments)

Generate invoices. Line items, subtotal, tax, total. PDF-ready.

**What's new:**
- `invoices` table: number (INV-1001), status, totals
- `invoice_items` table: description, quantity, unit_price
- Auto-numbering (INV-1001, INV-1002, ...)
- 8% tax calculation
- Status: draft → paid
- Due date (optional)

**Why line items?** An invoice can have many products. Each is a row: description, quantity, unit price, total. The sum of all lines is the subtotal.

**Why tax?** Required by law in most places. Calculated on the subtotal. We use 8% as a flat rate; real systems vary by jurisdiction.

**Why invoice number?** Sequential, unique, human-readable. Customers reference it. Internal accounting uses it. It's required on every real invoice.

## Run
```bash
npm install && node server.js
```

```bash
# Create
curl -X POST http://localhost:3000/invoices -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cus_alice",
    "due_days": 30,
    "items": [
      {"description": "Pro plan", "quantity": 1, "unit_price_cents": 1999},
      {"description": "Add-on", "quantity": 2, "unit_price_cents": 500}
    ]
  }'
# 201 { id, number: "INV-1001", subtotal: 2999, tax: 240, total: 3239 }

# Get the invoice
curl http://localhost:3000/invoices/inv_xxx
# { items: [...], ... }

# Mark as paid
curl -X POST http://localhost:3000/invoices/inv_xxx/pay
# { paid: true }
```

## What we learned
- Invoice line items
- Tax calculation
- Auto-numbering
- Status (draft → paid)
- PDF-ready data structure

## Next
**05-refunds** — refund a charge. Full or partial. Track the reason.
