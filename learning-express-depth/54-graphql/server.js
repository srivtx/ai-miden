// 54 — GraphQL
// NEW CONCEPT: a different API style.
// REST: many URLs, each returns fixed data.
// GraphQL: one URL, client asks for exactly what it wants.
const express = require('express');
const { graphqlHTTP } = require('express-graphql');
const { buildSchema, graphql } = require('graphql');
const app = express();

// Sample data
const users = [
  { id: 1, name: 'Alice', email: 'alice@example.com' },
  { id: 2, name: 'Bob', email: 'bob@example.com' },
];
const posts = [
  { id: 1, userId: 1, title: 'First post', body: 'Hello world' },
  { id: 2, userId: 1, title: 'Second post', body: 'More content' },
  { id: 3, userId: 2, title: 'Bob writes', body: 'Hi from Bob' },
];

// Schema: defines what the client can ask for
const schema = buildSchema(`
  type User {
    id: Int
    name: String
    email: String
    posts: [Post]
  }
  type Post {
    id: Int
    title: String
    body: String
    user: User
  }
  type Query {
    users: [User]
    user(id: Int!): User
    posts: [Post]
  }
`);

// Resolvers: how to actually get the data
const root = {
  users: () => users,
  user: ({ id }) => users.find(u => u.id === id),
  posts: () => posts,
  // Nested resolvers
  'User.posts': (user) => posts.filter(p => p.userId === user.id),
  'Post.user': (post) => users.find(u => u.id === post.userId),
};

app.use('/graphql', graphqlHTTP({ schema, rootValue: root, graphiql: true }));

app.listen(3000, () => console.log('GraphQL on http://localhost:3000/graphql (GraphiQL UI)'));
