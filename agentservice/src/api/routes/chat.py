from __future__ import annotations

from typing import Any
from uuid import uuid4

from src.models.events import ApprovalRequiredEvent
from src.models.state import ErrorResponse, OrchestratorRequest, OrchestratorResponse, SupportedDomain


SUPPORTED_SPECIALISTS: set[SupportedDomain] = {
	"calendar",
	"travel",
	"dining",
	"news",
	"companion",
}


def build_error_payload(
	*,
	error_code: str,
	message: str,
	request_id: str,
) -> ErrorResponse:
	return {
		"error_code": error_code,
		"message": message,
		"request_id": request_id,
	}


def deliver_approval_request_to_frontend(event: ApprovalRequiredEvent) -> dict[str, object]:
	"""Return a transport envelope used by the API layer to surface approval requests."""

	return {
		"type": "approval_request",
		"event_name": event["event_name"],
		"request": event["request"],
	}


def post_assistant_request(
	payload: dict[str, Any],
	*,
	orchestrator_graph: Any,
	force_downstream_failure: bool = False,
) -> tuple[int, OrchestratorResponse | ErrorResponse]:
	request_id = str(payload.get("request_id") or uuid4())
	validation_error = _validate_ingress_payload(payload, request_id=request_id)
	if validation_error is not None:
		return validation_error

	request: OrchestratorRequest = {
		"request_id": request_id,
		"user_id": str(payload["user_id"]),
		"session_id": str(payload["session_id"]),
		"message": str(payload["message"]).strip(),
		"metadata": payload.get("metadata", {}),
	}
	response = orchestrator_graph.run_orchestrator_ingress(
		request,
		force_downstream_failure=force_downstream_failure,
	)
	if response["status"] == "failed":
		return 503, response["response"]
	return 200, response


def post_agent_invoke(
	agent: str,
	payload: dict[str, Any],
	*,
	orchestrator_graph: Any,
) -> tuple[int, ErrorResponse]:
	if agent not in SUPPORTED_SPECIALISTS:
		request_id = str(payload.get("request_id") or uuid4())
		return (
			404,
			build_error_payload(
				error_code="agent_not_found",
				message="Agent not found.",
				request_id=request_id,
			),
		)

	request_id = str(payload.get("request_id") or uuid4())
	denied = orchestrator_graph.deny_direct_specialist_access(
		agent=agent,
		request_id=request_id,
	)
	return 403, denied


def _validate_ingress_payload(
	payload: dict[str, Any],
	*,
	request_id: str,
) -> tuple[int, ErrorResponse] | None:
	if not isinstance(payload, dict) or not payload:
		return (
			400,
			build_error_payload(
				error_code="malformed_request",
				message="Request body must be a non-empty JSON object.",
				request_id=request_id,
			),
		)

	missing = [field for field in ("request_id", "user_id", "session_id", "message") if field not in payload]
	if missing:
		return (
			422,
			build_error_payload(
				error_code="incomplete_request",
				message=f"Missing required fields: {', '.join(missing)}",
				request_id=request_id,
			),
		)

	message = str(payload.get("message", "")).strip()
	if not message:
		return (
			422,
			build_error_payload(
				error_code="incomplete_request",
				message="Field 'message' must be a non-empty string.",
				request_id=request_id,
			),
		)

	return None
