// Social Media — Posts, follows, feed (timeline), likes, comments, notifications.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const posts = []; const follows = new Set(); const likes = new Set(); const comments = []; const notifications = [];
let postId = 1, cmtId = 1, notifId = 1;

function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }

function notify(userId, type, message, relatedId) { notifications.push({ id: notifId++, userId, type, message, relatedId, read: false, createdAt: new Date().toISOString() }); }

function userPublic(user) { return { id: user.id, name: user.name, email: user.email, bio: user.bio }; }

app.post('/auth/register', async (req, res) => {
  const { name, email, password, bio } = req.body;
  if (!email || !password || !name) return res.status(400).json({ error: 'name, email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  const user = { id: users.length + 1, name, email, password: await bcrypt.hash(password, 10), bio: bio || '', followerCount: 0, followingCount: 0 };
  users.push(user);
  res.status(201).json({ user: userPublic(user), token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ user: userPublic(user), token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});

// USERS
app.get('/users', auth, (req, res) => {
  if (req.query.search) { const q = req.query.search.toLowerCase(); return res.json(users.filter(u => u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)).map(userPublic)); }
  res.json(users.map(userPublic));
});
app.get('/users/:id', auth, (req, res) => {
  const user = users.find(u => u.id === parseInt(req.params.id));
  if (!user) return res.status(404).json({ error: 'Not found' });
  const userPosts = posts.filter(p => p.userId === user.id).length;
  res.json({ ...userPublic(user), postCount: userPosts, followerCount: [...follows].filter(f => f.endsWith(`:${user.id}`)).length, followingCount: [...follows].filter(f => f.startsWith(`${user.id}:`)).length });
});

// FOLLOW/UNFOLLOW
app.post('/users/:id/follow', auth, (req, res) => {
  if (parseInt(req.params.id) === req.user.id) return res.status(400).json({ error: 'Cannot follow yourself' });
  const key = `${req.user.id}:${req.params.id}`;
  if (follows.has(key)) { follows.delete(key); notify(parseInt(req.params.id), 'unfollow', `${users.find(u => u.id === req.user.id)?.name} unfollowed you`, req.user.id); return res.json({ following: false }); }
  follows.add(key);
  notify(parseInt(req.params.id), 'follow', `${users.find(u => u.id === req.user.id)?.name} started following you`, req.user.id);
  res.json({ following: true });
});

app.get('/users/:id/followers', auth, (req, res) => {
  const followerIds = [...follows].filter(f => f.endsWith(`:${req.params.id}`)).map(f => parseInt(f.split(':')[0]));
  res.json(followerIds.map(id => userPublic(users.find(u => u.id === id))));
});

// POSTS
app.post('/posts', auth, (req, res) => {
  const { content, image } = req.body;
  if (!content) return res.status(400).json({ error: 'Content required' });
  const post = { id: postId++, userId: req.user.id, content, image: image || null, likeCount: 0, commentCount: 0, createdAt: new Date().toISOString() };
  posts.push(post);
  res.status(201).json({ ...post, author: userPublic(users.find(u => u.id === req.user.id)) });
});

app.get('/posts', auth, (req, res) => {
  const result = [...posts].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  const page = Math.max(1, parseInt(req.query.page) || 1); const limit = parseInt(req.query.limit) || 20;
  const total = result.length;
  const enriched = result.slice((page - 1) * limit, page * limit).map(p => ({
    ...p, author: userPublic(users.find(u => u.id === p.userId)),
    liked: likes.has(`post_${p.id}_${req.user.id}`),
    likeCount: [...likes].filter(l => l.startsWith(`post_${p.id}_`)).length,
    commentCount: comments.filter(c => c.postId === p.id).length,
  }));
  res.json({ total, page, data: enriched });
});

// FEED (posts from followed users + own posts)
app.get('/feed', auth, (req, res) => {
  const followingIds = new Set([...follows].filter(f => f.startsWith(`${req.user.id}:`)).map(f => parseInt(f.split(':')[1])));
  followingIds.add(req.user.id);
  const result = posts.filter(p => followingIds.has(p.userId)).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  const page = Math.max(1, parseInt(req.query.page) || 1); const limit = parseInt(req.query.limit) || 20;
  const enriched = result.slice((page - 1) * limit, page * limit).map(p => ({
    ...p, author: userPublic(users.find(u => u.id === p.userId)),
    liked: likes.has(`post_${p.id}_${req.user.id}`),
    likeCount: [...likes].filter(l => l.startsWith(`post_${p.id}_`)).length,
    commentCount: comments.filter(c => c.postId === p.id).length,
  }));
  res.json({ total: result.length, page, data: enriched });
});

// LIKE (toggle)
app.post('/posts/:id/like', auth, (req, res) => {
  const key = `post_${req.params.id}_${req.user.id}`;
  if (likes.has(key)) { likes.delete(key); return res.json({ liked: false }); }
  likes.add(key);
  const post = posts.find(p => p.id === parseInt(req.params.id));
  if (post && post.userId !== req.user.id) notify(post.userId, 'like', `${users.find(u => u.id === req.user.id)?.name} liked your post`, req.params.id);
  res.json({ liked: true });
});

// COMMENTS
app.post('/posts/:id/comments', auth, (req, res) => {
  if (!req.body.content) return res.status(400).json({ error: 'Content required' });
  const post = posts.find(p => p.id === parseInt(req.params.id));
  if (!post) return res.status(404).json({ error: 'Not found' });
  const comment = { id: cmtId++, postId: post.id, userId: req.user.id, content: req.body.content, createdAt: new Date().toISOString() };
  comments.push(comment);
  if (post.userId !== req.user.id) notify(post.userId, 'comment', `${users.find(u => u.id === req.user.id)?.name} commented on your post`, req.params.id);
  res.status(201).json({ ...comment, author: userPublic(users.find(u => u.id === req.user.id)) });
});

app.get('/posts/:id/comments', auth, (req, res) => {
  res.json(comments.filter(c => c.postId === parseInt(req.params.id)).map(c => ({ ...c, author: userPublic(users.find(u => u.id === c.userId)) })));
});

// NOTIFICATIONS
app.get('/notifications', auth, (req, res) => {
  const myNotifs = notifications.filter(n => n.userId === req.user.id).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt)).slice(0, 50);
  const unread = myNotifs.filter(n => !n.read).length;
  res.json({ total: myNotifs.length, unread, data: myNotifs });
});

app.post('/notifications/read-all', auth, (req, res) => {
  let count = 0;
  notifications.forEach(n => { if (n.userId === req.user.id && !n.read) { n.read = true; count++; } });
  res.json({ marked: count });
});

app.listen(3000, () => console.log('Social Media :3000'));
module.exports = app;
