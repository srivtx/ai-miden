# Learning Express — 60 Small Projects

60 apps, each introducing a concept. Each one is 50-100 lines. Each one has a deep README explaining the new idea.

**The point is to see patterns and to know when to reach for new tools.**

## The 60 apps

### Part 1: CRUD shape (01-40)
The basics. Every project is a list of things: create, read, update, delete. Each one has a different data shape.

- **01-05**: hello server, express, todo list/add/delete
- **06-20**: notes, blog, products, chat, bookmarks, weather, calendar, contacts, password vault, expenses, polls, quiz, recipes, habits, url shortener
- **21-40**: emoji, mood journal, fitness, water, sleep, reading list, movies, music playlists, photos, meal planner, grocery, bug tracker, feedback, surveys, pomodoro, flashcards, kanban, inventory, resume, event rsvp

### Part 2: New concepts (41-50)
Things you can't do with just CRUD.

| # | Project | Concept |
|---|---|---|
| 41 | websocket-chat | Real-time bidirectional (ws library) |
| 42 | file-upload | multipart/form-data, multer |
| 43 | search-with-ranking | TF ranking, title boost |
| 44 | rate-limiter | Token bucket, 429 status |
| 45 | cron-scheduler | Cron parsing, scheduled tasks |
| 46 | pub-sub | Event bus, topics, subscribers |
| 47 | job-queue | Async work, 202 Accepted |
| 48 | caching | Cache-aside, TTL |
| 49 | rate-counter | Sliding window analytics |
| 50 | jwt-auth | JSON Web Tokens, Bearer auth |

### Part 3: More concepts (51-60)
Production-readiness concerns.

| # | Project | Concept |
|---|---|---|
| 51 | streams | Stream large files, NDJSON, CSV |
| 52 | sse | Server-Sent Events (one-way real-time) |
| 53 | redis-cache | External cache (Redis) |
| 54 | graphql | GraphQL instead of REST |
| 55 | encryption | Encrypt data at rest (AES-256) |
| 56 | csrf | Cross-site request forgery protection |
| 57 | cors | Cross-origin resource sharing |
| 58 | helmet | Security headers in one line |
| 59 | i18n | Multi-language support |
| 60 | validation-joi | Joi validation library |

## How to use this folder

For each project:
1. Read the README — it explains the new concept
2. Read the code — it's short
3. Run it: `npm install && node server.js`
4. Try the curl examples
5. Modify it, break it, fix it

The 60 apps take you from "I know Express basics" to "I know what every backend tool does." After this, when you see a concept in a job description or library docs, you'll recognize it.

## What's after this

The 60 projects are the foundation. From here you can:
- Add a database to any of them (so data survives restarts)
- Add user accounts to any of them (so each user has their own data)
- Combine concepts (e.g., a real-time chat with auth and rate limiting)
- Build something new from scratch

The shape is in your head now. The data can be anything.
