from __future__ import annotations

from src.api.routes.chat import post_assistant_request
from src.graph.main_graph import OrchestratorGraph
from src.services.routing_service import RoutingRecordService


def _graph() -> OrchestratorGraph:
    return OrchestratorGraph(routing_service=RoutingRecordService())


def _payload(request_id: str, message: str) -> dict[str, object]:
    return {
        "request_id": request_id,
        "user_id": "u-tie",
        "session_id": "s-tie",
        "message": message,
        "metadata": {},
    }


def test_replayed_equivalent_requests_produce_identical_routing_decision() -> None:
    graph = _graph()
    message = "Schedule a meeting and book a flight"

    status_1, body_1 = post_assistant_request(
        _payload("req-tie-replay-1", message),
        orchestrator_graph=graph,
    )
    status_2, body_2 = post_assistant_request(
        _payload("req-tie-replay-2", message),
        orchestrator_graph=graph,
    )

    assert status_1 == 200
    assert status_2 == 200
    assert body_1["selected_domain"] == body_2["selected_domain"]
    assert body_1["tie_detected"] == body_2["tie_detected"]
    assert body_1["rationale"]["reason_code"] == body_2["rationale"]["reason_code"]
    assert body_1["rationale"]["tie_break_winner"] == body_2["rationale"]["tie_break_winner"]


def test_tied_specialist_candidates_resolve_with_fixed_precedence() -> None:
    graph = _graph()

    status, body = post_assistant_request(
        _payload("req-tie-precedence", "Schedule flight"),
        orchestrator_graph=graph,
    )

    assert status == 200
    assert body["tie_detected"] is True
    assert body["selected_domain"] == "calendar"
    assert body["rationale"]["tie_break_winner"] == "calendar"
    assert body["rationale"]["reason_code"] == "tie_break_selected"


def test_top_candidates_payload_order_is_deterministic_across_replays() -> None:
    graph = _graph()
    message = "schedule travel dining"

    status_1, body_1 = post_assistant_request(
        _payload("req-tie-order-1", message),
        orchestrator_graph=graph,
    )
    status_2, body_2 = post_assistant_request(
        _payload("req-tie-order-2", message),
        orchestrator_graph=graph,
    )

    assert status_1 == 200
    assert status_2 == 200
    assert body_1["rationale"]["top_candidates"] == body_2["rationale"]["top_candidates"]
