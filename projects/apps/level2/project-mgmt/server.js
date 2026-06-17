// Project Management — Boards, lists, cards, assignees, labels, activity log.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const boards = []; const lists = []; const cards = []; const activity = [];
let boardId = 1, listId = 1, cardId = 1, actId = 1;

function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }

function log(boardId, userId, action, target) { activity.push({ id: actId++, boardId, userId, action, target, time: new Date().toISOString() }); }

app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  users.push({ id: users.length + 1, name, email, password: await bcrypt.hash(password, 10) });
  res.status(201).json({ token: jwt.sign({ id: users.length }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});

// BOARDS
app.post('/boards', auth, (req, res) => {
  const board = { id: boardId++, name: req.body.name, description: req.body.description || '', ownerId: req.user.id, members: [req.user.id], createdAt: new Date().toISOString() };
  boards.push(board);
  // Create default lists
  ['To Do', 'In Progress', 'Done'].forEach(name => { lists.push({ id: listId++, boardId: board.id, name, position: lists.filter(l => l.boardId === board.id).length }); });
  log(board.id, req.user.id, 'created_board', board.name);
  res.status(201).json(board);
});

app.get('/boards', auth, (req, res) => {
  const myBoards = boards.filter(b => b.members.includes(req.user.id));
  res.json(myBoards.map(b => ({ ...b, listCount: lists.filter(l => l.boardId === b.id).length, cardCount: cards.filter(c => lists.find(l => l.id === c.listId)?.boardId === b.id).length })));
});

// LISTS
app.get('/boards/:id/lists', auth, (req, res) => {
  const board = boards.find(b => b.id === parseInt(req.params.id));
  if (!board) return res.status(404).json({ error: 'Board not found' });
  const boardLists = lists.filter(l => l.boardId === board.id).sort((a, b) => a.position - b.position);
  const enriched = boardLists.map(l => ({ ...l, cards: cards.filter(c => c.listId === l.id).sort((a, b) => a.position - b.position).map(c => ({ ...c, assignee: c.assigneeId ? users.find(u => u.id === c.assigneeId)?.name : null })) }));
  res.json(enriched);
});

app.post('/boards/:id/lists', auth, (req, res) => {
  const board = boards.find(b => b.id === parseInt(req.params.id));
  if (!board) return res.status(404).json({ error: 'Not found' });
  const list = { id: listId++, boardId: board.id, name: req.body.name, position: lists.filter(l => l.boardId === board.id).length };
  lists.push(list);
  log(board.id, req.user.id, 'created_list', list.name);
  res.status(201).json(list);
});

// CARDS
app.post('/lists/:id/cards', auth, (req, res) => {
  const list = lists.find(l => l.id === parseInt(req.params.id));
  if (!list) return res.status(404).json({ error: 'List not found' });
  const board = boards.find(b => b.id === list.boardId);
  const card = { id: cardId++, listId: list.id, title: req.body.title, description: req.body.description || '', assigneeId: req.body.assigneeId || null, labels: req.body.labels || [], priority: req.body.priority || 'medium', dueDate: req.body.dueDate || null, position: cards.filter(c => c.listId === list.id).length, createdAt: new Date().toISOString() };
  cards.push(card);
  log(board.id, req.user.id, 'created_card', card.title);
  res.status(201).json(card);
});

app.patch('/cards/:id', auth, (req, res) => {
  const card = cards.find(c => c.id === parseInt(req.params.id));
  if (!card) return res.status(404).json({ error: 'Not found' });
  if (req.body.title !== undefined) card.title = req.body.title;
  if (req.body.description !== undefined) card.description = req.body.description;
  if (req.body.assigneeId !== undefined) card.assigneeId = req.body.assigneeId;
  if (req.body.labels !== undefined) card.labels = req.body.labels;
  if (req.body.priority !== undefined) card.priority = req.body.priority;
  if (req.body.dueDate !== undefined) card.dueDate = req.body.dueDate;
  if (req.body.listId !== undefined) { const oldList = lists.find(l => l.id === card.listId); card.listId = req.body.listId; const newBoard = boards.find(b => b.id === lists.find(l => l.id === req.body.listId)?.boardId); if (newBoard) log(newBoard.id, req.user.id, 'moved_card', `${card.title} (${oldList?.name} -> ${lists.find(l => l.id === req.body.listId)?.name})`); }
  res.json(card);
});

// ACTIVITY
app.get('/boards/:id/activity', auth, (req, res) => {
  res.json(activity.filter(a => a.boardId === parseInt(req.params.id)).slice(-50).reverse().map(a => ({ ...a, user: users.find(u => u.id === a.userId)?.name })));
});

// MEMBERS
app.post('/boards/:id/members', auth, (req, res) => {
  const board = boards.find(b => b.id === parseInt(req.params.id));
  if (!board) return res.status(404).json({ error: 'Not found' });
  const memberId = parseInt(req.body.userId);
  if (board.members.includes(memberId)) return res.status(409).json({ error: 'Already a member' });
  board.members.push(memberId);
  log(board.id, req.user.id, 'added_member', users.find(u => u.id === memberId)?.name);
  res.json({ members: board.members.map(id => users.find(u => u.id === id)?.name) });
});

app.listen(3000, () => console.log('Project Mgmt :3000'));
module.exports = app;
