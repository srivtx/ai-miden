# The Decisions

> *"LIKE is a table scan. FTS5 is an inverted index. Choose wisely."*

## Decision 1: FTS5 and not LIKE

**Alternative**: `WHERE title LIKE '%foo%'`.

**Why FTS5: It's **O(log n)** instead of **O(n)**. For 1M rows, FTS5 is milliseconds; LIKE is seconds. FTS5 also has BM25 ranking; LIKE has no relevance.

**Trade-off**: FTS5 requires a virtual table, triggers, and a learning curve. LIKE is one line. We accept the trade-off for performance.

## Decision 2: SQLite FTS5 and not Elasticsearch

**Alternatives**:
- **Elasticsearch** — distributed, fast, feature-rich, separate service
- **Meilisearch** — Rust-based, fast, easy to deploy, separate service
- **Postgres `tsvector`** — built into Postgres, decent FTS

**Why SQLite FTS5: It's built into our existing database. No separate service. No extra infrastructure. For our scale (1M rows), it's enough.

**Trade-off**: For 100M rows, Elasticsearch is better. For multi-language or fuzzy search, Meilisearch is better. We use FTS5 because it's simple and already there.

## Decision 3: BM25 ranking, exposed as `rank` column

**Alternative**: Just return matches, no ranking. Or use TF-IDF.

**Why BM25: It's the standard. It considers term frequency, inverse document frequency, and document length. It gives sensible results.

**Trade-off**: The `rank` is negative in SQLite's convention. We could flip the sign, but the client can do it.

## Decision 4: Triggers for sync

**Alternative**: Application-level sync (insert into both tables in the handler).

**Why triggers: They run automatically. The handler doesn't have to remember to update the FTS table. The FTS table is always in sync with the source.

**Trade-off**: Triggers are a bit hidden. If you bypass them (e.g., `db.raw('INSERT INTO posts ...')`), the FTS table is out of sync. We use the Knex query builder, which doesn't bypass triggers.

## Decision 5: Search the FTS table, not the posts table

**Alternative**: `SELECT * FROM posts WHERE title LIKE '%q%' OR body LIKE '%q%'`.

**Why FTS: FTS5 uses the inverted index. LIKE does a table scan. FTS5 is O(log n); LIKE is O(n).

**Trade-off**: The query is more complex (JOIN to the FTS table). We accept this for performance.

## Decision 6: Keep the no-query behavior (return all)

When `?q=` is not provided, we return all posts (the old behavior). When `?q=` is provided, we search.

**Why both: The list endpoint is for browsing. The search endpoint is for finding. The same URL with or without `?q=` serves both purposes.

**Trade-off**: The handler has two branches. We accept this for flexibility.

## Decision 7: No typo tolerance

**Alternative**: Use Meilisearch or add a fuzzy matcher to FTS5.

**Why not: FTS5 doesn't support fuzzy matching. We could approximate with prefix matching (`?q=hel*`), but that's not the same. For typo tolerance, you'd use a different engine.

**Trade-off**: A user who types "helo" gets no results. They have to spell correctly. We accept this for simplicity.

## Decision 8: No highlighting

**Alternative**: Use FTS5's `highlight()` function to mark matches with `**hello**`.

**Why not: We can add later. For now, we return the full text. The client can highlight in the frontend.

**Trade-off**: The client has to do highlighting. We accept this for simplicity.

## Decision 9: No column filter

**Alternative**: `?q=title:hello` to search only the title.

**Why not: The client can use the full query syntax (`?q=title:hello body:world`). FTS5 supports it. We don't enforce column restrictions.

**Trade-off**: A user can search only the body, bypassing the title. We accept this for flexibility.

## Decision 10: No multi-language stemming

**Alternative**: Use a different tokenizer for other languages (e.g., `unicode61` for Chinese, `trigram` for languages without word boundaries).

**Why not: We use the default `unicode61` tokenizer with the `porter` stemmer (English). For multi-language, we'd need a different setup.

**Trade-off**: Non-English text isn't stemmed. We accept this for our use case (English content).

---

## What We Did Not Decide

- **Typo tolerance** — out of scope (use Meilisearch)
- **Highlighting** — out of scope (client can do it)
- **Multi-language stemming** — out of scope
- **Search-as-you-type** — out of scope
- **Faceted search** — out of scope
- **Synonyms** — out of scope
- **Search analytics** — out of scope (track what users search for)
- **Personalized ranking** — out of scope (would need user history)

Each is a future decision.

---

## The Meta-Decision: The API Has Search

For 18 projects, the API had no search. The client could filter by exact fields. They couldn't find by text. The user had to scroll through everything.

Now the API has search. The client can find by text. Results are ranked by relevance. The query is fast. The user is happy.

This is the foundation of *every* searchable API. Search is non-negotiable for any user-facing product. The patterns (FTS5, inverted index, BM25, MATCH) are universal.

The next 21 projects will assume search exists. The path diverges:

- **File upload** (project 20): accept files
- **Email** (project 21): send notifications
- **Caching** (project 22): reduce DB load
- **Redis** (project 23): shared state
- **Rate limiting** (project 24): throttle abuse
- **Cron** (project 25): scheduled jobs
- **Queue** (project 26): move slow work off the request
- **Transactions** (project 27): atomic multi-write operations
- **WebSocket** (project 28): bidirectional channel
- **SSE** (project 29): server-push
- **Presence** (project 30): who's online
- **CRDT** (project 31): co-editing
- **WebRTC** (project 32): voice
- **RBAC** (project 33): permissions
- **Webhook** (project 34): outbound push
- **Payment** (project 35): Stripe
- **Tests** (project 36): automated
- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The API has search. The path continues.
