# 08 — Segments (Analytics)

Define user segments. "Users who purchased in the last 30 days in the US."

**What's new:**
- Segment rule: country, plan, signup_after, did_event
- Preview endpoint: who matches this rule
- Stats endpoint: distribution by country, plan

**Why segments?** Marketing: target the right people. Product: understand which features work for which users. Support: prioritize high-value customers. Without segments, you treat everyone the same.

**The rule:** a list of conditions. The user matches if all conditions are true. Build the SQL dynamically from the rule.

## Run
```bash
npm install && node server.js
```

```bash
# US users on pro plan
curl -X POST http://localhost:3000/segments/preview -H "Content-Type: application/json" \
  -d '{"country": "US", "plan": "pro"}'

# Users who purchased
curl -X POST http://localhost:3000/segments/preview -H "Content-Type: application/json" \
  -d '{"did_event": "purchase"}'

# Stats
curl -X POST http://localhost:3000/segments/stats -H "Content-Type: application/json" \
  -d '{"country": "US"}'
# { count: 20, by_country: { US: 20 }, by_plan: { free: 7, pro: 7, enterprise: 6 } }
```

## What this stage teaches
- Dynamic SQL building
- Segment definition
- Subqueries for "users who did X"
- Aggregation on filtered sets

## Next
**09-ab-tests** — A/B testing. Show variant A to some users, B to others. Measure which works.
