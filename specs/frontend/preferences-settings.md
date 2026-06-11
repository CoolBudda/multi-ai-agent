# Preferences Settings

## Purpose
Let users view and update their saved assistant preferences from a dedicated settings page.

## Scope
Settings page layout, preference form, validation, save action, and backend write via the Memory Service.

## Requirements
- A settings page displays all stored preference fields: preferred airline, seat preference, meeting start time, favorite cuisine, and news topics.
- Each field is editable via a form.
- On save, updated preferences are written to the backend Memory Service.
- Validation prevents saving empty required fields.

## Inputs
- Current preferences loaded from the backend.
- User edits to preference fields.
- Save form submission.

## Outputs
- Rendered preference form with current values.
- PATCH or PUT request to the backend via `src/lib/api.ts`.
- Success or error feedback after save.

## Business Rules
- All backend calls go through `src/lib/api.ts`.
- Use TanStack Query `useQuery` to load preferences and `useMutation` to save them.
- The settings page must be marked `'use client'` (uses Zustand store or mutation hooks).
- Domain preference state lives in `src/features/<domain>/` store slices; cross-domain state in `src/stores/`.

## Workflow
1. User navigates to the settings page.
2. Current preferences are loaded via `useQuery`.
3. User edits one or more fields.
4. User submits the form.
5. Validation runs client-side.
6. On success, `useMutation` writes the updated preferences to the backend.
7. Success or failure feedback is shown.

## Data Model
- `UserPreferences`: `{ preferred_airline, seat_preference, meeting_start_time, favorite_cuisine, news_topics }`

## Error Handling
- If preferences cannot be loaded, show an error and allow retry.
- If the save request fails, show an inline error and preserve the user's edits.
- Validate that required fields are not submitted empty.

## Acceptance Criteria
- The settings page displays all stored preference fields.
- Each field is editable.
- Saving updates preferences in the backend Memory Service.
- Validation blocks submitting empty required fields.
- Save errors are shown inline without losing the user's edits.

## Open Questions
- None identified from the current requirements.
