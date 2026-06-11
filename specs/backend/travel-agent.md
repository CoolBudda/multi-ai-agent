# Travel Agent

## Purpose
Help users search for flights, apply travel preferences, coordinate with the calendar, and initiate bookings or holds.

## Scope
Flight search, result ranking, preference application, calendar conflict coordination, booking initiation, and approval handling.

## Requirements
- Search for flights by destination, dates, and constraints.
- Rank results by price, duration, and preference match.
- Apply user travel preferences automatically.
- Coordinate with the calendar to avoid conflicting travel dates.
- Initiate booking or hold after approval.

## Inputs
- Travel request text.
- User travel preferences from the Memory Service.
- Calendar availability (via Orchestrator → Calendar Agent).
- Flight search API results.
- User approval decision.

## Outputs
- Ranked flight options.
- Booking or hold initiation request.
- Approval request payload.
- `travel.search.completed`, `travel.booking.requested`, `travel.search.failed` events.

## Business Rules
- Load `preferred_airline` and `seat_preference` at agent start; continue without blocking if absent.
- Calendar coordination goes through the Orchestrator — the Travel Agent never calls the Calendar Agent directly.
- Flight booking or hold requires approval before execution.
- All flight API calls go through the service layer tool node.

## Workflow
1. Load travel preferences from the Memory Service.
2. Parse the travel request.
3. Request calendar availability via the Orchestrator (if dates are unspecified).
4. Search and rank flights.
5. Present ranked options.
6. Request approval for the selected option.
7. Initiate booking or hold after approval.

## Data Model
- `FlightQuery`: `{ origin, destination, departure_date, return_date, constraints }`
- `FlightOption`: `{ airline, price, duration, stops, departure, arrival, seat_class }`
- `BookingRequest`: `{ selected_option, user_id }`

## Error Handling
- If the flight API fails, emit `travel.search.failed` with the error code and return a user-facing retry message.
- If approval is rejected, do not book or hold the flight.
- If no flights match, indicate limited availability and offer alternatives.

## Acceptance Criteria
- Flight search returns ranked results.
- Travel preferences are applied automatically.
- Calendar conflicts are avoided when recommending dates.
- Booking requires and respects the approval decision.

## Open Questions
- None identified from the current requirements.
