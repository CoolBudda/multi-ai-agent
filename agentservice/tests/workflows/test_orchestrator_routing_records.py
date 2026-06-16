from __future__ import annotations

from src.api.routes.chat import post_assistant_request
from src.graph.main_graph import OrchestratorGraph
from src.services.routing_service import RoutingRecordService


def test_successful_ingress_persists_orchestrator_first_routing_record() -> None:
    service = RoutingRecordService()
    graph = OrchestratorGraph(routing_service=service)

    status, body = post_assistant_request(
        {
            "request_id": "req-record-success",
            "user_id": "u1",
            "session_id": "s1",
            "message": "Find flight options",
            "metadata": {},
        },
        orchestrator_graph=graph,
    )

    record = service.get_record("req-record-success")
    assert status == 200
    assert body["initial_handler"] == "orchestrator"
    assert record is not None
    assert record["initial_handler"] == "orchestrator"
    assert record["status"] == "succeeded"
    assert record["routed_to"] == "travel"
