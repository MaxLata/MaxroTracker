from __future__ import annotations

import sqlite3
from datetime import date

from maxro_tracker.db.repositories import (
    create_meal_entry,
    get_active_daily_target,
    get_daily_note,
    get_food_item,
    get_weight_log,
    list_meal_entries_for_date,
    list_weight_logs,
    upsert_weight_log,
)
from maxro_tracker.domain.models import DaySummary, MacroTotals, MealEntry, MealEntryItem, WeightLog
from maxro_tracker.services.macro_calculator import (
    calculate_macro_percentages,
    calculate_remaining,
    scale_macro_totals,
    sum_macro_totals,
)
from maxro_tracker.services.weight_trend import calculate_rolling_average


def log_manual_macro_entry(
    connection: sqlite3.Connection,
    log_date: date,
    macros: MacroTotals,
    description: str,
    meal_name: str | None = None,
) -> MealEntry:
    return create_meal_entry(
        connection,
        MealEntry(log_date=log_date, raw_text=description, meal_name=meal_name),
        [
            MealEntryItem(
                name_snapshot=description,
                quantity=1,
                unit="manual entry",
                calories=macros.calories,
                protein_g=macros.protein_g,
                carbs_g=macros.carbs_g,
                fat_g=macros.fat_g,
                fiber_g=macros.fiber_g,
                source="manual",
                confidence="high",
                user_overridden=True,
            )
        ],
    )


def log_weight(
    connection: sqlite3.Connection,
    log_date: date,
    weight_lbs: float,
    note: str | None = None,
) -> WeightLog:
    return upsert_weight_log(
        connection,
        WeightLog(log_date=log_date, weight_lbs=weight_lbs, note=note),
    )


def log_known_food_entry(
    connection: sqlite3.Connection,
    log_date: date,
    food_item_id: int,
    quantity: float,
    meal_name: str | None = None,
) -> MealEntry:
    if quantity <= 0:
        raise ValueError("quantity must be positive")

    food = get_food_item(connection, food_item_id)
    scaled = scale_macro_totals(food, quantity)

    return create_meal_entry(
        connection,
        MealEntry(log_date=log_date, meal_name=meal_name),
        [
            MealEntryItem(
                food_item_id=food.id,
                name_snapshot=food.name,
                quantity=quantity,
                unit=food.default_unit,
                calories=scaled.calories,
                protein_g=scaled.protein_g,
                carbs_g=scaled.carbs_g,
                fat_g=scaled.fat_g,
                fiber_g=scaled.fiber_g,
                source=food.source,
                confidence=food.confidence,
            )
        ],
    )


def get_day_summary(connection: sqlite3.Connection, log_date: date) -> DaySummary:
    entries = tuple(list_meal_entries_for_date(connection, log_date))
    consumed = sum_macro_totals([item for entry in entries for item in entry.items])
    target = get_active_daily_target(connection)
    weight_logs = list_weight_logs(connection)

    return DaySummary(
        log_date=log_date,
        consumed=consumed,
        target=target,
        remaining=calculate_remaining(consumed, target) if target else None,
        percentages=calculate_macro_percentages(consumed, target) if target else None,
        entries=entries,
        weight_log=get_weight_log(connection, log_date),
        weight_average_7_day=calculate_rolling_average(weight_logs, as_of=log_date),
        note=get_daily_note(connection, log_date),
    )
