## Why it exists (THE PROBLEM)

You have `users` and `orders`. You store the user's address in the users table. You store the order's shipping address in the orders table. Now a user changes their address. The user's profile shows the new address, but their old orders show the new address too. But the order was shipped to the old address. The data is now wrong.

Or: you have `users` and `posts`. You store the author's name in each post. The user changes their name from "Alice" to "Alicia". All the posts still say "Alice" by [Alice]. You have to update all the posts. If you miss one, the data is wrong.

**Database design** (or schema design) is the art of organizing data so it's correct, fast, and maintainable. Three forces:
1. **Correctness**: no anomalies (data getting out of sync).
2. **Performance**: queries are fast at scale.
3. **Maintainability**: easy to add features, easy to change.

Get the schema wrong, and every feature is a fight. Get it right, and features fall into place.

## Definition (very simple)

**Normalization** = splitting data into tables to avoid duplication. `users` has name, email. `orders` has user_id (not name, not email). To get the user's name with an order, JOIN.

**Denormalization** = the opposite. Store the name in the order, accept the duplication, trade correctness for read speed. Common for read-heavy workloads (analytics, search).

**Primary key (PK)** = a unique identifier for each row. `id INTEGER PRIMARY KEY`. Never null, never changes.

**Foreign key (FK)** = a column that points to another table's PK. `orders.user_id REFERENCES users(id)`. Enforces: every order's user must exist.

**Index** = a separate data structure that lets you find rows fast. Like a book index: "users with email='alice@x.com'" → row id, no full table scan.

**Many-to-one** = many rows in table A point to one row in table B. Many orders → one user.

**Many-to-many** = many rows in A point to many in B. Users ↔ roles. Requires a junction table: `user_roles(user_id, role_id)`.

**One-to-one** = each row in A has one matching row in B. User ↔ user_profile. Rare, used for splitting hot/cold data.

**Anomaly** = a problem caused by bad schema. Update anomaly: change user name, miss some posts. Insert anomaly: can't add a category without a product. Delete anomaly: delete a product, lose the category.

## Real-life analogy

**Bad schema = a kitchen where ingredients are mixed.** Eggs in the flour bin, sugar in the salt shaker. You can't find anything. You make mistakes.

**Good schema = a kitchen with labeled bins.** Eggs in the egg bin. Sugar in the sugar bin. Fast to find. Easy to maintain. No confusion.

**Normalization = a library with cross-references.** A book mentions another. The library has a card catalog (index) that says "see also...". You can find related books without flipping through every book.

**Denormalization = a book that includes the relevant pages of another book inside itself.** No need to find the other book. But if the other book changes, this book is out of date.

## Tiny numeric example

**Bad schema** (denormalized, has anomalies):
```sql
CREATE TABLE orders (
  id INT PRIMARY KEY,
  user_name TEXT,        -- duplicated
  user_email TEXT,       -- duplicated
  product_name TEXT,     -- duplicated
  total DECIMAL
);
```
Problems: if user changes email, all orders are stale. If product is renamed, all orders are stale. Storage is wasted.

**Good schema** (normalized):
```sql
CREATE TABLE users (
  id INT PRIMARY KEY,
  name TEXT,
  email TEXT
);
CREATE TABLE products (
  id INT PRIMARY KEY,
  name TEXT,
  price DECIMAL
);
CREATE TABLE orders (
  id INT PRIMARY KEY,
  user_id INT REFERENCES users(id),
  product_id INT REFERENCES products(id),
  total DECIMAL,
  created_at TIMESTAMP
);
```
To get "orders with user name and product name":
```sql
SELECT o.*, u.name AS user_name, p.name AS product_name
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN products p ON o.product_id = p.id;
```

## Common confusion (5+ bullet points)

1. **"Normalize everything to 5NF."** No. 5th normal form is academic. In practice, 3NF is usually enough. Over-normalization means more JOINs, slower reads, harder queries. Pick 3NF, denormalize where reads are hot.

2. **"Foreign keys are slow."** FKs add a check on insert/update. The check is O(log N) with the index. The cost is negligible. The benefit: data integrity. Use FKs unless you have a measured reason not to.

3. **"I'll add indexes later if queries are slow."** Add them upfront. Find the slow queries with `EXPLAIN`. Index the columns in WHERE, JOIN, ORDER BY. Indexes are cheap to add, expensive to live without.

4. **"The schema is fine for 1000 users, why redesign for 10K?"** Because the redesign at 100K is 10x harder. The cost of getting it right early is small. The cost of getting it wrong is rewriting every query at scale.

5. **"I'll just store JSON in a TEXT column."** Sometimes right. For variable-shape data (preferences, settings, attributes), JSON is great. But then you can't query inside it efficiently. Pick: structured columns (queryable) or JSON (flexible). Don't mix.

6. **"UUIDs as primary keys are fine."** Yes but they have cost: 16 bytes vs 4 bytes for INT, random inserts cause page splits, worse cache. For internal PKs, use auto-increment INT. For external IDs (URL `/users/abc123`), use a separate UUID column.

7. **"Soft delete is a good idea."** Maybe. Soft delete = `deleted_at` column, never actually delete. Pros: recoverable, audit trail. Cons: every query needs `WHERE deleted_at IS NULL`, easy to forget, table grows forever. For most apps, hard delete is fine. Soft delete only for legal/audit reasons.

## Key properties

| Normal form | Rule | Anomalies prevented |
|---|---|---|
| 1NF | Atomic values, no repeating groups | None really |
| 2NF | 1NF + no partial dependencies | Some update anomalies |
| 3NF | 2NF + no transitive dependencies | Most update anomalies |
| BCNF | 3NF + every determinant is a key | Edge cases |

## Indexing strategy

| Query pattern | Index |
|---|---|
| `WHERE email = ?` | `email` |
| `WHERE user_id = ? ORDER BY created_at DESC` | `(user_id, created_at)` |
| `WHERE status = ? AND created_at > ?` | `(status, created_at)` |
| `JOIN users ON orders.user_id` | `orders.user_id` (FK index) |
| `ORDER BY created_at` | `created_at` |

Composite indexes: column order matters. `(a, b)` covers `WHERE a = ?` AND `WHERE a = ? AND b = ?` but NOT `WHERE b = ?` alone.

## When to denormalize

1. **Read-heavy, write-light** (analytics, dashboards): denormalize for fast reads.
2. **Counters** (user.posts_count): UPDATE on every post, denormalize to avoid COUNT(*) on every read.
3. **Search** (full-text search): store a denormalized index in Elasticsearch.
4. **Audit logs** (event sourcing): append-only, never updated.

## Connection to our projects

For our 73 apps, the schemas are simple: 1-5 tables each, normalized to 3NF. For real production:
- Add indexes on FKs, common WHERE columns, sort columns
- Use FK constraints
- Add `created_at`, `updated_at` to every table
- Add `id` as auto-increment INT primary key
- Soft delete only where required

For CortexCode: store training data in SQLite (or Postgres). Tables: `code_blocks(id, source, language, content)`, `train_runs(id, started_at, finished_at, loss)`. Indexed by `language`, `started_at`.

For logogen: similar — `logos(id, prompt, generated_image, created_at, style)`.
