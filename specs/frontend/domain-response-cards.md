# Domain Response Cards

## Purpose
Render structured, domain-specific UI cards for travel, dining, and calendar responses so users can compare options at a glance instead of reading plain text.

## Scope
Flight comparison cards, restaurant result cards, calendar slot cards, and plain text fallback for companion and news responses.

## Requirements
- Travel responses render a flight card showing airline, price, duration, and stops.
- Dining responses render a restaurant card showing name, cuisine, rating, and distance.
- Calendar responses render available time slots as selectable options.
- Companion and news responses render as plain formatted text.

## Inputs
- Structured agent response payload from the backend.
- Domain type identifier in the response.

## Outputs
- Rendered domain-specific card component.
- Plain text for non-structured responses.

## Business Rules
- Card components must contain no business logic.
- One component per file; file name matches the component name (PascalCase).
- Domain card components live in `src/features/<domain>/`.
- Components that do not use hooks or browser APIs remain Server Components.

## Workflow
1. Backend returns a response with a domain type label.
2. The frontend reads the domain label and selects the matching card component.
3. The card component renders the structured data.
4. Unknown or text-only responses fall back to plain text rendering.

## Data Model
- `FlightOption`: `{ airline, price, duration, stops, departureTime, arrivalTime }`
- `RestaurantOption`: `{ name, cuisine, rating, distance, availableTime }`
- `CalendarSlot`: `{ startTime, endTime, label }`
- `TextResponse`: `{ content: string }`

## Error Handling
- If the domain label is unrecognized, fall back to plain text rendering.
- If a required card field is missing, render a degraded card without crashing.

## Acceptance Criteria
- Flight responses render a card with airline, price, duration, and stops.
- Dining responses render a card with name, cuisine, rating, and distance.
- Calendar responses render selectable time slots.
- Unstructured responses render as plain text.

## Open Questions
- None identified from the current requirements.
