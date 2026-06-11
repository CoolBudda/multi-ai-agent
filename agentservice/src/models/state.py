from __future__ import annotations

from typing import Any, Literal, TypedDict


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

