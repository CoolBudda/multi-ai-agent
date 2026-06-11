from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable
from uuid import uuid4

from src.models.events import (
	ApprovalCompletedEvent,
	ApprovalRequiredEvent,
	DomainActionRejectedEvent,
	build_approval_completed_event,
	build_approval_required_event,
	build_domain_action_rejected_event,
)
from src.models.state import ApprovalRequest, ApprovalResult


class ApprovalServiceUnavailableError(RuntimeError):
	pass


class RejectedActionRetryBlockedError(RuntimeError):
	pass


@dataclass(slots=True)
class ApprovalService:
	id_factory: Callable[[], str] = field(default=lambda: str(uuid4()))
	_rejected_fingerprints: set[str] = field(default_factory=set)

	def create_approval_request(
		self,
		write_action_payload: dict[str, Any],
	) -> tuple[ApprovalRequest, ApprovalRequiredEvent]:
		action_type = str(write_action_payload["action_type"])
		domain = str(write_action_payload["domain"])
		summary = str(write_action_payload["summary"])
		payload = write_action_payload.get("payload", write_action_payload)

		if not isinstance(payload, dict):
			raise ValueError("payload must be a dictionary")

		request: ApprovalRequest = {
			"request_id": self.id_factory(),
			"action_type": action_type,
			"domain": domain,
			"summary": summary,
			"payload": payload,
		}
		return request, build_approval_required_event(request)

	def await_user_decision(
		self,
		request_id: str,
		*,
		decision: str | None,
		service_available: bool = True,
		session_expired: bool = False,
	) -> tuple[ApprovalResult, ApprovalCompletedEvent]:
		if not service_available:
			raise ApprovalServiceUnavailableError("Approval service unavailable")

		if session_expired:
			result: ApprovalResult = {"request_id": request_id, "status": "rejected"}
			return result, build_approval_completed_event(result)

		if decision not in {"approved", "rejected"}:
			raise ValueError("decision must be 'approved' or 'rejected'")

		result = {"request_id": request_id, "status": decision}
		return result, build_approval_completed_event(result)

	def process_approval_outcome(
		self,
		request: ApprovalRequest,
		result: ApprovalResult,
		*,
		is_new_user_request: bool = False,
	) -> dict[str, Any]:
		fingerprint = self._request_fingerprint(request)
		if fingerprint in self._rejected_fingerprints and not is_new_user_request:
			raise RejectedActionRetryBlockedError(
				"Rejected actions require a new explicit user request before retry"
			)

		if result["status"] == "approved":
			return {
				"status": "approved",
				"allow_execution": True,
				"message": None,
				"rejection_event": None,
			}

		rejection_event = build_domain_action_rejected_event(
			request_id=request["request_id"],
			domain=request["domain"],
			action_type=request["action_type"],
		)
		self._rejected_fingerprints.add(fingerprint)
		return {
			"status": "rejected",
			"allow_execution": False,
			"message": "Action cancelled. No changes were made.",
			"rejection_event": rejection_event,
		}

	def execute_or_cancel_write_action(
		self,
		request: ApprovalRequest,
		result: ApprovalResult,
		write_action: Callable[[], Any],
		*,
		is_new_user_request: bool = False,
	) -> dict[str, Any]:
		outcome = self.process_approval_outcome(
			request,
			result,
			is_new_user_request=is_new_user_request,
		)

		if not outcome["allow_execution"]:
			return {
				"status": "cancelled",
				"result": None,
				"message": outcome["message"],
				"rejection_event": outcome["rejection_event"],
			}

		execution_result = write_action()
		return {
			"status": "executed",
			"result": execution_result,
			"message": None,
			"rejection_event": None,
		}

	@staticmethod
	def _request_fingerprint(request: ApprovalRequest) -> str:
		return f"{request['domain']}:{request['action_type']}:{request['summary']}"


def create_approval_request(
	service: ApprovalService,
	write_action_payload: dict[str, Any],
) -> tuple[ApprovalRequest, ApprovalRequiredEvent]:
	return service.create_approval_request(write_action_payload)


def await_user_decision(
	service: ApprovalService,
	request_id: str,
	*,
	decision: str | None,
	service_available: bool = True,
	session_expired: bool = False,
) -> tuple[ApprovalResult, ApprovalCompletedEvent]:
	return service.await_user_decision(
		request_id,
		decision=decision,
		service_available=service_available,
		session_expired=session_expired,
	)


def process_approval_outcome(
	service: ApprovalService,
	request: ApprovalRequest,
	result: ApprovalResult,
	*,
	is_new_user_request: bool = False,
) -> dict[str, Any]:
	return service.process_approval_outcome(
		request,
		result,
		is_new_user_request=is_new_user_request,
	)


def execute_or_cancel_write_action(
	service: ApprovalService,
	request: ApprovalRequest,
	result: ApprovalResult,
	write_action: Callable[[], Any],
	*,
	is_new_user_request: bool = False,
) -> dict[str, Any]:
	return service.execute_or_cancel_write_action(
		request,
		result,
		write_action,
		is_new_user_request=is_new_user_request,
	)
