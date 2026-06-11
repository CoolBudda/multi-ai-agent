# Approval Service Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: gate all real-world write actions behind explicit user confirmation and handle the outcome of approval or rejection.

## 2. Scope Mapping
- Included: Approval request creation, user decision handling, rejection event emission, write-action blocking until approval is received.
- Excluded: TBD.

## 3. File Changes
- backend/agentservice/src/services/approval_service.py
- backend/agentservice/src/models/state.py
- backend/agentservice/src/models/events.py
- backend/agentservice/src/api/routes/chat.py
- backend/agentservice/tests/services/test_approval_service.py
- backend/agentservice/tests/workflows/test_approval_flow.py

## 4. LangGraph Nodes (if applicable)
- create_approval_request
- await_user_decision
- process_approval_outcome
- execute_or_cancel_write_action

## 5. Tools
- Orchestrator

## 6. State Updates
- request_id
- action_type
- domain
- summary
- payload
- status

## 7. Implementation Steps (strict order)
1. Implement ApprovalRequest creation from specialist agent write-action payload.
2. Implement approval.required event emission and frontend delivery path.
3. Implement user decision intake and ApprovalResult mapping.
4. Implement approval.completed event emission on completed decisions.
5. Implement approved path to allow downstream write action execution.
6. Implement rejected path to emit <domain>.<action>.rejected event and return cancellation confirmation.
7. Enforce no automatic retry for rejected actions without a new explicit user request.
8. Implement service-unavailable and expired-session handling by preventing write execution and treating expired decision windows as rejected.

## 8. Dependencies
- Orchestrator

## 9. Test Plan
- Unit tests: ApprovalRequest mapping, decision-state transitions, rejection event naming, retry-block logic.
- Integration tests: Frontend approval request delivery, approved execution path, rejected cancellation path.
- Workflow tests: End-to-end write action blocked-until-approval flow including unavailable-service and expired-session rejection handling.

## 10. Acceptance Criteria Mapping
- FR-001 Require approval before any write action (calendar event, flight booking, restaurant reservation). -> Validate all write operations are blocked before approved status.
- FR-002 Present the user with a clear summary of the pending action. -> Validate summary field is present in ApprovalRequest and surfaced.
- FR-003 Execute the action only after the user approves. -> Validate execution path depends on approved decision.
- FR-004 Cancel the action and emit a rejection event if the user rejects. -> Validate cancellation response and <domain>.<action>.rejected emission.
- FR-005 Prevent automatic retry of a rejected action. -> Validate rejected actions are not retried absent a new explicit request.

## 11. Open Questions
- None identified from the current requirements.
