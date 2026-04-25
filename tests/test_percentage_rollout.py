"""Percentage rollout — there is a real bug here. These tests fail on main.

Hints, in order of subtlety:
  - Determinism works (same user always lands the same way for a given flag).
  - Distribution is roughly correct (50% rollout across many users → ~50%).
  - The failure shows up when you compare rollouts across *different flags*.

Two flags both rolled out to 50% should produce *independent* populations —
whether a user is enabled for flag A should not predict whether they're
enabled for flag B. The bug in `app/rules.py` breaks that independence.
"""

from __future__ import annotations

from app import storage


def _seed_two_rollouts(percentage: int) -> None:
    storage._flags["exp-a"] = {
        "key": "exp-a",
        "rules": [{"type": "percentage_rollout", "percentage": percentage, "enabled": True}],
        "default": {"enabled": False},
    }
    storage._flags["exp-b"] = {
        "key": "exp-b",
        "rules": [{"type": "percentage_rollout", "percentage": percentage, "enabled": True}],
        "default": {"enabled": False},
    }


def _enabled(client, flag: str, user: str) -> bool:
    return client.post("/evaluate", json={"flag": flag, "user": user}).json()["enabled"]


def test_rollout_is_deterministic_for_same_user(client):
    _seed_two_rollouts(50)
    first = _enabled(client, "exp-a", "user-42")
    for _ in range(5):
        assert _enabled(client, "exp-a", "user-42") == first


def test_rollout_distributes_roughly_to_percentage(client):
    _seed_two_rollouts(50)
    users = [f"user-{i}" for i in range(1000)]
    enabled = sum(_enabled(client, "exp-a", u) for u in users)
    # Allow ±10% slack for a 50% rollout over 1000 users.
    assert 400 <= enabled <= 600, f"expected ~500, got {enabled}"


def test_rollouts_are_independent_across_flags(client):
    """Two different flags at 50% should produce independent populations."""
    _seed_two_rollouts(50)
    users = [f"user-{i}" for i in range(1000)]

    only_a = 0
    only_b = 0
    for u in users:
        a = _enabled(client, "exp-a", u)
        b = _enabled(client, "exp-b", u)
        if a and not b:
            only_a += 1
        elif b and not a:
            only_b += 1

    # If the buckets were truly independent, ~25% of users land in only_a and
    # ~25% in only_b. We assert a generous floor — 15% — which still fails
    # hard when the buckets are perfectly correlated (i.e. the bug).
    assert only_a > 150, f"expected >150 users enabled for A but not B, got {only_a}"
    assert only_b > 150, f"expected >150 users enabled for B but not A, got {only_b}"
