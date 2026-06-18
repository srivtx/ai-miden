# The Build

> *"URLs are resources. Methods are verbs. Status codes are meanings. Refactor accordingly."*

We are going to refactor the URLs to be REST-shaped, add missing methods, and add missing endpoints.

## The New Endpoint Map

```
POST   /users
GET    /users
GET    /users/:id
PATCH  /users/:id
DELETE /users/:id

POST   /sessions
DELETE /sessions
GET    /sessions/me

GET    /posts
GET    /posts/:id
POST   /posts
PATCH  /posts/:id
DELETE /posts/:id

GET    /users/:id/posts
POST   /users/:id/posts
```

## The Code

The full server.js is restructured around these endpoints. The auth, post, and user logic is the same as project 16. The new pieces are PATCH/DELETE handlers, list handlers, and the new endpoint paths.

### Schemas

We need new schemas for the new endpoints:

```js
const userCreateSchema = z.object({
  username: z.string().min(3).max(30).regex(/^[a-zA-Z0-9_]+$/),
  password: z.string().min(8).max(100),
  email: z.string().email().optional(),
});

const userUpdateSchema = z.object({
  username: z.string().min(3).max(30).regex(/^[a-zA-Z0-9_]+$/).optional(),
  email: z.string().email().optional(),
});

const sessionCreateSchema = z.object({
  username: z.string().min(1),
  password: z.string().min(1),
});

const postCreateSchema = z.object({
  title: z.string().min(1).max(200),
  body: z.string().min(1).max(10000),
});

const postUpdateSchema = z.object({
  title: z.string().min(1).max(200).optional(),
  body: z.string().min(1).max(10000).optional(),
});
```

`userCreateSchema` and `sessionCreateSchema` are the same as `signupSchema` and `loginSchema` from project 16. We rename for clarity.

`userUpdateSchema` and `postUpdateSchema` are PATCH schemas — all fields are optional (you can update just one field).

### User Endpoints

```js
// Create user
app.post('/users', validate(userCreateSchema), asyncHandler(async (req, res) => {
  const { username, password, email } = req.validated;
  const existing = await db('users').where({ username }).first();
  if (existing) {
    req.log.warn({ username }, 'user create conflict');
    throw new ConflictError('username already taken');
  }
  const hash = await bcrypt.hash(password, 10);
  const [id] = await db('users').insert({ username, hash, email: email || null, created_at: Date.now() });
  req.log.info({ userId: id, username }, 'user created');
  res.status(201).json({ id, username, email: email || null });
}));

// List users
app.get('/users', asyncHandler(async (req, res) => {
  const users = await db('users').select('id', 'username', 'email', 'created_at');
  res.json(users);
}));

// Get one user
app.get('/users/:id', asyncHandler(async (req, res) => {
  const user = await db('users').select('id', 'username', 'email', 'created_at').where({ id: req.params.id }).first();
  if (!user) {
    throw new NotFoundError('User not found');
  }
  res.json(user);
}));

// Update user
app.patch('/users/:id', authMiddleware, validate(userUpdateSchema), asyncHandler(async (req, res) => {
  if (Number(req.params.id) !== req.user.userId) {
    throw new ForbiddenError('You can only update your own user');
  }
  const updates = req.validated;
  if (Object.keys(updates).length === 0) {
    throw new ValidationError([{ path: '', message: 'no fields to update' }]);
  }
  await db('users').where({ id: req.params.id }).update(updates);
  const user = await db('users').select('id', 'username', 'email', 'created_at').where({ id: req.params.id }).first();
  req.log.info({ userId: req.params.id, updates }, 'user updated');
  res.json(user);
}));

// Delete user
app.delete('/users/:id', authMiddleware, asyncHandler(async (req, res) => {
  if (Number(req.params.id) !== req.user.userId) {
    throw new ForbiddenError('You can only delete your own user');
  }
  await db('users').where({ id: req.params.id }).delete();
  req.log.info({ userId: req.params.id }, 'user deleted');
  res.status(204).end();
}));
```

### Session Endpoints

```js
// Create session (login)
app.post('/sessions', validate(sessionCreateSchema), asyncHandler(async (req, res) => {
  const { username, password } = req.validated;
  const user = await db('users').where({ username }).first();
  if (!user) {
    throw new UnauthorizedError('invalid credentials');
  }
  const ok = await bcrypt.compare(password, user.hash);
  if (!ok) {
    throw new UnauthorizedError('invalid credentials');
  }
  const token = jwt.sign({ userId: user.id, username: user.username }, SECRET, { expiresIn: TOKEN_TTL });
  req.log.info({ userId: user.id, username }, 'session created');
  res.status(201).json({ token, user: { id: user.id, username: user.username, email: user.email } });
}));

// Delete session (logout)
app.delete('/sessions', authMiddleware, asyncHandler(async (req, res) => {
  req.log.info({ userId: req.user.userId }, 'session deleted');
  res.status(204).end();
}));

// Get current session (me)
app.get('/sessions/me', authMiddleware, asyncHandler(async (req, res) => {
  const user = await db('users').select('id', 'username', 'email', 'created_at').where({ id: req.user.userId }).first();
  if (!user) {
    throw new NotFoundError('User not found');
  }
  res.json(user);
}));
```

