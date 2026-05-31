from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from contextlib import contextmanager
from datetime import date
from pathlib import Path

from maxro_tracker.db.schema import DEFAULT_DB_PATH
from maxro_tracker.domain.models import (
    DailyNote,
    FoodItem,
    MacroTarget,
    MealEntry,
    MealEntryItem,
    WeightLog,
)


@contextmanager
def open_database(db_path: Path = DEFAULT_DB_PATH):
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def create_daily_target(connection: sqlite3.Connection, target: MacroTarget) -> MacroTarget:
    start_date = target.start_date or date.today()
    cursor = connection.execute(
        """
        INSERT INTO daily_targets (
          start_date,
          end_date,
          calories,
          protein_g,
          carbs_g,
          fat_g,
          fiber_g,
          goal_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            start_date.isoformat(),
            target.end_date.isoformat() if target.end_date else None,
            target.calories,
            target.protein_g,
            target.carbs_g,
            target.fat_g,
            target.fiber_g,
            target.goal_name,
        ),
    )
    return get_daily_target(connection, cursor.lastrowid)


def get_daily_target(connection: sqlite3.Connection, target_id: int) -> MacroTarget:
    row = connection.execute(
        "SELECT * FROM daily_targets WHERE id = ?",
        (target_id,),
    ).fetchone()
    if row is None:
        raise LookupError(f"daily target not found: {target_id}")
    return _row_to_macro_target(row)


def get_active_daily_target(connection: sqlite3.Connection) -> MacroTarget | None:
    row = connection.execute(
        """
        SELECT *
        FROM daily_targets
        WHERE end_date IS NULL
        ORDER BY start_date DESC, id DESC
        LIMIT 1
        """
    ).fetchone()
    return _row_to_macro_target(row) if row else None


def create_food_item(connection: sqlite3.Connection, food: FoodItem) -> FoodItem:
    cursor = connection.execute(
        """
        INSERT INTO food_items (
          name,
          brand,
          default_unit,
          calories_per_unit,
          protein_per_unit,
          carbs_per_unit,
          fat_per_unit,
          fiber_per_unit,
          source,
          confidence
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            food.name,
            food.brand,
            food.default_unit,
            food.calories,
            food.protein_g,
            food.carbs_g,
            food.fat_g,
            food.fiber_g,
            food.source,
            food.confidence,
        ),
    )
    return get_food_item(connection, cursor.lastrowid)


def get_food_item(connection: sqlite3.Connection, food_item_id: int) -> FoodItem:
    row = connection.execute(
        "SELECT * FROM food_items WHERE id = ?",
        (food_item_id,),
    ).fetchone()
    if row is None:
        raise LookupError(f"food item not found: {food_item_id}")
    return _row_to_food_item(row)


def add_food_alias(connection: sqlite3.Connection, food_item_id: int, alias: str) -> None:
    connection.execute(
        "INSERT OR IGNORE INTO food_aliases (food_item_id, alias) VALUES (?, ?)",
        (food_item_id, _normalize_lookup(alias)),
    )


def find_food_item(connection: sqlite3.Connection, lookup: str) -> FoodItem | None:
    normalized_lookup = _normalize_lookup(lookup)
    row = connection.execute(
        """
        SELECT *
        FROM food_items
        WHERE LOWER(name) = ?
        LIMIT 1
        """,
        (normalized_lookup,),
    ).fetchone()
    if row:
        return _row_to_food_item(row)

    row = connection.execute(
        """
        SELECT food_items.*
        FROM food_aliases
        JOIN food_items ON food_items.id = food_aliases.food_item_id
        WHERE food_aliases.alias = ?
        LIMIT 1
        """,
        (normalized_lookup,),
    ).fetchone()
    return _row_to_food_item(row) if row else None


