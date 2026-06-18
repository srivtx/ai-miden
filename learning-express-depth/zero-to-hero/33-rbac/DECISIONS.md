# The Decisions

> *"Authentication says who you are. Authorization says what you can do."*

## Decision 1: RBAC and not ABAC

**Alternative**: ABAC (Attribute-Based Access Control).

**Why RBAC: Simpler. Most apps don't need ABAC's complexity. RBAC with 4 roles covers 95% of use cases.

**Trade-off**: For complex enterprise apps, ABAC is more flexible. We use RBAC.

## Decision 2: 4 fixed roles, not custom

**Alternative**: Custom roles (admin can define new roles with custom permissions).

**Why fixed: Simpler. We have 4 roles that cover most needs. Custom roles are out of scope.

**Trade-off**: Can't define "Editor" or "Commenter" as a custom role. We accept this.

## Decision 3: Role hierarchy

**Alternative**: Flat roles (no hierarchy).

**Why hierarchy: Simpler code. `admin` gets all `member` permissions without listing them.

**Trade-off**: Less flexible. Can't have an `admin` with fewer permissions than `member` (rare in practice).

## Decision 4: Per-workspace membership

**Alternative**: Global roles (one role per user across the platform).

**Why per-workspace: Users have different roles in different workspaces. Slack works this way.

**Trade-off**: More complex data model. We accept it.

## Decision 5: `requireRole(...)` middleware

**Alternative**: Inline role checks in each handler.

**Why middleware: Composable. Reusable. Easy to add to any route.

**Trade-off**: Slightly more indirection. We accept it.

## Decision 6: Combine role + ownership

**Alternative**: Just role-based.

**Why combined: Some actions require both. E.g., "edit a post" requires being a `member` *and* being the author. We check both.

**Trade-off**: Two checks per request. Negligible cost.

## Decision 7: No resource-level permissions

**Alternative**: Permissions per resource (e.g., "Bob can read post 42 but not edit it").

**Why workspace-level: Simpler. Most apps don't need resource-level.

**Trade-off**: Can't have "Bob can read this one post but not others." We accept this.

## Decision 8: Owner can't be removed

The owner is special. In our model, the owner is a member with role `owner`. To prevent the owner from being removed, we'd add a check (only the owner can remove themselves, or transfer ownership first).

**Why this restriction: If the owner is removed, no one can manage the workspace. We prevent this.

**Trade-off**: Slightly more complex. We accept it.

## Decision 9: Role check via SQL constraint

We use a CHECK constraint to ensure the role is one of the 4 valid values. This prevents invalid data at the database level.

**Alternative**: Validate in the application only.

**Why SQL constraint: Defense in depth. Even if the application has a bug, the database rejects invalid data.

**Trade-off**: Slightly more complex migration. We accept it.

## Decision 10: Composite primary key

`workspace_members` has a composite primary key `(workspace_id, user_id)`. This prevents a user from being added twice to the same workspace.

**Why composite: One row per user per workspace. The primary key enforces uniqueness.

**Trade-off**: None. Standard.

---

## What We Did Not Decide

- **Custom roles** — out of scope
- **Resource-level permissions** — out of scope
- **Global roles** — out of scope
- **Time-based access** — out of scope
- **Audit log** — out of scope (project 39)
- **Role inheritance** — out of scope
- **Multiple roles per user per workspace** — out of scope (would need a `role_assignments` table)
- **Department / team hierarchy** — out of scope
- **SSO integration** — out of scope
- **Fine-grained attribute policies** — out of scope (ABAC)

Each is a future decision.

---

## The Meta-Decision: The Server Knows What You Can Do

For 32 projects, we knew *who* you are (authentication) and enforced *ownership* (you can edit your own posts). But we didn't have *roles* — what you can do in shared resources.

Now the server knows. Roles are hierarchical. Membership is per-workspace. The `requireRole` middleware is composable. The server enforces the rules.

This is the foundation of *authorization*. From here, every project that needs permissions can use RBAC. The patterns (role hierarchy, `requireRole` middleware, workspace membership) are universal.

The next 7 projects will assume RBAC exists. The path diverges:

- **Webhook** (project 34): outbound push
- **Payment** (project 35): Stripe
- **Tests** (project 36): automated
- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The server knows what you can do. The path continues.
