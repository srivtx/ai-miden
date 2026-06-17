# 24 — Water Tracker

Track how much water you drink. Each entry is just an amount in ml. New thing: **filter by date** (today only).

## Run it

```bash
npm install
node server.js
```

```bash
# Log some water
curl -X POST http://localhost:3000/entries -H "Content-Type: application/json" -d '{"amount": 250}'
curl -X POST http://localhost:3000/entries -H "Content-Type: application/json" -d '{"amount": 500}'

# Today's total
curl http://localhost:3000/today
# { "date": "2024-12-15", "total": 750, "count": 2, "entries": [...] }
```

## How to think about it

Same shape as before. The new thing: a date-based filter. We use `string.startsWith` to check if the entry was made today. Real apps use proper date libraries, but for now, simple string matching works.

## How to build it (line by line)

```js
const today = new Date().toISOString().slice(0, 10);
const todayEntries = entries.filter(e => e.date.startsWith(today));
```

**Lines 21-22.** Get today's date as a string, then filter entries that start with that date.

**`e.date.startsWith(today)`** — does the entry's date start with today's date? If yes, it's from today.

## What we learned

1. Date-based filtering is common
2. `String.startsWith` is one way to compare dates as strings
3. We've now seen calendar, range, and date-prefix filters — three date patterns

## What's next

In **25-sleep-tracker** we track sleep. Each entry has bedtime and wake time. We compute duration.
