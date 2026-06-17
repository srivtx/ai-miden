// GraphQL API — Same data as REST, client picks the exact fields they want.
const { ApolloServer, gql } = require('apollo-server-express');
const express = require('express');

// ---- DATA (same as any REST API) ----
const users = [
  { id: '1', name: 'Zen', email: 'zen@test.com' },
  { id: '2', name: 'Ava', email: 'ava@test.com' },
];
const posts = [
  { id: '1', title: 'Hello World', content: 'First post!', authorId: '1', likes: 5 },
  { id: '2', title: 'GraphQL Rocks', content: 'So flexible', authorId: '1', likes: 12 },
  { id: '3', title: 'REST vs GraphQL', content: 'GraphQL wins', authorId: '2', likes: 8 },
];

// ---- SCHEMA (type definitions) ----
const typeDefs = gql`
  type User {
    id: ID!
    name: String!
    email: String!
    posts: [Post!]!
  }
  type Post {
    id: ID!
    title: String!
    content: String!
    author: User!
    likes: Int!
  }
  type Query {
    users: [User!]!
    user(id: ID!): User
    posts: [Post!]!
    post(id: ID!): Post
  }
  type Mutation {
    createPost(title: String!, content: String!, authorId: ID!): Post!
    likePost(id: ID!): Post!
  }
`;

// ---- RESOLVERS (how to fetch each field) ----
const resolvers = {
  Query: {
    users: () => users,
    user: (_, { id }) => users.find(u => u.id === id),
    posts: () => posts,
    post: (_, { id }) => posts.find(p => p.id === id),
  },
  User: {
    posts: (user) => posts.filter(p => p.authorId === user.id), // N+1 naive, for demo
  },
  Post: {
    author: (post) => users.find(u => u.id === post.authorId),
  },
  Mutation: {
    createPost: (_, { title, content, authorId }) => {
      const post = { id: String(posts.length + 1), title, content, authorId, likes: 0 };
      posts.push(post);
      return post;
    },
    likePost: (_, { id }) => {
      const post = posts.find(p => p.id === id);
      if (post) post.likes++;
      return post;
    },
  },
};

async function startServer() {
  const app = express();
  const server = new ApolloServer({ typeDefs, resolvers });
  await server.start();
  server.applyMiddleware({ app });
  app.listen(3000, () => console.log(`GraphQL: http://localhost:3000${server.graphqlPath}`));
}
startServer();
/*
Test queries (paste in GraphQL playground at http://localhost:3000/graphql):

# Get all users with their posts (one query, no over-fetching)
query {
  users {
    name
    email
    posts { title likes }
  }
}

# Get one user with minimal fields
query { user(id: "1") { name } }

# Create a post (mutation)
mutation {
  createPost(title: "New Post", content: "Hello", authorId: "1") { id title author { name } }
}
*/
