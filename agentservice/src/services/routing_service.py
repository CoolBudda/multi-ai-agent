from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable
from uuid import uuid4

from src.models.events import build_routing_record_lifecycle_event, now_iso
from src.models.state import RoutingRecord, SupportedDomain


@dataclass(slots=True)
class RoutingRecordService:
    id_factory: Callable[[], str] = field(default=lambda: str(uuid4()))
    _records: dict[str, RoutingRecord] = field(default_factory=dict)

    def create_open_record(
        self,
        *,
        request_id: str,
        routed_to: SupportedDomain,
        user_message: str,
    ) -> tuple[RoutingRecord, dict[str, object]]:
        timestamp = now_iso()
        record: RoutingRecord = {
            "record_id": self.id_factory(),
            "request_id": request_id,
            "entry_path": "orchestrator",
            "initial_handler": "orchestrator",
            "routed_to": routed_to,
            "status": "failed",
            "failure_code": None,
            "rejection_code": None,
            "user_message": user_message,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        self._records[request_id] = record
        event = build_routing_record_lifecycle_event(record, action="created", status="failed")
        return record, event

    def mark_succeeded(
        self,
        *,
        request_id: str,
        user_message: str,
    ) -> tuple[RoutingRecord, dict[str, object]]:
        record = self._require_record(request_id)
        record["status"] = "succeeded"
        record["user_message"] = user_message
        record["failure_code"] = None
        record["rejection_code"] = None
        record["updated_at"] = now_iso()
        event = build_routing_record_lifecycle_event(record, action="updated", status="succeeded")
        return record, event

    def mark_failed(
        self,
        *,
        request_id: str,
        failure_code: str,
        user_message: str,
    ) -> tuple[RoutingRecord, dict[str, object]]:
        record = self._require_record(request_id)
        record["status"] = "failed"
        record["failure_code"] = failure_code
        record["rejection_code"] = None
        record["user_message"] = user_message
        record["updated_at"] = now_iso()
        event = build_routing_record_lifecycle_event(record, action="updated", status="failed")
        return record, event

    def mark_rejected(
        self,
        *,
        request_id: str,
        rejection_code: str,
        user_message: str,
    ) -> tuple[RoutingRecord, dict[str, object]]:
        record = self._require_record(request_id)
        record["status"] = "rejected"
        record["rejection_code"] = rejection_code
        record["failure_code"] = None
        record["user_message"] = user_message
        record["updated_at"] = now_iso()
        event = build_routing_record_lifecycle_event(record, action="updated", status="rejected")
        return record, event

    def get_record(self, request_id: str) -> RoutingRecord | None:
        record = self._records.get(request_id)
        if record is None:
            return None
        return dict(record)

    def _require_record(self, request_id: str) -> RoutingRecord:
        if request_id not in self._records:
            raise KeyError(f"No routing record for request_id={request_id}")
        return self._records[request_id]
