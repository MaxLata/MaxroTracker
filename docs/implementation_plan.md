# MaxroTracker Implementation Plan

## Stack Decision

MaxroTracker should be a local Electron app with a Python core.

- Electron + React/TypeScript: desktop shell and rendering layer.
- Python: domain logic, SQLite access, parsers, nutrition resolution, and future LLM providers.
- SQLite: local structured source of truth.
- pytest: pure logic and repository tests.

This keeps JavaScript close to the UI while preserving Python for the parts where correctness matters most.

## Milestone 1: Structured Core

Status: complete

Deliver:

1. Python domain models for macros, targets, meal item snapshots, parsed food items, and weight logs.
2. Pure macro functions for totals, remaining macros, percentages, and adherence status.
3. Pure weight trend function for a 7-day average.
4. SQLite P0 migration files.
5. Public demo seed data only. Real foods and targets stay local/private.

## Milestone 2: Local Data Access

Status: complete

Deliver:

1. Repository layer for daily targets, food items, meal entries, meal item snapshots, weight logs, and notes.
2. Database initialization command for `./data/maxro_tracker.sqlite`.
3. Tests for create/read/update/delete behavior and snapshot preservation.
4. Application service for manual macro logging, known-food logging, weight logging, and daily summaries.

## Milestone 3: Minimal Desktop UI

Status: next

Deliver:

1. Electron shell.
2. Today dashboard.
3. Manual macro entry form.
4. Known-food logging form.
5. Weight logging form.

## Milestone 4: Natural Language Input

Deliver:

1. Rule-based parser for manual macro commands.
2. Rule-based parser for weight commands.
3. LLM provider interface.
4. Mock provider for tests.
5. Nutrition resolver that never invents macros for unknown foods.
