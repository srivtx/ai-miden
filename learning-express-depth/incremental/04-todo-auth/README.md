# 04 — Todo (auth)

Add users. Signup, login, JWT. Each user has their own todos.

**What's new:**
- `users` table with hashed passwords
- `user_id` column on todos
- `/auth/signup` and `/auth/login` endpoints
- JWT in the `Authorization: Bearer <token>` header
- `auth` middleware sets `req.user`
- Every todo query filters by `user_id`

**Why hashed passwords?** Never store plain text. If your database leaks, attackers can't read the passwords.

**Why JWT?** Stateless. The server doesn't keep track of who's logged in. The token itself proves it. The server can verify the signature without looking anything up.

## Run
```bash
npm install
node server.js
```

```bash
# Signup
TOKEN=$(curl -X POST http://localhost:3000/auth/signup -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "password123"}' | grep -o '"token":"[^"]*' | cut -d'"' -f4)

# Create a todo (with the token)
curl -H "Authorization: Bearer $TOKEN" -X POST http://localhost:3000/todos \
  -H "Content-Type: application/json" -d '{"title": "Buy milk"}'

# Without token: 401
curl http://localhost:3000/todos
```

## What this stage teaches
- Password hashing (PBKDF2)
- JWT signing and verification
- Auth middleware
- User-scoped queries (the most important security pattern)

## Next
**05-todo-multi-tenant** — add teams. A user belongs to a team. All team members see the team's todos.
