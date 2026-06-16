from __future__ import annotations

from src.agents.orchestrator_agent import compute_routing_decision


def _request(message: str) -> dict[str, object]:
    return {
        "request_id": "req-agent-1",
        "user_id": "u1",
        "session_id": "s1",
        "message": message,
        "metadata": {},
    }


def test_routes_calendar_intent_with_high_confidence() -> None:
    decision, event = compute_routing_decision(_request("Schedule a meeting tomorrow"))

    assert decision["selected_domain"] == "calendar"
    assert decision["selected_confidence"] >= 0.6
    assert decision["fallback_to_companion"] is False
    assert event["event_name"] == "orchestrator.intent.detected"
    assert event["selected_domain"] == "calendar"


def test_routes_travel_intent_with_high_confidence() -> None:
    decision, _ = compute_routing_decision(_request("Find me a flight to Seattle"))

    assert decision["selected_domain"] == "travel"
    assert decision["fallback_to_companion"] is False


def test_routes_dining_intent_with_high_confidence() -> None:
    decision, _ = compute_routing_decision(_request("Find a dining reservation near downtown"))

    assert decision["selected_domain"] == "dining"
    assert decision["threshold_passed"] is True


def test_routes_news_intent_with_high_confidence() -> None:
    decision, _ = compute_routing_decision(_request("Show me the latest news headlines"))

    assert decision["selected_domain"] == "news"
    assert decision["threshold_passed"] is True


def test_includes_per_domain_confidence_candidates_for_specialists() -> None:
    decision, _ = compute_routing_decision(_request("Book a travel flight and check travel options"))

    candidates = decision["rationale"]["top_candidates"]
    assert len(candidates) == 2
    assert all(candidate["domain"] in {"calendar", "travel", "dining", "news", "companion"} for candidate in candidates)
    assert all(0.0 <= candidate["confidence"] <= 1.0 for candidate in candidates)


def test_low_confidence_falls_back_to_companion() -> None:
    decision, _ = compute_routing_decision(
        _request("hello"),
        confidence_threshold=0.75,
    )

    assert decision["selected_domain"] == "companion"
    assert decision["fallback_to_companion"] is True


def test_ambiguous_request_uses_companion_fallback_when_threshold_not_exceeded() -> None:
    decision, _ = compute_routing_decision(
        _request("I might need some help maybe later"),
        confidence_threshold=0.6,
    )

    assert decision["selected_domain"] == "companion"
    assert decision["fallback_to_companion"] is True
    assert decision["rationale"]["reason_code"] == "below_threshold_fallback"


def test_out_of_domain_request_uses_companion_fallback() -> None:
    decision, _ = compute_routing_decision(
        _request("Explain quantum entanglement in simple terms"),
        confidence_threshold=0.6,
    )

    assert decision["selected_domain"] == "companion"
    assert decision["fallback_to_companion"] is True
    assert decision["threshold_passed"] is False


def test_tie_window_detected_when_delta_is_at_most_point_zero_three() -> None:
    decision, _ = compute_routing_decision(
        _request("Schedule a flight"),
        confidence_threshold=0.6,
    )

    assert decision["tie_detected"] is True
    assert decision["rationale"]["tie_window"] == 0.03


def test_tie_break_precedence_prefers_calendar_over_travel() -> None:
    decision, _ = compute_routing_decision(
        _request("Schedule travel"),
        confidence_threshold=0.6,
    )

    assert decision["tie_detected"] is True
    assert decision["tie_resolved_by_precedence"] is True
    assert decision["selected_domain"] == "calendar"
    assert decision["rationale"]["tie_break_winner"] == "calendar"
    assert decision["rationale"]["reason_code"] == "tie_break_selected"


def test_tie_break_precedence_prefers_travel_over_dining_when_calendar_absent() -> None:
    decision, _ = compute_routing_decision(
        _request("Travel dining"),
        confidence_threshold=0.6,
    )

    assert decision["tie_detected"] is True
    assert decision["tie_resolved_by_precedence"] is True
    assert decision["selected_domain"] == "travel"
    assert decision["rationale"]["tie_break_winner"] == "travel"
