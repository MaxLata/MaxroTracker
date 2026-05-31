PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS daily_targets (
  id INTEGER PRIMARY KEY,
  start_date TEXT NOT NULL,
  end_date TEXT NULL,
  calories INTEGER NOT NULL,
  protein_g REAL NOT NULL,
  carbs_g REAL NOT NULL,
  fat_g REAL NOT NULL,
  fiber_g REAL NULL,
  goal_name TEXT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS food_items (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  brand TEXT NULL,
  default_unit TEXT NOT NULL,
  calories_per_unit REAL NOT NULL,
  protein_per_unit REAL NOT NULL,
  carbs_per_unit REAL NOT NULL,
  fat_per_unit REAL NOT NULL,
  fiber_per_unit REAL NULL,
  source TEXT NOT NULL CHECK (source IN (
    'personal_food',
    'personal_recipe',
    'common_database',
    'nutrition_api',
    'manual',
    'llm_estimate'
  )),
  confidence TEXT NOT NULL CHECK (confidence IN ('high', 'medium', 'low')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_food_items_name_brand_unit
ON food_items (
  name,
  COALESCE(brand, ''),
  default_unit
);

CREATE TABLE IF NOT EXISTS food_aliases (
  id INTEGER PRIMARY KEY,
  food_item_id INTEGER NOT NULL,
  alias TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (food_item_id) REFERENCES food_items(id)
);

CREATE TABLE IF NOT EXISTS recipes (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  serving_name TEXT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recipe_components (
  id INTEGER PRIMARY KEY,
  recipe_id INTEGER NOT NULL,
  food_item_id INTEGER NOT NULL,
  quantity REAL NOT NULL,
  unit TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (recipe_id) REFERENCES recipes(id),
  FOREIGN KEY (food_item_id) REFERENCES food_items(id)
);

CREATE TABLE IF NOT EXISTS meal_entries (
  id INTEGER PRIMARY KEY,
  date TEXT NOT NULL,
  time TEXT NULL,
  raw_text TEXT NULL,
  meal_name TEXT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_meal_entries_date ON meal_entries(date);

CREATE TABLE IF NOT EXISTS meal_entry_items (
  id INTEGER PRIMARY KEY,
  meal_entry_id INTEGER NOT NULL,
  food_item_id INTEGER NULL,
  recipe_id INTEGER NULL,
  name_snapshot TEXT NOT NULL,
  quantity REAL NOT NULL,
  unit TEXT NOT NULL,
  -- Macro snapshots preserve what was logged at the time. Known foods and
  -- recipes can be corrected later without rewriting historical daily totals.
  calories REAL NOT NULL,
  protein_g REAL NOT NULL,
  carbs_g REAL NOT NULL,
  fat_g REAL NOT NULL,
  fiber_g REAL NULL,
  source TEXT NOT NULL CHECK (source IN (
    'personal_food',
    'personal_recipe',
    'common_database',
    'nutrition_api',
    'manual',
    'llm_estimate'
  )),
  confidence TEXT NOT NULL CHECK (confidence IN ('high', 'medium', 'low')),
  user_overridden INTEGER NOT NULL DEFAULT 0 CHECK (user_overridden IN (0, 1)),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (meal_entry_id) REFERENCES meal_entries(id) ON DELETE CASCADE,
  FOREIGN KEY (food_item_id) REFERENCES food_items(id),
  FOREIGN KEY (recipe_id) REFERENCES recipes(id)
);

CREATE INDEX IF NOT EXISTS idx_meal_entry_items_meal_entry_id
ON meal_entry_items(meal_entry_id);

CREATE TABLE IF NOT EXISTS weight_logs (
  id INTEGER PRIMARY KEY,
  date TEXT NOT NULL UNIQUE,
  weight_lbs REAL NOT NULL,
  note TEXT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_notes (
  id INTEGER PRIMARY KEY,
  date TEXT NOT NULL UNIQUE,
  training_type TEXT NULL,
  hunger_rating TEXT NULL,
  energy_rating TEXT NULL,
  adherence_note TEXT NULL,
  freeform_note TEXT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

