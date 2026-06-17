# Database Design Demo — 3NF with users, products, orders

A normalized schema with foreign keys, indexes, joins, and aggregates. SQLite with FK enforcement on.

## Schema
```
users (id, name, email, created_at)
categories (id, name)
products (id, name, price_cents, category_id → categories.id)
orders (id, user_id → users.id, total_cents, status, created_at)
order_items (id, order_id → orders.id, product_id → products.id, quantity, price_cents)
```

## Endpoints
```
GET /users            # simple SELECT
GET /orders?status=   # WHERE + ORDER BY
GET /orders/full      # 4-table JOIN
GET /stats            # GROUP BY aggregate
GET /test/fk          # FK violation demo
GET /test/update      # 3NF: changing user name doesn't affect orders
```

## Try
```bash
curl http://localhost:3000/orders/full
# Returns: order_id, user_name, user_email, product_name, category_name, quantity, price_cents, status, created_at

curl http://localhost:3000/stats
# Returns: category, order_count, revenue_dollars

curl http://localhost:3000/test/fk
# Returns 400: "FOREIGN KEY constraint failed"
# (Cannot insert order with non-existent user_id)

curl http://localhost:3000/test/update
# Updates Alice → Alicia. Returns:
# - users: Alicia
# - orders: unchanged (because 3NF — name is in users, not duplicated in orders)
```

## What this teaches
1. **3NF schema**: 5 tables, no duplication, FKs enforce integrity
2. **Indexes**: `idx_products_category`, `idx_orders_user`, `idx_orders_status`, `idx_order_items_order`
3. **Joins**: 4-table join to get full order data
4. **Aggregates**: `COUNT`, `SUM`, `GROUP BY` for analytics
5. **FK enforcement**: trying to insert a non-existent user_id fails
6. **Update anomaly prevention**: change user name, orders don't need updating
