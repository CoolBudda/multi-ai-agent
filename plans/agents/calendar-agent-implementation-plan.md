# Calendar Agent Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: enable natural-language meeting scheduling, availability checking, conflict detection, and calendar event management via Microsoft 365.

## 2. Scope Mapping
- Included: Time expression parsing, availability lookup, slot suggestion, conflict detection, event creation/update/cancellation, scheduling preference application.
- Excluded: TBD.

## 3. File Changes
- backend/agentservice/src/agents/calendar_agent.py
- backend/agentservice/src/tools/calendar_tools.py
- backend/agentservice/src/services/memory_service.py
- backend/agentservice/src/services/approval_service.py
- backend/agentservice/src/models/state.py
- backend/agentservice/src/models/events.py
- backend/agentservice/tests/agents/test_calendar_agent.py
- backend/agentservice/tests/tools/test_calendar_tools.py

## 4. LangGraph Nodes (if applicable)
- load_scheduling_preferences
- parse_meeting_request
- check_calendar_availability
- generate_candidate_slots
- present_slot_options
- request_approval
- apply_calendar_write_action

## 5. Tools
- Memory Service
- Microsoft Graph API
- Approval Service

## 6. State Updates
- title
- attendees
- requested_time
- duration
- time_zone
- start
- end
- available
- id

## 7. Implementation Steps (strict order)
1. Implement memory preference load for meeting_start_time with default 09:00.
2. Implement meeting request parsing into MeetingRequest fields.
3. Implement calendar availability query through service layer tool node using Microsoft Graph API.
4. Implement candidate slot generation filtered by meeting_start_time.
5. Implement conflict reporting and alternative slot generation.
6. Implement approval request creation before create/update/cancel operations.
7. Implement calendar write execution only after approval status is approved.
8. Emit calendar.availability.checked, calendar.event.created, and calendar.availability.failed events at required points.
9. Return user-facing retry message on availability failure and block writes on rejection.

## 8. Dependencies
- Microsoft Graph API
- Memory Service
- Approval Service

## 9. Test Plan
- Unit tests: Meeting parsing, slot filtering by meeting_start_time, conflict detection, event emission.
- Integration tests: Memory Service load, Microsoft Graph availability call path, Approval Service gate for write actions.
- Workflow tests: End-to-end schedule flow with approval approved and approval rejected outcomes.

## 10. Acceptance Criteria Mapping
- FR-001 Parse natural-language date and time expressions. -> Validate parsed MeetingRequest fields from natural-language inputs.
- FR-002 Check calendar availability via Microsoft Graph API. -> Validate service-layer availability call and returned slot data.
- FR-003 Suggest available time slots that respect user scheduling preferences. -> Validate slot outputs are at/after meeting_start_time.
- FR-004 Detect and report scheduling conflicts. -> Validate conflict response includes conflict details and alternatives.
- FR-005 Create, update, and cancel calendar events. -> Validate write paths execute after approval and return event outcome.
- FR-006 All calendar write actions must go through the Approval Service. -> Validate write actions are blocked without approved status.

## 11. Open Questions
- None identified from the current requirements.
