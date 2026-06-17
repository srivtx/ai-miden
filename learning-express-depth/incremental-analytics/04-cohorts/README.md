# 04 — Cohorts (Analytics)

Group users by when they signed up. Track retention over time.

**What's new:**
- `users` table with `signup_date`
- Group users into weekly cohorts
- For each cohort, compute retention (% still active each week)
- Returns a retention matrix

**Why cohorts?** "Are we getting better at retention?" You can't tell from a single number. With cohorts, you can see: "users who signed up in week 1 retained 80%, week 2 retained 60%, week 3 retained 50% — getting worse." Or: "week 3 is 70% — better than week 1." Trends become visible.

**Why by week?** Common unit. Could be daily (more granular) or monthly (longer trends). Weekly is the standard for most products.

## Run
```bash
npm install && node server.js
```

```bash
# Get the retention matrix
curl http://localhost:3000/cohorts/retention
# {
#   cohorts: [
#     { cohort: "2024-49", size: 10, retention: [
#       { week: 0, count: 10, percent: 100 },
#       { week: 1, count: 8, percent: 80 },
#       { week: 2, count: 6, percent: 60 },
#       { week: 3, count: 5, percent: 50 }
#     ] }
#   ]
# }
```

## What this stage teaches
- Cohort analysis
- Retention curves
- Date-based grouping
- The retention matrix pattern

## Next
**05-dashboards** — pre-computed metrics, served fast. The data that powers the dashboard.
