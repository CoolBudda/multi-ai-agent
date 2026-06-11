from __future__ import annotations

from typing import Literal, TypedDict

from src.models.state import ApprovalRequest, ApprovalResult, UserPreferences


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

