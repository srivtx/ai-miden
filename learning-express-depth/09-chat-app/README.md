# 09 — Chat App

A chat is different from a todo: there are many messages from many users, organized into "rooms."

## Run it

```bash
npm install
node server.js
```

```bash
# Send a message to the "general" room
curl -X POST http://localhost:3000/rooms/general/messages \
  -H "Content-Type: application/json" \
  -d '{"from": "Alice", "text": "Hello everyone!"}'

# Send another to "general"
curl -X POST http://localhost:3000/rooms/general/messages \
  -H "Content-Type: application/json" \
  -d '{"from": "Bob", "text": "Hey Alice"}'

# Send one to a different room
curl -X POST http://localhost:3000/rooms/random/messages \
  -H "Content-Type: application/json" \
  -d '{"from": "Alice", "text": "Different room"}'

# Get messages from "general"
curl http://localhost:3000/rooms/general/messages
# { "room": "general", "count": 2, "messages": [...] }

# Get messages from "random"
curl http://localhost:3000/rooms/random/messages
# { "room": "random", "count": 1, "messages": [...] }
```

## How to think about it

The shape is similar to before — we're still creating and listing things. The new idea is **nesting**: messages belong to rooms. The URL tells us which room: `/rooms/:room/messages`.

This is called "nested resources." Messages are nested inside rooms. We could go further and nest rooms inside users: `/users/:user/rooms/:room/messages`. But for now, rooms at the top level is enough.

## How to build it (line by line)

```js
app.get('/rooms/:room/messages', (req, res) => {
  const room = req.params.room;
  const roomMessages = messages.filter(m => m.room === room);
  res.json({ room, count: roomMessages.length, messages: roomMessages });
});
```

**Lines 10-14.** Get messages for a specific room.

**`/rooms/:room/messages`** — the URL has two parts: the room name and then `/messages`. We capture the room name with `:room`.

**`req.params.room`** — the room name from the URL. If the URL is `/rooms/general/messages`, then `req.params.room` is `"general"`.

**`messages.filter(m => m.room === room)`** — keep only messages where the room matches.

```js
app.post('/rooms/:room/messages', (req, res) => {
  const room = req.params.room;
  const { from, text } = req.body;
  const message = {
    id: messages.length + 1,
    room,
    from,
    text,
    sentAt: new Date().toISOString(),
  };
  messages.push(message);
  res.status(201).json(message);
});
```

**Lines 17-29.** Post a message.

**The new field is `room`.** We use the room from the URL — the client doesn't send it in the body. This is important: the URL says where the message is going, the body says what's in it.

**Why?** It would be confusing if the client could send `room: "general"` in the body to a `/rooms/random/messages` URL. The URL is the source of truth.

## What we learned

1. URLs can have multiple parts: `/rooms/:room/messages`
2. Nested resources: messages belong to rooms
3. The URL is the source of truth — don't trust the body to override it
4. The CRUD pattern still works, just with the resource nested in the URL
5. We've built 4 apps with the same shape — todos, notes, posts, messages

## What's next

In **10-bookmarks-app** we build a bookmark saver. Bookmarks have a URL and a title. Same CRUD, but the data is a URL. We also add a "duplicate detection" feature — you can't save the same URL twice.
