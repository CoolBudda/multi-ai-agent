from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal, TypedDict

from src.models.state import (
	ApprovalRequest,
	ApprovalResult,
	ErrorResponse,
	RoutingDecision,
	RoutingRecord,
	SupportedDomain,
	UserPreferences,
)


class MemoryPreferenceLoadedEvent(TypedDict):
	event_name: Literal["memory.preference.loaded"]
	user_id: str
	preferences: UserPreferences
	error_code: str | None


class MemoryPreferenceFailedEvent(TypedDict):
	event_name: Literal["memory.preference.failed"]
	user_id: str
	action: str
	error_code: str


class ApprovalRequiredEvent(TypedDict):
	event_name: Literal["approval.required"]
	request: ApprovalRequest


class ApprovalCompletedEvent(TypedDict):
	event_name: Literal["approval.completed"]
	result: ApprovalResult


class DomainActionRejectedEvent(TypedDict):
	event_name: str
	request_id: str
	domain: str
	action_type: str


class RoutingDecisionComputedEvent(TypedDict):
	event_name: Literal["orchestrator.intent.detected"]
	request_id: str
	selected_domain: SupportedDomain
	decision: RoutingDecision


class RoutingRecordLifecycleEvent(TypedDict):
	event_name: str
	action: Literal["created", "updated"]
	record: RoutingRecord


class DirectSpecialistAccessDeniedPayload(ErrorResponse):
	agent: SupportedDomain


def build_memory_preference_loaded_event(
	user_id: str,
	preferences: UserPreferences,
	*,
	error_code: str | None = None,
) -> MemoryPreferenceLoadedEvent:
	return {
		"event_name": "memory.preference.loaded",
		"user_id": user_id,
		"preferences": preferences,
		"error_code": error_code,
	}


def build_memory_preference_failed_event(
	user_id: str,
	*,
	action: str,
	error_code: str,
) -> MemoryPreferenceFailedEvent:
	return {
		"event_name": "memory.preference.failed",
		"user_id": user_id,
		"action": action,
		"error_code": error_code,
	}


def build_approval_required_event(request: ApprovalRequest) -> ApprovalRequiredEvent:
	return {
		"event_name": "approval.required",
		"request": request,
	}


def build_approval_completed_event(result: ApprovalResult) -> ApprovalCompletedEvent:
	return {
		"event_name": "approval.completed",
		"result": result,
	}


def build_domain_action_rejected_event(
	*,
	request_id: str,
	domain: str,
	action_type: str,
) -> DomainActionRejectedEvent:
	return {
		"event_name": f"{domain}.{action_type}.rejected",
		"request_id": request_id,
		"domain": domain,
		"action_type": action_type,
	}


def build_routing_decision_computed_event(
	decision: RoutingDecision,
) -> RoutingDecisionComputedEvent:
	return {
		"event_name": "orchestrator.intent.detected",
		"request_id": decision["request_id"],
		"selected_domain": decision["selected_domain"],
		"decision": decision,
	}


def build_routing_record_lifecycle_event(
	record: RoutingRecord,
	*,
	action: Literal["created", "updated"],
	status: Literal["succeeded", "failed", "rejected"],
) -> RoutingRecordLifecycleEvent:
	return {
		"event_name": f"orchestrator.routing_record.{status}",
		"action": action,
		"record": record,
	}


def build_direct_specialist_access_denied_payload(
	*,
	request_id: str,
	agent: SupportedDomain,
) -> DirectSpecialistAccessDeniedPayload:
	return {
		"error_code": "direct_specialist_access_denied",
		"message": "Requests must be submitted through the Orchestrator entry path.",
		"request_id": request_id,
		"agent": agent,
	}


def build_downstream_failure_payload(
	*,
	request_id: str,
	failure_code: str,
) -> ErrorResponse:
	return {
		"error_code": failure_code,
		"message": "The request entered through the Orchestrator but could not be completed. Please retry.",
		"request_id": request_id,
	}


def now_iso() -> str:
	return datetime.now(UTC).isoformat()

