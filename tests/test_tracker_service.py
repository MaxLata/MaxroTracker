from datetime import date

from maxro_tracker.db.repositories import create_daily_target, create_food_item, open_database
from maxro_tracker.db.schema import initialize_database
from maxro_tracker.domain.models import FoodItem, MacroTarget, MacroTotals, WeightLog
from maxro_tracker.services.tracker import (
    get_day_summary,
    log_known_food_entry,
    log_manual_macro_entry,
    log_weight,
)


def test_log_manual_macro_entry_creates_high_confidence_snapshot(tmp_path) -> None:
    db_path = initialize_database(tmp_path / "maxro_tracker.sqlite", seed=False)

    with open_database(db_path) as connection:
        entry = log_manual_macro_entry(
            connection,
            date(2026, 5, 31),
            MacroTotals(calories=500, protein_g=40, carbs_g=50, fat_g=12),
            description="example manual meal",
            meal_name="lunch",
        )

    assert entry.meal_name == "lunch"
    assert entry.items[0].name_snapshot == "example manual meal"
    assert entry.items[0].source == "manual"
    assert entry.items[0].confidence == "high"
    assert entry.items[0].user_overridden is True


def test_log_known_food_entry_scales_food_macros_by_quantity(tmp_path) -> None:
    db_path = initialize_database(tmp_path / "maxro_tracker.sqlite", seed=False)

    with open_database(db_path) as connection:
        food = create_food_item(
            connection,
            FoodItem(
                name="example selected food",
                default_unit="serving",
                calories=120,
                protein_g=15,
                carbs_g=8,
                fat_g=4,
                fiber_g=2,
                source="personal_food",
                confidence="high",
            ),
        )

        entry = log_known_food_entry(
            connection,
            date(2026, 5, 31),
            food_item_id=food.id,
            quantity=2,
            meal_name="snack",
        )

    assert entry.items[0].food_item_id == food.id
    assert entry.items[0].name_snapshot == "example selected food"
    assert entry.items[0].quantity == 2
    assert entry.items[0].unit == "serving"
    assert entry.items[0].calories == 240
    assert entry.items[0].protein_g == 30
    assert entry.items[0].fiber_g == 4
    assert entry.items[0].source == "personal_food"


def test_log_known_food_entry_rejects_non_positive_quantity(tmp_path) -> None:
    db_path = initialize_database(tmp_path / "maxro_tracker.sqlite", seed=False)

    with open_database(db_path) as connection:
        food = create_food_item(
            connection,
            FoodItem(
                name="example selected food",
                default_unit="serving",
                calories=120,
                protein_g=15,
                carbs_g=8,
                fat_g=4,
            ),
        )

        try:
            log_known_food_entry(connection, date(2026, 5, 31), food.id, quantity=0)
        except ValueError as error:
            assert str(error) == "quantity must be positive"
        else:
            raise AssertionError("expected non-positive quantity to be rejected")


def test_get_day_summary_returns_consumed_remaining_and_percentages(tmp_path) -> None:
    db_path = initialize_database(tmp_path / "maxro_tracker.sqlite", seed=False)

    with open_database(db_path) as connection:
        create_daily_target(
            connection,
            MacroTarget(
                start_date=date(2026, 5, 1),
                calories=1000,
                protein_g=100,
                carbs_g=120,
                fat_g=30,
            ),
        )
        log_manual_macro_entry(
            connection,
            date(2026, 5, 31),
            MacroTotals(calories=400, protein_g=45, carbs_g=50, fat_g=10),
            description="example first meal",
        )
        log_manual_macro_entry(
            connection,
            date(2026, 5, 31),
            MacroTotals(calories=250, protein_g=20, carbs_g=30, fat_g=8),
            description="example second meal",
        )

        summary = get_day_summary(connection, date(2026, 5, 31))

    assert summary.consumed == MacroTotals(
        calories=650,
        protein_g=65,
        carbs_g=80,
        fat_g=18,
        fiber_g=None,
    )
    assert summary.remaining == MacroTotals(
        calories=350,
        protein_g=35,
        carbs_g=40,
        fat_g=12,
        fiber_g=None,
    )
    assert summary.percentages.calories == 65
    assert len(summary.entries) == 2


def test_get_day_summary_includes_weight_and_seven_day_average(tmp_path) -> None:
    db_path = initialize_database(tmp_path / "maxro_tracker.sqlite", seed=False)

    with open_database(db_path) as connection:
        for day in range(25, 32):
            log_weight(connection, date(2026, 5, day), weight_lbs=100 + day)

        summary = get_day_summary(connection, date(2026, 5, 31))

    assert summary.weight_log == WeightLog(log_date=date(2026, 5, 31), weight_lbs=131, note=None)
    assert summary.weight_average_7_day == 128
