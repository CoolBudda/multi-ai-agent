from __future__ import annotations

from src.api.routes.chat import post_assistant_request
from src.graph.main_graph import OrchestratorGraph
from src.services.routing_service import RoutingRecordService


def _graph() -> OrchestratorGraph:
    return OrchestratorGraph(routing_service=RoutingRecordService())


def _payload(message: str, request_id: str = "req-ing-1") -> dict[str, object]:
    return {
        "request_id": request_id,
        "user_id": "u-1",
        "session_id": "s-1",
        "message": message,
        "metadata": {"source": "test"},
    }


def test_orchestrator_ingress_accepts_calendar_request() -> None:
    status, body = post_assistant_request(_payload("Check my calendar availability"), orchestrator_graph=_graph())

    assert status == 200
    assert body["initial_handler"] == "orchestrator"
    assert body["routed_to"] == "calendar"


def test_orchestrator_ingress_accepts_travel_request() -> None:
    status, body = post_assistant_request(_payload("Find flight options"), orchestrator_graph=_graph())

    assert status == 200
    assert body["initial_handler"] == "orchestrator"
    assert body["routed_to"] == "travel"


def test_orchestrator_ingress_accepts_dining_request() -> None:
    status, body = post_assistant_request(_payload("Find a restaurant reservation"), orchestrator_graph=_graph())

    assert status == 200
    assert body["initial_handler"] == "orchestrator"
    assert body["routed_to"] == "dining"


def test_orchestrator_ingress_accepts_news_request() -> None:
    status, body = post_assistant_request(_payload("Show me top news headlines"), orchestrator_graph=_graph())

    assert status == 200
    assert body["initial_handler"] == "orchestrator"
    assert body["routed_to"] == "news"


def test_orchestrator_ingress_regression_companion_fallback_still_accepts() -> None:
    status, body = post_assistant_request(_payload("How are you today?"), orchestrator_graph=_graph())

    assert status == 200
    assert body["initial_handler"] == "orchestrator"
    assert body["routed_to"] == "companion"