### Post Endpoints

```js
// List posts
app.get('/posts', asyncHandler(async (req, res) => {
  const posts = await db('posts')
    .join('users', 'posts.user_id', 'users.id')
    .select('posts.*', 'users.username as author')
    .orderBy('posts.created_at', 'desc');
  res.json(posts);
}));

// Get one post
app.get('/posts/:id', asyncHandler(async (req, res) => {
  const post = await db('posts')
    .join('users', 'posts.user_id', 'users.id')
    .select('posts.*', 'users.username as author')
    .where('posts.id', req.params.id)
    .first();
  if (!post) {
    throw new NotFoundError('Post not found');
  }
  res.json(post);
}));

// Create post
app.post('/posts', authMiddleware, validate(postCreateSchema), asyncHandler(async (req, res) => {
  const { title, body } = req.validated;
  const [id] = await db('posts').insert({ user_id: req.user.userId, title, body, created_at: Date.now() });
  req.log.info({ postId: id, userId: req.user.userId, title }, 'post created');
  res.status(201).json({ id, userId: req.user.userId, title, body });
}));

// Update post
app.patch('/posts/:id', authMiddleware, validate(postUpdateSchema), asyncHandler(async (req, res) => {
  const updates = req.validated;
  if (Object.keys(updates).length === 0) {
    throw new ValidationError([{ path: '', message: 'no fields to update' }]);
  }
  const post = await db('posts').where({ id: req.params.id }).first();
  if (!post) {
    throw new NotFoundError('Post not found');
  }
  if (post.user_id !== req.user.userId) {
    throw new ForbiddenError('You can only update your own posts');
  }
  await db('posts').where({ id: req.params.id }).update(updates);
  const updated = await db('posts').where({ id: req.params.id }).first();
  req.log.info({ postId: req.params.id, updates }, 'post updated');
  res.json(updated);
}));

// Delete post
app.delete('/posts/:id', authMiddleware, asyncHandler(async (req, res) => {
  const post = await db('posts').where({ id: req.params.id }).first();
  if (!post) {
    throw new NotFoundError('Post not found');
  }
  if (post.user_id !== req.user.userId) {
    throw new ForbiddenError('You can only delete your own posts');
  }
  await db('posts').where({ id: req.params.id }).delete();
  req.log.info({ postId: req.params.id }, 'post deleted');
  res.status(204).end();
}));
```

### Nested Resources

```js
// List posts by user
app.get('/users/:id/posts', asyncHandler(async (req, res) => {
  const posts = await db('posts').where({ user_id: req.params.id }).orderBy('created_at', 'desc');
  res.json(posts);
}));

// Create post by user (alternative to POST /posts)
app.post('/users/:id/posts', authMiddleware, validate(postCreateSchema), asyncHandler(async (req, res) => {
  if (Number(req.params.id) !== req.user.userId) {
    throw new ForbiddenError('You can only post as yourself');
  }
  const { title, body } = req.validated;
  const [id] = await db('posts').insert({ user_id: req.user.userId, title, body, created_at: Date.now() });
  res.status(201).json({ id, userId: req.user.userId, title, body });
}));
```

---

## Status Codes Recap

Every endpoint returns the right code:

- 200 OK for successful GET, PUT, PATCH
- 201 Created for successful POST
- 204 No Content for successful DELETE
- 400 Bad Request for validation errors
- 401 Unauthorized for missing/invalid auth
- 403 Forbidden for authed but not allowed
- 404 Not Found for missing resources
- 409 Conflict for state conflicts
- 500 Internal Server Error for unexpected errors

The wall handles all of this (project 15).

---

## What You Should Do Now

This is a refactor project — the new file is ~250 lines. Read it carefully. Notice:

- The new URL patterns
- The new methods (PATCH, DELETE)
- The new status codes
- The new endpoints (list, get, update, delete for users and posts)
- The new schemas (userUpdateSchema, postUpdateSchema)
- The `ForbiddenError` (added in this project, see Decisions)

The behavior is the same as project 16. The structure is REST.

In project 18, we will add pagination to the list endpoints (`GET /posts?limit=20&offset=0`).

In [CONNECT.md](./CONNECT.md) we will see what pain this project leaves.
