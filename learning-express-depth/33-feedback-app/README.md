# 33 — Feedback App

A feedback form. Submissions have a rating (1-5) and a comment. New thing: **distribution stats** — count how many 1-star, 2-star, etc.

## Run it

```bash
npm install
node server.js
```

```bash
# Submit feedback
curl -X POST http://localhost:3000/feedback -H "Content-Type: application/json" -d '{"rating": 5, "comment": "Great!"}'
curl -X POST http://localhost:3000/feedback -H "Content-Type: application/json" -d '{"rating": 4, "comment": "Good"}'
curl -X POST http://localhost:3000/feedback -H "Content-Type: application/json" -d '{"rating": 5}'

# Stats
curl http://localhost:3000/feedback/stats
# { "average": "4.67", "count": 3, "distribution": { "1": 0, "2": 0, "3": 0, "4": 1, "5": 2 } }
```

## How to think about it

Aggregations can be more than just sum and average. We can build a histogram — count of each value. Useful for ratings, votes, anything with discrete values.

## How to build it (line by line)

```js
const distribution = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
for (const f of submissions) distribution[f.rating]++;
```

**Lines 22-24.** Build a histogram.

**`distribution[1] = 0`** starts each bucket at 0.

**`distribution[f.rating]++`** increments the bucket for this submission's rating.

## What we learned

1. Histograms are useful aggregations
2. We pre-initialize the buckets to 0
3. We've now seen several aggregation patterns

## What's next

In **34-survey-app** we build a survey. A survey has multiple questions, each with options.
