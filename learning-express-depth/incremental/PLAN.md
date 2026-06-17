# Plan — Complex Apps, Built Incrementally

Each app is built in 8-12 stages. Each stage adds ONE new thing. The full app at the end is production-quality.

## App 1: Todo (the foundation)
Already have basic CRUD. Add complexity incrementally:
1. todo-memory → in-memory CRUD (the start)
2. todo-sqlite → add a database
3. todo-relations → tags, categories (many-to-many)
4. todo-auth → users, login, JWT
5. todo-multi-tenant → teams, data isolation
6. todo-soft-delete → deleted_at, restore
7. todo-audit → who did what, when
8. todo-versioning → optimistic locking, conflicts
9. todo-caching → Redis, invalidation
10. todo-rate-limit → per-user limits
11. todo-search → full-text search
12. todo-webhooks → notify on changes

## App 2: E-commerce (the marketplace)
Stages: 1. products, 2. cart, 3. checkout, 4. payments, 5. orders, 6. inventory, 7. reviews, 8. shipping, 9. refunds, 10. coupons, 11. recommendations, 12. analytics

## App 3: Blog/CMS (the publishing platform)
Stages: 1. posts, 2. comments, 3. users, 4. roles, 5. media uploads, 6. drafts/publish, 7. revisions, 8. search, 9. RSS feed, 10. SEO, 11. analytics, 12. newsletter

## App 4: Chat (the real-time app)
Stages: 1. messages, 2. rooms, 3. users/presence, 4. typing indicators, 5. read receipts, 6. file sharing, 7. reactions, 8. threads, 9. notifications, 10. search, 11. encryption, 12. federation

## App 5: Analytics (the data platform)
Stages: 1. events, 2. sessions, 3. funnels, 4. cohorts, 5. dashboards, 6. exports, 7. alerts, 8. segments, 9. A/B tests, 10. real-time, 11. data warehouse, 12. ML pipeline

## App 6: Auth (the identity service)
Stages: 1. signup, 2. login, 3. JWT, 4. refresh tokens, 5. password reset, 6. email verify, 7. 2FA, 8. OAuth providers, 9. API keys, 10. SSO/SAML, 11. audit log, 12. compliance

## App 7: File Storage (the dropbox)
Stages: 1. upload, 2. download, 3. folders, 4. sharing, 5. versions, 6. trash, 7. search, 8. thumbnails, 9. compression, 10. encryption, 11. quotas, 12. team folders

## App 8: Notifications (the messaging hub)
Stages: 1. email, 2. SMS, 3. push, 4. in-app, 5. templates, 6. preferences, 7. digest, 8. batch, 9. priority, 10. retry, 11. tracking, 12. analytics

## App 9: Payment (the billing engine)
Stages: 1. charges, 2. customers, 3. subscriptions, 4. invoices, 5. refunds, 6. disputes, 7. webhooks, 8. payouts, 9. tax, 10. fraud, 11. reporting, 12. multi-currency

## App 10: Search (the elasticsearch)
Stages: 1. basic search, 2. relevance, 3. filters, 4. facets, 5. autocomplete, 6. spell check, 7. synonyms, 8. ranking, 9. analytics, 10. personalization, 11. federated, 12. ML ranking

## Strategy
- Build the todo app stages first (foundation for everything)
- Then pick 2-3 more apps based on interest
- Each stage is a working app (you can run it)
- Each stage is small (50-200 lines)
- Each stage adds ONE concept, deeply

## Current focus: todo app, 12 stages
