"""Load and access JSON schemas from the knowledge base."""
import json
from pathlib import Path


def load_safe_ranges(path: Path | str) -> dict:
    """Load safe-ranges.json and return the parsed data."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_schema(path: Path | str) -> dict:
    """Load any JSON schema file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_hard_limit(ranges: dict, parameter: str, limit_type: str) -> float | None:
    """Get a hard limit value. limit_type is 'min' or 'max'."""
    param = ranges.get("parameters", {}).get(parameter, {})
    return param.get("hard_limits", {}).get(limit_type)


def find_schemas_dir() -> Path | None:
    """Walk up from CWD to find knowledge/schemas/."""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        candidate = parent / "knowledge" / "schemas"
        if candidate.is_dir():
            return candidate
    return None
