# Routing Demo — Static, dynamic, regex, optional params, nested routers

All the ways to define routes in Express. Most specific to least specific.

## Endpoints
```
GET  /                                    # static
GET  /about                               # static
GET  /users/:id                           # single param
GET  /users/:id/posts/:postId             # multiple params
GET  /products/:category/:productId?      # optional param
GET  /*fly                                # regex: anything ending in "fly"
GET  /^\/api\/v(\d+)\/.*                  # regex: API version
GET  /search?q=...&page=...&limit=...     # query strings
GET  /admin/*                             # nested router (admin)
GET  /api/v1/items                        # nested router (api v1)
GET  /api/v2/items                        # nested router (api v2, different shape)
```

## What this teaches
1. **Route matching order**: Express matches in declaration order. `/about` must come before `/:id`.
2. **req.params**: dynamic path segments become params
3. **req.query**: `?key=value` pairs
4. **Optional params**: `:productId?` makes the segment optional
5. **Regex routes**: match arbitrary patterns
6. **Nested routers (express.Router)**: sub-applications with their own middleware
7. **API versioning**: mount v1 and v2 routers at different paths
