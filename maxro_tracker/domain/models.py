from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal


Confidence = Literal["high", "medium", "low"]
NutritionSource = Literal[
    "personal_food",
    "personal_recipe",
    "common_database",
    "nutrition_api",
    "manual",
    "llm_estimate",
]
AdherenceStatus = Literal["green", "yellow", "red"]


@dataclass(frozen=True)
class MacroTotals:
    calories: float = 0
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0
    fiber_g: float | None = None


@dataclass(frozen=True)
class MacroTarget(MacroTotals):
    id: int | None = None
    goal_name: str | None = None
    start_date: date | None = None
    end_date: date | None = None


@dataclass(frozen=True)
class MacroPercentages:
    calories: float | None
    protein_g: float | None
    carbs_g: float | None
    fat_g: float | None
    fiber_g: float | None = None


@dataclass(frozen=True)
class DaySummary:
    log_date: date
    consumed: MacroTotals
    target: MacroTarget | None = None
    remaining: MacroTotals | None = None
    percentages: MacroPercentages | None = None
    entries: tuple["MealEntry", ...] = ()
    weight_log: "WeightLog | None" = None
    weight_average_7_day: float | None = None
    note: "DailyNote | None" = None


@dataclass(frozen=True)
class MealEntryItem:
    name_snapshot: str
    quantity: float
    unit: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float | None
    source: NutritionSource
    confidence: Confidence
    food_item_id: int | None = None
    recipe_id: int | None = None
    user_overridden: bool = False
    id: int | None = None
    meal_entry_id: int | None = None


@dataclass(frozen=True)
class FoodItem(MacroTotals):
    name: str = ""
    default_unit: str = ""
    source: NutritionSource = "common_database"
    confidence: Confidence = "medium"
    brand: str | None = None
    id: int | None = None


@dataclass(frozen=True)
class MealEntry:
    log_date: date
    raw_text: str | None = None
    meal_name: str | None = None
    log_time: str | None = None
    id: int | None = None
    items: tuple[MealEntryItem, ...] = ()


@dataclass(frozen=True)
class ParsedFoodItem:
    name: str
    quantity: float | None
    unit: str | None
    confidence: Confidence
    preparation: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class ResolvedNutritionItem(MacroTotals):
    name_snapshot: str = ""
    quantity: float = 0
    unit: str = ""
    source: NutritionSource = "common_database"
    confidence: Confidence = "medium"
    food_item_id: int | None = None
    recipe_id: int | None = None
    needs_review: bool = False
    review_reason: str | None = None


@dataclass(frozen=True)
class WeightLog:
    log_date: date
    weight_lbs: float
    note: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True)
class DailyNote:
    log_date: date
    training_type: str | None = None
    hunger_rating: str | None = None
    energy_rating: str | None = None
    adherence_note: str | None = None
    freeform_note: str | None = None
    id: int | None = None
