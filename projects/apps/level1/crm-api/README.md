# CRM API — Step 18 in the learning path

Builds on Ticket Booking. Adds: companies, contacts, deals with pipeline stages, activity log (calls/emails/meetings/notes).

## Endpoints
```
POST   /companies                  # { name, industry, size, website }
GET    /companies                  # with contact and deal counts

POST   /contacts                   # { first_name, last_name, company_id, email, ... }
GET    /contacts
GET    /contacts/:id               # with deals and recent activities

POST   /deals                      # { contact_id, title, value_cents, stage? }
PATCH  /deals/:id/stage            # { stage: lead|qualified|proposal|negotiation|won|lost }
GET    /pipeline                   # deals grouped by stage, with weighted value

POST   /activities                 # { contact_id, deal_id?, type, subject, body }
```

## Pipeline stages
- `lead` (10% probability)
- `qualified` (25%)
- `proposal` (50%)
- `negotiation` (75%)
- `won` (100%)
- `lost` (0%)

## Try
```bash
# Create a company and contact
CO=$(curl -X POST http://localhost:3000/companies -H "Content-Type: application/json" -d '{"name": "Acme Corp", "industry": "Tech"}' | jq -r .id)
CT=$(curl -X POST http://localhost:3000/contacts -H "Content-Type: application/json" -H "X-User-Id: u_alice" -d "{\"company_id\": \"$CO\", \"first_name\": \"Alice\", \"last_name\": \"Smith\", \"email\": \"alice@acme.com\"}" | jq -r .id)

# Create a deal
curl -X POST http://localhost:3000/deals -H "Content-Type: application/json" -H "X-User-Id: u_alice" -d "{\"contact_id\": \"$CT\", \"title\": \"Annual contract\", \"value_cents\": 1000000, \"stage\": \"qualified\"}"

# Log a call
curl -X POST http://localhost:3000/activities -H "Content-Type: application/json" -H "X-User-Id: u_alice" -d "{\"contact_id\": \"$CT\", \"type\": \"call\", \"subject\": \"Intro call\", \"body\": \"Discussed needs\"}"

# Move to proposal
curl -X PATCH http://localhost:3000/deals/<id>/stage -H "Content-Type: application/json" -d '{"stage": "proposal"}'

# See the full pipeline
curl http://localhost:3000/pipeline
# { stages, summary: [{ stage, count, total_value_cents, weighted_value_cents }], deals: {...} }
```

## What this teaches
1. **Pipeline / funnel**: stage-based progression
2. **Weighted value**: `value * probability` for forecasting
3. **Activity log**: calls/emails/meetings linked to contact and optionally deal
4. **Aggregations across stages**: total value per stage
5. **Enum-like columns**: stage constrained to a known list

## Next project
→ **restaurant-api** — adds: menu, tables, reservations, orders
