# Project 33: The RBAC

> *"Authentication says who you are. Authorization says what you can do."*

In projects 08-32, any authenticated user can do anything: create posts, update their own profile, transfer their own money. We've enforced **ownership** (you can only update *your* posts), but not **roles**.

For the final artifact (Cove), we need real **RBAC** (Role-Based Access Control):
- `owner` — full control over a workspace
- `admin` — manage members, settings
- `member` — read/write posts
- `guest` — read-only

This is **authorization** — what you can do, based on your role. We add a `workspaces` table, a `workspace_members` table, and a `requireRole(...)` middleware that checks the user's role for the requested resource.

By the end, the server knows not just *who* you are, but *what you can do*.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is ownership not enough? What is RBAC?
2. [The Thought](./THOUGHT.md) — How do roles work? What is the role hierarchy?
3. [The Build](./BUILD.md) — Line-by-line construction of the RBAC
4. [The Decisions](./DECISIONS.md) — Why RBAC? Why a separate permissions table?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

RBAC (Role-Based Access Control) is a model where users are assigned roles, and roles have permissions. We add `workspaces` and `workspace_members` tables, a `role` column (`owner`, `admin`, `member`, `guest`), and a `requireRole(role)` middleware that checks the user's role for the requested resource. Ownership checks remain (you can edit your own posts), but role checks are added for shared resources (workspaces).

---

## The Code

```js
// Schemas
const workspaceCreateSchema = z.object({
  name: z.string().min(1).max(100),
});

const memberAddSchema = z.object({
  userId: z.number().int().positive(),
  role: z.enum(['admin', 'member', 'guest']),
});

async function getRole(userId, workspaceId) {
  const member = await db('workspace_members').where({ user_id: userId, workspace_id: workspaceId }).first();
  return member ? member.role : null;
}

function requireRole(role) {
  return async (req, res, next) => {
    const member = await db('workspace_members').where({ user_id: req.user.userId, workspace_id: req.params.workspaceId }).first();
    if (!member) throw new ForbiddenError('Not a member');
    if (!hasPermission(member.role, role)) throw new ForbiddenError('Insufficient role');
    req.workspaceRole = member.role;
    next();
  };
}

const roleHierarchy = { owner: 4, admin: 3, member: 2, guest: 1 };
function hasPermission(actual, required) {
  return roleHierarchy[actual] >= roleHierarchy[required];
}
```

The pain of "everyone has the same permissions" is solved. The server knows what each user can do.

---

## What You Will Have Learned

- What RBAC is (Role-Based Access Control)
- The role hierarchy (owner > admin > member > guest)
- How to implement `requireRole(...)` middleware
- The difference between authentication and authorization
- How to combine ownership checks with role checks

These are the foundations of *authorization*. From here, every project that needs permissions can use RBAC.
