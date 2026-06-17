# 03 — Funnels (Analytics)

Track a sequence of events. "Of people who visited /home, how many signed up?"

**What's new:**
- Funnel definitions: ordered list of event names
- Compute funnel: how many users reached each step
- Drop-off: how many fell off at each step
- Conversion rates (from first step, from previous step)

**Why funnels?** The most important question for any business: "where do users drop off?" If 1000 people see the pricing page, 100 click "buy," 10 actually pay — your checkout is broken.

**The query:** for each step, count distinct users who did this step AND all previous steps. The intersection tells you how many completed the full path.

## Run
```bash
npm install && node server.js
```

```bash
# Track some events
for i in {1..10}; do
  curl -X POST http://localhost:3000/track -H "Content-Type: application/json" -d '{"user_id": "u'$i'", "event_name": "page_view"}'
done

# 5 of them click signup
for i in {1..5}; do
  curl -X POST http://localhost:3000/track -H "Content-Type: application/json" -d '{"user_id": "u'$i'", "event_name": "click_signup"}'
done

# 2 of them complete signup
for i in {1..2}; do
  curl -X POST http://localhost:3000/track -H "Content-Type: application/json" -d '{"user_id": "u'$i'", "event_name": "account_created"}'
done

# Get the funnel
curl http://localhost:3000/funnels/signup
# {
#   funnel: "signup",
#   steps: [
#     { step: 1, event: "page_view", count: 10, conversion_from_first: 100 },
#     { step: 2, event: "click_signup", count: 5, conversion_from_first: 50, drop_off: 5 },
#     { step: 3, event: "account_created", count: 2, conversion_from_first: 20, drop_off: 3 }
#   ]
# }
```

## What this stage teaches
- Funnel definition and computation
- Drop-off and conversion rates
- Subqueries for "users who did all of these"
- The most important analytics query

## Next
**04-cohorts** — group users by when they signed up. Track retention over time.
