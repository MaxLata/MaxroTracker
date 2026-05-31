-- Public demo data only.
--
-- Real targets, foods, recipes, and aliases are user-specific and should be
-- written into the local SQLite database through app flows or private,
-- gitignored seed files.

INSERT OR IGNORE INTO food_items (
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
) VALUES
  ('demo food, per serving', NULL, 'serving', 100, 10, 10, 2, NULL, 'common_database', 'low');

