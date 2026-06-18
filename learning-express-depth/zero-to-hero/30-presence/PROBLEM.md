# The Problem

> *"Who's online? The server knows. The clients should too."*

## Why Presence Is Needed

In projects 28-29, we have real-time communication. But we don't know *who* is connected. The final artifact (Cove) needs to show:

- **Online status**: "Alice is online" (green dot), "Bob is offline" (gray dot)
- **Typing indicator**: "Carol is typing..." (animated dots)
- **Viewing counter**: "3 people viewing this document" (avatar stack)
- **Last seen**: "Dave was last seen 5 minutes ago"

These are all *presence* features. The server tracks who's connected, what they're doing, and broadcasts updates to all clients.

## What Pain Is This Solving?

Imagine you're building Slack. You open a channel. You see a list of users in the sidebar. Each user has a green dot if they're online, a gray dot if they're offline, and a clock if they were last seen recently.

Where does this come from? The server. The server tracks who's connected. When a user connects, the server marks them online. When they disconnect, the server marks them offline. The server broadcasts presence updates to all clients.

Without presence, the client would have to poll. "Is Alice online? Is Bob online?" Every second. Wasteful and laggy.

With presence, the server pushes updates. "Alice is online." "Bob is offline." Real time.

## The Deeper Problem: Detecting Disconnects

The hard part of presence is detecting disconnects. A client might:

- **Disconnect normally**: close the WebSocket. We know.
- **Crash**: the process dies. We don't know until we try to send.
- **Network drop**: the client is still running, but we can't reach it. We don't know.
- **Sleep**: the laptop is closed. We don't know.

For normal disconnects, we get a `close` event. For crashes and network drops, we need a different mechanism: the **heartbeat**.

The client (or the server) sends a periodic message ("I'm still here"). If the server doesn't receive a heartbeat for a while, it assumes the client is dead and marks them offline.

We use Redis TTL for this:

1. Client connects. Server sets `presence:<userId>` with TTL 30 seconds.
2. Server sends a heartbeat every 10 seconds (refreshes the TTL).
3. If the client crashes, no more heartbeats. The TTL expires. The user is marked offline.
4. If the client disconnects normally, server deletes the key and marks them offline.

## Multi-Process Presence

In a multi-process deployment (multiple Node servers behind a load balancer), each process has its own WebSocket connections. A user might be connected to process 1, but process 2 doesn't know.

The fix: **Redis pub/sub**. When a user connects to process 1, process 1 publishes `presence:connect` to Redis. All processes (1, 2, 3, ...) subscribe and update their local view.

When a client of process 2 needs to know "is Alice online?", process 2 checks its local view (which was updated via pub/sub from process 1).

## What This Project Will Solve

This project will:

1. Track online status with Redis TTL
2. Use heartbeats to keep the TTL alive
3. Use Redis pub/sub to broadcast presence updates across processes
4. Authenticate WebSocket connections (token in query string)
5. Send presence updates to all WebSocket clients

By the end, the server knows who's online. Clients receive real-time presence updates.

## What This Project Will *Not* Solve

- **Typing indicators** — out of scope. Use a separate "typing" event.
- **Last seen** — we know online/offline, not "5 minutes ago". We could store the last disconnect time.
- **Viewing counter** — we know who's online, not who's viewing a specific document. Out of scope.
- **Per-room presence** — we have global presence, not per-channel/per-document. Out of scope.
- **Cross-region** — we use one Redis. For multi-region, use a global Redis or a different approach.

## The Question This Project Answers

> *"How do I know who's connected and broadcast their status in real time?"*

If you can answer: "use Redis with TTL for the source of truth, pub/sub for cross-process updates, broadcast to WebSocket clients," you are ready for project 31.
