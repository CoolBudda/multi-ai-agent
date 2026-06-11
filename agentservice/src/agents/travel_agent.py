from __future__ import annotations

from src.models.events import MemoryPreferenceLoadedEvent
from src.models.state import UserPreferences
from src.services.memory_service import MemoryService


def load_preferences_at_agent_start(
    memory_service: MemoryService,
    user_id: str,
) -> tuple[UserPreferences, MemoryPreferenceLoadedEvent]:
    defaults: UserPreferences = {
        "preferred_airline": "",
        "seat_preference": "Aisle",
    }
    return memory_service.retrieve_user_preferences_at_agent_start(user_id, defaults=defaults)
