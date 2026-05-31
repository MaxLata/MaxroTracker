from maxro_tracker.domain.models import MacroTarget, MacroTotals, MealEntryItem
from maxro_tracker.services.macro_calculator import (
    calculate_adherence_status,
    calculate_macro_percentages,
    calculate_remaining,
    sum_macro_totals,
)


def test_sum_macro_totals_sums_meal_item_snapshots() -> None:
    items = [
        _item("chicken", calories=330, protein_g=62, carbs_g=0, fat_g=7),
        _item("rice", calories=360, protein_g=7, carbs_g=80, fat_g=1),
    ]

    totals = sum_macro_totals(items)

    assert totals == MacroTotals(calories=690, protein_g=69, carbs_g=80, fat_g=8, fiber_g=None)


def test_sum_macro_totals_handles_missing_and_present_fiber() -> None:
    totals = sum_macro_totals(
        [
            MacroTotals(calories=100, protein_g=5, carbs_g=20, fat_g=1, fiber_g=None),
            MacroTotals(calories=50, protein_g=1, carbs_g=10, fat_g=0, fiber_g=3),
        ]
    )

    assert totals.fiber_g == 3


def test_calculate_remaining_subtracts_consumed_from_target() -> None:
    consumed = MacroTotals(calories=1420, protein_g=152, carbs_g=120, fat_g=34)
    target = MacroTarget(id=1, calories=2000, protein_g=170, carbs_g=180, fat_g=55)

    remaining = calculate_remaining(consumed, target)

    assert remaining == MacroTotals(calories=580, protein_g=18, carbs_g=60, fat_g=21, fiber_g=None)


def test_calculate_macro_percentages_returns_none_for_missing_or_zero_target() -> None:
    consumed = MacroTotals(calories=1000, protein_g=100, carbs_g=0, fat_g=20)
    target = MacroTarget(id=1, calories=2000, protein_g=0, carbs_g=100, fat_g=40)

    percentages = calculate_macro_percentages(consumed, target)

    assert percentages.calories == 50
    assert percentages.protein_g is None
    assert percentages.carbs_g == 0
    assert percentages.fat_g == 50


def test_calculate_adherence_status_green_when_calories_close_and_protein_hit() -> None:
    consumed = MacroTotals(calories=1980, protein_g=170, carbs_g=180, fat_g=55)
    target = MacroTarget(id=1, calories=2000, protein_g=170, carbs_g=180, fat_g=55)

    assert calculate_adherence_status(consumed, target) == "green"


def test_calculate_adherence_status_yellow_when_close_but_imperfect() -> None:
    consumed = MacroTotals(calories=1800, protein_g=150, carbs_g=180, fat_g=55)
    target = MacroTarget(id=1, calories=2000, protein_g=170, carbs_g=180, fat_g=55)

    assert calculate_adherence_status(consumed, target) == "yellow"


def test_calculate_adherence_status_red_when_missed_substantially() -> None:
    consumed = MacroTotals(calories=1300, protein_g=80, carbs_g=180, fat_g=55)
    target = MacroTarget(id=1, calories=2000, protein_g=170, carbs_g=180, fat_g=55)

    assert calculate_adherence_status(consumed, target) == "red"


def _item(
    name: str,
    calories: float,
    protein_g: float,
    carbs_g: float,
    fat_g: float,
    fiber_g: float | None = None,
) -> MealEntryItem:
    return MealEntryItem(
        name_snapshot=name,
        quantity=1,
        unit="test",
        calories=calories,
        protein_g=protein_g,
        carbs_g=carbs_g,
        fat_g=fat_g,
        fiber_g=fiber_g,
        source="manual",
        confidence="high",
    )

