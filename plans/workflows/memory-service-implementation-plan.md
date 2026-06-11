# Memory Service Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: store and retrieve user preferences so specialist agents can personalize their responses without users repeating themselves.

## 2. Scope Mapping
- Included: Preference storage, retrieval, missing-field defaults, DynamoDB-backed persistence.
- Excluded: TBD.

## 3. File Changes
- backend/agentservice/src/services/memory_service.py
- backend/agentservice/src/models/state.py
- backend/agentservice/src/models/events.py
- backend/agentservice/tests/services/test_memory_service.py

## 4. LangGraph Nodes (if applicable)
- retrieve_user_preferences_at_agent_start
- apply_preferences_or_defaults
- write_preference_update

## 5. Tools
- DynamoDB

## 6. State Updates
- user_id
- preferred_airline
- seat_preference
- meeting_start_time
- favorite_cuisine
- news_topics

## 7. Implementation Steps (strict order)
1. Implement preference read by user_id from DynamoDB table user-preferences.
2. Implement memory.preference.loaded event emission on successful retrieval.
3. Return full preference object or empty object when no record exists.
4. Enforce agent-start retrieval usage through service layer path.
5. Implement missing-field handling support so agents can apply per-agent defaults without blocking.
6. Implement preference write/update by field and value.
7. Implement read-failure handling returning empty preferences object.
8. Implement write-failure handling with user-facing error and failure event emission.

## 8. Dependencies
- DynamoDB

## 9. Test Plan
- Unit tests: Read/write mapping, empty-object fallback, failure-path event emission.
- Integration tests: DynamoDB read/write operations for user-preferences table and partition key user_id.
- Workflow tests: Specialist-agent start load path and write-update path with surfaced write failure.

## 10. Acceptance Criteria Mapping
- FR-001 Store user preferences by field. -> Validate field-level write and persisted read-back behavior.
- FR-002 Retrieve all preferences for a given user at agent start. -> Validate full-object retrieval during agent-start flow.
- FR-003 Provide sensible per-agent defaults for missing fields. -> Validate missing fields do not block and defaultable behavior is supported.
- FR-004 Preferences must be accessible to all specialist agents. -> Validate service-layer retrieval is callable from each specialist-agent flow.

## 11. Open Questions
- None identified from the current requirements.
