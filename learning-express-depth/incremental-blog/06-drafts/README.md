# 06 — Drafts

Auto-save as you type, schedule for later, draft list.

**What's new:**
- New status: `scheduled` (publish at a future date)
- `last_autosave_at` timestamp
- Auto-save endpoint (called by the editor every few seconds)
- Schedule endpoint with future-date validation
- Publish / unpublish actions

**Why auto-save?** Writers lose work. A network hiccup, browser crash, accidentally closing the tab. Auto-save means the worst case is losing a few seconds.

**Why schedule?** Time zones, marketing strategy, "post at 9am on Tuesday." You can write on Sunday, schedule for Tuesday morning.

**The flow:**
1. Writer creates a draft (always starts as draft)
2. Editor calls autosave every 5-10 seconds
3. Writer schedules for a specific date, or publishes immediately
4. A background job (next stage?) actually publishes scheduled posts

## Run
```bash
npm install && node server.js
```

```bash
# Create a draft
T=$(curl -X POST http://localhost:3000/posts -H "Content-Type: application/json" \
  -d '{"title": "My Post", "author_id": "u_alice"}')
ID=$(echo $T | grep -o '"id":[0-9]*' | cut -d: -f2)

# Auto-save
curl -X PATCH http://localhost:3000/posts/$ID/autosave -H "Content-Type: application/json" \
  -d '{"body": "Working on it..."}'

# Schedule for tomorrow
curl -X POST http://localhost:3000/posts/$ID/schedule -H "Content-Type: application/json" \
  -d '{"scheduled_for": "2025-12-31T09:00:00Z"}'

# Publish now
curl -X POST http://localhost:3000/posts/$ID/publish
```

## What this stage teaches
- Auto-save pattern
- Scheduled posts
- Status transitions
- Future-date validation

## Next
**07-revisions** — every save creates a revision. See history, restore old versions.
