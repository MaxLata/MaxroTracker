from datetime import date

from maxro_tracker.db.repositories import (
    add_food_alias,
    create_daily_target,
    create_food_item,
    create_meal_entry,
    delete_meal_entry,
    find_food_item,
    get_active_daily_target,
    get_daily_note,
    get_food_item,
    get_meal_entry,
    get_weight_log,
    list_meal_entries_for_date,
    list_weight_logs,
    open_database,
    upsert_daily_note,
    upsert_weight_log,
)
from maxro_tracker.db.schema import initialize_database
from maxro_tracker.domain.models import (
    DailyNote,
    FoodItem,
    MacroTarget,
    MealEntry,
    MealEntryItem,
    WeightLog,
)


def test_create_daily_target_and_get_active_target(tmp_path) -> None:
    db_path = initialize_database(tmp_path / "maxro_tracker.sqlite", seed=False)

    with open_database(db_path) as connection:
        create_daily_target(
            connection,
            MacroTarget(
                start_date=date(2026, 1, 1),
                calories=2100,
                protein_g=150,
                carbs_g=220,
                fat_g=60,
                goal_name="example old target",
            ),
        )
        newest = create_daily_target(
            connection,
            MacroTarget(
                start_date=date(2026, 2, 1),
                calories=2300,
                protein_g=160,
                carbs_g=240,
                fat_g=70,
                goal_name="example current target",
            ),
        )

        active = get_active_daily_target(connection)

    assert active == newest


def test_create_food_item_and_find_by_alias(tmp_path) -> None:
    db_path = initialize_database(tmp_path / "maxro_tracker.sqlite", seed=False)

    with open_database(db_path) as connection:
        food = create_food_item(
            connection,
            FoodItem(
                name="example food",
                default_unit="serving",
                calories=123,
                protein_g=12,
                carbs_g=20,
                fat_g=3,
                source="personal_food",
                confidence="high",
            ),
        )
        add_food_alias(connection, food.id, "Example Alias")

        by_name = find_food_item(connection, "example food")
        by_alias = find_food_item(connection, "  example   alias ")

    assert by_name == food
    assert by_alias == food


def test_create_meal_entry_with_item_snapshots(tmp_path) -> None:
    db_path = initialize_database(tmp_path / "maxro_tracker.sqlite", seed=False)

    with open_database(db_path) as connection:
        food = create_food_item(
            connection,
            FoodItem(
                name="example ingredient",
                default_unit="serving",
                calories=100,
                protein_g=10,
                carbs_g=12,
                fat_g=2,
                source="personal_food",
                confidence="high",
            ),
        )
        entry = create_meal_entry(
            connection,
            MealEntry(
                log_date=date(2026, 5, 31),
                raw_text="example meal",
                meal_name="lunch",
            ),
            [
                MealEntryItem(
                    food_item_id=food.id,
                    name_snapshot=food.name,
                    quantity=2,
                    unit="serving",
                    calories=200,
                    protein_g=20,
                    carbs_g=24,
                    fat_g=4,
                    fiber_g=None,
                    source=food.source,
                    confidence=food.confidence,
                )
            ],
        )
        connection.execute(
            "UPDATE food_items SET calories_per_unit = 999 WHERE id = ?",
            (food.id,),
        )

        loaded = get_meal_entry(connection, entry.id)
        loaded_food = get_food_item(connection, food.id)

    assert loaded.items[0].calories == 200
    assert loaded.items[0].name_snapshot == "example ingredient"
    assert loaded_food.calories == 999


def test_list_and_delete_meal_entries_for_date(tmp_path) -> None:
    db_path = initialize_database(tmp_path / "maxro_tracker.sqlite", seed=False)

    with open_database(db_path) as connection:
        first = create_meal_entry(
            connection,
            MealEntry(log_date=date(2026, 5, 31), meal_name="first"),
            [_manual_item("first item", calories=100)],
        )
        create_meal_entry(
            connection,
            MealEntry(log_date=date(2026, 5, 31), meal_name="second"),
            [_manual_item("second item", calories=200)],
        )

        assert len(list_meal_entries_for_date(connection, date(2026, 5, 31))) == 2

        delete_meal_entry(connection, first.id)
        remaining = list_meal_entries_for_date(connection, date(2026, 5, 31))

    assert len(remaining) == 1
    assert remaining[0].meal_name == "second"
    assert remaining[0].items[0].name_snapshot == "second item"


def test_upsert_weight_log_replaces_same_date(tmp_path) -> None:
    db_path = initialize_database(tmp_path / "maxro_tracker.sqlite", seed=False)

    with open_database(db_path) as connection:
        upsert_weight_log(connection, WeightLog(log_date=date(2026, 5, 31), weight_lbs=150))
        updated = upsert_weight_log(
            connection,
            WeightLog(log_date=date(2026, 5, 31), weight_lbs=151, note="example note"),
        )
        all_logs = list_weight_logs(connection)
        loaded = get_weight_log(connection, date(2026, 5, 31))

    assert updated.weight_lbs == 151
    assert loaded == updated
    assert all_logs == [updated]


def test_upsert_daily_note_replaces_same_date(tmp_path) -> None:
    db_path = initialize_database(tmp_path / "maxro_tracker.sqlite", seed=False)

    with open_database(db_path) as connection:
        upsert_daily_note(
            connection,
            DailyNote(log_date=date(2026, 5, 31), freeform_note="first note"),
        )
        updated = upsert_daily_note(
            connection,
            DailyNote(
                log_date=date(2026, 5, 31),
                training_type="training",
                freeform_note="updated note",
            ),
        )
        loaded = get_daily_note(connection, date(2026, 5, 31))

    assert loaded == updated
    assert updated.training_type == "training"
    assert updated.freeform_note == "updated note"


def _manual_item(name: str, calories: float) -> MealEntryItem:
    return MealEntryItem(
        name_snapshot=name,
        quantity=1,
        unit="manual entry",
        calories=calories,
        protein_g=10,
        carbs_g=10,
        fat_g=2,
        fiber_g=None,
        source="manual",
        confidence="high",
        user_overridden=True,
    )
