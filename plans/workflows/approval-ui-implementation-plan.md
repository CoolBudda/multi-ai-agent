# Approval UI Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: surface booking and reservation approval requests to the user and collect an explicit approve or reject decision before any write action is executed.

## 2. Scope Mapping
- Included: Approval modal or inline card, approve/reject actions, backend confirmation/cancellation requests, and post-decision messaging.
- Excluded: Backend approval gate logic (covered by approval-service plan).

## 3. File Changes
- webapp/src/features/companion/ApprovalCard.tsx
- webapp/src/lib/api.ts
- webapp/src/types/index.ts

## 4. LangGraph Nodes (if applicable)
- N/A

## 5. Tools
- N/A

## 6. State Updates
- N/A

## 7. Implementation Steps (strict order)
1. Define ApprovalRequest { actionType, summary, domain, actionPayload } and ApprovalDecision { approved: boolean, requestId } types in src/types/index.ts.
2. Implement approval send endpoints in src/lib/api.ts (approve and reject calls).
3. Implement ApprovalCard component marked 'use client'; renders action summary from ApprovalRequest payload; exposes Approve and Reject buttons.
4. On Approve: send confirmation to backend via api.ts and close the surface.
5. On Reject: send cancellation to backend via api.ts and render cancellation confirmation message.
6. If backend send fails: show inline error and keep the surface open for retry.
7. Do not reopen the approval surface for the same action automatically after rejection.
8. Integrate ApprovalCard rendering into ChatWindow when backend response signals approval-required.

## 8. Dependencies
- src/lib/api.ts
- ChatWindow (approval surface is rendered within chat flow)

## 9. Test Plan
- Unit tests: ApprovalCard renders summary; Approve and Reject buttons emit correct api calls; error state keeps surface open.
- Integration tests: Backend approval-required signal triggers ApprovalCard; approve closes surface; reject shows cancellation message.
- Workflow tests: Full approve flow confirms write action; full reject flow cancels and confirms no write.

## 10. Acceptance Criteria Mapping
- FR-001 An approval-required backend response triggers the approval UI. -> Validate ApprovalCard renders on approval-required signal.
- FR-002 The user can approve or reject from the UI. -> Validate both Approve and Reject interactions are functional.
- FR-003 An approval sends the confirmation to the backend and closes the surface. -> Validate api call on approve and surface dismissal.
- FR-004 A rejection sends the cancellation to the backend and shows a cancellation confirmation. -> Validate api call on reject and cancellation message.
- FR-005 No write action proceeds without a user approval interaction. -> Validate write path is blocked until decision is received.

## 11. Open Questions
- None identified from the current requirements.
