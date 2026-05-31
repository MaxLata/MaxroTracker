# MaxroTracker

Local-first macro and weight tracking app with a structured data core and a future natural-language input layer.

## Product idea

MaxroTracker is designed to make nutrition logging lower-friction while keeping calculations grounded in structured local data.

The LLM should eventually parse food text into structured candidates. It should not be the source of truth for nutrition values.

## Current scaffold

The first implementation slice is the structured Python core:

- domain models for macros, meal item snapshots, parsed foods, and weight logs
- pure macro calculator functions
- pure 7-day weight average function
- SQLite P0 schema
- public demo seed data only

The intended app stack is Electron + React for the desktop shell, with Python owning business logic and SQLite access.

## Local setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
```

## Initialize a local database

```bash
.venv/bin/python - <<'PY'
from maxro_tracker.db.schema import initialize_database

print(initialize_database())
PY
```

This creates `data/maxro_tracker.sqlite`, which is ignored by git.

## Privacy note

Public repo seed data intentionally avoids real foods, recipes, targets, weight logs, and personal examples. User-specific data should be entered through app flows or stored in private, gitignored local seed files.
