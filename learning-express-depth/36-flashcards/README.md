# 36 — Flashcards

Flashcards with a question, answer, and status (new / known / review).

## Run it

```bash
npm install
node server.js
```

```bash
# Add cards
curl -X POST http://localhost:3000/cards -H "Content-Type: application/json" -d '{"question": "Capital of France?", "answer": "Paris"}'
curl -X POST http://localhost:3000/cards -H "Content-Type: application/json" -d '{"question": "2 + 2?", "answer": "4"}'

# Filter by status
curl 'http://localhost:3000/cards?status=new'

# Mark as known
curl -X PATCH http://localhost:3000/cards/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "known"}'
```

## How to think about it

Same shape, different domain. The status field has three values. We've seen this before (books, bugs, todos). The pattern is: things have a state, and we change the state with PATCH.

## How to build it (line by line)

Same as the bug tracker, but with fewer fields. The new thing is the `status` field starting as 'new' by default. The client doesn't send it; the server sets it.

## What we learned

1. Default field values are set in the server, not the client
2. The pattern: a few fields from the client, a few defaults from the server
3. We've now seen this pattern in many apps

## What's next

In **37-kanban-board** we build a Kanban board. Cards have a column (todo/in_progress/done). We can move them between columns.
