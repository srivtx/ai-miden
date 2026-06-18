# The Thought

> *"A role is a label. A label has permissions. Check the label."*

## The Role Hierarchy

We have 4 roles, ordered by privilege:

```
owner (4) > admin (3) > member (2) > guest (1)
```

- **owner**: full control. Can delete the workspace, change billing, etc.
- **admin**: manage members, settings. Can do everything except delete the workspace.
- **member**: read/write posts. Standard user.
- **guest**: read-only. Can view posts, can't create.

The hierarchy means: a user with role `admin` has all permissions of `member` and `guest`. To check permissions:

```js
const roleHierarchy = { owner: 4, admin: 3, member: 2, guest: 1 };
function hasPermission(actual, required) {
  return roleHierarchy[actual] >= roleHierarchy[required];
}
```

If you have `admin` (3) and we need `member` (2), 3 >= 2, so allowed. If we need `owner` (4), 3 < 4, so denied.

## The Data Model

We need a way to assign roles to users for each resource. We use a `workspace_members` join table:

```sql
CREATE TABLE workspaces (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  owner_id INTEGER NOT NULL REFERENCES users(id),
  created_at INTEGER NOT NULL
);

CREATE TABLE workspace_members (
  workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('owner', 'admin', 'member', 'guest')),
  PRIMARY KEY (workspace_id, user_id)
);
```

The `workspace_members` table has a composite primary key `(workspace_id, user_id)` — a user can be a member of a workspace at most once. The `role` column is one of the 4 values.

## The `requireRole` Middleware

```js
function requireRole(role) {
  return async (req, res, next) => {
    const member = await db('workspace_members')
      .where({ workspace_id: req.params.workspaceId, user_id: req.user.userId })
      .first();
    if (!member) throw new ForbiddenError('Not a member');
    if (!hasPermission(member.role, role)) throw new ForbiddenError('Insufficient role');
    req.workspaceRole = member.role;
    next();
  };
}
```

The middleware:
1. Looks up the user's role in the workspace
2. If not a member, throw 403
3. If insufficient role, throw 403
4. If sufficient, attach the role to `req.workspaceRole` and call `next()`

Use it in routes:

```js
app.post('/workspaces/:workspaceId/posts', authMiddleware, requireRole('member'), handler);
```

This requires the user to be at least a `member` of the workspace to create a post.

## Combining with Ownership

Some actions require *both* a role *and* ownership. For example, "edit a post" requires:
- The user is a `member` or higher of the workspace
- The user is the author of the post

We check both:

```js
app.patch('/posts/:id', authMiddleware, requireRole('member'), async (req, res) => {
  const post = await db('posts').where({ id: req.params.id }).first();
  if (!post) throw new NotFoundError('Post not found');
  if (post.user_id !== req.user.userId) throw new ForbiddenError('You can only edit your own posts');
  // ...
});
```

`requireRole('member')` ensures the user is a member of the workspace. The ownership check ensures the user is the author.

## Common Confusions (read these)

**Confusion 1: "Why a hierarchy? Why not just check exact role?"**
A hierarchy is simpler. "admin" gets all "member" permissions without you listing them.

**Confusion 2: "Why a separate table for members? Why not a `role` column on `users`?"**
Users can have different roles in different workspaces. A user is `owner` in workspace A and `guest` in workspace B. The join table captures this.

**Confusion 3: "What about global roles (admin of the platform)?"**
Out of scope. We have workspace-level roles. For global roles, you'd add a `role` column to `users`.

**Confusion 4: "What about the `owner` of a workspace? Can they be removed?"**
The `owner` is special. In our model, the owner is also a member with role `owner`. To prevent the owner from being removed, we'd add a check (only the owner can remove themselves, or transfer ownership first).

**Confusion 5: "What about resource-level permissions (e.g., this post)?"**
Out of scope. We have workspace-level. For resource-level, you'd add another join table (e.g., `post_permissions`).

**Confusion 6: "What about custom roles?"**
Out of scope. We have 4 fixed roles. For custom roles, you'd add a `roles` table and a `role_permissions` table.

**Confusion 7: "What if a user has no role in a workspace?"**
The middleware returns 403. They're not a member.

**Confusion 8: "What if a user has multiple roles in a workspace?"**
We don't allow this (composite primary key). One role per user per workspace.

## What We Are About to Build

A ~700-line Express app that:

1. Has `workspaces` and `workspace_members` tables
2. Has endpoints to create workspaces, invite members, change roles
3. Has a `requireRole(role)` middleware
4. Applies role checks to workspace-scoped actions
5. Combines role checks with ownership checks

The HTTP handlers are extended. The new piece is the RBAC.

In [BUILD.md](./BUILD.md) we will go line by line.
