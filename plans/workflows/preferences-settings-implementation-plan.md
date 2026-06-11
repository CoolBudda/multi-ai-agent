# Preferences Settings Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: let users view and update their saved assistant preferences from a dedicated settings page.

## 2. Scope Mapping
- Included: Settings page layout, preference form, validation, save action, and backend write via the Memory Service.
- Excluded: Backend Memory Service implementation (covered by memory-service plan).

## 3. File Changes
- webapp/src/app/preferences/page.tsx
- webapp/src/features/companion/usePreferencesStore.ts
- webapp/src/lib/api.ts
- webapp/src/types/index.ts

## 4. LangGraph Nodes (if applicable)
- N/A

## 5. Tools
- TanStack Query

## 6. State Updates
- preferred_airline
- seat_preference
- meeting_start_time
- favorite_cuisine
- news_topics

## 7. Implementation Steps (strict order)
1. Define UserPreferences { preferred_airline, seat_preference, meeting_start_time, favorite_cuisine, news_topics } type in src/types/index.ts.
2. Implement preferences load endpoint in src/lib/api.ts (GET /preferences).
3. Implement preferences save endpoint in src/lib/api.ts (PUT /preferences).
4. Implement preferences page marked 'use client' in src/app/preferences/page.tsx.
5. Implement useQuery to load current preferences on page mount.
6. Implement editable form fields for all five preference fields.
7. Implement client-side validation blocking empty required fields on submit.
8. Implement useMutation to save preferences on form submission.
9. Show inline success feedback on successful save.
10. Show inline error and preserve edits on save failure.
11. Show inline error and allow retry on load failure.

## 8. Dependencies
- TanStack Query
- src/lib/api.ts
- Memory Service backend (preferences read/write endpoints must be live)

## 9. Test Plan
- Unit tests: Form validation blocks empty required fields; useMutation called on valid submit; error states preserve edits.
- Integration tests: Preferences load renders current values; save updates backend and shows success.
- Workflow tests: Full view-edit-save flow; save failure inline error; load failure retry.

## 10. Acceptance Criteria Mapping
- FR-001 The settings page displays all stored preference fields. -> Validate all five fields render with current values from backend.
- FR-002 Each field is editable. -> Validate each input is interactive.
- FR-003 Saving updates preferences in the backend Memory Service. -> Validate useMutation PUT call reaches backend.
- FR-004 Validation blocks submitting empty required fields. -> Validate empty required field prevents submission.
- FR-005 Save errors are shown inline without losing the user's edits. -> Validate error message renders and form retains edited values.

## 11. Open Questions
- None identified from the current requirements.
