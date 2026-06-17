# 12 — Calendar App

Events have a `startTime` and `endTime`. The new thing: **range queries** with `?from=` and `?to=`.

## Run it

```bash
npm install
node server.js
```

```bash
# Add some events
curl -X POST http://localhost:3000/events \
  -H "Content-Type: application/json" \
  -d '{"title": "Standup", "startTime": "2024-01-15T09:00:00Z", "endTime": "2024-01-15T09:30:00Z"}'

curl -X POST http://localhost:3000/events \
  -H "Content-Type: application/json" \
  -d '{"title": "Lunch", "startTime": "2024-01-20T12:00:00Z", "endTime": "2024-01-20T13:00:00Z"}'

# Get all events
curl http://localhost:3000/events
# { "count": 2, "events": [...] }

# Get events in January
curl 'http://localhost:3000/events?from=2024-01-01&to=2024-01-31'
# { "count": 2, ... }

# Get events in February (none)
curl 'http://localhost:3000/events?from=2024-02-01&to=2024-02-28'
# { "count": 0, "events": [] }
```

## How to think about it

A list endpoint that doesn't let you filter by date is useless for a calendar. Range queries are everywhere:
- Calendar: events between two dates
- Bank: transactions between two dates
- Logs: errors in the last hour
- Sales: orders in Q1

The pattern is the same: client sends `?from=X&to=Y`, server filters.

## How to build it (line by line)

```js
if (from) {
  const fromDate = new Date(from);
  result = result.filter(e => new Date(e.startTime) >= fromDate);
}
```

**Lines 11-14.** Filter events that start on or after `from`.

**`new Date(from)`** — convert the string to a Date object. The string is in ISO format like `"2024-01-15T09:00:00Z"`. Date objects can be compared with `>=` and `<=`.

**Why create a new Date for `from`?** We do it once outside the filter. Otherwise we'd convert it for every event. (For 1000 events, that's 1000 conversions. For 1, that's fine either way.)

**`new Date(e.startTime) >= fromDate`** — is this event's start time at or after the from date? If yes, keep it.

## What we learned

1. Range queries are everywhere — dates, numbers, anything ordered
2. `new Date(string)` parses ISO date strings
3. Date objects can be compared with `>=`, `<=`
4. Both filters (`from` and `to`) are optional
5. We've now seen filtering by category, range by date — same pattern

## What's next

In **13-contacts-app** we build a contact list. Contacts have name, email, phone. New thing: we look up by email, which should be unique.
