# 09 — Shipping

Shipping methods, rates by zone, tracking.

**What's new:**
- `shipping_zones` (US Domestic, International)
- `shipping_methods` (Standard, Express, International)
- Rate calculation: `base + per_kg * weight`
- Country check: method not available everywhere
- Tracking number generation
- Shipment tracking endpoint

**Why zones?** Different countries have different shipping options and rates. US has overnight, international takes a week. We model this with zones.

## Run
```bash
npm install && node server.js
```

```bash
# See all methods
curl http://localhost:3000/shipping/methods

# Calculate for 2kg to US
curl -X POST http://localhost:3000/shipping/calculate -H "Content-Type: application/json" \
  -d '{"method_id": 1, "weight_kg": 2, "country": "US"}'
# { method: "Standard", cost: "7.99" }

# Try international with US-only method
curl -X POST http://localhost:3000/shipping/calculate -H "Content-Type: application/json" \
  -d '{"method_id": 1, "weight_kg": 2, "country": "FR"}'
# 422 not available

# Create a shipment
curl -X POST http://localhost:3000/shipments -H "Content-Type: application/json" \
  -d '{"order_id": "ord_001", "method_id": 2, "weight_kg": 1.5}'
# { id, tracking: "TRK...", cost: 17.99 }

# Track it
curl http://localhost:3000/shipments/TRK...
```

## What this stage teaches
- Shipping zones
- Per-kg pricing
- Country restrictions
- Tracking numbers
- Rate calculation

## Next
**10-recommendations** — the final stage. "Customers who bought X also bought Y."
