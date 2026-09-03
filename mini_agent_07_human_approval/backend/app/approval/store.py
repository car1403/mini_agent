from copy import deepcopy
from typing import Any


RUNS: dict[str, dict[str, Any]] = {}
PROCESSED_CALLS: set[str] = set()
AUDIT_LOG: list[dict[str, Any]] = []


def save_run(state: dict[str, Any]) -> None:
    RUNS[state["run_id"]] = deepcopy(state)


def get_run(run_id: str) -> dict[str, Any] | None:
    state = RUNS.get(run_id)
    return deepcopy(state) if state else None


def add_audit(event: dict[str, Any]) -> None:
    AUDIT_LOG.append(deepcopy(event))


def list_audit(run_id: str | None = None) -> list[dict[str, Any]]:
    events = AUDIT_LOG if run_id is None else [event for event in AUDIT_LOG if event["run_id"] == run_id]
    return deepcopy(events)