def create_meal_entry(
    connection: sqlite3.Connection,
    entry: MealEntry,
    items: Iterable[MealEntryItem],
) -> MealEntry:
    cursor = connection.execute(
        """
        INSERT INTO meal_entries (date, time, raw_text, meal_name)
        VALUES (?, ?, ?, ?)
        """,
        (
            entry.log_date.isoformat(),
            entry.log_time,
            entry.raw_text,
            entry.meal_name,
        ),
    )
    meal_entry_id = cursor.lastrowid
    for item in items:
        add_meal_entry_item(connection, meal_entry_id, item)
    return get_meal_entry(connection, meal_entry_id)


def add_meal_entry_item(
    connection: sqlite3.Connection,
    meal_entry_id: int,
    item: MealEntryItem,
) -> MealEntryItem:
    cursor = connection.execute(
        """
        INSERT INTO meal_entry_items (
          meal_entry_id,
          food_item_id,
          recipe_id,
          name_snapshot,
          quantity,
          unit,
          calories,
          protein_g,
          carbs_g,
          fat_g,
          fiber_g,
          source,
          confidence,
          user_overridden
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            meal_entry_id,
            item.food_item_id,
            item.recipe_id,
            item.name_snapshot,
            item.quantity,
            item.unit,
            item.calories,
            item.protein_g,
            item.carbs_g,
            item.fat_g,
            item.fiber_g,
            item.source,
            item.confidence,
            int(item.user_overridden),
        ),
    )
    return get_meal_entry_item(connection, cursor.lastrowid)


def get_meal_entry(connection: sqlite3.Connection, meal_entry_id: int) -> MealEntry:
    row = connection.execute(
        "SELECT * FROM meal_entries WHERE id = ?",
        (meal_entry_id,),
    ).fetchone()
    if row is None:
        raise LookupError(f"meal entry not found: {meal_entry_id}")
    items = tuple(list_meal_entry_items(connection, meal_entry_id))
    return _row_to_meal_entry(row, items)


def list_meal_entries_for_date(
    connection: sqlite3.Connection,
    log_date: date,
) -> list[MealEntry]:
    rows = connection.execute(
        """
        SELECT *
        FROM meal_entries
        WHERE date = ?
        ORDER BY COALESCE(time, ''), id
        """,
        (log_date.isoformat(),),
    ).fetchall()
    return [get_meal_entry(connection, row["id"]) for row in rows]


def delete_meal_entry(connection: sqlite3.Connection, meal_entry_id: int) -> None:
    connection.execute("DELETE FROM meal_entries WHERE id = ?", (meal_entry_id,))


def get_meal_entry_item(connection: sqlite3.Connection, item_id: int) -> MealEntryItem:
    row = connection.execute(
        "SELECT * FROM meal_entry_items WHERE id = ?",
        (item_id,),
    ).fetchone()
    if row is None:
        raise LookupError(f"meal entry item not found: {item_id}")
    return _row_to_meal_entry_item(row)


def list_meal_entry_items(
    connection: sqlite3.Connection,
    meal_entry_id: int,
) -> list[MealEntryItem]:
    rows = connection.execute(
        """
        SELECT *
        FROM meal_entry_items
        WHERE meal_entry_id = ?
        ORDER BY id
        """,
        (meal_entry_id,),
    ).fetchall()
    return [_row_to_meal_entry_item(row) for row in rows]


def upsert_weight_log(connection: sqlite3.Connection, log: WeightLog) -> WeightLog:
    connection.execute(
        """
        INSERT INTO weight_logs (date, weight_lbs, note)
        VALUES (?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
          weight_lbs = excluded.weight_lbs,
          note = excluded.note,
          updated_at = CURRENT_TIMESTAMP
        """,
        (log.log_date.isoformat(), log.weight_lbs, log.note),
    )
    return get_weight_log(connection, log.log_date)


def get_weight_log(connection: sqlite3.Connection, log_date: date) -> WeightLog | None:
    row = connection.execute(
        "SELECT * FROM weight_logs WHERE date = ?",
        (log_date.isoformat(),),
    ).fetchone()
    return _row_to_weight_log(row) if row else None


def list_weight_logs(connection: sqlite3.Connection) -> list[WeightLog]:
    rows = connection.execute(
        "SELECT * FROM weight_logs ORDER BY date",
    ).fetchall()
    return [_row_to_weight_log(row) for row in rows]


def upsert_daily_note(connection: sqlite3.Connection, note: DailyNote) -> DailyNote:
    connection.execute(
        """
        INSERT INTO daily_notes (
          date,
          training_type,
          hunger_rating,
          energy_rating,
          adherence_note,
          freeform_note
        ) VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
          training_type = excluded.training_type,
          hunger_rating = excluded.hunger_rating,
          energy_rating = excluded.energy_rating,
          adherence_note = excluded.adherence_note,
          freeform_note = excluded.freeform_note,
          updated_at = CURRENT_TIMESTAMP
        """,
        (
            note.log_date.isoformat(),
            note.training_type,
            note.hunger_rating,
            note.energy_rating,
            note.adherence_note,
            note.freeform_note,
        ),
    )
    return get_daily_note(connection, note.log_date)


def get_daily_note(connection: sqlite3.Connection, log_date: date) -> DailyNote | None:
    row = connection.execute(
        "SELECT * FROM daily_notes WHERE date = ?",
        (log_date.isoformat(),),
    ).fetchone()
    return _row_to_daily_note(row) if row else None


def _row_to_macro_target(row: sqlite3.Row) -> MacroTarget:
    return MacroTarget(
        id=row["id"],
        start_date=date.fromisoformat(row["start_date"]),
        end_date=date.fromisoformat(row["end_date"]) if row["end_date"] else None,
        calories=row["calories"],
        protein_g=row["protein_g"],
        carbs_g=row["carbs_g"],
        fat_g=row["fat_g"],
        fiber_g=row["fiber_g"],
        goal_name=row["goal_name"],
    )


def _row_to_food_item(row: sqlite3.Row) -> FoodItem:
    return FoodItem(
        id=row["id"],
        name=row["name"],
        brand=row["brand"],
        default_unit=row["default_unit"],
        calories=row["calories_per_unit"],
        protein_g=row["protein_per_unit"],
        carbs_g=row["carbs_per_unit"],
        fat_g=row["fat_per_unit"],
        fiber_g=row["fiber_per_unit"],
        source=row["source"],
        confidence=row["confidence"],
    )


def _row_to_meal_entry(row: sqlite3.Row, items: tuple[MealEntryItem, ...]) -> MealEntry:
    return MealEntry(
        id=row["id"],
        log_date=date.fromisoformat(row["date"]),
        log_time=row["time"],
        raw_text=row["raw_text"],
        meal_name=row["meal_name"],
        items=items,
    )


def _row_to_meal_entry_item(row: sqlite3.Row) -> MealEntryItem:
    return MealEntryItem(
        id=row["id"],
        meal_entry_id=row["meal_entry_id"],
        food_item_id=row["food_item_id"],
        recipe_id=row["recipe_id"],
        name_snapshot=row["name_snapshot"],
        quantity=row["quantity"],
        unit=row["unit"],
        calories=row["calories"],
        protein_g=row["protein_g"],
        carbs_g=row["carbs_g"],
        fat_g=row["fat_g"],
        fiber_g=row["fiber_g"],
        source=row["source"],
        confidence=row["confidence"],
        user_overridden=bool(row["user_overridden"]),
    )


def _row_to_weight_log(row: sqlite3.Row) -> WeightLog:
    return WeightLog(
        log_date=date.fromisoformat(row["date"]),
        weight_lbs=row["weight_lbs"],
        note=row["note"],
    )


def _row_to_daily_note(row: sqlite3.Row) -> DailyNote:
    return DailyNote(
        id=row["id"],
        log_date=date.fromisoformat(row["date"]),
        training_type=row["training_type"],
        hunger_rating=row["hunger_rating"],
        energy_rating=row["energy_rating"],
        adherence_note=row["adherence_note"],
        freeform_note=row["freeform_note"],
    )


def _normalize_lookup(value: str) -> str:
    return " ".join(value.casefold().split())
