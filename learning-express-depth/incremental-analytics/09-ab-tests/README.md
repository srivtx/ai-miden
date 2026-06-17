# 09 — A/B Tests (Analytics)

A/B testing. Assign users to variants. Measure which works.

**What's new:**
- `experiments` table: name, variants (array)
- `assignments` table: user_id, experiment_id, variant
- `conversions` table: who converted
- Deterministic assignment by hash (same user always gets the same variant)
- Results endpoint: conversion rate per variant

**Why A/B test?** Instead of guessing, you measure. "Will users click this button more if it's blue?" Make it blue for half the users, red for the other half. Wait a week. See which got more clicks.

**Why deterministic by hash?** Same user always gets the same variant. If a user reloads the page, they don't flip between A and B. The hash ensures consistency.

**Why store the assignment?** Once assigned, always assigned. Even if the experiment ends, we know which variant the user saw.

## Run
```bash
npm install && node server.js
```

```bash
# Create an experiment
curl -X POST http://localhost:3000/experiments -H "Content-Type: application/json" \
  -d '{"name": "Button color", "variants": ["red", "blue", "green"]}'

# Assign 100 users
for i in {1..100}; do
  curl -s "http://localhost:3000/experiments/e_xxx/assignment?user_id=u$i" > /dev/null
done

# Convert 20 of them
for i in {1..20}; do
  curl -s -X POST "http://localhost:3000/experiments/e_xxx/conversions" -H "Content-Type: application/json" -d "{\"user_id\": \"u$i\"}" > /dev/null
done

# Results
curl http://localhost:3000/experiments/e_xxx/results
# { results: [
#   { variant: "red", assigned: 33, converted: 8, conversion_rate: 24.2 },
#   { variant: "blue", assigned: 34, converted: 7, conversion_rate: 20.6 },
#   { variant: "green", assigned: 33, converted: 5, conversion_rate: 15.2 }
# ] }
```

## What this stage teaches
- A/B testing concepts
- Deterministic assignment (hash-based)
- Variant allocation
- Conversion measurement

## Next
**10-realtime** — the final stage. Real-time event streams.
