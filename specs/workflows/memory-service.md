# Memory Service

## Purpose
Store and retrieve user preferences so specialist agents can personalize their responses without users repeating themselves.

## Scope
Preference storage, retrieval, missing-field defaults, and DynamoDB-backed persistence.

## Requirements
- Store user preferences by field.
- Retrieve all preferences for a given user at agent start.
- Provide sensible per-agent defaults for missing fields.
- Preferences must be accessible to all specialist agents.

## Inputs
- User ID.
- Preference field name and value (for writes).
- Read request from a specialist agent.

## Outputs
- Full preference record for a user.
- Updated preference record after write.
- `memory.preference.loaded` event on retrieval.

## Business Rules
- Memory retrieval at agent start is the only permitted side effect in an agent node; it must go through the service layer.
- If a field is absent or null, the agent must proceed with a per-agent default and must not block execution.
- Agents should prompt the user to set a missing preference only when it materially affects response quality.
- Only essential user data is stored; no sensitive PII beyond what is required.

## Workflow
1. Agent start: call the Memory Service with the user ID.
2. Memory Service reads the DynamoDB record.
3. Return the preference object (or empty dict if no record exists).
4. Agent applies preferences or falls back to defaults.
5. On preference update: write the new value to DynamoDB.

## Data Model
- `UserPreferences`: `{ user_id, preferred_airline, seat_preference, meeting_start_time, favorite_cuisine, news_topics }`
- DynamoDB table: `user-preferences`, partition key `user_id`.

## Error Handling
- If DynamoDB read fails, return an empty preferences object and proceed with agent defaults.
- If DynamoDB write fails, return a user-facing error; do not silently discard the update.
- Emit a failure event on write errors.

## Acceptance Criteria
- Preferences can be written and later read back correctly.
- Missing fields do not block agent execution.
- All specialist agents load preferences at agent start via the service layer.
- Write failures surface a user-facing error.

## Open Questions
- None identified from the current requirements.
