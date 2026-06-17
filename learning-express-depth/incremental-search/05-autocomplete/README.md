# 05 — Autocomplete (Search)

As the user types, suggest completions. FTS5 prefix matching.

**What's new:**
- FTS5 virtual table
- Prefix matching: `iPhone*` matches "iPhone", "iPhone 15", "iPhone 15 Pro Max"
- `DISTINCT` to avoid duplicates
- Popular searches fallback

**Why autocomplete?** Speed. The user types "iP" and sees "iPhone", "iPad". They click instead of typing. Saves time. Standard for any search box.

**Why prefix matching (`*`)?** As the user types, they have a partial query. "iP" should match "iPhone". The `*` in FTS5 means "match anything starting with this."

**Why DISTINCT?** Same product name might appear in multiple rows (different SKUs). We want unique suggestions.

## Run
```bash
npm install && node server.js
```

```bash
# Type "iP"
curl 'http://localhost:3000/autocomplete?q=iP'
# [iPhone 15 Pro Max, iPhone 15, iPhone 14, iPad Pro, iPad Air]

# Type "Mac"
curl 'http://localhost:3000/autocomplete?q=Mac'
# [MacBook Pro, MacBook Air]

# Type "Ga"
curl 'http://localhost:3000/autocomplete?q=Ga'
# [Galaxy S24 Ultra, Galaxy S24, Galaxy Tab]

# Popular searches
curl http://localhost:3000/popular
```

## What we learned
- Autocomplete pattern
- FTS5 prefix matching
- DISTINCT for unique suggestions
- The "type-ahead" UX

## Next
**06-spellcheck** — "javscript" should match "javascript". Fix typos.
