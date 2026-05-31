from __future__ import annotations

from maxro_tracker.domain.models import (
    AdherenceStatus,
    MacroPercentages,
    MacroTarget,
    MacroTotals,
    MealEntryItem,
)


def sum_macro_totals(items: list[MacroTotals] | list[MealEntryItem]) -> MacroTotals:
    """Sum stored macro values without recalculating from food definitions."""
    fiber_values = [item.fiber_g for item in items if item.fiber_g is not None]

    return MacroTotals(
        calories=sum(item.calories for item in items),
        protein_g=sum(item.protein_g for item in items),
        carbs_g=sum(item.carbs_g for item in items),
        fat_g=sum(item.fat_g for item in items),
        fiber_g=sum(fiber_values) if fiber_values else None,
    )


def calculate_remaining(consumed: MacroTotals, target: MacroTarget) -> MacroTotals:
    return MacroTotals(
        calories=target.calories - consumed.calories,
        protein_g=target.protein_g - consumed.protein_g,
        carbs_g=target.carbs_g - consumed.carbs_g,
        fat_g=target.fat_g - consumed.fat_g,
        fiber_g=_remaining_optional(consumed.fiber_g, target.fiber_g),
    )


def calculate_macro_percentages(consumed: MacroTotals, target: MacroTarget) -> MacroPercentages:
    return MacroPercentages(
        calories=_percentage(consumed.calories, target.calories),
        protein_g=_percentage(consumed.protein_g, target.protein_g),
        carbs_g=_percentage(consumed.carbs_g, target.carbs_g),
        fat_g=_percentage(consumed.fat_g, target.fat_g),
        fiber_g=_percentage(consumed.fiber_g, target.fiber_g),
    )


def calculate_adherence_status(consumed: MacroTotals, target: MacroTarget) -> AdherenceStatus:
    calorie_ratio = _ratio(consumed.calories, target.calories)
    protein_ratio = _ratio(consumed.protein_g, target.protein_g)

    if calorie_ratio is None or protein_ratio is None:
        return "red"

    calories_close = 0.9 <= calorie_ratio <= 1.1
    calories_near = 0.8 <= calorie_ratio <= 1.2
    protein_hit = protein_ratio >= 0.95
    protein_near = protein_ratio >= 0.85

    if calories_close and protein_hit:
        return "green"
    if calories_near and protein_near:
        return "yellow"
    return "red"


def _remaining_optional(consumed: float | None, target: float | None) -> float | None:
    if target is None:
        return None
    return target - (consumed or 0)


def _percentage(consumed: float | None, target: float | None) -> float | None:
    ratio = _ratio(consumed, target)
    if ratio is None:
        return None
    return ratio * 100


def _ratio(consumed: float | None, target: float | None) -> float | None:
    if consumed is None or target is None or target == 0:
        return None
    return consumed / target

