# The Thought

> *"Hashing is one-way. Salting defeats rainbow tables. Slowness defeats brute-force. bcrypt is all three."*

## What Hashing Is

A *hash function* takes an input of any size and produces a fixed-size output. The output is called a *hash* or *digest*.

```
hash("hello")     → "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
hash("hello!")    → "ce060f9c34bbcc79a4e705be7d3c3aa1b8c8408a4a55b1f8174b8a3a45c9d18e"
hash("hunter2")   → "f3bbbd66a63d4bf1747940578ec3d0103530e21d86f6eddee2e73fe8e978b1a2"
```

Properties of a good hash function:

1. **Deterministic**: the same input always produces the same output
2. **One-way**: given the output, you cannot recover the input
3. **Collision-resistant**: it's hard to find two inputs with the same output
4. **Fast**: easy to compute

SHA-256 is a great hash function. It has all these properties. So why not use it for passwords?

Because it's *too fast*.

## Why Fast Is Bad for Passwords

A modern GPU can compute ~10 billion SHA-256 hashes per second. An attacker with a single GPU can try every 8-character password (lowercase + digits) in minutes.

Most users have weak passwords. "12345678", "password", "qwerty" — these are in every wordlist. An attacker doesn't need to try every possible password; they just need to try the top 10,000 most common ones. With SHA-256, that's a millisecond.

**We need a slow hash function.**

## bcrypt: The Slow Hash

bcrypt is a hash function designed for passwords. It is *intentionally slow*. A modern CPU can compute ~10 bcrypt hashes per second. A GPU can compute maybe 100. Brute-force becomes infeasible.

The "slowness" is configurable. The *cost factor* (or *work factor*) controls how slow:

- `bcrypt.hash(password, 10)` — 2^10 = 1024 iterations. Default.
- `bcrypt.hash(password, 12)` — 2^12 = 4096 iterations. 4x slower.
- `bcrypt.hash(password, 14)` — 2^14 = 16384 iterations. 16x slower.

Cost 10 is the modern default. As CPUs get faster, you increase the cost. The cost is stored in the hash, so old hashes still work.

bcrypt also uses a *salt* automatically. The salt is a random 16-byte value generated for each hash. It's stored at the beginning of the hash output. So two users with the same password get different hashes.

bcrypt hash format:

```
$2b$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy
│  │  │                              │
│  │  │                              └─ the actual hash
│  │  └─ the salt (22 chars, base64)
│  └─ the cost factor (10 = 2^10 = 1024 iterations)
└─ algorithm version (2b = bcrypt)
```

The full string is what we store. It has the salt embedded. We don't need to store the salt separately.

## `bcrypt.hash` and `bcrypt.compare`

```js
const bcrypt = require('bcrypt');

// Hash a password
const hash = await bcrypt.hash('hunter2', 10);
// hash: '$2b$10$N9qo8uLOickgx2ZMRZoMye...'

// Verify a password
const ok = await bcrypt.compare('hunter2', hash);
// ok: true

const bad = await bcrypt.compare('wrong', hash);
// bad: false
```

`bcrypt.hash` is async (returns a Promise) because hashing is slow. We `await` it.

`bcrypt.compare` extracts the salt and cost from the stored hash, hashes the input with the same salt and cost, and compares. Returns a boolean. Also async.

The salt is *embedded in the hash*. We don't need to store it separately. bcrypt handles it.

## The Signup Flow

```js
app.post('/signup', async (req, res) => {
  const { username, password } = req.body;
  // ... validation ...
  const hash = await bcrypt.hash(password, 10);
  USERS.set(username, { username, hash, createdAt: Date.now() });
  res.status(201).json({ username });
});
```

1. Receive the plaintext password from the client
2. Hash it with bcrypt (cost 10)
3. Store the *hash*, not the password
4. Return success

The plaintext password is in `req.body.password` for ~1 millisecond. Then it's hashed. The hash is what we keep.

