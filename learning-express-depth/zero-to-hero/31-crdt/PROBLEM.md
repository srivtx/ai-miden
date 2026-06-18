# The Problem

> *"Last-write-wins is a recipe for lost work. CRDTs are the fix."*

## Why Co-Editing Is Hard

Imagine two users editing the same Google Doc. User A types "Hello" at position 0. User B types "World" at position 0. What happens?

The naive approach: **last-write-wins**. Whoever saves last wins. The other's changes are lost. Annoying. Lost work.

The smart approach: **CRDT** (Conflict-free Replicated Data Type). A CRDT is a data structure that can be edited by multiple users simultaneously and merged without conflicts.

```
User A's view:  "Hello"
User B's view:  "World"
Server's view:  "HelloWorld" (merged automatically)
```

Both users see the same final state. No conflicts. No server-side merging. No "your changes were lost" messages.

## What Pain Is This Solving?

Imagine building a collaborative text editor. Two users type simultaneously. The server receives two sets of changes. How do you merge them?

- **Append A then B**: "HelloWorld"
- **Append B then A**: "WorldHello"
- **Interleave**: "HWeolrllod" (broken)

Without a CRDT, you have to choose. With a CRDT, the operations are *commutative*: order doesn't matter. A then B gives the same result as B then A. The CRDT handles the merging.

## The Deeper Problem: Distributed State

The fundamental challenge of co-editing is *distributed state*. Each user has a local copy of the document. They edit locally (fast). They sync with the server (eventually). The server syncs with other users (eventually).

The questions:
- What if two users edit the same position?
- What if a user disconnects and reconnects?
- What if the server crashes?
- What if messages arrive out of order?

CRDTs solve all of these. Each operation has a unique ID (timestamp + client ID + counter). Operations are commutative. The merge is automatic. The state is always consistent (eventually).

## Two Main Approaches: CRDT and OT

There are two main approaches to co-editing:

### CRDT (Conflict-free Replicated Data Type)

- Data structure with mathematical properties that guarantee convergence
- Operations are commutative and idempotent
- No central server needed (can be P2P)
- Examples: Yjs, Automerge, Delta

### OT (Operational Transform)

- Server transforms operations based on the current state
- More complex (server-side logic)
- Used by Google Docs (originally), Etherpad
- Examples: ShareDB, OT.js

CRDTs are simpler for the developer (no server-side logic). OT requires a server that knows the current state and transforms operations. CRDTs are the modern choice for most apps.

We use **Yjs**, the most popular CRDT library.

## What This Project Will Solve

This project will:

1. Add `y-websocket` and `yjs` as dependencies
2. Set up a Yjs WebSocket server (relay)
3. The server forwards Yjs updates between clients
4. Yjs handles the merging (commutative operations)

By the end, two clients can edit the same document simultaneously. Changes are merged automatically.

## What This Project Will *Not* Solve

- **Rich text formatting** — Yjs supports it via `Y.XmlFragment`. We use plain text.
- **Persistence** — we don't persist the document. The state is in memory. For persistence, use `y-leveldb` or similar.
- **Authentication** — anyone with the doc name can connect. We add auth in a future project.
- **Permissions** — anyone can edit. We add permissions in project 33 (RBAC).
- **Offline editing** — Yjs supports it via `y-indexeddb` on the client. We don't add it here.
- **Versioning** — we don't track document versions. Out of scope.

## The Question This Project Answers

> *"How do two users edit the same document without conflicts?"*

If you can answer: "use a CRDT (Yjs), each operation has a unique ID, the server is just a relay, the CRDT handles the merging," you are ready for project 32.
