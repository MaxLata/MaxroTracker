import sqlite3

from maxro_tracker.db.schema import initialize_database


def test_initialize_database_creates_p0_tables(tmp_path) -> None:
    db_path = initialize_database(tmp_path / "maxro_tracker.sqlite")

    with sqlite3.connect(db_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

    assert {
        "daily_targets",
        "food_items",
        "food_aliases",
        "recipes",
        "recipe_components",
        "meal_entries",
        "meal_entry_items",
        "weight_logs",
        "daily_notes",
    }.issubset(tables)


def test_initialize_database_seeds_public_demo_food_only(tmp_path) -> None:
    db_path = initialize_database(tmp_path / "maxro_tracker.sqlite")

    with sqlite3.connect(db_path) as connection:
        foods = connection.execute(
            """
            SELECT name, source, confidence
            FROM food_items
            """
        ).fetchall()
        target_count = connection.execute("SELECT COUNT(*) FROM daily_targets").fetchone()[0]

    assert foods == [("demo food, per serving", "common_database", "low")]
    assert target_count == 0


def test_meal_item_snapshots_survive_food_definition_updates(tmp_path) -> None:
    db_path = initialize_database(tmp_path / "maxro_tracker.sqlite")

    with sqlite3.connect(db_path) as connection:
        food_id = connection.execute(
            "SELECT id FROM food_items WHERE name = 'demo food, per serving'"
        ).fetchone()[0]
        meal_id = connection.execute(
            "INSERT INTO meal_entries (date, raw_text) VALUES ('2026-05-31', 'demo meal')"
        ).lastrowid
        connection.execute(
            """
            INSERT INTO meal_entry_items (
              meal_entry_id,
              food_item_id,
              name_snapshot,
              quantity,
              unit,
              calories,
              protein_g,
              carbs_g,
              fat_g,
              source,
              confidence
            ) VALUES (?, ?, 'demo food, per serving', 1, 'serving', 100, 10, 10, 2,
                      'common_database', 'low')
            """,
            (meal_id, food_id),
        )
        connection.execute(
            "UPDATE food_items SET calories_per_unit = 999 WHERE id = ?",
            (food_id,),
        )

        snapshot_calories = connection.execute(
            "SELECT calories FROM meal_entry_items WHERE meal_entry_id = ?",
            (meal_id,),
        ).fetchone()[0]

    assert snapshot_calories == 100
