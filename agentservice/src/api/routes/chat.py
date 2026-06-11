from __future__ import annotations

from src.models.events import ApprovalRequiredEvent


def deliver_approval_request_to_frontend(event: ApprovalRequiredEvent) -> dict[str, object]:
	"""Return a transport envelope used by the API layer to surface approval requests."""

	return {
		"type": "approval_request",
		"event_name": event["event_name"],
		"request": event["request"],
	}
