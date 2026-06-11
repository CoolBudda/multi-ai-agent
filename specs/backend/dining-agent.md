# Dining Agent

## Purpose
Help users find restaurants, check reservation availability, and make reservations through natural language while respecting dietary preferences.

## Scope
Restaurant search, cuisine/location/budget filtering, dietary preference application, availability checking, reservation creation, and approval handling.

## Requirements
- Recommend restaurants by cuisine, location, and budget.
- Check reservation availability.
- Make reservations after approval.
- Respect dietary restrictions and preferences.
- Offer alternatives when availability is limited.

## Inputs
- Restaurant search query.
- Cuisine, location, budget, and party size.
- Desired reservation time.
- Dietary preferences from the Memory Service.
- Restaurant API search and availability data.
- User approval decision.

## Outputs
- Restaurant options list.
- Availability results.
- Reservation confirmation.
- Alternative suggestions when needed.
- `dining.search.completed`, `dining.reservation.requested`, `dining.search.failed` events.

## Business Rules
- Load dietary preferences at agent start; continue with unfiltered results if absent.
- Reservation creation requires approval before execution.
- All restaurant API calls go through the service layer tool node.

## Workflow
1. Load dietary preferences from the Memory Service.
2. Parse the restaurant request.
3. Search restaurants with applied filters.
4. Check availability for shortlisted options.
5. Present results with alternatives if needed.
6. Request approval before placing a reservation.
7. Create the reservation after approval.

## Data Model
- `RestaurantQuery`: `{ cuisine, location, budget, party_size, time }`
- `RestaurantOption`: `{ name, cuisine, rating, distance, price_range }`
- `ReservationRequest`: `{ restaurant_id, time, party_size, user_id }`

## Error Handling
- If the restaurant API fails, emit `dining.search.failed` with the error code and return a user-facing retry message.
- If availability is limited, provide alternatives.
- If approval is rejected, do not place the reservation.

## Acceptance Criteria
- Restaurant searches return relevant, filtered results.
- Dietary preferences are applied when available.
- Availability is checked before presenting options.
- Reservations require and respect the approval decision.

## Open Questions
- None identified from the current requirements.
