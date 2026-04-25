"""In-memory flag storage.

Flags are seeded at import time. The data model is deliberately small — a flag
has a key, an optional default variant, and an ordered list of rules. The first
rule that matches wins.
"""

from __future__ import annotations

from typing import Any


# Seed data — keep this small and readable. Tests reset the store between runs.
_SEED: dict[str, dict[str, Any]] = {
    "new-dashboard": {
        "key": "new-dashboard",
        "rules": [
            {"type": "user_ids", "user_ids": ["alice", "bob"], "enabled": True},
            {"type": "percentage_rollout", "percentage": 50, "enabled": True},
        ],
        "default": {"enabled": False},
    },
    "dark-mode": {
        "key": "dark-mode",
        "rules": [
            {"type": "all_users", "enabled": True, "variant": "on"},
        ],
        "default": {"enabled": False},
    },
    "beta-checkout": {
        "key": "beta-checkout",
        "rules": [
            {"type": "user_ids", "user_ids": ["carol"], "enabled": True, "variant": "v2"},
        ],
        "default": {"enabled": False},
    },
}


_flags: dict[str, dict[str, Any]] = {}


def reset() -> None:
    """Restore the seed state. Called by the test fixture between tests."""
    global _flags
    _flags = {key: _clone(value) for key, value in _SEED.items()}


def get_flag(key: str) -> dict[str, Any] | None:
    return _flags.get(key)


def all_flags() -> list[dict[str, Any]]:
    return list(_flags.values())


def _clone(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _clone(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_clone(v) for v in value]
    return value


reset()
