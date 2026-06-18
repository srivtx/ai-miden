# The Problem

> *"Authentication says who you are. Authorization says what you can do. They're different."*

## Why Ownership Is Not Enough

In projects 08-32, we enforce ownership: a user can only edit *their* posts, transfer *their* own money, etc. The rule is "you can do this to your own resources."

But real apps have *shared* resources:
- A workspace has many members
- A document has many editors
- A channel has many participants
- A team has many admins

For shared resources, "ownership" doesn't apply. We need *roles*.

A user might be:
- The **owner** of a workspace (full control)
- An **admin** (manage members)
- A **member** (read/write posts)
- A **guest** (read-only)

Different roles have different permissions. The owner can do everything. The guest can only read. We need a way to check "what can this user do in this workspace?"

## What Pain Is This Solving?

Imagine you build Slack. You open a workspace. You see channels, members, settings. You can post messages, invite people, change settings.

But the intern shouldn't be able to change billing. The contractor shouldn't be able to invite people. The customer (guest) shouldn't be able to post in internal channels.

These are role-based restrictions. The server must check the user's role before allowing the action.

Without RBAC:
- Anyone with the URL can do anything
- The founder is the same as a contractor
- Security is a mess

With RBAC:
- Each user has a role for each resource
- The role determines what they can do
- The server checks the role before each action

## The Deeper Problem: Permissions vs. Roles

There are two common models:

- **RBAC (Role-Based Access Control)**: users have roles, roles have permissions. Simple.
- **ABAC (Attribute-Based Access Control)**: access is based on attributes (e.g., "user is in the same department as the resource"). Complex.

For most apps, RBAC is enough. ABAC is for complex enterprise apps.

We use RBAC with 4 roles: `owner`, `admin`, `member`, `guest`. The roles have a hierarchy:

```
owner (4) > admin (3) > member (2) > guest (1)
```

A user with role `admin` has all permissions of `member` and `guest`. We use this hierarchy to check permissions:

```js
if (roleHierarchy[userRole] >= roleHierarchy[requiredRole]) { /* allowed */ }
```

## What This Project Will Solve

This project will:

1. Add `workspaces` and `workspace_members` tables
2. Add a `role` column on `workspace_members`
3. Add a `requireRole(role)` middleware
4. Add endpoints to create workspaces, invite members, change roles
5. Apply role checks to workspace-scoped actions

By the end, the server knows what each user can do in each workspace.

## What This Project Will *Not* Solve

- **Resource-level permissions** — e.g., "Bob can read post 42 but not edit it." We do workspace-level, not resource-level.
- **Custom roles** — we have 4 fixed roles. Custom roles are out of scope.
- **Inheritance** — workspaces within teams within orgs. Out of scope.
- **Time-based access** — "Alice can edit until tomorrow." Out of scope.

## The Question This Project Answers

> *"How do I know what a user is allowed to do?"*

If you can answer: "use RBAC, assign roles, check the role against a hierarchy," you are ready for project 34.
