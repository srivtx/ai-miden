# The Decisions

> *"A CRDT is a data structure that merges without conflicts. Yjs is a popular CRDT library."*

## Decision 1: Yjs and not Automerge / ShareDB

**Alternatives**:
- **Automerge** — another CRDT library, JSON-focused
- **ShareDB** — OT-based, used by Google Docs originally
- **Yjs** — CRDT, popular, integrations with Quill/ProseMirror/CodeMirror

**Why Yjs: Most popular. Best integrations. Plain text and rich text. Awareness (cursors, selections). Active community.

**Trade-off**: Lock-in to Yjs. The data format is Yjs-specific (not portable to other CRDTs).

## Decision 2: y-websocket and not custom

**Alternative**: Build a custom Yjs sync protocol over WebSocket.

**Why y-websocket: It's the standard. It handles the protocol details (sync step 1, sync step 2, awareness). We use it.

**Trade-off**: We depend on `y-websocket`. If it becomes unmaintained, we'd have to migrate.

## Decision 3: Plain text and not rich text

**Alternative**: Rich text (bold, italic, links, etc.) via Quill or ProseMirror.

**Why plain text: Simpler. The pattern is the same for rich text (use `Y.XmlFragment` or a Quill binding). We use plain text for the demo.

**Trade-off**: No formatting. We accept this.

## Decision 4: No persistence

**Alternative**: Use `y-leveldb` to persist to disk.

**Why no: Out of scope. The state is in memory. Restart the server, the document is gone. We add persistence in a future project.

**Trade-off**: Restart = data loss. We accept this.

## Decision 5: No authentication

**Alternative**: Verify a token in the WebSocket handshake.

**Why no: Out of scope. We add auth in project 33 (RBAC).

**Trade-off**: Anyone with the doc name can connect. We accept this.

## Decision 6: No permissions

**Alternative**: Read-only, write-only, owner-only modes.

**Why no: Out of scope. We add permissions in project 33 (RBAC).

**Trade-off**: Anyone can edit. We accept this.

## Decision 7: No awareness (yet)

**Alternative**: Use Yjs awareness to share cursors and selections.

**Why no: Out of scope. The pattern is "set your awareness, listen for changes." We don't add it here.

**Trade-off**: Can't see other users' cursors. We accept this.

## Decision 8: Separate Yjs WebSocket from chat WebSocket

**Alternative**: One WebSocket server handles both chat and Yjs.

**Why separate: Different protocols. The chat is JSON over WebSocket (project 28). Yjs has its own binary protocol. Mixing them is messy.

**Trade-off**: Two WebSocket servers. We accept this for clarity.

## Decision 9: Yjs at the root path

The Yjs client connects to `ws://localhost:3000/<doc-name>`. The chat client connects to `ws://localhost:3000/`. They share the HTTP server but use different paths.

**Alternative**: Different ports.

**Why same port: Simpler. The HTTP server is shared. The `upgrade` handler routes based on path.

**Trade-off**: A bit of routing logic. We accept this.

## Decision 10: No version history

**Alternative**: Store every version of the document (for undo/redo or history).

**Why no: Out of scope. Yjs has built-in undo/redo. We don't add custom version history.

**Trade-off**: Can't view the document as it was yesterday. We accept this.

---

## What We Did Not Decide

- **Rich text** — out of scope
- **Persistence** — out of scope
- **Authentication** — out of scope
- **Permissions** — out of scope
- **Awareness** — out of scope
- **Version history** — out of scope
- **Offline editing** — out of scope (client-side concern)
- **Image embedding** — out of scope
- **Comments / suggestions** — out of scope
- **Export to PDF** — out of scope

Each is a future decision.

---

## The Meta-Decision: The Server Supports Co-Editing

For 30 projects, every interaction was a single user or a broadcast. We couldn't have two users editing the same document.

Now the server supports co-editing. Two users can edit the same document in real time. Yjs handles the merging. The server is a relay. The CRDT does the work.

This is the foundation of *collaborative editing*. From here, every project that needs real-time co-editing can use Yjs. The patterns (Y.Doc, y-websocket, awareness) are universal.

The next 9 projects will assume Yjs exists. The path diverges:

- **WebRTC** (project 32): voice
- **RBAC** (project 33): permissions
- **Webhook** (project 34): outbound push
- **Payment** (project 35): Stripe
- **Tests** (project 36): automated
- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The server supports co-editing. The path continues.
