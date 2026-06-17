# GraphQL Demo — Schema, resolvers, queries, mutations (no external libs)

A 200-line GraphQL executor that parses queries, resolves fields, and handles nested selection sets. Shows: how GraphQL works, why it's typed, and what resolvers do.

## Endpoints
```
POST /graphql         { query, variables }   -> { data, errors }
GET  /graphql/schema                       -> SDL text
GET  /graphql/examples                     -> ready-to-use queries
```

## Try
```bash
# Simple query
curl -X POST http://localhost:3000/graphql -H "Content-Type: application/json" \
  -d '{"query": "{ users { id name } }"}'
# { data: { users: [{ id: 1, name: "Alice" }, { id: 2, name: "Bob" }] } }

# Nested query (selects fields from related entities)
curl -X POST http://localhost:3000/graphql -H "Content-Type: application/json" \
  -d '{"query": "{ user(id: 1) { name posts { title comments { author } } } }"}'

# Mutation
curl -X POST http://localhost:3000/graphql -H "Content-Type: application/json" \
  -d '{"query": "mutation { createUser(name: \"Carol\", email: \"c@x.com\") { id name } }"}'
```

## What this teaches
1. **GraphQL schema**: types (User, Post, Comment) and their fields
2. **Query vs mutation**: read vs write
3. **Selection sets**: client picks exactly which fields it wants
4. **Nested resolvers**: User.posts, Post.user, Post.comments
5. **Variables**: `query($id: Int!) { user(id: $id) { name } }` with `{ variables: { id: 1 } }`
6. **vs REST**: one endpoint, client controls response shape, no over-fetching
7. **Real GraphQL** (Apollo, graphql-yoga) does the same with proper parsing, validation, and execution
