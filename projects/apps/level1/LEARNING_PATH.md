# Backend Learning Path — 20 Classic Projects, in Order

This is the recommended sequence for learning backend engineering. Each project builds on the last. Don't skip ahead.

**Rule of thumb: read the README, run the server, try the curl examples, read the code, modify it, then move on.**

---

## Week 1: Foundations (Days 1-5)

### Day 1 — Todo API
**`projects/apps/level1/todo-api/`**
The classic first project. CRUD on a list. Add filter, sort, mark done. Teaches: REST basics, SQLite CRUD, query params, validation.

### Day 2 — Notes API
**`projects/apps/level1/notes-api/`**
Builds on Todo. Adds tags, full-text search, categories, archive. Teaches: many-to-many, JOIN queries, search, soft state.

### Day 3 — Blog API
**`projects/apps/level1/blog-api/`**
Builds on Notes. Adds users, posts, comments, slugs, published/draft. Teaches: multi-table relationships, public vs private routes, simple auth.

### Day 4 — Products API
**`projects/apps/level1/products-api/`**
Builds on Blog. Adds categories, prices in cents, inventory, search, sort, filter. Teaches: money handling, multi-field search, stock management.

### Day 5 — Weather API
**`projects/apps/level1/weather-api/`**
Builds on Products. Adds external API calls, in-memory caching, time-series, fallback. Teaches: cache-aside, TTL, error handling.

---

## Week 2: Real-time and Social (Days 6-10)

### Day 6 — Chat API
**`projects/apps/level1/chat-api/`**
Builds on Weather. Adds WebSockets, rooms, real-time messaging. Teaches: bidirectional comms, broadcasting, message history.

### Day 7 — Forum API
**`projects/apps/level1/forum-api/`**
Builds on Chat. Adds threads, nested replies, voting, categories, moderation. Teaches: self-referencing FKs, polymorphic associations, ranking.

### Day 8 — Calendar API
**`projects/apps/level1/calendar-api/`**
Builds on Forum. Adds events, time ranges, recurring events, attendees, conflict detection. Teaches: time handling, RRULE expansion, range queries.

### Day 9 — Reminders API
**`projects/apps/level1/reminders-api/`**
Builds on Calendar. Adds simple scheduled tasks, recurring reminders, "what's due now". Teaches: time-based queries, auto-create on complete.

### Day 10 — Books API
**`projects/apps/level1/books-api/`**
Builds on Calendar. Adds ISBN lookup, many-to-many authors, ratings, reviews. Teaches: polymorphic references, aggregations, CHECK constraints.

---

## Week 3: Media (Days 11-15)

### Day 11 — Movies API
**`projects/apps/level1/movies-api/`**
Builds on Books. Adds genres, cast, similar movies, watchlist. Teaches: composite entities, recommendation by overlap, personal collections.

### Day 12 — Music API
**`projects/apps/level1/music-api/`**
Builds on Movies. Adds artists → albums → tracks hierarchy, playlists, play counts, top charts. Teaches: hierarchical data, aggregations, ordered lists.

### Day 13 — Photos API
**`projects/apps/level1/photos-api/`**
Builds on Music. Adds image upload, albums with order, public/private, EXIF-like metadata, tags. Teaches: multipart upload, binary storage, privacy.

### Day 14 — Library API
**`projects/apps/level1/library-api/`**
Combines Books + Movies + Music into one unified catalog. Teaches: polymorphic associations, unified search across types, status tracking.

### Day 15 — Twitter API
**`projects/apps/level1/twitter-api/`**
Builds on Library. Adds follow graph, posts with char limit, likes, timeline. Teaches: social graph, timeline queries, self-referencing many-to-many.

---

## Week 4: Business Apps (Days 16-20)

### Day 16 — Helpdesk API
**`projects/apps/level1/helpdesk-api/`**
Builds on Twitter. Adds tickets, agents, assignments, SLA tracking, priority. Teaches: state machines, SLA computation, role-based actions, event log.

### Day 17 — Ticket Booking API
**`projects/apps/level1/ticket-booking-api/`**
Builds on Helpdesk. Adds venues with seat generation, events, seat selection, booking with payment, cancellation. Teaches: unique constraints, availability, payment integration.

