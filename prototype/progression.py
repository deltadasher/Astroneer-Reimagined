"""Pure mission-state reference. No Astroneer/Unreal integration or game I/O.

Events represent verified semantic actions, not raw game callbacks. An adapter
must check site identity, planet, inventory, crafting, and authoritative game
state before supplying them. This module intentionally cannot grant items.
"""
from dataclasses import dataclass, replace
import json
from pathlib import Path

CONTENT_PATH = Path(__file__).resolve().parents[1] / "content" / "resonance.json"
CONTENT = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
MISSIONS = tuple(m["id"] for m in CONTENT["missions"])
EVENTS = {m["event"]: m["id"] for m in CONTENT["missions"] if "event" in m}
ALLOWED_EVENTS = frozenset(EVENTS) | {"core_awakened_observed"}


@dataclass(frozen=True)
class State:
    completed: tuple[str, ...] = ()
    core_awakened: bool = False

    def __post_init__(self):
        if type(self.core_awakened) is not bool:
            raise ValueError("core_awakened must be a boolean")
        if not isinstance(self.completed, tuple) or self.completed != MISSIONS[:len(self.completed)]:
            raise ValueError("completed missions must be an ordered prefix")
        if "awaken" in self.completed and not self.core_awakened:
            raise ValueError("awaken mission requires an observed awakened core")


def _reconcile(state: State) -> State:
    if state.core_awakened and state.completed == MISSIONS[:4]:
        return replace(state, completed=MISSIONS[:5])
    return state


def apply_event(state: State, event: str) -> State:
    """Apply one authoritative semantic event; repeats and premature actions are no-ops.

    Core observation is latched even before discovery. A runtime adapter should
    query current core state on initialization/load as well as observe changes.
    Non-core action events are NOT retroactive; existing saves replay site actions.
    """
    if event not in ALLOWED_EVENTS:
        raise ValueError(f"Unknown semantic event: {event}")
    state = _reconcile(state)
    if event == "core_awakened_observed":
        return _reconcile(replace(state, core_awakened=True))
    if len(state.completed) < len(MISSIONS) and EVENTS[event] == MISSIONS[len(state.completed)]:
        return _reconcile(replace(state, completed=state.completed + (EVENTS[event],)))
    return state


def active_mission(state: State) -> str | None:
    state = _reconcile(state)
    return MISSIONS[len(state.completed)] if len(state.completed) < len(MISSIONS) else None


def dumps(state: State) -> str:
    """Reference serialization, NOT an Astroneer save format."""
    return json.dumps({"schema_version": 1, "completed": list(state.completed), "core_awakened": state.core_awakened}, sort_keys=True)


def loads(payload: str) -> State:
    data = json.loads(payload)
    if not isinstance(data, dict) or set(data) != {"schema_version", "completed", "core_awakened"}:
        raise ValueError("Invalid state envelope")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("Unsupported state version; explicit migration required")
    if not isinstance(data["completed"], list):
        raise ValueError("completed must be a list")
    return _reconcile(State(tuple(data["completed"]), data["core_awakened"]))
