"""Read-only Change Event listing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class EventListError(Exception):
    """Raised when change events cannot be loaded as minimal valid objects."""


def load_events(root: Path) -> list[dict[str, Any]]:
    events_dir = root / ".progress" / "events"
    if not events_dir.is_dir():
        raise EventListError(f"missing events directory: {events_dir}")

    return [_load_event(path) for path in sorted(events_dir.glob("*.yaml"))]


def render_event_list(events: list[dict[str, Any]]) -> str:
    lines = ["Change events:"]
    if not events:
        lines.append("- none")
        return "\n".join(lines)

    for event in events:
        human_review = str(event["requires_human_review"]).lower()
        lines.append(
            f"- {event['id']} [{event['severity']}] {event['type']} "
            f"({len(event['affected_dimensions'])} dimensions; human_review={human_review})"
        )

    return "\n".join(lines)


def _load_event(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as event_file:
            data = yaml.safe_load(event_file)
    except yaml.YAMLError as exc:
        raise EventListError(f"change event YAML parse failed for {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise EventListError(f"change event file must be a YAML mapping: {path}")

    event = data.get("change_event")
    if not isinstance(event, dict):
        raise EventListError(f"change event file is missing root mapping 'change_event': {path}")

    event_id = event.get("id")
    for key in ("id", "type", "severity", "summary"):
        if not isinstance(event.get(key), str) or not event[key]:
            raise EventListError(
                f"change event {event_id or path.name} is missing string field: {key}"
            )

    dimensions = event.get("affected_dimensions")
    if not isinstance(dimensions, list) or not all(
        isinstance(dimension, str) and dimension for dimension in dimensions
    ):
        raise EventListError(
            f"change event {event_id or path.name} is missing string list field: "
            "affected_dimensions"
        )

    if not isinstance(event.get("requires_human_review"), bool):
        raise EventListError(
            f"change event {event_id or path.name} is missing boolean field: "
            "requires_human_review"
        )

    if not path.name.startswith(event["id"]):
        raise EventListError(
            f"change event filename must start with id {event['id']}: {path.name}"
        )

    return event
