# The Decisions

> *"Hashing is one-way. Salting defeats rainbow tables. Slowness defeats brute-force. bcrypt is all three."*

## Decision 1: bcrypt and not MD5/SHA-1/SHA-256/PBKDF2/Argon2

**Alternatives**:
- **MD5** — fast, broken, do not use
- **SHA-1** — fast, broken for collisions, do not use
- **SHA-256** — fast, secure for integrity, not for passwords
- **PBKDF2** — slow, NIST-approved, used in some standards
- **scrypt** — slow, memory-hard, used in some crypto coins
- **Argon2** — modern winner of the Password Hashing Competition, more secure than bcrypt

**Why bcrypt**: It is the most widely-used password hash. It is slow on purpose. It is salted. It has a cost factor that can be increased over time. It is what every Node tutorial uses. It is what every Node developer knows.

**Trade-off**: Argon2 is theoretically more secure (memory-hard, resistant to GPU attacks). We use bcrypt because it is the standard. The migration to Argon2 is straightforward if needed.

## Decision 2: Cost factor 10

**Alternative**: Higher (12, 14) for more security, lower (8) for faster login.

**Why 10**: The modern default. ~100ms per hash on a typical server. Fast enough for login UX, slow enough to defeat brute-force.

**Trade-off**: As CPUs get faster, increase the cost. We can re-hash on login to upgrade. For now, 10 is fine.

## Decision 3: Same error for "user not found" and "wrong password"

**Alternative**: Different errors.

**Why same**: Prevents username enumeration. An attacker can't tell which usernames exist by the error message.

**Trade-off**: Slightly worse UX (user doesn't know if they mistyped the username or the password). For an API, this is fine. The error message is the same.

## Decision 4: No dummy hash for timing attack

**Alternative**: Always call `bcrypt.compare`, even for non-existent users, against a dummy hash.

**Why we don't**: The timing leak is small (~100ms). For most apps, the username-enumeration attack is theoretical. We accept the leak for simpler code.

**Trade-off**: A sophisticated attacker can enumerate usernames via timing. We'll revisit in project 33 (RBAC).

## Decision 5: No password strength requirements

**Alternative**: Require min length, complexity, etc.

**Why we don't**: Out of scope for this project. We'll add validation in project 14 (Validator).

**Trade-off**: Users can sign up with "a" as their password. Bad. We accept this for now.

## Decision 6: No email verification

**Alternative**: Send a verification email, require click.

**Why we don't**: We don't have email yet (project 21). And we don't have a real user model with email (project 11+).

**Trade-off**: Users can sign up with fake emails. We accept this for now.

## Decision 7: Username as primary key

**Alternative**: Numeric ID, email, etc.

**Why username**: Simple. Easy to reason about. We don't have a database yet, so the in-memory Map uses username as the key.

**Trade-off**: Username can't be changed (it's the key). Email-based login is more common. We'll move to ID-based in project 11 (Foreign Key).

## Decision 8: In-memory USERS Map

**Alternative**: Database (project 10).

**Why in-memory**: We don't have a database yet. In-memory is fine for development.

**Trade-off**: Restart the server, all users are gone. We'll move to a DB in project 10.

## Decision 9: No rate limiting

**Alternative**: Limit login attempts to prevent brute-force.

**Why we don't**: Out of scope for this project. We'll add rate limiting in project 24 (Rate Limiter).

**Trade-off**: An attacker can try millions of passwords. We accept this for now.

## Decision 10: bcrypt native binding

`bcrypt` uses a native C binding for speed. The pure-JS alternative is `bcryptjs`, which is slower but easier to install (no compiler needed).

**Why bcrypt**: It's the standard. It's fast. The install is fine on most systems (it has prebuilt binaries).

**Trade-off**: If the install fails, you can use `bcryptjs` instead. The API is identical.

---

## What We Did Not Decide

- **Password reset** — out of scope (project 21, Mailroom)
- **Email verification** — out of scope (project 21)
- **Two-factor auth** — out of scope
- **Refresh tokens** — out of scope (project 09, JWT)
- **Session timeout** — out of scope (project 25, Cron)
- **Account lockout** — out of scope (project 24, Rate Limiter)
- **Argon2 migration** — out of scope
- **Password strength rules** — out of scope (project 14, Validator)
- **CAPTCHA on signup/login** — out of scope

Each is a future decision.

---

## The Meta-Decision: This Is Real Authentication

The signup/login flow in this project is *exactly* what every web app does. The patterns — hash on signup, compare on login, store the hash not the password — are universal. The libraries (bcrypt) are universal. The mistakes (plaintext storage, fast hashes) are universal — and now you know to avoid them.

Every subsequent project assumes passwords are bcrypt-hashed. The `USERS` Map will become a `users` table in project 10. The session will become a JWT in project 09. The password verification flow stays the same.

This is the foundation of identity. It is solid.