### Day 18 — CRM API
**`projects/apps/level1/crm-api/`**
Builds on Ticket Booking. Adds companies, contacts, deals with pipeline, activity log. Teaches: pipeline/funnel, weighted value forecasting, activity tracking.

### Day 19 — Restaurant API
**`projects/apps/level1/restaurant-api/`**
Builds on CRM. Adds menu with categories, tables, reservations with conflict detection, orders with line items. Teaches: hierarchical data, conflict detection, aggregate roots.

### Day 20 — Food Delivery API
**`projects/apps/level1/food-delivery-api/`**
Builds on Restaurant. Adds multi-party state machine (customer → restaurant → driver → delivered), real-time location updates. Teaches: complex state machines, multi-party authorization.

---

## After the 20-Project Sequence

You now have the full mental model of a backend engineer. Pick your path:

### Path A: Master the concepts (60+ focused projects)
**`projects/apps/level1/INDEX.md`** — one project per backend concept. Start with the basics you skipped, then the more advanced topics.

### Path B: Build full apps (level2/level3)
**`projects/apps/level2/`** — 18 production-style apps: blog-platform, ecommerce, social-media, multi-tenant, observability-service, etc.
**`projects/apps/level3/`** — 7 complex apps: real-time-dashboard, search-engine, webhook-delivery, etc.

### Path C: Read the curriculum docs
**`docs/backend/`** — 25+ topics in the ai-miden format (Problem → Definition → Analogy → Numeric → Confusions → Key Properties → Connection). Each doc links to a project in level1.

### Path D: Read about patterns and operations
- `routing-demo`, `middleware-demo`, `validation-demo` — request/response patterns
- `database-design-demo`, `indexing-demo`, `migrations-demo` — data layer
- `rate-limiting-demo`, `pagination-demo`, `idempotency-demo` — API patterns
- `jwt-demo`, `security-patterns-demo`, `password-reset-demo`, `two-factor-auth-demo` — auth
- `websocket-demo`, `pubsub-demo`, `background-jobs-demo`, `email-demo`, `cron-demo` — async
- `caching-demo`, `multi-tenant-demo`, `feature-flags-demo`, `audit-log-demo` — state
- `observability-demo`, `docker-demo`, `ci-cd-demo`, `graceful-shutdown-demo` — operations
- `event-sourcing-demo`, `feature-flags-demo`, `bulk-ops-demo` — architecture

---

## How to use this

1. **For each project, follow this loop:**
   - Read the README
   - Run `node server.js` (some need `npm install` first)
   - Try the curl examples
   - Read the code (it's 100-300 lines, readable)
   - Modify it: add a feature, change a query, break it and fix it
   - Move on

2. **Don't skip steps.** Each builds on the last. If you skip Calendar, you'll struggle with Reminders.

3. **One day per project, five days a week.** In 4 weeks you'll have the full mental model.

4. **If you get stuck:** the answer is in the code. Read it. Modify it. Run it again.

5. **If you finish all 20:** pick a level2 or level3 project. They combine everything you learned.

---

## The 20 apps in one screen

| # | App | What it adds |
|---|---|---|
| 1 | Todo | CRUD, filter |
| 2 | Notes | Tags, search |
| 3 | Blog | Users, comments, slugs |
| 4 | Products | Categories, prices, stock |
| 5 | Weather | External API, caching |
| 6 | Chat | WebSockets, rooms |
| 7 | Forum | Threads, replies, voting |
| 8 | Calendar | Events, recurring, conflict |
| 9 | Reminders | Scheduled tasks |
| 10 | Books | ISBN, authors, reviews |
| 11 | Movies | Genres, cast, similar |
| 12 | Music | Hierarchy, playlists, charts |
| 13 | Photos | Upload, albums, EXIF |
| 14 | Library | Unified catalog |
| 15 | Twitter | Follow graph, timeline |
| 16 | Helpdesk | Tickets, SLA, agents |
| 17 | Ticket Booking | Seats, payment |
| 18 | CRM | Pipeline, deals |
| 19 | Restaurant | Menu, reservations |
| 20 | Food Delivery | Multi-party state machine |

**Each project is 100-300 lines. All use SQLite (no setup). All runnable. All have a README with curl examples.**
