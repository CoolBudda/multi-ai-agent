# Frontend Error Handling Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: ensure the UI remains usable and informative when backend API calls fail or streams terminate unexpectedly.

## 2. Scope Mapping
- Included: Inline error display, input recovery, retry affordance, and degraded state prevention for all API-driven surfaces.
- Excluded: Backend error handling (covered by each agent/service plan).

## 3. File Changes
- webapp/src/features/companion/ChatWindow.tsx
- webapp/src/features/companion/ApprovalCard.tsx
- webapp/src/features/auth/LoginForm.tsx
- webapp/src/app/preferences/page.tsx
- webapp/src/lib/api.ts
- webapp/src/types/index.ts

## 4. LangGraph Nodes (if applicable)
- N/A

## 5. Tools
- TanStack Query

## 6. State Updates
- N/A

## 7. Implementation Steps (strict order)
1. Define ApiError { message: string, statusCode?: number, retryable: boolean } type in src/types/index.ts.
2. Implement error mapping in src/lib/api.ts: map non-2xx responses and network errors to ApiError; no any types.
3. Implement inline error display in ChatWindow: show error message and re-enable input on stream failure or API error.
4. Implement inline error display in ApprovalCard: show error and keep surface open on send failure.
5. Implement inline error display for LoginForm: show error and allow retry on auth failure.
6. Implement inline error display for preferences page: show error and preserve user edits on save failure.
7. Validate all error surfaces route through TanStack Query error state or explicit catch handlers; no console-only errors.
8. Validate no surface becomes blank or unresponsive after any error.

## 8. Dependencies
- TanStack Query
- src/lib/api.ts
- ChatWindow, ApprovalCard, LoginForm, preferences page

## 9. Test Plan
- Unit tests: ApiError mapping for non-2xx and network errors; inline error renders in each component; input re-enabled after error.
- Integration tests: Simulated API failure triggers inline error in each surface.
- Workflow tests: Chat stream failure restores input; approval send failure keeps surface open; preference save failure preserves edits.

## 10. Acceptance Criteria Mapping
- FR-001 A failed API call shows an inline error message. -> Validate error message renders in each API-driven surface.
- FR-002 The error message includes a retry suggestion. -> Validate retry affordance is present in each error state.
- FR-003 The chat input is re-enabled after any error. -> Validate isStreaming is false and input enabled after error.
- FR-004 No surface becomes blank or unresponsive after an error. -> Validate each surface maintains usable state after error.

## 11. Open Questions
- None identified from the current requirements.
