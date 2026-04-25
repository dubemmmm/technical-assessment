"""Feature to implement: a `date_range` rule type.

Today the evaluator supports three rule types: `all_users`, `user_ids`, and
`percentage_rollout`. Add a fourth — `date_range` — that matches when the
current time falls inside a window:

    {"type": "date_range",
     "start": "2026-04-01T00:00:00+00:00",   # optional, ISO 8601
     "end":   "2026-05-01T00:00:00+00:00",   # optional, ISO 8601
     "enabled": true,
     "variant": "holiday"}                    # optional

Rules of thumb:
  - If `start` is present and `_now()` < start → rule does NOT match.
  - If `end`   is present and `_now()` > end   → rule does NOT match.
  - If both are missing, the rule always matches.
  - Use `app.rules._now()` (monkeypatched by these tests) — do not call
    `datetime.now(...)` directly inside the rule handler.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app import rules, storage


def _freeze(monkeypatch, when: datetime) -> None:
    monkeypatch.setattr(rules, "_now", lambda: when)


def _seed(rule: dict) -> None:
    storage._flags["promo"] = {
        "key": "promo",
        "rules": [rule],
        "default": {"enabled": False},
    }


def test_date_range_matches_inside_window(client, monkeypatch):
    _seed({
        "type": "date_range",
        "start": "2026-04-01T00:00:00+00:00",
        "end":   "2026-05-01T00:00:00+00:00",
        "enabled": True,
        "variant": "spring",
    })
    _freeze(monkeypatch, datetime(2026, 4, 15, tzinfo=timezone.utc))

    body = client.post("/evaluate", json={"flag": "promo", "user": "alice"}).json()
    assert body["enabled"] is True
    assert body["variant"] == "spring"
    assert body["reason"] == "rule:date_range"


def test_date_range_does_not_match_before_start(client, monkeypatch):
    _seed({
        "type": "date_range",
        "start": "2026-04-01T00:00:00+00:00",
        "end":   "2026-05-01T00:00:00+00:00",
        "enabled": True,
    })
    _freeze(monkeypatch, datetime(2026, 3, 30, tzinfo=timezone.utc))

    body = client.post("/evaluate", json={"flag": "promo", "user": "alice"}).json()
    assert body["enabled"] is False
    assert body["reason"] == "default"


def test_date_range_does_not_match_after_end(client, monkeypatch):
    _seed({
        "type": "date_range",
        "start": "2026-04-01T00:00:00+00:00",
        "end":   "2026-05-01T00:00:00+00:00",
        "enabled": True,
    })
    _freeze(monkeypatch, datetime(2026, 5, 2, tzinfo=timezone.utc))

    body = client.post("/evaluate", json={"flag": "promo", "user": "alice"}).json()
    assert body["enabled"] is False


def test_date_range_open_ended_end(client, monkeypatch):
    """Only `start` given — rule matches any time after start."""
    _seed({"type": "date_range", "start": "2026-04-01T00:00:00+00:00", "enabled": True})
    _freeze(monkeypatch, datetime(2030, 1, 1, tzinfo=timezone.utc))

    body = client.post("/evaluate", json={"flag": "promo", "user": "alice"}).json()
    assert body["enabled"] is True


def test_date_range_open_ended_start(client, monkeypatch):
    """Only `end` given — rule matches any time up to end."""
    _seed({"type": "date_range", "end": "2026-05-01T00:00:00+00:00", "enabled": True})
    _freeze(monkeypatch, datetime(1999, 1, 1, tzinfo=timezone.utc))

    body = client.post("/evaluate", json={"flag": "promo", "user": "alice"}).json()
    assert body["enabled"] is True
