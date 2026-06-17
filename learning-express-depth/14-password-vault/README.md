# 14 — Password Vault

Same CRUD. The new thing: we don't store passwords in plain text. We **hash** them.

## Run it

```bash
npm install
node server.js
```

```bash
# Save a password
curl -X POST http://localhost:3000/vault \
  -H "Content-Type: application/json" \
  -d '{"name": "Gmail", "password": "supersecret123"}'
# { "id": 1, "name": "Gmail" }
# Note: no password or hash in the response!

# List saved items
curl http://localhost:3000/vault
# { "count": 1, "items": [{ "id": 1, "name": "Gmail" }] }
```

## How to think about it

If someone steals your database, they should not be able to read the passwords. We do this with **hashing**: instead of storing the password, we store a "fingerprint" of it. The fingerprint is one-way — you can't go from fingerprint back to password.

## How to build it (line by line)

```js
const crypto = require('crypto');
```

**Line 3.** Node has a built-in `crypto` module. No install needed.

```js
function hash(password) {
  return crypto.createHash('sha256').update(password).digest('hex');
}
```

**Lines 9-11.** A simple hash function. `sha256` is a one-way function. Given a password, it gives back a fixed-length string. You can't reverse it.

**`createHash('sha256')`** — create a SHA-256 hasher.
**`.update(password)`** — feed the password in.
**`.digest('hex')`** — get the result as a hex string.

```js
const item = { id: vault.length + 1, name, passwordHash: hash(password), createdAt: new Date().toISOString() };
```

**Line 19.** We store `passwordHash`, not `password`. Even if someone reads the database, they see only the hash.

```js
res.status(201).json({ id: item.id, name: item.name });
```

**Line 22.** We don't return the hash either. Just the id and name. The hash stays in the database.

## What we learned

1. Never store passwords in plain text
2. Hashing is one-way — can't go back
3. SHA-256 is a simple hash. For real apps, use bcrypt (slower = harder to brute-force)
4. Don't return hashes in API responses
5. We can build a real security-aware app with the same CRUD pattern

## What's next

In **15-expense-tracker** we build an expense tracker. Each expense has an amount (a number, not a string). The new thing: we add up totals.
