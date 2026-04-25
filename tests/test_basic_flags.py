"""Baseline — these should already pass. They document how a correct
evaluator behaves and the shape of the API response.
"""


def test_unknown_flag_returns_disabled(client):
    response = client.post("/evaluate", json={"flag": "no-such-flag", "user": "alice"})
    assert response.status_code == 200
    body = response.json()
    assert body["enabled"] is False
    assert body["reason"] == "unknown_flag"


def test_user_ids_rule_matches_listed_user(client):
    response = client.post("/evaluate", json={"flag": "new-dashboard", "user": "alice"})
    body = response.json()
    assert body["enabled"] is True
    assert body["reason"] == "rule:user_ids"


def test_all_users_rule_enables_everyone(client):
    for user in ["alice", "bob", "carol", "dave"]:
        response = client.post("/evaluate", json={"flag": "dark-mode", "user": user})
        body = response.json()
        assert body["enabled"] is True, f"{user} should be enabled"
        assert body["variant"] == "on"


def test_variant_is_returned_when_rule_sets_it(client):
    response = client.post("/evaluate", json={"flag": "beta-checkout", "user": "carol"})
    body = response.json()
    assert body["enabled"] is True
    assert body["variant"] == "v2"


def test_default_fires_when_no_rule_matches(client):
    response = client.post("/evaluate", json={"flag": "beta-checkout", "user": "zoe"})
    body = response.json()
    assert body["enabled"] is False
    assert body["reason"] == "default"
