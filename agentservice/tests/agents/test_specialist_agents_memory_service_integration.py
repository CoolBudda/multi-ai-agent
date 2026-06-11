from __future__ import annotations

import ast
from pathlib import Path

import pytest


SPECIALIST_AGENT_FILES = [
    "calendar_agent.py",
    "travel_agent.py",
    "dining_agent.py",
    "news_agent.py",
]


def _agent_file_path(file_name: str) -> Path:
    return Path(__file__).resolve().parents[2] / "src" / "agents" / file_name


def _parse_agent_module(file_name: str) -> ast.Module:
    path = _agent_file_path(file_name)
    source = path.read_text(encoding="utf-8")
    return ast.parse(source)


def _contains_memory_service_import(module: ast.Module) -> bool:
    for node in ast.walk(module):
        if isinstance(node, ast.ImportFrom):
            if node.module == "src.services.memory_service":
                return True
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "src.services.memory_service":
                    return True
    return False


def _contains_agent_start_memory_retrieval_call(module: ast.Module) -> bool:
    """
    Compliance signal: specialist agent code must call
    MemoryService.retrieve_user_preferences_at_agent_start via service layer.
    """
    for node in ast.walk(module):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "retrieve_user_preferences_at_agent_start":
                return True
    return False


@pytest.mark.parametrize("agent_file", SPECIALIST_AGENT_FILES)
def test_specialist_agent_imports_memory_service_layer(agent_file: str) -> None:
    module = _parse_agent_module(agent_file)

    assert _contains_memory_service_import(module), (
        f"{agent_file} does not import src.services.memory_service. "
        "Specialist agents must access memory via the service layer."
    )


@pytest.mark.parametrize("agent_file", SPECIALIST_AGENT_FILES)
def test_specialist_agent_calls_memory_retrieval_at_agent_start(agent_file: str) -> None:
    module = _parse_agent_module(agent_file)

    assert _contains_agent_start_memory_retrieval_call(module), (
        f"{agent_file} does not call retrieve_user_preferences_at_agent_start. "
        "Specialist agents must load preferences at agent start through MemoryService."
    )
