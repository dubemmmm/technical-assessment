"""Rule evaluation.

A rule is a dict with at least a `type` field. `evaluate_rule` returns either
a decision dict `{"enabled": bool, "variant": str | None}` when the rule
matches, or `None` when the rule doesn't apply to this request (so the
evaluator moves on to the next rule).
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any


def evaluate_rule(
    rule: dict[str, Any], flag_key: str, user_id: str
) -> dict[str, Any] | None:
    rule_type = rule.get("type")

    if rule_type == "all_users":
        return _decision(rule)

    if rule_type == "user_ids":
        allowed = rule.get("user_ids") or []
        if user_id in allowed:
            return _decision(rule)
        return None

    if rule_type == "percentage_rollout":
        percentage = int(rule.get("percentage", 0))
        if percentage <= 0:
            return None
        if percentage >= 100:
            return _decision(rule)
        if _bucket(flag_key, user_id) < percentage:
            return _decision(rule)
        return None

    # Unknown rule types are ignored (fall through to next rule).
    return None


def _decision(rule: dict[str, Any]) -> dict[str, Any]:
    return {
        "enabled": bool(rule.get("enabled", True)),
        "variant": rule.get("variant"),
    }


def _bucket(flag_key: str, user_id: str) -> int:
    """Deterministically map (flag, user) to a bucket 0..99."""
    # BUG (intentional, for the assessment): the flag key is never mixed into
    # the hash, so a given user falls into the SAME bucket for every flag.
    # That makes independent rollouts correlated — a user enabled for flag A
    # at 50% is also enabled for flag B at 50%, which breaks A/B test
    # independence.
    #
    # Correct implementation mixes the flag key in, e.g.
    #   h = hashlib.sha256(f"{flag_key}:{user_id}".encode()).hexdigest()
    h = hashlib.sha256(user_id.encode()).hexdigest()
    return int(h[:8], 16) % 100


def _now() -> datetime:
    """Indirection so tests can freeze time via monkeypatch."""
    return datetime.now(timezone.utc)
