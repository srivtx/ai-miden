# 09 — Tax (Payments)

Tax calculation per region. Sales tax, VAT, GST.

**What's new:**
- `tax_rates` table: country, region, rate, type
- Pre-seeded rates for US states, EU countries, etc.
- `POST /tax/calculate` — given an amount and location, return the tax

**Why per-region?** Tax isn't one rate. California is 7.25%, Texas is 6.25%, Delaware is 0%. UK is 20% VAT. Germany is 19%. Australia is 10% GST. Each region has its own rules.

**Why a separate endpoint?** Tax is a pure calculation. No side effects. Easy to test. Real services like TaxJar, Avalara handle this with much more nuance (per product type, exemptions, etc.).

**The "region = ''" pattern:** Some countries have a single national rate (UK, FR, DE). Some have state-level rates (US). We use empty string for "country-wide" and the region for "state-level."

## Run
```bash
npm install && node server.js
```

```bash
# California sales tax
curl -X POST http://localhost:3000/tax/calculate -H "Content-Type: application/json" \
  -d '{"country": "US", "region": "CA", "amount_cents": 10000}'
# { country: "US", region: "CA", type: "sales_tax", rate: 0.0725, tax_cents: 725, total_cents: 10725 }

# UK VAT
curl -X POST http://localhost:3000/tax/calculate -H "Content-Type: application/json" \
  -d '{"country": "GB", "amount_cents": 10000}'
# { country: "GB", type: "vat", rate: 0.20, tax_cents: 2000, total_cents: 12000 }

# Delaware (no sales tax)
curl -X POST http://localhost:3000/tax/calculate -H "Content-Type: application/json" \
  -d '{"country": "US", "region": "DE", "amount_cents": 10000}'
# { rate: 0, tax_cents: 0, total_cents: 10000 }

# Unknown country
curl -X POST http://localhost:3000/tax/calculate -H "Content-Type: application/json" \
  -d '{"country": "XX", "amount_cents": 10000}'
# { rate: 0, note: "no tax rate for region" }
```

## What we learned
- Per-region tax rates
- Sales tax, VAT, GST
- Country vs state granularity
- Pure calculation endpoints
- The hard problem of tax in real life

## Next
**10-fraud** — the final stage. Detect and prevent fraudulent charges.
