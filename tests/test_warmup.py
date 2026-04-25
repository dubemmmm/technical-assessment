"""Warmup — proves your tooling works.

This test fails on a fresh checkout. Find the one place in `app/main.py` that
returns the wrong status string and make it match. One-line change.
"""


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
