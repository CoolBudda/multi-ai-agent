from __future__ import annotations

from src.api.routes.chat import post_assistant_request
from src.graph.main_graph import OrchestratorGraph
from src.services.routing_service import RoutingRecordService


def _graph() -> OrchestratorGraph:
    return OrchestratorGraph(routing_service=RoutingRecordService())


def test_malformed_payload_returns_400_and_no_routing_record() -> None:
    service = RoutingRecordService()
    graph = OrchestratorGraph(routing_service=service)

    status, body = post_assistant_request({}, orchestrator_graph=graph)

    assert status == 400
    assert body["error_code"] == "malformed_request"
    assert service.get_record(body["request_id"]) is None


def test_incomplete_payload_returns_422_and_no_specialist_execution() -> None:
    service = RoutingRecordService()
    graph = OrchestratorGraph(routing_service=service)

    status, body = post_assistant_request(
        {
            "request_id": "req-incomplete",
            "user_id": "u-1",
            "session_id": "s-1",
            "message": "   ",
        },
        orchestrator_graph=graph,
    )

    assert status == 422
    assert body["error_code"] == "incomplete_request"
    assert service.get_record("req-incomplete") is None
