# Domain Response Cards Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: render structured, domain-specific UI cards for travel, dining, and calendar responses so users can compare options at a glance instead of reading plain text.

## 2. Scope Mapping
- Included: Flight comparison cards, restaurant result cards, calendar slot cards, and plain text fallback for companion and news responses.
- Excluded: Data fetching, business logic, approval actions (covered by approval-ui plan).

## 3. File Changes
- webapp/src/features/travel/FlightCard.tsx
- webapp/src/features/dining/RestaurantCard.tsx
- webapp/src/features/calendar/CalendarSlotCard.tsx
- webapp/src/components/TextResponse.tsx
- webapp/src/features/companion/ChatWindow.tsx
- webapp/src/types/index.ts

## 4. LangGraph Nodes (if applicable)
- N/A

## 5. Tools
- N/A

## 6. State Updates
- N/A

## 7. Implementation Steps (strict order)
1. Define FlightOption, RestaurantOption, CalendarSlot, and TextResponse types in src/types/index.ts.
2. Implement FlightCard Server Component in src/features/travel/: renders airline, price, duration, stops; no business logic.
3. Implement RestaurantCard Server Component in src/features/dining/: renders name, cuisine, rating, distance; no business logic.
4. Implement CalendarSlotCard Server Component in src/features/calendar/: renders start/end time as selectable option; no business logic.
5. Implement TextResponse Server Component in src/components/: renders plain formatted text.
6. Implement domain-label-to-component dispatch in ChatWindow: reads domain label from response and renders matching card; falls back to TextResponse for unknown or text-only.
7. Implement degraded card rendering when a required field is missing; card renders without crashing.

## 8. Dependencies
- ChatWindow (cards are rendered within the chat response area)
- src/types/index.ts

## 9. Test Plan
- Unit tests: Each card renders correct fields from props; missing field renders degraded without error; unknown domain falls back to TextResponse.
- Integration tests: Backend response with domain label renders correct card type.
- Workflow tests: Travel, dining, and calendar full responses render respective cards in the chat interface.

## 10. Acceptance Criteria Mapping
- FR-001 Travel responses render a flight card with airline, price, duration, and stops. -> Validate FlightCard renders all four fields.
- FR-002 Dining responses render a restaurant card with name, cuisine, rating, and distance. -> Validate RestaurantCard renders all four fields.
- FR-003 Calendar responses render selectable time slots. -> Validate CalendarSlotCard renders start/end as selectable option.
- FR-004 Unstructured responses render as plain text. -> Validate TextResponse is used for companion and news responses.

## 11. Open Questions
- None identified from the current requirements.
