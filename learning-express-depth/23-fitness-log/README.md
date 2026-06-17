# 23 — Fitness Log

A fitness log. Each entry: exercise, sets, reps, weight. New thing: **computed total** (sets × reps × weight = volume).

## Run it

```bash
npm install
node server.js
```

```bash
# Add a log
curl -X POST http://localhost:3000/logs \
  -H "Content-Type: application/json" \
  -d '{"exercise": "squat", "sets": 3, "reps": 10, "weight": 100}'

# Get the total volume
curl http://localhost:3000/volume
# { "totalVolume": 3000, "count": 1 }
# 3 sets × 10 reps × 100 weight = 3000
```

## How to think about it

Aggregations show up in many apps. The pattern: take a list, combine it into one number. We use `reduce` to walk through and accumulate.

## How to build it (line by line)

```js
const total = logs.reduce((s, l) => s + l.sets * l.reps * (l.weight || 0), 0);
```

**Line 23.** Sum up the volume. For each log `l`, compute `sets * reps * weight` and add to the running total `s`.

**`(l.weight || 0)`** — if weight is missing or 0, use 0. Prevents `undefined * 10 = NaN`.

## What we learned

1. `reduce` is the standard way to combine a list into one value
2. We can do math inside `reduce`
3. Default values prevent `NaN`
4. We've now seen aggregation in 2 different apps

## What's next

In **24-water-tracker** we build a water tracker. Each entry is just an amount. We add up the total for today.
