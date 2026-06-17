# Restaurant API — Step 19 in the learning path

Builds on CRM. Adds: menu with categories, tables, reservations with conflict detection, orders with line items.

## Endpoints
```
POST   /menu/categories
POST   /menu/items
GET    /menu                       # full menu with items grouped by category

POST   /tables                     # { number, seats, location }
POST   /reservations               # { table_id, customer_name, reserved_at, party_size }
GET    /reservations?date=&table_id=

POST   /orders                     # { table_id, reservation_id? }
POST   /orders/:id/items           # { menu_item_id, quantity, notes? }
GET    /orders/:id                 # with all line items
```

## Try
```bash
# Set up menu
CAT=$(curl -X POST http://localhost:3000/menu/categories -H "Content-Type: application/json" -d '{"name": "Pizzas"}' | jq -r .id)
ITEM=$(curl -X POST http://localhost:3000/menu/items -H "Content-Type: application/json" -d "{\"category_id\": \"$CAT\", \"name\": \"Margherita\", \"price_cents\": 1200}" | jq -r .id)

# See menu
curl http://localhost:3000/menu

# Create a table and reservation
TBL=$(curl -X POST http://localhost:3000/tables -H "Content-Type: application/json" -d '{"number": 5, "seats": 4, "location": "window"}' | jq -r .id)
curl -X POST http://localhost:3000/reservations -H "Content-Type: application/json" \
  -d "{\"table_id\": \"$TBL\", \"customer_name\": \"Alice\", \"reserved_at\": \"2024-12-15T19:00:00Z\", \"party_size\": 2}"

# Open an order
ORDER=$(curl -X POST http://localhost:3000/orders -H "Content-Type: application/json" -d "{\"table_id\": \"$TBL\"}" | jq -r .id)

# Add items
curl -X POST http://localhost:3000/orders/$ORDER/items -H "Content-Type: application/json" \
  -d "{\"menu_item_id\": \"$ITEM\", \"quantity\": 2}"

# See the bill
curl http://localhost:3000/orders/$ORDER
# { total_cents: 2400, items: [{ name: "Margherita", quantity: 2, price_cents: 2400 }] }
```

## What this teaches
1. **Hierarchical data**: menu_category → menu_items
2. **Conflict detection**: reservations within ±1 hour of an existing one
3. **Order as aggregate root**: order → order_items
4. **Running totals**: update order total when items added
5. **State machine on orders**: open → in_progress → paid → closed
6. **Practical scheduling**: restaurant reservations

## Next project
→ **food-delivery-api** — adds: restaurants, drivers, deliveries, real-time tracking
