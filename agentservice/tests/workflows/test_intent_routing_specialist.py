from __future__ import annotations

from src.api.routes.chat import post_assistant_request
from src.graph.main_graph import OrchestratorGraph
from src.services.routing_service import RoutingRecordService


def _graph() -> OrchestratorGraph:
    return OrchestratorGraph(routing_service=RoutingRecordService())


def _payload(message: str, request_id: str) -> dict[str, object]:
    return {
        "request_id": request_id,
        "user_id": "u-specialist",
        "session_id": "s-specialist",
        "message": message,
        "metadata": {},
    }


def test_single_destination_dispatches_calendar_for_high_confidence_request() -> None:
    status, body = post_assistant_request(
        _payload("Schedule a calendar meeting tomorrow morning", "req-specialist-calendar"),
        orchestrator_graph=_graph(),
    )

    assert status == 200
    assert body["selected_domain"] == "calendar"
    assert body["fallback_to_companion"] is False


def test_single_destination_dispatches_travel_for_high_confidence_request() -> None:
    status, body = post_assistant_request(
        _payload("Find flight travel options for Seattle", "req-specialist-travel"),
        orchestrator_graph=_graph(),
    )

    assert status == 200
    assert body["selected_domain"] == "travel"
    assert body["fallback_to_companion"] is False


def test_single_destination_dispatches_dining_for_high_confidence_request() -> None:
    status, body = post_assistant_request(
        _payload("Get a dining restaurant reservation for tonight", "req-specialist-dining"),
        orchestrator_graph=_graph(),
    )

    assert status == 200
    assert body["selected_domain"] == "dining"
    assert body["fallback_to_companion"] is False


def test_single_destination_dispatches_news_for_high_confidence_request() -> None:
    status, body = post_assistant_request(
        _payload("Show me today news article headlines", "req-specialist-news"),
        orchestrator_graph=_graph(),
    )

    assert status == 200
    assert body["selected_domain"] == "news"
    assert body["fallback_to_companion"] is False
