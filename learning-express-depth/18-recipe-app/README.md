# 18 — Recipe App

A recipe has ingredients and steps — both lists inside the recipe. New thing: **nested data**.

## Run it

```bash
npm install
node server.js
```

```bash
# Create a recipe
curl -X POST http://localhost:3000/recipes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pasta",
    "ingredients": ["pasta", "tomato sauce", "cheese"],
    "steps": ["Boil water", "Add pasta", "Drain", "Add sauce"],
    "cookTime": 20
  }'
# { "id": 1, "name": "Pasta", "ingredients": [...], "steps": [...], "cookTime": 20 }

# Get the recipe
curl http://localhost:3000/recipes/1
```

## How to think about it

Recipes are the same CRUD pattern. The new thing is that the data is **nested**: a recipe has a list of ingredients, a list of steps. We've seen lists before (we made the products list), but those were top-level. Here, the list is *inside* a single recipe.

JSON supports this naturally. A field can be a string, a number, a boolean, an array, or an object. Arrays can hold more arrays or objects.

## How to build it (line by line)

```js
ingredients: ingredients || [],
steps: steps || [],
```

**Lines 16-17.** Default to empty arrays. If the client didn't send ingredients or steps, we use `[]` instead of `undefined`. This way the recipe always has these fields.

**`[]` vs `undefined`?** When you `JSON.stringify` an object with `undefined`, the field is omitted entirely. With `[]`, it's an empty array. The client can rely on the field always being there.

## What we learned

1. JSON can nest: objects inside objects, arrays inside objects
2. Default values prevent `undefined` from leaking out
3. The CRUD pattern works for nested data
4. We've now built 13 apps

## What's next

In **19-habit-tracker** we build a habit tracker. Each habit has a name, and you can mark it "done" for today. We add a date-based summary.
