# Approval UI

## Purpose
Surface booking and reservation approval requests to the user and collect an explicit approve or reject decision before any write action is executed.

## Scope
Approval modal or inline card, approve/reject actions, backend confirmation/cancellation requests, and post-decision messaging.

## Requirements
- When the backend signals an approval-required response, the frontend renders a confirmation surface with a summary of the action.
- The user can approve or reject the action.
- On approve, the frontend sends confirmation to the backend.
- On reject, the frontend sends a cancellation and shows a confirmation message.
- No write action executes without explicit user interaction.

## Inputs
- Approval-required response payload from the backend.
- User approve or reject interaction.

## Outputs
- Rendered approval modal or inline confirmation card.
- Approval or rejection request sent to the backend via `src/lib/api.ts`.
- Post-decision status message in the UI.

## Business Rules
- Approval UI must be marked `'use client'` (uses event handlers).
- The approval surface must clearly describe the action being approved.
- Write actions must be gated behind this approval surface; they cannot be bypassed.

## Workflow
1. Backend response includes an approval-required signal.
2. Frontend renders the approval surface with the action summary.
3. User clicks Approve or Reject.
4. Frontend sends the decision to the backend.
5. On approve, the action proceeds and the surface closes.
6. On reject, a cancellation confirmation is shown.

## Data Model
- `ApprovalRequest`: `{ actionType, summary, domain, actionPayload }`
- `ApprovalDecision`: `{ approved: boolean, requestId }`

## Error Handling
- If the approval request cannot be sent to the backend, show an error and keep the surface open so the user can retry.
- If the action is rejected, show a clear cancellation message and do not reopen the approval surface for the same action automatically.

## Acceptance Criteria
- An approval-required backend response triggers the approval UI.
- The user can approve or reject from the UI.
- An approval sends the confirmation to the backend and closes the surface.
- A rejection sends the cancellation to the backend and shows a cancellation confirmation.
- No write action proceeds without a user approval interaction.

## Open Questions
- None identified from the current requirements.
