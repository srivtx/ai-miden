# Ticket Booking API — Step 17 in the learning path

Builds on Helpdesk. Adds: venues with seat generation, events, seat selection, booking with payment, cancellation.

## Endpoints
```
POST   /venues                       # { name, generate_seats: { rows, seats_per_row } }
POST   /events                       # { venue_id, name, start_at, base_price_cents, ... }
GET    /events                       # with available seat count
GET    /events/:id                   # with seat map (taken/available)

POST   /events/:id/book              # { seat_id } (X-User-Id) — with simulated payment
POST   /bookings/:id/cancel
GET    /my-bookings
```

## Try
```bash
# Create a venue with seats
curl -X POST http://localhost:3000/venues -H "Content-Type: application/json" \
  -d '{"name": "Apollo Theater", "capacity": 50, "generate_seats": {"rows": 5, "seats_per_row": 10}}'

# Create an event
curl -X POST http://localhost:3000/events -H "Content-Type: application/json" \
  -d '{"venue_id": "<id>", "name": "Concert", "start_at": "2024-12-31T20:00:00Z", "base_price_cents": 5000}'

# See the seat map
curl http://localhost:3000/events/<event-id>
# { event: {...}, seats: [{ id, row: "A", number: 1, taken: false }, ...] }

# Book a seat
curl -X POST http://localhost:3000/events/<event-id>/book -H "Content-Type: application/json" \
  -H "X-User-Id: u_alice" -d '{"seat_id": "<seat-id>"}'
# 201 { booking_id, payment_id, status: "confirmed", amount_cents: 5000 }

# Try to book the same seat again
curl -X POST http://localhost:3000/events/<event-id>/book -H "Content-Type: application/json" \
  -H "X-User-Id: u_bob" -d '{"seat_id": "<same-seat-id>"}'
# 409 { error: "seat_taken" }
```

## What this teaches
1. **Unique constraints**: `(event_id, seat_id)` prevents double-booking
2. **Auto-generation**: create seats in a grid
3. **Availability calculation**: NOT EXISTS subquery
4. **Payment integration**: simulated, returns payment_id
5. **Cancellation**: status update, frees up the seat
6. **Authorization**: only the booker can cancel

## Next project
→ **crm-api** — adds: contacts, deals, pipeline, activity tracking
