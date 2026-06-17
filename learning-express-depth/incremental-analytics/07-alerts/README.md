# 07 — Alerts (Analytics)

Define alert rules. When a metric crosses a threshold, fire.

**What's new:**
- `alert_rules` table: name, metric, operator, threshold, window
- Create, list, disable
- Evaluate endpoint (called by a cron job every minute or so)
- Alert history

**Why alerts?** Without alerts, you only know about problems when a customer tells you. With alerts, you know the moment something goes wrong: error rate spike, traffic drop, conversion drop.

**The flow:**
1. Define rules: "alert if errors > 100 in 5 minutes"
2. A cron job calls `/alerts/evaluate` every minute
3. For each rule, query the metric over the window
4. If it crosses the threshold, log it and notify

**Why separate evaluation?** Alert rules are slow to evaluate (queries over big data). You don't want to run them on every event. Run them periodically.

## Run
```bash
npm install && node server.js
```

```bash
# Create a rule
curl -X POST http://localhost:3000/alerts -H "Content-Type: application/json" \
  -d '{"name": "Error spike", "metric": "error_rate", "operator": ">", "threshold": 0.05, "window_minutes": 5}'

# Track some events (some errors)
for i in {1..10}; do
  curl -X POST http://localhost:3000/track -H "Content-Type: application/json" -d '{"event_name": "error"}'
done

# Evaluate
curl -X POST http://localhost:3000/alerts/evaluate
# { evaluated: 1, fired: 1, alerts: [{ name: "Error spike", value: 1, threshold: 0.05 }] }

# History
curl http://localhost:3000/alerts/history
```

## What this stage teaches
- Rule-based alerts
- Operator overloading (`>`, `<`, `>=`, `<=`)
- Windowed queries
- Periodic evaluation pattern

## Next
**08-segments** — define user segments. "Users who bought last week."
