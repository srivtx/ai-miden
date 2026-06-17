# Chat API — Step 6 in the learning path

Builds on Weather. Adds: WebSockets, rooms, real-time messaging, message history.

## Endpoints
```
GET  /rooms                       # list rooms with message counts
POST /rooms                       # create room { name }
GET  /rooms/:id/messages          # message history (limit=50)

WS   /ws                          # WebSocket connection
```

## Try
```bash
# Create a room
curl -X POST http://localhost:3000/rooms -H "Content-Type: application/json" -d '{"name": "general"}'

# Connect via wscat
wscat -c ws://localhost:3000/ws
> {"type": "join", "userId": "alice", "roomId": "general"}
< {"type": "joined", "history": [], "members": 1}
> {"type": "message", "text": "Hello!"}
< {"type": "message", "userId": "alice", "text": "Hello!", ...}

# Get history
curl http://localhost:3000/rooms/general/messages
```

## What this teaches
1. **WebSockets**: bidirectional real-time communication
2. **Rooms**: users join named channels
3. **Broadcasting**: send a message to all members of a room
4. **Message persistence**: store in DB, load on join
5. **Connection state**: track who is in which room

## Next project
→ **forum-api** — adds: threads, replies, votes, categories, moderation
