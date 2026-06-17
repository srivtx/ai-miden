// GraphQL Demo — Schema, resolvers, queries, mutations, without external libs.
const express = require('express');
const app = express();
app.use(express.json());

// === In-memory data ===
const users = [
  { id: 1, name: 'Alice', email: 'alice@example.com' },
  { id: 2, name: 'Bob', email: 'bob@example.com' },
];
const posts = [
  { id: 1, title: 'First post', body: 'Hello world', userId: 1 },
  { id: 2, title: 'GraphQL is great', body: 'Typed queries are nice', userId: 1 },
  { id: 3, title: 'Bob writes', body: 'Hi from Bob', userId: 2 },
];
const comments = [
  { id: 1, postId: 1, author: 'Bob', text: 'Great post!' },
  { id: 2, postId: 1, author: 'Alice', text: 'Thanks!' },
];

// === GraphQL schema (simple string-based DSL) ===
const schema = `
type User { id: Int, name: String, email: String, posts: [Post] }
type Post { id: Int, title: String, body: String, user: User, comments: [Comment] }
type Comment { id: Int, postId: Int, author: String, text: String }

type Query {
  users: [User]
  user(id: Int): User
  posts: [Post]
  post(id: Int): Post
}

type Mutation {
  createUser(name: String!, email: String!): User
  createPost(title: String!, userId: Int!): Post
  addComment(postId: Int!, author: String!, text: String!): Comment
}
`;

// === Resolvers ===
const resolvers = {
  Query: {
    users: () => users,
    user: ({ id }) => users.find(u => u.id === id),
    posts: () => posts,
    post: ({ id }) => posts.find(p => p.id === id),
  },
  Mutation: {
    createUser: ({ name, email }) => {
      const u = { id: users.length + 1, name, email };
      users.push(u);
      return u;
    },
    createPost: ({ title, userId }) => {
      const p = { id: posts.length + 1, title, body: '', userId };
      posts.push(p);
      return p;
    },
    addComment: ({ postId, author, text }) => {
      const c = { id: comments.length + 1, postId, author, text };
      comments.push(c);
      return c;
    },
  },
  User: {
    posts: (user) => posts.filter(p => p.userId === user.id),
  },
  Post: {
    user: (post) => users.find(u => u.id === post.userId),
    comments: (post) => comments.filter(c => c.postId === post.id),
  },
};

// === Tiny GraphQL executor (parses, validates, executes) ===
function executeQuery(query, variables = {}) {
  const errors = [];
  // Very small parser: find the first query/mutation block
  const queryMatch = query.match(/(query|mutation)\s*(\([^)]*\))?\s*\{([\s\S]*)\}/);
  if (!queryMatch) return { errors: [{ message: 'Could not parse query' }] };
  const opType = queryMatch[1];
  const body = queryMatch[3];

  // Parse selection sets
  function parseSelections(text) {
    return text.trim();
  }

  function resolve(typename, selections, root) {
    if (Array.isArray(root)) return root.map(r => resolveObj(typename, selections, r));
    return resolveObj(typename, selections, root);
  }

  function resolveObj(typename, selections, root) {
    if (!root) return null;
    const result = {};
    const fieldRegex = /(\w+)(?:\s*\(([^)]*)\))?\s*(?:\{([^}]*)\})?/g;
    let m;
    while ((m = fieldRegex.exec(selections)) !== null) {
      const fieldName = m[1];
      const args = parseArgs(m[2] || '', variables);
      const subSelections = m[3];
      const resolver = resolvers[typename]?.[fieldName];
      let value;
      if (resolver) value = resolver({ ...args }, root);
      else if (root[fieldName] !== undefined) value = root[fieldName];
      else { errors.push({ message: `Cannot resolve field ${typename}.${fieldName}` }); continue; }
      if (subSelections) {
        // Determine the inner type from the schema (very rough)
        const innerType = typename === 'Query' && fieldName === 'users' ? 'User' : fieldName === 'posts' ? 'Post' : fieldName === 'user' ? 'User' : fieldName === 'post' ? 'Post' : 'Post';
        const arrayValue = Array.isArray(value) ? value : [value];
        const resolved = arrayValue.map(v => resolveObj(innerType, subSelections, v));
        result[fieldName] = Array.isArray(value) ? resolved : resolved[0];
      } else {
        result[fieldName] = value;
      }
    }
    return result;
  }

  function parseArgs(argStr, vars) {
    if (!argStr.trim()) return {};
    const args = {};
    const re = /(\w+):\s*("[^"]*"|[\d.]+|\w+)/g;
    let m;
    while ((m = re.exec(argStr)) !== null) {
      const key = m[1];
      let val = m[2];
      if (val.startsWith('"')) val = val.slice(1, -1);
      else if (!isNaN(val)) val = Number(val);
      else if (vars[val] !== undefined) val = vars[val];
      args[key] = val;
    }
    return args;
  }

  const data = resolveObj(opType === 'query' ? 'Query' : 'Mutation', parseSelections(body), {});
  return { data, errors: errors.length ? errors : undefined };
}

// === Routes ===
app.post('/graphql', (req, res) => {
  const { query, variables } = req.body;
  if (!query) return res.status(400).json({ errors: [{ message: 'missing_query' }] });
  res.json(executeQuery(query, variables));
});

app.get('/graphql/schema', (req, res) => res.type('text/plain').send(schema));

// === Try these queries via POST /graphql ===
const examples = {
  listUsers: '{ users { id name email } }',
  oneUser: '{ user(id: 1) { name posts { title } } }',
  allPosts: '{ posts { id title user { name } comments { author text } } }',
  mutation: 'mutation { createUser(name: "Carol", email: "carol@x.com") { id name } }',
};

app.get('/graphql/examples', (req, res) => res.json(examples));

app.listen(3000, () => console.log('GraphQL demo :3000 — POST /graphql with { query, variables }'));
module.exports = app;
