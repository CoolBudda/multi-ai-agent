from __future__ import annotations

from typing import Any, Literal, TypedDict


SupportedDomain = Literal["calendar", "travel", "dining", "news", "companion"]
RoutingStatus = Literal["succeeded", "failed", "rejected"]


class UserPreferences(TypedDict, total=False):
	user_id: str
	preferred_airline: str
	seat_preference: str
	meeting_start_time: str
	favorite_cuisine: str
	news_topics: list[str]


class ApprovalRequest(TypedDict):
	request_id: str
	action_type: str
	domain: str
	summary: str
	payload: dict[str, Any]


class ApprovalResult(TypedDict):
	request_id: str
	status: Literal["approved", "rejected"]


class CompanionRequest(TypedDict):
	message: str
	conversation_history: list[str]


class SafetyCheck(TypedDict):
	flagged: bool
	category: str | None


class CompanionResponse(TypedDict):
	response_text: str


class ClientRequest(TypedDict):
	request_id: str
	user_id: str
	session_id: str
	message: str
	channel: Literal["web", "mobile", "api"]
	created_at: str
	metadata: dict[str, Any]


class OrchestratorRequest(TypedDict):
	request_id: str
	user_id: str
	session_id: str
	message: str
	metadata: dict[str, Any]


class RoutingDecision(TypedDict):
	request_id: str
	initial_handler: Literal["orchestrator"]
	target_domain: SupportedDomain
	confidence: float
	fallback_applied: bool
	rationale: str
	decided_at: str


class RoutingRecord(TypedDict):
	record_id: str
	request_id: str
	entry_path: Literal["orchestrator"]
	initial_handler: Literal["orchestrator"]
	routed_to: SupportedDomain
	status: RoutingStatus
	failure_code: str | None
	rejection_code: str | None
	user_message: str
	created_at: str
	updated_at: str


class OrchestratorResponse(TypedDict):
	request_id: str
	initial_handler: Literal["orchestrator"]
	routed_to: SupportedDomain
	status: Literal["succeeded", "failed"]
	response: dict[str, Any]
	routing_record: RoutingRecord


class ErrorResponse(TypedDict):
	error_code: str
	message: str
	request_id: str

