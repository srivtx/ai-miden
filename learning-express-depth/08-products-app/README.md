# 08 — Products App

Same CRUD pattern, but with two new things:
1. A `price` field (a number, not a string)
2. A `category` field, plus a way to filter by it

## Run it

```bash
npm install
node server.js
```

```bash
# Add some products
curl -X POST http://localhost:3000/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "price": 999, "category": "electronics"}'

curl -X POST http://localhost:3000/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Book", "price": 20, "category": "books"}'

curl -X POST http://localhost:3000/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Headphones", "price": 50, "category": "electronics"}'

# Get all products
curl http://localhost:3000/products
# { "count": 3, "products": [...] }

# Filter by category (NEW!)
curl 'http://localhost:3000/products?category=electronics'
# { "count": 2, "products": [Laptop, Headphones] }

# No filter
curl http://localhost:3000/products?category=books
# { "count": 1, "products": [Book] }
```

## How to think about it

The CRUD pattern is the same. But now we have a new concept: **query parameters**. These are the `?key=value` parts of the URL. We use them to filter or search.

A list endpoint that doesn't support filtering is rarely useful. Almost every app needs "show me all the X, but only the ones where Y = Z."

## How to build it (line by line)

```js
app.get('/products', (req, res) => {
  const { category } = req.query;
  let result = products;
  if (category) {
    result = result.filter(p => p.category === category);
  }
  res.json({ count: result.length, products: result });
});
```

**The new thing here is `req.query`.**

`req.query` is an object that contains all the `?key=value` pairs from the URL. If the URL is `/products?category=books&sort=price`, then `req.query` is `{ category: 'books', sort: 'price' }`.

```js
const { category } = req.query;
```

**Line 10.** Destructure `category` from the query. If the URL has `?category=books`, then `category` is `'books'`. If not, `category` is `undefined`.

```js
let result = products;
if (category) {
  result = result.filter(p => p.category === category);
}
```

**Lines 11-14.** Filter the list. `filter` returns a new array with only the items that match the condition.

**`p.category === category`** — for each product `p`, check if its category matches what the client asked for.

**Why `let result` and not just modifying `products`?** `filter` returns a new array; it doesn't change the original. We assign to `result` so the rest of the function uses the filtered list.

## What we learned

1. `req.query` has the `?key=value` parts of the URL
2. Query parameters are always strings
3. `array.filter` returns a new array with only matching items
4. The CRUD pattern gets a "search/filter" addition on list endpoints
5. The data shape can have different types: strings, numbers, even arrays

## What's next

In **09-chat-app** we build something different — a chat. The shape is different: instead of one user creating things, multiple users send messages to a room. This introduces the idea of a "real-time" feel (even if we're not using websockets yet).
