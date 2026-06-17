# 15 — Expense Tracker

Same CRUD. New thing: a **summary endpoint** that calculates totals.

## Run it

```bash
npm install
node server.js
```

```bash
# Add some expenses
curl -X POST http://localhost:3000/expenses -H "Content-Type: application/json" -d '{"amount": 50, "category": "food"}'
curl -X POST http://localhost:3000/expenses -H "Content-Type: application/json" -d '{"amount": 30, "category": "transport"}'
curl -X POST http://localhost:3000/expenses -H "Content-Type: application/json" -d '{"amount": 20, "category": "food"}'

# Get the summary (NEW!)
curl http://localhost:3000/summary
# { "total": 100, "count": 3, "byCategory": { "food": 70, "transport": 30 } }
```

## How to think about it

Most apps have one or two "summary" or "stats" endpoints. They don't fit the CRUD pattern — they're aggregations. The pattern: loop through everything, accumulate a result, return it.

## How to build it (line by line)

```js
const total = expenses.reduce((sum, e) => sum + e.amount, 0);
```

**Line 27.** Add up all the amounts. `reduce` is a way to combine an array into a single value. `sum + e.amount` adds each expense's amount to the running sum, starting at 0.

```js
const byCategory = {};
for (const e of expenses) {
  byCategory[e.category] = (byCategory[e.category] || 0) + e.amount;
}
```

**Lines 28-31.** Group by category.

For each expense, add its amount to a running total for that category. `(byCategory[e.category] || 0)` means: if we haven't seen this category before, start at 0.

## What we learned

1. `reduce` combines an array into one value
2. Grouping by a key: build an object, accumulate as you go
3. Summary endpoints are common and don't fit the CRUD pattern
4. We've now built 10 apps — the pattern is automatic

## What's next

In **16-poll-app** we build polls. A poll has a question and a list of options. The new thing: when someone votes, we count the vote. So we have a "vote" endpoint that mutates state in a different way.
