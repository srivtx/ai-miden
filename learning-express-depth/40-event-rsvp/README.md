# 40 — Event RSVP

The last project. Events have a list of attendees. People can RSVP yes, no, or maybe. New thing: **updating an existing entry** (the same person can change their RSVP).

## Run it

```bash
npm install
node server.js
```

```bash
# Create an event
curl -X POST http://localhost:3000/events \
  -H "Content-Type: application/json" \
  -d '{"title": "Birthday party", "date": "2024-12-25T19:00:00Z", "location": "Alice'\''s place"}'

# RSVP yes
curl -X POST http://localhost:3000/events/1/rsvp \
  -H "Content-Type: application/json" \
  -d '{"name": "Bob", "status": "yes"}'

# Change RSVP to maybe
curl -X POST http://localhost:3000/events/1/rsvp \
  -H "Content-Type: application/json" \
  -d '{"name": "Bob", "status": "maybe"}'

# See the event with attendees
curl http://localhost:3000/events/1
# { "id": 1, "title": "...", "attendees": [{ "name": "Bob", "status": "maybe", ... }] }
```

## How to think about it

A common pattern: an action that creates OR updates. If the person already RSVPed, replace their entry. If not, add a new one. We do this by removing the old entry first, then adding the new one.

## How to build it (line by line)

```js
event.attendees = event.attendees.filter(a => a.name !== name);
event.attendees.push({ name, status, rsvpAt: new Date().toISOString() });
```

**Lines 30-31.** Two steps:
1. Remove any existing entry for this person
2. Add the new entry

**Why two steps?** If the person already RSVPed, we want to update their entry, not add a second one. So we remove first.

**`filter`** keeps everyone whose name is NOT the one we're updating. After this, the person is gone from the list. Then we add them back with the new status.

## What we learned

1. Update-or-create pattern: remove old, add new
2. The action endpoint is `/rsvp`, not `/attendees`
3. We've now built 40 small apps

## The end of the sequence

You've built 40 small apps. The patterns you've seen:

- **CRUD** (every app)
- **Filtering** by string, by date range, by enum
- **Aggregation** (sum, average, count, distribution)
- **Validation** (range, enum, type)
- **Nesting** (one level, two levels)
- **Uniqueness** checks
- **Hashing** (don't store plain text)
- **Actions** (vote, submit, move, rsvp)
- **PUT vs PATCH** (full vs partial)
- **Redirects**
- **Date math**
- **Lookup by non-id**

You have the structure now. You can build anything.

When you're ready, take any of these 40 apps and add:
- A database (so data survives restarts)
- User accounts (so each user has their own data)
- Tests (so you can change code without breaking)
- Error handling (graceful failures)
- Rate limiting (so people can't hammer the API)
