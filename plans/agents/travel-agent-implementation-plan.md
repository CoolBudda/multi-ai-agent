# Travel Agent Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: help users search for flights, apply travel preferences, coordinate with the calendar, and initiate bookings or holds.

## 2. Scope Mapping
- Included: Flight search, result ranking, preference application, calendar conflict coordination, booking initiation, approval handling.
- Excluded: TBD.

## 3. File Changes
- backend/agentservice/src/agents/travel_agent.py
- backend/agentservice/src/tools/travel_tools.py
- backend/agentservice/src/services/memory_service.py
- backend/agentservice/src/services/approval_service.py
- backend/agentservice/src/agents/orchestrator_agent.py
- backend/agentservice/src/models/state.py
- backend/agentservice/src/models/events.py
- backend/agentservice/tests/agents/test_travel_agent.py
- backend/agentservice/tests/tools/test_travel_tools.py

## 4. LangGraph Nodes (if applicable)
- load_travel_preferences
- parse_travel_request
- request_calendar_availability_via_orchestrator
- search_flights
- rank_flights
- present_ranked_options
- request_approval
- initiate_booking_or_hold

## 5. Tools
- Memory Service
- Orchestrator
- Calendar Agent
- Flight search API
- Approval Service

## 6. State Updates
- preferred_airline
- seat_preference
- origin
- destination
- departure_date
- return_date
- constraints
- selected_option
- user_id

## 7. Implementation Steps (strict order)
1. Implement memory preference load for preferred_airline and seat_preference with non-blocking defaults.
2. Implement travel request parsing into FlightQuery fields.
3. Implement calendar availability coordination through Orchestrator routing path when dates are unspecified.
4. Implement flight search call through service layer tool node.
5. Implement flight ranking by price, duration, and preference match.
6. Present ranked options and capture selected option.
7. Implement approval request before booking or hold initiation.
8. Initiate booking or hold only when approval status is approved.
9. Emit travel.search.completed, travel.booking.requested, and travel.search.failed events at required points.

## 8. Dependencies
- Memory Service
- Orchestrator
- Calendar Agent
- Flight search API
- Approval Service

## 9. Test Plan
- Unit tests: Travel parsing, ranking logic, preference application, event emission.
- Integration tests: Memory Service load, Orchestrator calendar coordination path, Approval Service gate, flight API error handling.
- Workflow tests: End-to-end travel flow for approved booking, rejected booking, and no-match alternatives.

## 10. Acceptance Criteria Mapping
- FR-001 Search for flights by destination, dates, and constraints. -> Validate query-to-results behavior for destination/date/constraint inputs.
- FR-002 Rank results by price, duration, and preference match. -> Validate deterministic ranking ordering against criteria.
- FR-003 Apply user travel preferences automatically. -> Validate preferred_airline and seat_preference are applied when present.
- FR-004 Coordinate with the calendar to avoid conflicting travel dates. -> Validate Orchestrator-mediated calendar check path is used.
- FR-005 Initiate booking or hold after approval. -> Validate booking/hold executes only after approved status.

## 11. Open Questions
- None identified from the current requirements.
