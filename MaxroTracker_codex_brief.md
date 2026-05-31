# MaxroTracker Local — Codex Project Brief

## Purpose

This document is a starting artifact to give to Codex for scaffolding a first personal project.

The goal is **not** to have Codex magically generate the full app. The goal is to use Codex as a coding SME that can propose file structure, function signatures, implementation steps, tests, and small vetted functions.

The app should be built incrementally, with the human reviewing and approving each layer.

---

# Product Summary

## Working name

**MaxroTracker**

## Core idea

A local-first macro and weight tracking app that lets the user enter food in natural language, stores structured nutrition data locally, and shows daily macro progress plus weight trend.

The app should feel lower-friction than MyFitnessPal while being more structured and trustworthy than using ChatGPT alone.

User is a developer who prefers Python for anything logical. For rendering, user can understand Javascript, but prefers it to only be at rendering level. 

## Core product thesis

This is **not** “an LLM that tracks macros.”

It is:

> A structured macro tracker with an LLM-powered input layer and coaching layer.

The LLM should help parse, explain, and suggest. It should not be the source of truth for nutrition values.

---

# User Goals

The user wants to:

1. Quickly log food using natural language.
2. See calories, protein, carbs, and fat for the current day.
3. Know what remains to eat for the day.
4. Manually override or edit macros when needed.
5. Track body weight.
6. See whether consistent macro adherence corresponds with weight trend.
7. Keep data local at first.
8. Avoid overbuilding cloud sync, barcode scanning, or a full mobile app in the first version.

---

# Non-Goals for First Version

Do **not** build these in the initial scaffold:

- Authentication
- Cloud backend
- iPhone app
- Barcode scanning
- Photo meal estimation
- Full USDA/nutrition database integration
- Social features
- Automatic macro target optimization
- Complex meal planning
- Multi-user support
- Payment/subscriptions

---

# Recommended Initial Stack

Codex should help evaluate this stack, but the proposed default is:

- Frontend: local web app
- Framework: React or Next.js
- Backend: Python
- Database: SQLite
- LLM integration: abstraction layer, initially mockable
- Runtime: local development on MacBook Pro

Important: the LLM provider should be swappable.

Possible providers:

- Mock provider for tests
- Local provider through Ollama
- Remote provider later

The app should not hard-code one LLM provider deeply into business logic.

---

# Product Principles

1. **Fast beats perfect**  
   A rough logged day is better than an unlogged day.

2. **Structured state beats chat history**  
   Food logs, weights, targets, and notes should be stored as structured records.

3. **LLM estimates must be labeled**  
   Never silently pretend low-confidence estimates are precise.

4. **Manual overrides are first-class**  
   The user should be able to log exact calories/macros without specifying food items.

5. **Personal foods beat generic databases**  
   The user eats many repeat foods. A personal food library should be central.

6. **Weight trend is the outcome layer**  
   Macros are inputs. Weight trend, training performance, and adherence are outcomes.

---

# P0 Requirements

## P0.1 Macro targets

User can set daily targets:

- Calories
- Protein grams
- Carbs grams
- Fat grams
- Optional: fiber grams later

For first version, a single active target is enough.

Example target:

```text
2,000 kcal
170g protein
180g carbs
55g fat
```

---

## P0.2 Manual macro entries

Before natural language food parsing, the app should support manual entries.

Example input:

```text
Add 500 calories, 40 protein, 50 carbs, 12 fat as lunch estimate
```

Expected behavior:

- Create a meal entry for today.
- Store macro values directly.
- Mark source as `manual`.
- Mark confidence as `high` because the user provided the values.

---

## P0.3 Known food library

The app should support a local table of known foods.

Examples:

- Chicken breast, raw, per 100g
- White rice, dry, per gram
- Quinoa, dry, per gram
- ON whey, one scoop
- Banana, medium
- Whole milk, per cup
- Greek yogurt, per 100g or per serving
- Frozen berries, per cup
- Rice Krispie Treat, one bar
- Core Power 42g, one bottle
- Cucumber
- Cherry tomatoes
- Feta
- Olive oil
- Sesame oil
- Eggs
- Potatoes
- Edamame
- Carrots

Known foods should provide trusted nutrition values and be used before any LLM estimate.

---

## P0.4 Natural language food logging

User can type:

```text
Log 300g chicken breast, 1/2 cup dry rice, cucumber, 2 tbsp feta.
```

Expected behavior:

