# Twitter API — Step 15 in the learning path

Builds on Forum. Adds: social graph (follow/unfollow), posts with 280 char limit, likes, timeline (posts from people you follow + your own), reply_to and retweet_of.

## Endpoints
```
POST   /users                       # create
GET    /users/:username             # with follower/following/post counts

POST   /follow/:username
DELETE /follow/:username

POST   /posts                       # { body, reply_to?, retweet_of? } (X-User-Id)
POST   /like/:postId

GET    /timeline                    # your feed (X-User-Id)
GET    /users/:username/posts       # a user's posts
```

## Try
```bash
# Two users follow each other, then one posts, the other sees it in their timeline
A=$(curl -X POST http://localhost:3000/users -H "Content-Type: application/json" -d '{"username": "alice"}' | jq -r .id)
B=$(curl -X POST http://localhost:3000/users -H "Content-Type: application/json" -d '{"username": "bob"}' | jq -r .id)

curl -X POST http://localhost:3000/follow/alice -H "X-User-Id: $B"
curl -X POST http://localhost:3000/follow/bob -H "X-User-Id: $A"

curl -X POST http://localhost:3000/posts -H "Content-Type: application/json" -H "X-User-Id: $A" -d '{"body": "Hello world!"}'

# Bob's timeline shows Alice's post
curl http://localhost:3000/timeline -H "X-User-Id: $B"
# { count: 1, posts: [{ body: "Hello world!", username: "alice", ... }] }
```

## What this teaches
1. **Social graph**: `follows` table, self-referential many-to-many
2. **Timeline query**: `IN (subquery)` to get posts from followed users
3. **Polymorphic content**: posts can be original, replies (`reply_to`), or retweets (`retweet_of`)
4. **Length validation**: 280 char limit on post body
5. **Likes**: many-to-many, dedup via unique constraint
6. **Aggregations in subquery**: like count per post, "liked by me" boolean

## Next project
→ **helpdesk-api** — adds: tickets, agents, assignments, SLA tracking
