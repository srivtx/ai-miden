# 04 — Roles

Three roles: reader, author, admin. Different permissions.

**What's new:**
- `role` column on users: `reader`, `author`, `admin`
- `requireRole(...roles)` middleware checks the user's role
- Authors can create posts and edit their own
- Admins can edit any post, delete any post, change roles
- Readers can only read published posts

**Why three roles?**
- **Reader**: the default. Just reads.
- **Author**: can write. But only their own stuff.
- **Admin**: can do anything to anything.

This is the most common permission system. Real apps add more: `editor` (can edit any post but not change roles), `moderator` (can hide comments), etc.

## Run
```bash
npm install && node server.js
```

The server expects a user table to be set up. For demo, you can manually insert users in SQLite or use a separate auth endpoint.

## What this stage teaches
- Role-based access control
- `requireRole(...roles)` middleware factory
- Author vs admin permissions
- 403 Forbidden for wrong role

## Next
**05-media** — let authors upload images. Posts need featured images.
