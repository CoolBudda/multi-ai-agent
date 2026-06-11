# Calendar Agent

## Purpose
Enable natural-language meeting scheduling, availability checking, conflict detection, and calendar event management via Microsoft 365.

## Scope
Time expression parsing, availability lookup, slot suggestion, conflict detection, event creation/update/cancellation, and scheduling preference application.

## Requirements
- Parse natural-language date and time expressions.
- Check calendar availability via Microsoft Graph API.
- Suggest available time slots that respect user scheduling preferences.
- Detect and report scheduling conflicts.
- Create, update, and cancel calendar events.
- All calendar write actions must go through the Approval Service.

## Inputs
- Meeting request text.
- User scheduling preferences from the Memory Service.
- Microsoft Graph API availability data.
- User approval decision from the Approval Service.

## Outputs
- Available time slots.
- Conflict details and alternative slots.
- Created, updated, or cancelled calendar event.
- Approval request payload.
- `calendar.availability.checked`, `calendar.event.created`, `calendar.availability.failed` events.

## Business Rules
- Load `meeting_start_time` preference at agent start; default to `09:00` if absent.
- Never suggest slots before the user's preferred start time.
- Calendar write actions require approval before execution.
- All Microsoft Graph API calls go through the service layer tool node, not the agent node.

## Workflow
1. Load scheduling preferences from the Memory Service.
2. Parse the meeting request.
3. Query Microsoft Graph API for availability.
4. Generate candidate slots, filtered by preferences.
5. Present slots to the user.
6. On selection, trigger approval.
7. After approval, create/update/cancel the event.

## Data Model
- `MeetingRequest`: `{ title, attendees, requested_time, duration, time_zone }`
- `CalendarSlot`: `{ start, end, available: bool }`
- `CalendarEvent`: `{ id, title, start, end, attendees, time_zone }`

## Error Handling
- If the Microsoft Graph API call fails, emit `calendar.availability.failed` with the error code and return a user-facing retry message.
- If approval is rejected, do not create or modify the event.
- Do not return partial results without indicating degradation.

## Acceptance Criteria
- A meeting can be scheduled from a natural-language request.
- Scheduling preferences are respected in slot suggestions.
- Conflicts are detected and alternatives offered.
- Write operations require and respect the approval decision.

## Open Questions
- None identified from the current requirements.
