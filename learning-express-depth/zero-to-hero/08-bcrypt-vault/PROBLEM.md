# The Problem

> *"Plaintext passwords are criminal. They are also the most common security mistake in history."*

## Why Plaintext Is Bad

Imagine you store passwords in plaintext:

```js
USERS.set('alice', { username: 'alice', password: 'hunter2' });
```

Now imagine an attacker steals your database. They get:

```
alice: hunter2
bob: correcthorsebatterystaple
carol: 12345678
```

Every user's password is exposed. The attacker can:
- Log in as any user
- Try the same password on other sites (most users reuse passwords)
- Sell the database on the dark web
- Phish users by pretending to be a service they use

This is the **#1 cause of data breaches**. It is so common that there are websites dedicated to tracking it (haveibeenpwned.com). It is so preventable that storing plaintext is considered professional malpractice.

**The pain**: We must never store plaintext passwords. We must store a *hash* — a one-way function of the password that cannot be reversed.

## What Pain Is This Solving?

In project 07, our `/login` had no password. Anyone could be anyone. This is not authentication; this is theater.

This project adds real auth:
1. User signs up with a password
2. Server hashes the password and stores the hash
3. User logs in with a password
4. Server hashes the input with the same salt
5. Server compares the hashes
6. If they match, the user is authenticated

The plaintext password is *never* stored. The hash is what we keep. If the database is stolen, the attacker gets hashes, not passwords. They cannot reverse the hash to get the password (in theory).

## The Deeper Problem: Hashes Alone Are Not Enough

A *hash* is a one-way function: `hash(password) → fixed-length output`. Examples: MD5, SHA-1, SHA-256.

If you store `hash("hunter2") = "ab12cd34..."`, an attacker can:
- Pre-compute hashes of common passwords (a "rainbow table")
- Look up `ab12cd34...` in the table to find "hunter2"
- Brute-force: try every common password, hash it, see if it matches

Common passwords are in every rainbow table. The attack is fast.

**The fix**: a *salt* — random data added to the password before hashing. The salt is stored alongside the hash. Two users with the same password get different hashes.

**The second fix**: a *slow* hash function. SHA-256 is fast — billions of hashes per second on a GPU. Brute-force is trivial. bcrypt is *slow* on purpose: ~10 hashes per second per CPU core. Brute-force becomes infeasible.

bcrypt is the standard. It is slow. It is salted. It is one-way. It is what we use.

## What This Project Will Solve

This project will:

1. Add `POST /signup` that creates a user with a hashed password
2. Add `POST /login` that verifies a password
3. Use bcrypt with cost factor 10 (the default)
4. Store users in an in-memory `USERS` Map
5. Return the same error for "user not found" and "wrong password" (to prevent username enumeration)

By the end, only users with the correct password can log in. The server never sees the plaintext password after signup.

## What This Project Will *Not* Solve

- **Stateless tokens** — sessions are still in memory. Project 09 (JWT).
- **Persistent storage** — users are in memory. Project 10 (SQLite).
- **Password reset** — out of scope for this project.
- **Email verification** — out of scope.
- **Two-factor auth** — out of scope.
- **Rate limiting login attempts** — out of scope (project 24).
- **Password strength requirements** — out of scope (project 14, Validator).
- **Argon2** — a newer, more secure hash function. bcrypt is still the standard. We use bcrypt.

## The Question This Project Answers

> *"How do I store passwords securely?"*

If you can answer: "hash with bcrypt, store the hash, verify with bcrypt.compare, never store plaintext," you are ready for project 09.