1. LLM parses the text into candidate food items and quantities.
2. App attempts to match candidates to known foods.
3. App computes macros from structured food records.
4. App stores a meal entry and item-level snapshots.
5. UI shows updated daily totals.

Important: the LLM should not directly decide final macro totals unless there is no known-food match and the user accepts a low-confidence estimate.

---

## P0.5 Today dashboard

The app should show:

- Calories consumed / target
- Protein consumed / target
- Carbs consumed / target
- Fat consumed / target
- Remaining calories
- Remaining protein
- Remaining carbs
- Remaining fat

Example:

```text
Calories: 1,420 / 2,000
Protein: 152 / 170g
Carbs: 120 / 180g
Fat: 34 / 55g
```

---

## P0.6 Edit and delete entries

User can correct entries.

Examples:

```text
Actually the chicken was 250g.
```

```text
Remove the feta.
```

```text
That rice was cooked, not dry.
```

For first scaffold, this can be implemented manually through UI controls before NLP correction is added.

---

## P0.7 Weight tracking

User can log daily body weight.

Example:

```text
Weight 153.8
```

Expected behavior:

- Store date and weight.
- Show current weight.
- Show 7-day average if enough data exists.
- Show recent trend later.

---

## P0.8 Daily notes

User can optionally add notes to a day.

Examples:

- Training day
- Rest day
- High hunger
- Poor sleep
- Big hike
- Ate out
- Felt flat in workout

This supports later analysis of “stacked good days.”

---

# P1 Requirements

Do not build immediately unless P0 is stable.

## P1.1 Recipes / personal foods

User can define repeat meals.

Example:

```text
my smoothie = banana + 2 scoops whey + 3/4 cup whole milk + 1/2 cup Greek yogurt + 1/2 cup frozen berries
```

Then user can log:

```text
Had my smoothie.
```

---

## P1.2 Confidence labeling

Every logged item should have:

```text
source:
- personal_food
- personal_recipe
- nutrition_api
- common_database
- manual
- llm_estimate

confidence:
- high
- medium
- low
```

Example UI:

```text
Chicken breast, raw, 300g — high confidence
Restaurant curry bowl — low confidence
```

---

## P1.3 Recommendation engine

Given current macros and daily targets, the app can suggest what to eat next.

Example:

```text
You have 580 calories left, with 18g protein, 70g carbs, and 21g fat remaining.
Protein is mostly handled. A carb-forward dinner with moderate fat would fit best.
```

The recommendation should use structured macro state, not freeform guesses.

---

# Suggested Database Design

Use SQLite.

The database should be local and easy to inspect.

Suggested dev path:

```text
./data/macrocoach.sqlite
```

Suggested production-ish local path later:

```text
~/Library/Application Support/MacroCoach/macrocoach.sqlite
```

---

## Table: daily_targets

Purpose: store active macro targets.

Suggested fields:

```sql
id INTEGER PRIMARY KEY
start_date TEXT NOT NULL
end_date TEXT NULL
calories INTEGER NOT NULL
protein_g REAL NOT NULL
carbs_g REAL NOT NULL
fat_g REAL NOT NULL
fiber_g REAL NULL
goal_name TEXT NULL
created_at TEXT NOT NULL
updated_at TEXT NOT NULL
```

For first version, assume one active target where `end_date IS NULL`.

---

## Table: food_items

Purpose: canonical known foods.

Suggested fields:

```sql
id INTEGER PRIMARY KEY
name TEXT NOT NULL
brand TEXT NULL
default_unit TEXT NOT NULL
calories_per_unit REAL NOT NULL
protein_per_unit REAL NOT NULL
carbs_per_unit REAL NOT NULL
fat_per_unit REAL NOT NULL
fiber_per_unit REAL NULL
source TEXT NOT NULL
confidence TEXT NOT NULL
created_at TEXT NOT NULL
updated_at TEXT NOT NULL
```

Examples:

```text
Chicken breast, raw, per 100g
ON whey, one scoop
Rice Krispie Treat, one bar
Banana, medium
```

---

## Table: recipes

Purpose: saved repeat meals.

```sql
id INTEGER PRIMARY KEY
name TEXT NOT NULL
serving_name TEXT NULL
created_at TEXT NOT NULL
updated_at TEXT NOT NULL
```

---

## Table: recipe_components

Purpose: foods inside recipes.

