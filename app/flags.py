"""Evaluator: walk a flag's rules in order, return the first decision."""

from __future__ import annotations

from typing import Any

from app import storage
from app.rules import evaluate_rule


def evaluate(flag_key: str, user_id: str) -> dict[str, Any]:
    flag = storage.get_flag(flag_key)
    if flag is None:
        return {"enabled": False, "variant": None, "reason": "unknown_flag"}

    for rule in flag.get("rules", []):
        decision = evaluate_rule(rule, flag_key, user_id)
        if decision is not None:
            return {**decision, "reason": f"rule:{rule.get('type')}"}

    default = flag.get("default") or {}
    return {
        "enabled": bool(default.get("enabled", False)),
        "variant": default.get("variant"),
        "reason": "default",
    }
