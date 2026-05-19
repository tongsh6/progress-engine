"""Reference resolution helpers for .progress objects."""

from __future__ import annotations

from pathlib import Path


def find_referenced_object_file(directory: Path, object_id: str) -> list[Path]:
    """Return files that match the canonical referenced object filename pattern."""

    return sorted(directory.glob(f"{object_id}-*.yaml"))
