from __future__ import annotations

from src.services.routing_service import RoutingRecordService


def test_routing_record_lifecycle_create_success_failure_rejected() -> None:
    service = RoutingRecordService(id_factory=lambda: "record-1")

    created, created_event = service.create_open_record(
        request_id="req-routing-1",
        routed_to="news",
        user_message="accepted",
    )
    assert created["record_id"] == "record-1"
    assert created_event["event_name"] == "orchestrator.routing_record.created.failed"

    succeeded, succeeded_event = service.mark_succeeded(
        request_id="req-routing-1",
        user_message="done",
    )
    assert succeeded["status"] == "succeeded"
    assert succeeded_event["event_name"] == "orchestrator.routing_record.updated.succeeded"

    failed, failed_event = service.mark_failed(
        request_id="req-routing-1",
        failure_code="failed.code",
        user_message="failed",
    )
    assert failed["status"] == "failed"
    assert failed["failure_code"] == "failed.code"
    assert failed_event["event_name"] == "orchestrator.routing_record.updated.failed"

    rejected, rejected_event = service.mark_rejected(
        request_id="req-routing-1",
        rejection_code="direct_specialist_access_denied",
        user_message="rejected",
    )
    assert rejected["status"] == "rejected"
    assert rejected["rejection_code"] == "direct_specialist_access_denied"
    assert rejected_event["event_name"] == "orchestrator.routing_record.updated.rejected"
