# 06 — Spell Check (Search)

"javscript" should match "javascript". Suggest corrections using Levenshtein distance.

**What's new:**
- Levenshtein distance algorithm
- Vocabulary from indexed docs
- Auto-correct: if no exact match, find closest
- Return both the corrected query and the original

**Why spell check?** Users make typos. "javscript" gets 0 results. Without correction, they think the system is broken. With correction, they find what they want.

**Why Levenshtein?** Standard edit distance. Counts insertions, deletions, substitutions. "javscript" → "javascript" = 1 insertion = distance 1.

**Why a max distance (2)?** Beyond 2 edits, the "correction" is probably wrong. Better to leave it alone than to suggest a totally different word.

## Run
```bash
npm install && node server.js
```

```bash
# Correct spelling
curl 'http://localhost:3000/search?q=javascript'
# { corrected_query: "javascript", did_correct: false, results: [...] }

# Typo
curl 'http://localhost:3000/search?q=javscript'
# { corrected_query: "javascript", did_correct: true, results: [...] }

# Bigger typo
curl 'http://localhost:3000/search?q=javascrpt'
# distance 1 → corrected

# Way off
curl 'http://localhost:3000/search?q=xyzabc'
# distance too high, no correction
```

## What we learned
- Levenshtein distance
- Auto-correct pattern
- Max distance threshold
- "Did you mean...?" UX

## Next
**07-synonyms** — "phone" and "mobile" should match. Expand the query.
