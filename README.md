# flag-eval — technical assessment

A small FastAPI service that evaluates feature flags. You'll debug one existing
rule and add one new rule type.

## Setup

Dependencies are pre-installed in your sandbox. Just run:

```bash
pytest
```

(If you ever need to reinstall: `pip install -e ".[dev]"`. No venv — the
sandbox is already isolated.)

## The repo

```
app/
  main.py       FastAPI routes: /health, /flags, /evaluate
  flags.py      Evaluator — walks a flag's rules and returns the first match
  rules.py      Rule handlers: all_users, user_ids, percentage_rollout
  storage.py    In-memory flag store, reset between tests
tests/
  test_warmup.py                One-line warm-up
  test_basic_flags.py           Baseline, already passes
  test_percentage_rollout.py    A bug lives here
  test_date_range_rule.py       A rule type lives here (you build it)
```

## Your tasks

**1. Warmup.** `tests/test_warmup.py` fails. Fix the one string in `app/main.py`
that makes it pass. This is just to confirm your tooling works.

**2. Debug the percentage rollout.** `tests/test_percentage_rollout.py` has
three tests — one fails. It's a real bug in `app/rules.py`. Find it, fix it,
and make sure the other rollout tests still pass.

**3. Add a `date_range` rule.** `tests/test_date_range_rule.py` is all failing.
Implement the new rule type in `app/rules.py`. The test file documents the
contract.

Run `pytest` whenever you want to see where you stand. When everything is
green, hit Submit.
