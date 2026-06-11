# Approval Service

## Purpose
Gate all real-world write actions behind explicit user confirmation and handle the outcome of approval or rejection.

## Scope
Approval request creation, user decision handling, rejection event emission, and write-action blocking until approval is received.

## Requirements
- Require approval before any write action (calendar event, flight booking, restaurant reservation).
- Present the user with a clear summary of the pending action.
- Execute the action only after the user approves.
- Cancel the action and emit a rejection event if the user rejects.
- Prevent automatic retry of a rejected action.

## Inputs
- Proposed action payload from the specialist agent.
- User approval or rejection decision.

## Outputs
- Approval request delivered to the frontend.
- Approved or rejected status returned to the agent.
- `approval.required`, `approval.completed`, `<domain>.<action>.rejected` events.
- User-facing cancellation confirmation on rejection.

## Business Rules
- No write action executes before approval is confirmed.
- Rejected actions must not be retried without a new explicit user request.
- The Orchestrator must return a cancellation confirmation when an action is rejected.

## Workflow
1. Specialist agent signals a write action with an action payload.
2. Approval Service creates an approval request and surfaces it to the user.
3. User approves or rejects.
4. On approval: the agent completes the write action.
5. On rejection: emit a `<domain>.<action>.rejected` event and return a cancellation message.

## Data Model
- `ApprovalRequest`: `{ request_id, action_type, domain, summary, payload }`
- `ApprovalResult`: `{ request_id, status: 'approved' | 'rejected' }`

## Error Handling
- If the approval service is unavailable, do not execute the write action.
- If the user session expires before a decision is made, treat the request as rejected.

## Acceptance Criteria
- Write actions are blocked until approval is received.
- Rejected actions are not executed.
- A `<domain>.<action>.rejected` event is emitted on rejection.
- The user receives a clear cancellation confirmation on rejection.

## Open Questions
- None identified from the current requirements.
