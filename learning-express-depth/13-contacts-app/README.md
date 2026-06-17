# 13 — Contacts App

Same CRUD. New thing: **lookup by a non-id field** (email).

## Run it

```bash
npm install
node server.js
```

```bash
# Add a contact
curl -X POST http://localhost:3000/contacts \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com", "phone": "555-1234"}'

# Get all
curl http://localhost:3000/contacts

# Get by id (the usual way)
curl http://localhost:3000/contacts/1

# Get by email (NEW!)
curl http://localhost:3000/contacts/by-email/alice@example.com
```

## How to think about it

Sometimes clients know a thing by something other than its id. "Find the user with this email" is more useful than "find the user with id 42." We expose a different URL for that lookup.

## How to build it (line by line)

```js
app.get('/contacts/by-email/:email', (req, res) => {
  const contact = contacts.find(c => c.email === req.params.email);
  if (!contact) return res.status(404).json({ error: 'Contact not found' });
  res.json(contact);
});
```

**Lines 25-29.** A new endpoint just for email lookup.

**Why a different path?** `/contacts/:email` is ambiguous — is `:email` an id or an email? `/contacts/by-email/:email` is explicit.

**Why not just `/contacts/:id`?** Because the value is a string (email) and our ids are numbers. If we did `parseInt`, `"alice@example.com"` would become `NaN`. So we keep them separate.

## What we learned

1. Sometimes clients need to look up by something other than id
2. Use explicit paths (`/by-email/:email`) to avoid confusion
3. We've now built 8 apps — the pattern is becoming muscle memory

## What's next

In **14-password-vault** we build a password manager. Same CRUD, but each item has a `password` field. We don't store the actual password — we store a "hash" so even if someone steals our data, they can't read the passwords.
