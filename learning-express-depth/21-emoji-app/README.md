# 21 — Emoji App

A list of emojis. Search by name. Get a random one. New thing: **search with substring matching** (not exact match).

## Run it

```bash
npm install
node server.js
```

```bash
# All emojis
curl http://localhost:3000/emojis

# Search by name (substring)
curl 'http://localhost:3000/emojis?q=hea'
# Matches "heart" and "heart eyes"

# Random emoji
curl http://localhost:3000/emojis/random
# { "char": "🔥", "name": "fire" }
```

## How to think about it

This is a read-only app with search. The data is hardcoded. The new thing: substring search with `String.includes`. The client's query is part of the URL — `q=hea` matches anything containing "hea."

## How to build it (line by line)

```js
result = result.filter(e => e.name.toLowerCase().includes(q.toLowerCase()));
```

**Line 23.** Substring search. `includes` returns true if the string contains the search term.

**`q.toLowerCase()`** makes the search case-insensitive. So "Hea", "hea", "HEA" all match "heart."

**`e.name.toLowerCase()`** does the same to the name we're checking against.

## What we learned

1. Substring search is everywhere — search boxes, filters
2. `String.includes` is the simplest way to do it
3. Lowercasing both sides makes it case-insensitive
4. We've now seen substring search — another list-endpoint pattern

## What's next

In **22-mood-journal** we build a mood journal. Each entry has a mood, a note, and a date. We can list, add, and see averages.
