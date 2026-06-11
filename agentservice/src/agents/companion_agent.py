from __future__ import annotations

from typing import Callable

from src.models.state import CompanionRequest, CompanionResponse, SafetyCheck

SafetyPolicyRouter = Callable[[CompanionRequest, SafetyCheck], CompanionResponse]


class SafetyPolicyUnavailableError(RuntimeError):
	pass


SAFE_FALLBACK_TEXT = (
	"I can't safely respond to that right now. "
	"If this is urgent, please contact local emergency services or a qualified professional."
)
LIMITATION_TEXT = "I may be mistaken, so I can't provide a confident answer right now."
DOMAIN_ACTION_TEXT = "I can help think through options, but I can't perform bookings or searches directly."

_SENSITIVE_PATTERNS: dict[str, tuple[str, ...]] = {
	"mental_health_distress": ("suicidal", "self-harm", "want to die", "kill myself"),
	"medical_advice": ("medical advice", "diagnose", "prescription", "dosage"),
	"legal_advice": ("legal advice", "lawsuit", "sue", "contract dispute"),
	"political_opinion": ("who should i vote", "political opinion", "election opinion"),
	"content_moderation": ("hate speech", "build a bomb", "graphic violence", "explicit sexual"),
}

_DOMAIN_ACTION_PATTERNS = (
	"book",
	"booking",
	"reserve",
	"reservation",
	"search flights",
	"find flights",
	"search restaurants",
)


def receive_message(message: str, conversation_history: list[str] | None = None) -> CompanionRequest:
	return {
		"message": message.strip(),
		"conversation_history": conversation_history or [],
	}


def check_sensitive_content(request: CompanionRequest) -> SafetyCheck:
	text = request["message"].lower()
	for category, patterns in _SENSITIVE_PATTERNS.items():
		if any(pattern in text for pattern in patterns):
			return {"flagged": True, "category": category}
	return {"flagged": False, "category": None}


def route_to_safety_policy(
	request: CompanionRequest,
	safety_check: SafetyCheck,
	safety_router: SafetyPolicyRouter,
) -> CompanionResponse:
	try:
		return safety_router(request, safety_check)
	except SafetyPolicyUnavailableError:
		return {"response_text": SAFE_FALLBACK_TEXT}


def generate_conversational_response(request: CompanionRequest) -> CompanionResponse:
	message = request["message"]
	lower_message = message.lower()

	if _is_domain_action_request(lower_message):
		return {"response_text": DOMAIN_ACTION_TEXT}

	if not _is_confident_answer_possible(message):
		return {"response_text": LIMITATION_TEXT}

	if "brainstorm" in lower_message:
		return {"response_text": "Let's brainstorm a few practical options and pick one to try first."}

	if "explain" in lower_message:
		return {"response_text": "Here is a clear explanation with the key points first, then details."}

	if message.endswith("?"):
		return {"response_text": "Here is a direct answer based on what you asked."}

	return {"response_text": "Happy to chat. Tell me what outcome you want, and we can shape ideas together."}


def enforce_consistent_tone(response: CompanionResponse) -> CompanionResponse:
	text = response["response_text"]
	if text.startswith("I can't safely respond"):
		return response
	if text.startswith("I can help think"):
		return response
	if text.startswith("I may be mistaken"):
		return response
	if text.startswith("I "):
		return response
	return {"response_text": f"I can help with that. {text}"}


def handle_message(
	message: str,
	conversation_history: list[str] | None = None,
	*,
	safety_router: SafetyPolicyRouter | None = None,
) -> dict[str, object]:
	request = receive_message(message, conversation_history)
	safety_check = check_sensitive_content(request)

	if safety_check["flagged"]:
		router = safety_router or _unavailable_safety_router
		response = route_to_safety_policy(request, safety_check, router)
		return {
			"response": enforce_consistent_tone(response),
			"safety_handoff": True,
			"safety_check": safety_check,
		}

	response = generate_conversational_response(request)
	return {
		"response": enforce_consistent_tone(response),
		"safety_handoff": False,
		"safety_check": safety_check,
	}


def _is_domain_action_request(text: str) -> bool:
	return any(pattern in text for pattern in _DOMAIN_ACTION_PATTERNS)


def _is_confident_answer_possible(message: str) -> bool:
	trimmed = message.strip()
	if not trimmed:
		return False
	if len(trimmed) < 3:
		return False
	if "???" in trimmed:
		return False
	return True


def _unavailable_safety_router(_: CompanionRequest, __: SafetyCheck) -> CompanionResponse:
	raise SafetyPolicyUnavailableError("Safety/Policy layer unavailable")