## The Login Flow

```js
app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  const user = USERS.get(username);
  if (!user) {
    return res.status(401).json({ error: 'invalid credentials' });
  }
  const ok = await bcrypt.compare(password, user.hash);
  if (!ok) {
    return res.status(401).json({ error: 'invalid credentials' });
  }
  req.session.username = user.username;
  res.json({ username: user.username });
});
```

1. Receive the plaintext password
2. Look up the user by username
3. If not found, return 401
4. Compare the input password with the stored hash
5. If they match, the user is authenticated
6. Set the session and return success

## Why the Same Error for Both

```js
if (!user) {
  return res.status(401).json({ error: 'invalid credentials' });
}
const ok = await bcrypt.compare(password, user.hash);
if (!ok) {
  return res.status(401).json({ error: 'invalid credentials' });
}
```

Both error cases return the *same* message: "invalid credentials". This prevents *username enumeration* — an attacker can't tell "this username exists" from "this username doesn't exist" by the error message.

If we returned "user not found" for unknown usernames and "wrong password" for known ones, the attacker could enumerate usernames. They'd know which usernames exist. They could then focus their password brute-force on real accounts.

By returning the same error, the attacker can't tell. They have to guess both username and password.

## The Timing Attack

There's also a *timing* attack. If `bcrypt.compare` is only called when the user exists, the response is faster for non-existent users. The attacker can measure response times to enumerate usernames.

The fix: always do a bcrypt compare, even for non-existent users. We'd hash a dummy password and compare against a dummy hash:

```js
const DUMMY_HASH = '$2b$10$abcdefghijklmnopqrstuv...';

if (!user) {
  await bcrypt.compare(password, DUMMY_HASH);
  return res.status(401).json({ error: 'invalid credentials' });
}
```

This is overkill for most apps. We don't do it here. We'll mention it again in project 33 (RBAC).

## Common Confusions (read these)

**Confusion 1: "Why not MD5 or SHA-1?"**
Both are *fast* hash functions. They are designed for speed (file integrity, etc.). They are not designed for passwords. They can be brute-forced in seconds. Use bcrypt or argon2.

**Confusion 2: "Why not SHA-256 with a salt?"**
SHA-256 is still fast. Salting defeats rainbow tables, but the slowness is what defeats brute-force. Use a slow hash.

**Confusion 3: "What is argon2?"**
The newer standard. Wins the Password Hashing Competition (2015). More secure than bcrypt. Not as widely supported. We use bcrypt because it's universal.

**Confusion 4: "Why cost 10?"**
The default. As CPUs get faster, increase it. The cost is in the hash itself, so old hashes still work. We can re-hash on login to upgrade.

**Confusion 5: "Can I decrypt a bcrypt hash?"**
No. That's the point. It's one-way. The only way to "decrypt" is to brute-force the input, which is expensive because bcrypt is slow.

**Confusion 6: "What if two users have the same password?"**
Different salts, different hashes. `bcrypt.hash('hunter2', 10)` for alice ≠ `bcrypt.hash('hunter2', 10)` for bob. The salt is random.

**Confusion 7: "Can I see the salt?"**
Yes, it's in the hash string: `$2b$10$N9qo8uLOickgx2ZMRZoMye...`. The first 22 characters after the cost are the salt.

**Confusion 8: "What about a user enumeration attack via timing?"**
As discussed. We accept the small timing leak for simplicity. In production, you'd use a dummy hash.

## What We Are About to Build

A ~50-line Express app that:

1. Has `POST /signup` with bcrypt hashing
2. Has `POST /login` with bcrypt comparison
3. Has `GET /me` (session check)
4. Has `POST /logout` (session destroy)
5. Stores users in memory with hashed passwords

The handlers are async (bcrypt is async). The patterns are the same as project 07. The new pieces are bcrypt and the USERS Map.

In [BUILD.md](./BUILD.md) we will go line by line.
