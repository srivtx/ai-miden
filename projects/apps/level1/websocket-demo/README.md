# WebSocket Demo — Real-time bidirectional communication

WebSockets keep a connection open between client and server. Both sides can send messages at any time. Used for: chat, real-time dashboards, multiplayer games, live notifications.

## Setup
```
npm install
node server.js
```

## Endpoints
```
WS   /ws               # WebSocket endpoint
GET  /                 # info
GET  /admin/rooms      # current room occupancy
```

## Try (with wscat or websocat)
```bash
npm install -g wscat
wscat -c ws://localhost:3000/ws
> {"type": "join", "room": "lobby", "username": "alice"}
< {"type": "joined", "room": "lobby", "members": 1}
> {"type": "chat", "text": "hello!"}
< {"type": "chat", "from": "alice", "text": "hello!", "ts": 1234567890}
```

## What this teaches
1. **WebSocket handshake**: HTTP upgrade, then full-duplex
2. **Rooms**: clients join named rooms, messages broadcast to room members
3. **Message types**: `welcome`, `join`, `chat`, `system`, `ping`/`pong`
4. **Connection lifecycle**: open → message → message → close
5. **vs HTTP**: HTTP is request-response, WebSocket is event-driven
6. **vs SSE**: SSE is server-to-client only, WebSocket is bidirectional
