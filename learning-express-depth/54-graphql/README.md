# 54 — GraphQL

**New concept:** a different API style. Instead of many URLs, one URL. The client asks for exactly what it wants.

REST: `GET /users/1` returns everything. `GET /users/1/posts` returns their posts. Two requests, two URLs.

GraphQL: one request to `/graphql`, client specifies the shape:
```graphql
{
  user(id: 1) {
    name
    posts {
      title
    }
  }
}
```
Server returns exactly that shape. No more, no less.

## Run it

```bash
npm install
node server.js
```

Open `http://localhost:3000/graphql` in a browser. You'll see GraphiQL — a UI to test queries.

Try these queries:

```graphql
# All users, just their name and email
{
  users {
    name
    email
  }
}

# One user with their posts
{
  user(id: 1) {
    name
    posts {
      title
      body
    }
  }
}

# All posts with author info
{
  posts {
    title
    user {
      name
    }
  }
}
```

## How to think about it

REST is like a menu. Each URL is a dish. You order one, you get what's on the plate.

GraphQL is like a buffet. One trip to the buffet. You take exactly what you want.

The trade-off: GraphQL is more flexible but more complex on both client and server. REST is simpler but less flexible.

## How to build it (line by line)

```js
const schema = buildSchema(`
  type User {
    id: Int
    name: String
    posts: [Post]
  }
  type Query {
    users: [User]
    user(id: Int!): User
  }
`);
```

**Lines 16-28.** Define the schema. This is the contract: what the client can ask for, and what they get back.

**`type User { ... }`** — a User has an id (Int), a name (String), and posts (an array of Post).

**`type Query { ... }`** — the top-level entry points. The client can start with `users`, `user`, or `posts`.

**`Int!`** — the `!` means required.

```js
const root = {
  users: () => users,
  user: ({ id }) => users.find(u => u.id === id),
  'User.posts': (user) => posts.filter(p => p.userId === user.id),
};
```

**Lines 31-38.** Resolvers. When the client asks for users, call `users()`. When they ask for a user by id, call `user({ id })`.

**`'User.posts'`** is a nested resolver: when the client asks for `user.posts`, this is what gets called.

## What we learned

1. GraphQL = one URL, flexible queries
2. Schema defines what's possible
3. Resolvers fetch the data
4. The client gets exactly what they ask for
5. GraphiQL is a UI for testing queries
6. Trade-off: flexibility vs simplicity

## What's next

In **55-encryption** we encrypt sensitive data at rest.
