# Cove Editor

A single-file collaborative workspace editor that connects to the zero-to-hero backend. Open two browser tabs, login as different users, and see every backend project in action.

## File

```
cove/
└── editor.html    (460 lines, self-contained HTML + CSS + JS)
```

## Architecture

The editor is a **single HTML file** — no build step, no framework, no `node_modules`. It talks to the backend server via REST + WebSocket. Every feature maps to a backend project.

```
editor.html
├── HTML structure (4 zones)
│   ├── #topbar       — auth login/signup
│   ├── #sidebar      — workspaces, posts, search, file upload
│   ├── #center       — canvas (drawing) + doc (collaborative text)
│   └── #rightside    — chat, online users, voice
├── CSS (130 lines)   — Linear-inspired dark design system, CSS custom properties
└── JS  (330 lines)   — vanilla JS, no libraries
    ├── Auth           — JWT login/signup via REST
    ├── WebSocket      — chat, draw, doc sync, presence, WebRTC signaling
    ├── Canvas         — pen/eraser tools, color cycling, remote draw replay
    ├── Doc            — contenteditable with WebSocket sync
    ├── Voice          — WebRTC peer connection, offer/answer, call notification
    ├── Workspaces     — create/list workspaces via REST
    ├── Posts/Search   — paginated posts, FTS5 search
    └── File Upload    — multipart form upload
```

## Design System

Built from the `claude-design` and `popular-web-designs` supercharger skills. Uses **Linear's dark palette**:

- **Canvas**: `#08090a` (near-black)
- **Panels**: `#0f1011` (one step up)
- **Elevated**: `#191a1b` (cards, modals)
- **Accent**: `#5e6ad2` indigo (buttons, active states)
- **Borders**: `rgba(255,255,255,0.05-0.08)` translucent white
- **Font**: Inter (Google Fonts CDN)
- **Scrollbars**: hidden globally
- **Anti-slop**: no gradients, no glassmorphism, no filler content

## Feature → Backend Project Map

| Editor Feature | Backend Project | Connection |
|---|---|---|
| Login/Signup | 09 JWT | `POST /sessions` returns JWT, stored in `localStorage` |
| User creation | 08 bcrypt + 09 JWT | `POST /users` auto-signs up on failed login |
| Chat messages | 28 WebSocket | `ws://localhost:3000/chat?token=X` — broadcast to all |
| Canvas drawing | 28 WebSocket | `type:draw` messages relayed; `type:draw:history` on connect |
| Draw replay on refresh | 28 WebSocket | Server stores last 200 ops, sends `draw:history` to new clients |
| Doc text sync | 31 Yjs CRDT | `type:doc-sync` via WebSocket with server-stored content |
| Online presence | 30 Presence | `type:presence:list` from server; Redis TTL + pub/sub |
| Voice call | 32 WebRTC | STUN via Google, SDP/ICE relayed through WebSocket |
| Call notification | 32 WebRTC | `type:webrtc-offer` with `from` username; callback bar with Accept/Decline |
| Workspaces | 33 RBAC | `GET /workspaces`, `POST /workspaces` with JWT header |
| Posts list | 17 REST + 18 Paginator | `GET /posts?limit=10` with pagination meta |
| Post search | 19 FTS5 | `GET /posts?q=term` — full-text search |
| File upload | 20 Multer | `POST /posts` with `multipart/form-data` |
| Rate limiting | 24 Rate Limiter | Handled server-side (100 req/min) |

## How It Was Built

### 1. First version — raw functional
- Dark CSS variables (harsh colors, no design system)
- Imported Yjs from CDN (broken — `lib0/observable` bare import failed)
- `<script type="module">` broke `onclick` handlers

### 2. Yjs fix + script fix
- Removed broken Yjs CDN import (canvas syncs via raw WebSocket, not CRDT)
- Changed `<script type="module">` to plain `<script>` so `onclick` works
- Added `doc-sync` via WebSocket

### 3. Canvas state persistence
- Server stores last 200 draw operations in `drawHistory[]`
- New WebSocket connections receive `type:draw:history` with full replay
- Doc content stored server-side and sent to new clients

### 4. Design system upgrade (claude-design + popular-web-designs)
- Installed supercharger skills: `curl | bash -s -- add design`
- Applied Linear dark palette (backgrounds, text, borders, accent)
- CSS custom properties for tokens
- Real hover/focus states
- Globally hidden scrollbars
- Clean component system (ghost/primary buttons)

### 5. WebSocket relay fix
- Server now forwards ALL message types (chat, draw, doc-sync, webrtc-*, ice-candidate)
- Not just `chat` type

### 6. Chat self-display fix
- Sender's own chat message rendered locally (server only broadcasts to others)

### 7. Voice signaling fix
- Added `handleOffer`, `handleAnswer`, `handleCandidate` functions
- Incoming call notification bar at bottom with Accept/Decline
- Caller username sent with offer

### 8. Server migration: 32 → 33
- Switched from 32-webrtc to 33-rbac for presence + workspaces
- Added `maxRetriesPerRequest: null` to Redis for BullMQ
- Added `try/catch` around `handleUpgrade` for WebSocket double-handle guard

## Running

```bash
cd zero-to-hero/33-rbac
npm install
node server.js
open http://localhost:3000/cove/editor.html
```

Open a second tab with different username to see collaboration.
