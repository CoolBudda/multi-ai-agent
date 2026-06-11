from __future__ import annotations

from src.agents.companion_agent import (
    DOMAIN_ACTION_TEXT,
    LIMITATION_TEXT,
    SAFE_FALLBACK_TEXT,
    SafetyPolicyUnavailableError,
    check_sensitive_content,
    enforce_consistent_tone,
    generate_conversational_response,
    handle_message,
    receive_message,
    route_to_safety_policy,
)


def test_step_1_message_intake_and_history_mapping() -> None:
    request = receive_message("  hi there  ", ["hello"])

    assert request["message"] == "hi there"
    assert request["conversation_history"] == ["hello"]


def test_step_2_sensitive_content_check() -> None:
    request = receive_message("I need legal advice about a contract", [])

    safety_check = check_sensitive_content(request)

    assert safety_check == {"flagged": True, "category": "legal_advice"}


def test_step_3_route_flagged_messages_to_safety_policy() -> None:
    request = receive_message("I feel suicidal", [])
    safety_check = check_sensitive_content(request)

    routed = route_to_safety_policy(
        request,
        safety_check,
        lambda req, check: {
            "response_text": f"routed:{check['category']}:{req['message']}"
        },
    )

    assert routed["response_text"].startswith("routed:mental_health_distress")


def test_step_4_generate_direct_response_for_non_flagged_messages() -> None:
    request = receive_message("What is dependency injection?", [])

    response = generate_conversational_response(request)

    assert "direct answer" in response["response_text"].lower()


def test_step_5_enforce_consistent_tone() -> None:
    response = enforce_consistent_tone({"response_text": "Let's brainstorm options."})

    assert response["response_text"].startswith("I can help with that.")


def test_step_6_enforce_domain_action_restriction() -> None:
    request = receive_message("Please book a flight to Seattle", [])

    response = generate_conversational_response(request)

    assert response["response_text"] == DOMAIN_ACTION_TEXT


def test_step_7_safety_layer_unavailable_returns_safe_fallback() -> None:
    request = receive_message("I want to die", [])
    safety_check = check_sensitive_content(request)

    response = route_to_safety_policy(
        request,
        safety_check,
        lambda _req, _check: (_ for _ in ()).throw(SafetyPolicyUnavailableError("down")),
    )

    assert response["response_text"] == SAFE_FALLBACK_TEXT


def test_step_8_uncertain_answer_returns_transparent_limitation() -> None:
    request = receive_message("??", [])

    response = generate_conversational_response(request)

    assert response["response_text"] == LIMITATION_TEXT


def test_requirement_fr_001_open_ended_dialogue() -> None:
    result = handle_message("Tell me something interesting", ["start"])

    assert result["safety_handoff"] is False
    assert isinstance(result["response"]["response_text"], str)


def test_requirement_fr_002_general_questions_answered_directly() -> None:
    result = handle_message("Why is the sky blue?", [])

    assert result["safety_handoff"] is False
    assert "direct answer" in result["response"]["response_text"].lower()


def test_requirement_fr_003_explanations_brainstorming_and_casual() -> None:
    explain = handle_message("Explain event sourcing", [])
    brainstorm = handle_message("Let's brainstorm app ideas", [])
    casual = handle_message("Nice weather today", [])

    assert "explanation" in explain["response"]["response_text"].lower()
    assert "brainstorm" in brainstorm["response"]["response_text"].lower()
    assert "chat" in casual["response"]["response_text"].lower()


def test_requirement_fr_004_consistent_tone_and_personality() -> None:
    first = handle_message("Explain caching", ["hello"])
    second = handle_message("Let's brainstorm API names", ["hello", "thanks"])

    assert first["response"]["response_text"].startswith("I ")
    assert second["response"]["response_text"].startswith("I ")


def test_requirement_fr_005_sensitive_content_routed_before_response() -> None:
    result = handle_message(
        "I need medical advice for this pain",
        [],
        safety_router=lambda _req, check: {"response_text": f"handoff:{check['category']}"},
    )

    assert result["safety_handoff"] is True
    assert result["safety_check"]["flagged"] is True
    assert result["response"]["response_text"].startswith("I can help with that. handoff:")


def test_acceptance_general_questions_answered_directly() -> None:
    result = handle_message("What is memoization?", [])

    assert result["safety_handoff"] is False
    assert "direct answer" in result["response"]["response_text"].lower()


def test_acceptance_sensitive_content_routed_to_safety_policy() -> None:
    result = handle_message(
        "Who should I vote for?",
        [],
        safety_router=lambda _req, check: {"response_text": f"policy:{check['category']}"},
    )

    assert result["safety_handoff"] is True
    assert result["response"]["response_text"].startswith("I can help with that. policy:political_opinion")


def test_acceptance_no_domain_actions_executed() -> None:
    result = handle_message("Can you reserve a table for tonight?", [])

    assert result["safety_handoff"] is False
    assert result["response"]["response_text"] == DOMAIN_ACTION_TEXT


def test_acceptance_consistent_tone_maintained() -> None:
    result_1 = handle_message("Explain queues", ["h1"])
    result_2 = handle_message("Let's brainstorm product names", ["h1", "h2"])

    assert result_1["response"]["response_text"].startswith("I ")
    assert result_2["response"]["response_text"].startswith("I ")
