# 01 — Messages (Chat)

A simple chat. One room, one timeline. Messages in, messages out.

**What's here:**
- Send a message: `POST /messages`
- List messages: `GET /messages?limit=50&before=N`
- Delete a message
- Cursor-based pagination (load older messages by passing the last id)

**Why `before` instead of `page`?** Same reason as in the todo app: cursor pagination is fast at any depth. Page pagination gets slow as you go back.

## Run
```bash
npm install && node server.js
```

```bash
# Send
curl -X POST http://localhost:3000/messages -H "Content-Type: application/json" \
  -d '{"sender": "alice", "text": "Hello!"}'

# List
curl http://localhost:3000/messages

# Get older (load messages before id 5)
curl 'http://localhost:3000/messages?before=5&limit=20'
```

## What this stage teaches
- Cursor pagination
- Message ordering
- Real-time-feeling without websockets (we'll add those later)

## Next
**02-rooms** — multiple rooms/channels. Messages belong to rooms.