```sql
id INTEGER PRIMARY KEY
recipe_id INTEGER NOT NULL
food_item_id INTEGER NOT NULL
quantity REAL NOT NULL
unit TEXT NOT NULL
created_at TEXT NOT NULL
updated_at TEXT NOT NULL
```

---

## Table: meal_entries

Purpose: top-level food logging event.

```sql
id INTEGER PRIMARY KEY
date TEXT NOT NULL
time TEXT NULL
raw_text TEXT NULL
meal_name TEXT NULL
created_at TEXT NOT NULL
updated_at TEXT NOT NULL
```

Example raw text:

```text
Had my smoothie and 300g chicken with rice
```

---

## Table: meal_entry_items

Purpose: item-level historical macro snapshots.

Important: store macro snapshots at logging time.

Do not rely only on food IDs. If the known food or recipe changes later, old meal logs should remain historically accurate.

```sql
id INTEGER PRIMARY KEY
meal_entry_id INTEGER NOT NULL
food_item_id INTEGER NULL
recipe_id INTEGER NULL
name_snapshot TEXT NOT NULL
quantity REAL NOT NULL
unit TEXT NOT NULL
calories REAL NOT NULL
protein_g REAL NOT NULL
carbs_g REAL NOT NULL
fat_g REAL NOT NULL
fiber_g REAL NULL
source TEXT NOT NULL
confidence TEXT NOT NULL
user_overridden INTEGER NOT NULL DEFAULT 0
created_at TEXT NOT NULL
updated_at TEXT NOT NULL
```

---

## Table: weight_logs

Purpose: daily body weight entries.

```sql
id INTEGER PRIMARY KEY
date TEXT NOT NULL
weight_lbs REAL NOT NULL
note TEXT NULL
created_at TEXT NOT NULL
updated_at TEXT NOT NULL
```

Consider enforcing one weight log per date, or allow multiple and treat latest as current.

---

## Table: daily_notes

Purpose: optional qualitative day-level notes.

```sql
id INTEGER PRIMARY KEY
date TEXT NOT NULL
training_type TEXT NULL
hunger_rating TEXT NULL
energy_rating TEXT NULL
adherence_note TEXT NULL
freeform_note TEXT NULL
created_at TEXT NOT NULL
updated_at TEXT NOT NULL
```

---

# Key Architecture Boundaries

## LLMProvider

Create an interface like:

```ts
interface LLMProvider {
  parseFoodLog(input: string): Promise<ParsedFoodLog>;
  parseCorrection(input: string, currentDay: DayState): Promise<ParsedCorrection>;
  generateRecommendation(dayState: DayState, target: MacroTarget): Promise<string>;
}
```

Implementations:

```text
MockLLMProvider
OllamaLLMProvider later
RemoteLLMProvider later
```

Start with `MockLLMProvider` or a very basic parser so the rest of the app can be built and tested without depending on an LLM.

---

## NutritionResolver

Responsible for turning parsed food candidates into actual macro records.

Suggested responsibilities:

1. Match parsed item to personal recipe.
2. Match parsed item to known food.
3. Convert units if possible.
4. Compute macros.
5. Return confidence/source.
6. Flag ambiguity.

Do not put this logic inside the LLM provider.

Suggested interface:

```ts
interface NutritionResolver {
  resolveItems(items: ParsedFoodItem[]): Promise<ResolvedNutritionItem[]>;
}
```

---

## MacroCalculator

Pure functions for calculating totals.

Examples:

```ts
sumMealItems(items: MealEntryItem[]): MacroTotals
calculateRemaining(consumed: MacroTotals, target: MacroTarget): MacroRemaining
calculateMacroPercentages(consumed: MacroTotals, target: MacroTarget): MacroPercentages
```

These functions should not call the database or LLM.

They should be easy to unit test.

---

## WeightTrendService

Pure or mostly pure functions for weight analysis.

Examples:

```ts
calculateRollingAverage(weights: WeightLog[], days: number): number | null
calculateWeeklyRate(weights: WeightLog[]): number | null
```

Start with 7-day average only.

---

# Types

Suggested TypeScript types.

