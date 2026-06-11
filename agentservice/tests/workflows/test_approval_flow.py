from __future__ import annotations

from src.api.routes.chat import deliver_approval_request_to_frontend
from src.services.approval_service import ApprovalService, ApprovalServiceUnavailableError


def _payload() -> dict[str, object]:
    return {
        "action_type": "reserve_table",
        "domain": "dining",
        "summary": "Reserve table for 2 at 19:00",
        "payload": {"party_size": 2, "time": "19:00"},
    }


def test_workflow_write_action_blocked_until_approval_received() -> None:
    service = ApprovalService(id_factory=lambda: "req-w1")
    request, _ = service.create_approval_request(_payload())

    called = {"value": False}

    def _write_action() -> str:
        called["value"] = True
        return "done"

    rejected_result, _ = service.await_user_decision(request["request_id"], decision="rejected")
    service.execute_or_cancel_write_action(request, rejected_result, _write_action)

    assert called["value"] is False


def test_workflow_approval_request_is_delivered_to_frontend() -> None:
    service = ApprovalService(id_factory=lambda: "req-w2")

    _, approval_required_event = service.create_approval_request(_payload())
    delivery = deliver_approval_request_to_frontend(approval_required_event)

    assert delivery["type"] == "approval_request"
    assert delivery["event_name"] == "approval.required"


def test_workflow_approved_decision_allows_write_execution() -> None:
    service = ApprovalService(id_factory=lambda: "req-w3")
    request, _ = service.create_approval_request(_payload())
    approved_result, _ = service.await_user_decision(request["request_id"], decision="approved")

    outcome = service.execute_or_cancel_write_action(request, approved_result, lambda: "booked")

    assert outcome["status"] == "executed"
    assert outcome["result"] == "booked"


def test_workflow_rejected_decision_returns_cancellation_confirmation() -> None:
    service = ApprovalService(id_factory=lambda: "req-w4")
    request, _ = service.create_approval_request(_payload())
    rejected_result, _ = service.await_user_decision(request["request_id"], decision="rejected")

    outcome = service.execute_or_cancel_write_action(request, rejected_result, lambda: "booked")

    assert outcome["status"] == "cancelled"
    assert outcome["message"] == "Action cancelled. No changes were made."


def test_workflow_rejected_decision_emits_domain_action_rejected_event() -> None:
    service = ApprovalService(id_factory=lambda: "req-w5")
    request, _ = service.create_approval_request(_payload())
    rejected_result, _ = service.await_user_decision(request["request_id"], decision="rejected")

    outcome = service.execute_or_cancel_write_action(request, rejected_result, lambda: "booked")

    assert outcome["rejection_event"]["event_name"] == "dining.reserve_table.rejected"


def test_workflow_service_unavailable_prevents_write_execution() -> None:
    service = ApprovalService(id_factory=lambda: "req-w6")
    request, _ = service.create_approval_request(_payload())

    called = {"value": False}

    def _write_action() -> str:
        called["value"] = True
        return "booked"

    try:
        service.await_user_decision(request["request_id"], decision="approved", service_available=False)
        assert False, "expected ApprovalServiceUnavailableError"
    except ApprovalServiceUnavailableError:
        pass

    assert called["value"] is False


def test_workflow_expired_session_treated_as_rejected() -> None:
    service = ApprovalService(id_factory=lambda: "req-w7")
    request, _ = service.create_approval_request(_payload())

    result, _ = service.await_user_decision(
        request["request_id"],
        decision=None,
        session_expired=True,
    )

    assert result["status"] == "rejected"


def test_acceptance_user_receives_clear_cancellation_on_rejection() -> None:
    service = ApprovalService(id_factory=lambda: "req-w8")
    request, _ = service.create_approval_request(_payload())
    rejected_result, _ = service.await_user_decision(request["request_id"], decision="rejected")

    outcome = service.execute_or_cancel_write_action(request, rejected_result, lambda: "booked")

    assert outcome["message"] == "Action cancelled. No changes were made."
