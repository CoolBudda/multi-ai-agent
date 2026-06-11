# Dining Agent Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: help users find restaurants, check reservation availability, and make reservations through natural language while respecting dietary preferences.

## 2. Scope Mapping
- Included: Restaurant search, cuisine/location/budget filtering, dietary preference application, availability checking, reservation creation, approval handling.
- Excluded: TBD.

## 3. File Changes
- backend/agentservice/src/agents/dining_agent.py
- backend/agentservice/src/tools/dining_tools.py
- backend/agentservice/src/services/memory_service.py
- backend/agentservice/src/services/approval_service.py
- backend/agentservice/src/models/state.py
- backend/agentservice/src/models/events.py
- backend/agentservice/tests/agents/test_dining_agent.py
- backend/agentservice/tests/tools/test_dining_tools.py

## 4. LangGraph Nodes (if applicable)
- load_dietary_preferences
- parse_restaurant_request
- search_restaurants
- check_reservation_availability
- present_options_with_alternatives
- request_approval
- create_reservation

## 5. Tools
- Memory Service
- Restaurant API
- Approval Service

## 6. State Updates
- cuisine
- location
- budget
- party_size
- time
- name
- rating
- distance
- price_range
- restaurant_id
- user_id

## 7. Implementation Steps (strict order)
1. Implement dietary preference load from Memory Service with non-blocking behavior when absent.
2. Implement dining request parsing into RestaurantQuery fields.
3. Implement restaurant search through service layer tool node with cuisine/location/budget/party_size filters.
4. Implement availability checks for shortlisted restaurant options.
5. Implement option presentation with alternatives when availability is limited.
6. Implement approval request before reservation creation.
7. Implement reservation creation only when approval status is approved.
8. Emit dining.search.completed, dining.reservation.requested, and dining.search.failed events at required points.

## 8. Dependencies
- Memory Service
- Restaurant API
- Approval Service

## 9. Test Plan
- Unit tests: Request parsing, filter application, alternative generation, event emission.
- Integration tests: Memory Service dietary load, restaurant API search/availability calls, approval gate for reservation creation.
- Workflow tests: End-to-end dining flow for available options, limited availability alternatives, and rejected approval.

## 10. Acceptance Criteria Mapping
- FR-001 Recommend restaurants by cuisine, location, and budget. -> Validate filtered recommendations by provided constraints.
- FR-002 Check reservation availability. -> Validate availability checks occur before reservation path.
- FR-003 Make reservations after approval. -> Validate reservation creation requires approved status.
- FR-004 Respect dietary restrictions and preferences. -> Validate dietary preferences are applied when available.
- FR-005 Offer alternatives when availability is limited. -> Validate alternatives are returned for limited availability.

## 11. Open Questions
- None identified from the current requirements.
