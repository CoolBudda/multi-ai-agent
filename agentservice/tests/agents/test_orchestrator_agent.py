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

    assert decision["target_domain"] == "calendar"
    assert decision["initial_handler"] == "orchestrator"
    assert decision["confidence"] >= 0.6
    assert decision["fallback_applied"] is False
    assert event["event_name"] == "orchestrator.intent.detected"


def test_routes_travel_intent_with_high_confidence() -> None:
    decision, _ = compute_routing_decision(_request("Find me a flight to Seattle"))

    assert decision["target_domain"] == "travel"
    assert decision["fallback_applied"] is False


def test_low_confidence_falls_back_to_companion() -> None:
    decision, _ = compute_routing_decision(
        _request("hello"),
        confidence_threshold=0.75,
    )

    assert decision["target_domain"] == "companion"
    assert decision["fallback_applied"] is True