```ts
type Confidence = "high" | "medium" | "low";

type NutritionSource =
  | "personal_food"
  | "personal_recipe"
  | "common_database"
  | "nutrition_api"
  | "manual"
  | "llm_estimate";

interface MacroTotals {
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g?: number | null;
}

interface MacroTarget extends MacroTotals {
  id: number;
  goal_name?: string | null;
}

interface ParsedFoodLog {
  intent: "log_food";
  rawText: string;
  items: ParsedFoodItem[];
}

interface ParsedFoodItem {
  name: string;
  quantity: number | null;
  unit: string | null;
  preparation?: string | null;
  notes?: string | null;
  confidence: Confidence;
}

interface ResolvedNutritionItem extends MacroTotals {
  name_snapshot: string;
  quantity: number;
  unit: string;
  food_item_id?: number | null;
  recipe_id?: number | null;
  source: NutritionSource;
  confidence: Confidence;
  needsReview?: boolean;
  reviewReason?: string | null;
}
```

---

# LLM Usage Rules

Codex should preserve these rules when generating code.

1. The LLM parses user text into structured candidates.
2. The LLM does not silently invent nutrition values when a known value is unavailable.
3. If an LLM estimate is used, mark it as `source = "llm_estimate"` and `confidence = "low"` unless explicitly reviewed.
4. All LLM outputs must be schema-validated.
5. All user-facing totals should come from structured records, not raw LLM prose.
6. The app should work in a limited mode without any LLM provider.

---

# Example User Inputs and Expected Structured Output

## Example 1

Input:

```text
Log 300g chicken breast and 1/2 cup dry rice
```

Expected parsed output:

```json
{
  "intent": "log_food",
  "rawText": "Log 300g chicken breast and 1/2 cup dry rice",
  "items": [
    {
      "name": "chicken breast",
      "quantity": 300,
      "unit": "g",
      "preparation": "raw",
      "confidence": "medium"
    },
    {
      "name": "white rice",
      "quantity": 0.5,
      "unit": "cup dry",
      "preparation": "dry",
      "confidence": "medium"
    }
  ]
}
```

---

## Example 2

Input:

```text
Add 600 calories, 35 protein, 60 carbs, 20 fat as restaurant lunch
```

Expected behavior:

Create a manual macro item:

```json
{
  "name_snapshot": "restaurant lunch",
  "quantity": 1,
  "unit": "manual entry",
  "calories": 600,
  "protein_g": 35,
  "carbs_g": 60,
  "fat_g": 20,
  "source": "manual",
  "confidence": "high",
  "user_overridden": true
}
```

---

## Example 3

Input:

```text
Weight 153.8
```

Expected behavior:

Create or update today’s weight log:

```json
{
  "date": "today",
  "weight_lbs": 153.8
}
```

---

# Initial Seed Foods

Codex can generate a seed file, but the user should verify nutrition values.

Seed foods should include placeholders or clearly marked approximate values.

Do not pretend values are verified unless the user manually provides them.

Suggested seed list:

```text
chicken breast raw per 100g
white rice dry per 100g
quinoa dry per 100g
Optimum Nutrition whey one scoop
banana medium
whole milk one cup
plain Greek yogurt per 100g
frozen mixed berries per 100g
Rice Krispie Treat one bar
Core Power 42g one bottle
cucumber per 100g
cherry tomatoes per 100g
feta per 28g
olive oil per tbsp
sesame oil per tbsp
egg large
russet potato per 100g
shelled edamame per 100g
carrots per 100g
```

---

# Suggested First Milestone

## Milestone 1: No LLM, structured tracker only

Deliver:

1. SQLite schema and migrations.
2. Seed known foods.
3. Manual macro entry.
4. Add known food by selecting food + quantity.
5. Today dashboard.
6. Weight logging.
7. 7-day weight average.

This milestone proves the app can track state.

---

# Suggested Second Milestone

## Milestone 2: Basic natural language input

Deliver:

1. Input box for commands.
2. Parser for manual macro command.
3. Parser for weight command.
4. Mock or simple rule-based parser for common food commands.
5. Route parsed foods through NutritionResolver.
6. Show unresolved items for review instead of guessing.

---

# Suggested Third Milestone

## Milestone 3: LLM parser abstraction

Deliver:

1. `LLMProvider` interface.
2. `MockLLMProvider` for tests.
3. Optional local provider implementation.
4. JSON schema validation for parsed LLM output.
5. Tests proving invalid LLM responses are rejected.

---

# Suggested Fourth Milestone

## Milestone 4: Coaching and recommendations

Deliver:

1. Macro remaining summary.
2. Recommendation generator using structured day state.
3. High/medium/low confidence summary.
4. Simple adherence labels:
   - Green: calories within target range and protein hit
   - Yellow: close but imperfect
   - Red: missed substantially

---

# Testing Requirements

Codex should suggest tests before implementation where possible.

Priority tests:

