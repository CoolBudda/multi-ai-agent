from __future__ import annotations

from typing import Any, Literal, TypedDict


SupportedDomain = Literal["calendar", "travel", "dining", "news", "companion"]
SupportedSpecialistDomain = Literal["calendar", "travel", "dining", "news"]
RoutingStatus = Literal["succeeded", "failed", "rejected"]
RoutingReasonCode = Literal[
	"highest_above_threshold",
	"tie_break_selected",
	"below_threshold_fallback",
]


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


class CandidateScore(TypedDict):
	domain: SupportedDomain
	confidence: float


class RoutingPolicySnapshot(TypedDict):
	specialist_threshold: float
	tie_window: float
	precedence_order: list[SupportedSpecialistDomain]


class RoutingRationale(TypedDict):
	threshold: float
	tie_window: float
	top_candidates: list[CandidateScore]
	reason_code: RoutingReasonCode
	tie_break_winner: SupportedDomain | None


class RoutingDecision(TypedDict):
	request_id: str
	selected_domain: SupportedDomain
	selected_confidence: float
	threshold_passed: bool
	tie_detected: bool
	tie_resolved_by_precedence: bool
	fallback_to_companion: bool
	rationale: RoutingRationale
	policy_snapshot: RoutingPolicySnapshot
	decided_at: str


class RoutingRecord(TypedDict):
	record_id: str
	request_id: str
	entry_path: Literal["orchestrator"]
	initial_handler: Literal["orchestrator"]
	routed_to: SupportedDomain
	routing_decision: RoutingDecision | None
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
	routing_record_id: str
	selected_domain: SupportedDomain
	fallback_to_companion: bool
	threshold_passed: bool
	tie_detected: bool
	rationale: RoutingRationale
	routing_decision: RoutingDecision
	status: Literal["succeeded", "failed"]
	response: dict[str, Any]
	routing_record: RoutingRecord


class ErrorResponse(TypedDict):
	error_code: str
	message: str
	request_id: str

