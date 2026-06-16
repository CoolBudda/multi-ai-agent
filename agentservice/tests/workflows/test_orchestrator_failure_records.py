from __future__ import annotations

from src.api.routes.chat import post_assistant_request
from src.graph.main_graph import OrchestratorGraph
from src.services.routing_service import RoutingRecordService


def test_downstream_failure_keeps_orchestrator_traceability_record() -> None:
    service = RoutingRecordService()
    graph = OrchestratorGraph(routing_service=service)

    status, body = post_assistant_request(
        {
            "request_id": "req-record-failure",
            "user_id": "u1",
            "session_id": "s1",
            "message": "Schedule meeting with team",
            "metadata": {},
        },
        orchestrator_graph=graph,
        force_downstream_failure=True,
    )

    record = service.get_record("req-record-failure")
    assert status == 503
    assert body["error_code"] == "orchestrator.dispatch.failed"
    assert record is not None
    assert record["initial_handler"] == "orchestrator"
    assert record["status"] == "failed"
    assert record["failure_code"] == "orchestrator.dispatch.failed"
