# Food Delivery API — Step 20 in the learning path

Builds on Restaurant. Adds: multiple restaurants, drivers with locations, three-party state machine (customer → restaurant → driver → delivered).

## Endpoints
```
POST   /restaurants                  # register a restaurant
GET    /restaurants?cuisine=
POST   /restaurants/:id/menu         # add items
GET    /restaurants/:id/menu

POST   /drivers                      # register a driver
PATCH  /drivers/:id/location         # { lat, lng } — real-time tracking

POST   /orders                       # customer places an order { items: [{menu_item_id, quantity}] }
GET    /orders/customer/:id          # your orders
GET    /orders/:id                   # with restaurant, driver, items

POST   /orders/:id/accept            # restaurant accepts (X-Restaurant-Id)
POST   /orders/:id/claim             # driver claims a ready order (X-Driver-Id)
POST   /orders/:id/pickup            # driver picked it up
POST   /orders/:id/deliver           # driver delivered
```

## Order state machine
```
pending → preparing → ready → delivering → delivered
   ↑        ↑         ↑         ↑
customer  restaurant restaurant driver
```

## Try
```bash
# Setup: restaurant, menu, customer, driver
R=$(curl -X POST http://localhost:3000/restaurants -H "Content-Type: application/json" -d '{"name": "Pizza Place", "cuisine": "Italian"}' | jq -r .id)
ITEM=$(curl -X POST http://localhost:3000/restaurants/$R/menu -H "Content-Type: application/json" -d '{"name": "Margherita", "price_cents": 1200}' | jq -r .id)
D=$(curl -X POST http://localhost:3000/drivers -H "Content-Type: application/json" -d '{"name": "Bob", "phone": "555-1234"}' | jq -r .id)

# Customer orders
O=$(curl -X POST http://localhost:3000/orders -H "Content-Type: application/json" \
  -d "{\"customer_id\": \"c_alice\", \"restaurant_id\": \"$R\", \"items\": [{\"menu_item_id\": \"$ITEM\", \"quantity\": 2}], \"delivery_address\": \"123 Main St\"}" | jq -r .id)

# Restaurant accepts
curl -X POST http://localhost:3000/orders/$O/accept -H "X-Restaurant-Id: $R"

# Driver claims
curl -X POST http://localhost:3000/orders/$O/claim -H "X-Driver-Id: $D"

# Driver updates location (real-time tracking)
curl -X PATCH http://localhost:3000/drivers/$D/location -H "Content-Type: application/json" -d '{"lat": 40.7, "lng": -74.0}'

# Driver picks up and delivers
curl -X POST http://localhost:3000/orders/$O/pickup -H "X-Driver-Id: $D"
curl -X POST http://localhost:3000/orders/$O/deliver -H "X-Driver-Id: $D"

# Track
curl http://localhost:3000/orders/$O
```

## What this teaches
1. **Multi-party state machine**: customer, restaurant, driver each have actions
2. **Real-time location updates**: PATCH /drivers/:id/location
3. **Authorization per role**: different headers for different actions
4. **JSON in DB**: `items_json` for variable-shape order data
5. **Server-side calculation**: subtotal, fees, total computed when order placed
6. **Transitions guarded by current state**: can't accept an already-accepted order

## 🎉 End of the 20-project beginner sequence!
Next: move to **level2** projects for more complex full apps, or pick a topic from the curriculum docs.
