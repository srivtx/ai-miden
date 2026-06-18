# The Build

> *"A role is a label. A label has permissions. Check the label."*

We are going to add RBAC. The change from project 32: add `workspaces` and `workspace_members` tables, a `requireRole` middleware, and apply role checks to workspace-scoped actions.

## The Code

### The Migration

```js
{
  version: 7,
  up: `
    CREATE TABLE IF NOT EXISTS workspaces (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      owner_id INTEGER NOT NULL REFERENCES users(id),
      created_at INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS workspace_members (
      workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
      user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      role TEXT NOT NULL CHECK (role IN ('owner', 'admin', 'member', 'guest')),
      PRIMARY KEY (workspace_id, user_id)
    );
  `,
},
```

### The Role Helpers

```js
const roleHierarchy = { owner: 4, admin: 3, member: 2, guest: 1 };
function hasPermission(actual, required) {
  return roleHierarchy[actual] >= roleHierarchy[required];
}

async function getRole(userId, workspaceId) {
  const member = await db('workspace_members').where({ user_id: userId, workspace_id: workspaceId }).first();
  return member ? member.role : null;
}

function requireRole(role) {
  return async (req, res, next) => {
    const member = await db('workspace_members').where({ workspace_id: req.params.workspaceId, user_id: req.user.userId }).first();
    if (!member) throw new ForbiddenError('Not a member');
    if (!hasPermission(member.role, role)) throw new ForbiddenError(`Requires role: ${role}`);
    req.workspaceRole = member.role;
    next();
  };
}
```

### Workspace Endpoints

```js
const workspaceCreateSchema = z.object({ name: z.string().min(1).max(100) });
const memberAddSchema = z.object({ userId: z.number().int().positive(), role: z.enum(['admin', 'member', 'guest']) });

app.post('/workspaces', authMiddleware, validate(workspaceCreateSchema), asyncHandler(async (req, res) => {
  const { name } = req.validated;
  const [id] = await db('workspaces').insert({ name, owner_id: req.user.userId, created_at: Date.now() });
  // Add the owner as a member with role 'owner'
  await db('workspace_members').insert({ workspace_id: id, user_id: req.user.userId, role: 'owner' });
  res.status(201).json({ id, name });
}));

app.get('/workspaces/:workspaceId', authMiddleware, requireRole('guest'), asyncHandler(async (req, res) => {
  const ws = await db('workspaces').where({ id: req.params.workspaceId }).first();
  if (!ws) throw new NotFoundError('Workspace not found');
  res.json(ws);
}));

app.post('/workspaces/:workspaceId/members', authMiddleware, requireRole('admin'), validate(memberAddSchema), asyncHandler(async (req, res) => {
  const { userId, role } = req.validated;
  await db('workspace_members').insert({ workspace_id: req.params.workspaceId, user_id: userId, role });
  res.status(201).json({ message: 'Member added' });
}));

app.patch('/workspaces/:workspaceId/members/:userId', authMiddleware, requireRole('admin'), asyncHandler(async (req, res) => {
  const { role } = req.body;
  if (!['admin', 'member', 'guest'].includes(role)) throw new ValidationError([{ path: 'role', message: 'invalid role' }]);
  await db('workspace_members').where({ workspace_id: req.params.workspaceId, user_id: req.params.userId }).update({ role });
  res.json({ message: 'Role updated' });
}));
```

### Workspace-Scoped Posts

```js
app.post('/workspaces/:workspaceId/posts', authMiddleware, requireRole('member'), validate(postCreateSchema), asyncHandler(async (req, res) => {
  const { title, body } = req.validated;
  const [id] = await db('posts').insert({ user_id: req.user.userId, workspace_id: req.params.workspaceId, title, body, created_at: Date.now() });
  res.status(201).json({ id, userId: req.user.userId, title, body });
}));

app.get('/workspaces/:workspaceId/posts', authMiddleware, requireRole('guest'), asyncHandler(async (req, res) => {
  const { limit, offset } = paginate(req);
  const [posts, c] = await Promise.all([
    db('posts').where({ workspace_id: req.params.workspaceId }).orderBy('created_at', 'desc').limit(limit).offset(offset),
    db('posts').where({ workspace_id: req.params.workspaceId }).count('id as count').first(),
  ]);
  res.json({ data: posts, meta: meta(c.count, limit, offset) });
}));
```

The `requireRole` middleware ensures the user has the right role. The handler does the work.

## Run It

```bash
# Create a workspace
curl -X POST http://localhost:3000/workspaces \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Workspace"}'
# {"id":1,"name":"My Workspace"}

# Add a member
curl -X POST http://localhost:3000/workspaces/1/members \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"userId":2,"role":"member"}'
# {"message":"Member added"}

# Get the workspace (as the member)
curl http://localhost:3000/workspaces/1 \
  -H "Authorization: Bearer $TOKEN_OF_USER_2"
# {"id":1,"name":"My Workspace"}

# Try to add a member as 'member' role (should fail)
curl -X POST http://localhost:3000/workspaces/1/members \
  -H "Authorization: Bearer $TOKEN_OF_USER_2" \
  -H "Content-Type: application/json" \
  -d '{"userId":3,"role":"guest"}'
# {"error":"Requires role: admin","code":"FORBIDDEN"}
```

The pain of "everyone has the same permissions" is solved. The server knows what each user can do.

---

## Experiments

### Experiment 1: Test the role hierarchy

Create a user with role `member`. Try to do an `admin` action. See the 403. Promote to `admin`. Try again. See the success.

### Experiment 2: Owner can do everything

The `owner` role has all permissions. Any `requireRole(...)` middleware accepts `owner`.

### Experiment 3: Audit the role checks

Use a linter to ensure every sensitive endpoint has a `requireRole(...)` middleware. Out of scope for this project, but a good practice.

### Experiment 4: Combine with ownership

Some actions require both role and ownership. For example, "edit a post" requires `member` role *and* being the author.

---

## Cove Editor Integration

The 33 server serves the Cove collaborative workspace editor at `/cove/editor.html`. Open two browser tabs, login as different users, and see:

- **Chat (project 28)**: messages sync via WebSocket relay
- **Canvas (project 28/31)**: draw commands sync in real-time; new tabs replay the last 200 draw ops
- **Doc (project 31)**: collaborative text editor syncs via WebSocket
- **Presence (project 30)**: Redis TTL heartbeat, live online user list
- **Voice (project 32)**: WebRTC with offer/answer signaling, incoming call notification with Accept/Decline
- **Workspaces (project 33)**: create workspaces in the left sidebar

The server broadcasts all WebSocket message types (chat, draw, doc-sync, webrtc-offer, webrtc-answer, ice-candidate) to other clients. Draw history (last 200 ops) and doc content are stored in memory and replayed to new connections.

### Setting Up

```bash
cd zero-to-hero/33-rbac
npm install
redis-server   # or brew services start redis
node server.js
open http://localhost:3000/cove/editor.html
```

CORS is enabled for development; the editor is served from the same origin via `express.static`.

---

## Summary

You now have RBAC. The server knows what each user can do. Roles are hierarchical. Membership is per-workspace. The `requireRole` middleware is composable.

This is the foundation of *authorization*. From here, every project that needs permissions can use RBAC. The patterns (role hierarchy, `requireRole` middleware, workspace membership) are universal.

In project 34, we will add **webhooks** — outbound push to other services. The server notifies external services when events happen.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.