## MacroCalculator tests

- Sums meal item calories correctly.
- Sums protein/carbs/fat correctly.
- Calculates remaining macros correctly.
- Handles missing fiber.

## NutritionResolver tests

- Resolves known food exact match.
- Resolves common alias.
- Flags unknown food as needs review.
- Does not invent macros for unknown food.

## WeightTrendService tests

- Calculates 7-day average.
- Handles fewer than 7 entries.
- Handles multiple entries on same date if allowed.

## LLMProvider validation tests

- Accepts valid parsed food JSON.
- Rejects missing quantity when required.
- Rejects invalid confidence values.
- Rejects malformed JSON.

---

# Codex Collaboration Instructions

When using Codex, ask it to work in small increments.

Recommended style:

```text
Do not implement the whole app. First propose a folder structure and explain why.
```

Then:

```text
Generate only the TypeScript types and pure macro calculator functions, with tests.
```

Then:

```text
Generate the SQLite schema and migration file. Do not build the UI yet.
```

Then:

```text
Generate a repository layer for daily targets, meal entries, meal items, and weight logs.
```

Then:

```text
Generate a minimal UI that reads from those repositories.
```

Important constraints to give Codex:

1. Do not skip tests for pure logic.
2. Do not hard-code one LLM provider into business logic.
3. Do not store nutrition state only in chat messages.
4. Do not silently use LLM estimates as truth.
5. Do not add cloud/auth/mobile features yet.
6. Favor small, reviewable functions.
7. Explain tradeoffs before adding a dependency.

---

# Suggested First Prompt to Codex

Use this as the first prompt:

```text
I am building a first personal project called MacroCoach Local. It is a local-first macro and weight tracking app with a natural language input layer. I want you to act as a coding SME, not just generate a whole app.

Please read the attached project brief. For the first step, do not write implementation code yet. Propose:

1. A simple stack recommendation for a local Mac-first app.
2. A folder/module structure.
3. The first 4 implementation milestones.
4. The first set of pure functions and TypeScript types we should implement.
5. A testing strategy for those pure functions.

Constraints:
- Use SQLite locally.
- Keep LLM integration behind an interface.
- The app must work in a limited mode without an LLM.
- Do not build cloud sync, auth, barcode scanning, or iPhone support yet.
- The LLM should parse food text into structured candidates, not be treated as the source of nutrition truth.
- Prefer small, reviewable functions that I can vet.
```

---

# Suggested Second Prompt to Codex

After reviewing the first response, use:

```text
Now generate only the TypeScript domain types and pure utility functions for macro totals, remaining macros, macro percentages, and simple adherence status. Include unit tests. Do not generate database code or UI code yet.
```

---

# Suggested Third Prompt to Codex

```text
Now generate the SQLite schema and migration files for the P0 data model. Include comments explaining why meal_entry_items stores macro snapshots. Do not generate UI code yet.
```

---

# Suggested Fourth Prompt to Codex

```text
Now generate a repository/data-access layer for daily targets, meal entries, meal entry items, food items, and weight logs. Keep functions small and testable. Do not add an LLM provider yet.
```

---

# Open Product Questions

These do not need to block the first scaffold, but should be answered soon. 

I, Max Lata the developer, have answered below with a > 

1. Should the app be Next.js, Vite React, Electron, Tauri, or native SwiftUI?
> Electron
2. Should weight logs allow multiple entries per day or upsert one per day?
> Just one per day is fine. I weigh myself every morning
3. Should macro targets be global or date-ranged from the start?
> Keep a table of macro targets where you can just select the last one inputted as the current goal.
4. Should the app use grams internally for all food quantities?
> App should default to grams internally. Take any other measurements like one cup dry rice and convert internally.
5. How should ambiguous units be handled, especially rice cooked vs dry?
> Dry/raw. Use context clues from prompt like "at home, cooked" to mean dry as user has a food scale.
6. Should recipes update historical logs or only future logs?
   > Recommended answer: only future logs; meal entries store snapshots.
7. Should unknown foods be blocked until reviewed, or logged as low-confidence estimates?
   > Recommended answer: ask for review by default.

---

# Recommended First Implementation Rule

Build the structured core first.

The order should be:

```text
Types → pure functions → tests → SQLite schema → repositories → minimal UI → NLP parser → LLM provider → recommendations
```

Do not start with the LLM.

The app becomes useful when structured data is reliable. The LLM should make input easier, not make the system magical and fragile.

