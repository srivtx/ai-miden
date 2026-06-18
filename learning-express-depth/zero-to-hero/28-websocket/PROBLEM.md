# The Problem

> *"HTTP is a question. WebSocket is a conversation."*

## Why HTTP Is Not Enough

In projects 01-27, every interaction is HTTP. The client sends a request. The server sends a response. The connection is closed. After the response, the server can't send more to the client.

This works for most things:
- Fetching a page
- Submitting a form
- Reading a post

But it doesn't work for *real-time*:
- **Chat**: user A sends a message; user B should see it immediately
- **Notifications**: a new comment on a post; the post author should see it
- **Live updates**: stock prices, sports scores, collaborative editing
- **Presence**: who's online, who's typing

For these, the server needs to *push* to the client without the client asking. HTTP can't do this efficiently. The client would have to poll ("any updates?" every second). That's wasteful and laggy.

The fix: **WebSocket**. A protocol that keeps the connection open. The server can push whenever. The client can listen.

## What Pain Is This Solving?

Imagine you're building Slack. User A sends a message. User B should see it in real time. With HTTP:

- User B's client polls every second: "any new messages?"
- The server checks: "no new messages since 1 second ago"
- User B's client waits another second
- Repeat

This is 1 request per second per user. For 10,000 users, that's 10,000 requests per second. Most are "no new messages." Wasteful.

With WebSocket:

- User B's client opens a WebSocket
- The server holds the connection open
- User A sends a message
- The server pushes it to User B over the WebSocket
- User B's client receives it immediately

This is 1 persistent connection per user. The server pushes only when there's something to push. Efficient and instant.

## The Deeper Problem: Polling vs Push

There are a few approaches to real-time:

1. **Polling**: client asks every N seconds. Simple, but wasteful and laggy.
2. **Long polling**: client asks, server holds the response open until there's something. Better, but still uses a connection per request.
3. **Server-Sent Events (SSE)**: server pushes over HTTP. One-way (server to client).
4. **WebSocket**: bidirectional, persistent. The most powerful.

We use WebSocket because it's the standard for real-time bidirectional communication. SSE (project 29) is a simpler alternative for one-way push.

## What This Project Will Solve

This project will:

1. Add `ws` as a dependency
2. Create a WebSocket server attached to the HTTP server
3. Handle connections, messages, and disconnections
4. Broadcast chat messages to all clients
5. Send a welcome message on connection

By the end, the server can push real-time updates. The chat example is the foundation for notifications, presence, and co-editing.

## What This Project Will *Not* Solve

- **Authentication** — anyone can connect. We add auth in a future project.
- **Rooms** — broadcast to all clients. We add rooms in a future project.
- **Persistence** — messages are not stored. We add persistence in a future project.
- **Scaling** — single-process WebSocket. For multi-process, use Redis pub/sub (project 30).
- **Binary messages** — we use JSON text. WebSocket supports binary too.
- **Reconnection** — if the connection drops, the client doesn't auto-reconnect. The client must handle this.

## The Question This Project Answers

> *"How do I push updates to the client without the client asking?"*

If you can answer: "use WebSocket, upgrade the HTTP connection, server can push anytime," you are ready for project 29.
